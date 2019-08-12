import abc
import asyncio
import json
from typing import ClassVar, List, Tuple
from pathlib import Path

from grpclib.client import Channel
from grpclib.utils import Wrapper

from golem_task_api.messages import (
    CreateTaskRequest,
    CreateTaskReply,
    NextSubtaskRequest,
    NextSubtaskReply,
    ComputeRequest,
    ComputeReply,
    VerifyRequest,
    VerifyReply,
    DiscardSubtasksRequest,
    DiscardSubtasksReply,
    RunBenchmarkRequest,
    RunBenchmarkReply,
    HasPendingSubtasksRequest,
    HasPendingSubtasksReply,
    ShutdownRequest,
)
from golem_task_api.proto.golem_task_api_grpc import (
    ProviderAppStub,
    RequestorAppStub,
)
from golem_task_api.structs import Subtask

class ShutdownException(Exception):
    pass

class TaskApiService(abc.ABC):

    @abc.abstractmethod
    def running(self) -> bool:
        """
        Checks if the service is still running.
        E.g. For inline this would be implemented as:
        `thread.is_alive()`
        """
        pass

    @abc.abstractmethod
    async def start(self, command: str, port: int) -> Tuple[str, int]:
        """
        This method is supposed to pass the command argument to the entrypoint
        which will asynchronously spawn the server and should return a tuple
        (host, port) where one can connect to this server. The method **should
        not** use the event loop in which it is being called to run the service
        (but rather spawn a new thread or process).
        E.g. for Docker app this could be implemented as:
        `docker run --detach <command>`
        """
        pass

    @abc.abstractmethod
    async def wait_until_shutdown_complete(self) -> None:
        """
        After sending the Shutdown request one should wait for the server to
        finish it's cleanup and shutdown completely.
        E.g. for Docker app this should wait for the container to exit
        """
        pass


class RequestorAppClient:
    DEFAULT_PORT: ClassVar[int] = 50005

    @classmethod
    async def create(
            cls,
            service: TaskApiService,
            port: int = DEFAULT_PORT
    ) -> 'RequestorAppClient':
        host, port = await service.start(f'requestor {port}', port)
        app_stub = RequestorAppStub(
            Channel(host, port, loop=asyncio.get_event_loop())
        )
        return cls(service, app_stub)

    def __init__(
            self,
            service: TaskApiService,
            app_stub: RequestorAppStub,
    ) -> None:
        self._service = service
        self._golem_app = app_stub

    async def create_task(
            self,
            task_id: str,
            max_subtasks_count: int,
            task_params: dict,
    ) -> None:
        request = CreateTaskRequest()
        request.task_id = task_id
        request.max_subtasks_count = max_subtasks_count
        request.task_params_json = json.dumps(task_params)
        await self._golem_app.CreateTask(request)

    async def next_subtask(
            self,
            task_id: str,
    ) -> Subtask:
        request = NextSubtaskRequest()
        request.task_id = task_id
        reply = await self._golem_app.NextSubtask(request)
        return Subtask(
            subtask_id=reply.subtask_id,
            params=json.loads(reply.subtask_params_json),
            resources=reply.resources,
        )

    async def verify(
            self,
            task_id: str,
            subtask_id: str,
    ) -> bool:
        request = VerifyRequest()
        request.task_id = task_id
        request.subtask_id = subtask_id
        reply = await self._golem_app.Verify(request)
        return reply.success

    async def discard_subtasks(
            self,
            task_id: str,
            subtask_ids: List[str],
    ) -> List[str]:
        request = DiscardSubtasksRequest()
        request.task_id = task_id
        request.subtask_ids.extend(subtask_ids)
        reply = await self._golem_app.DiscardSubtasks(request)
        return reply.discarded_subtask_ids

    async def run_benchmark(self) -> float:
        request = RunBenchmarkRequest()
        reply = await self._golem_app.RunBenchmark(request)
        return reply.score

    async def has_pending_subtasks(self, task_id: str) -> bool:
        request = HasPendingSubtasksRequest()
        request.task_id = task_id
        reply = await self._golem_app.HasPendingSubtasks(request)
        return reply.has_pending_subtasks

    async def shutdown(self) -> None:
        request = ShutdownRequest()
        await self._golem_app.Shutdown(request)
        await self._service.wait_until_shutdown_complete()


class ProviderAppClient:
    DEFAULT_PORT: ClassVar[int] = 50006

    @classmethod
    async def create(
            cls,
            service: TaskApiService,
            port: int = DEFAULT_PORT
    ) -> 'ProviderAppClient':
        host, port = await service.start(f'provider {port}', port)
        app_stub = ProviderAppStub(
            Channel(host, port, loop=asyncio.get_event_loop())
        )
        return cls(service, app_stub)

    def __init__(
            self,
            service: TaskApiService,
            app_stub: ProviderAppStub,
    ) -> None:
        self._service = service
        self._golem_app = app_stub
        self._kill_switch = Wrapper()

    async def compute(
            self,
            task_id: str,
            subtask_id: str,
            subtask_params: dict,
    ) -> Path:
        request = ComputeRequest()
        request.task_id = task_id
        request.subtask_id = subtask_id
        request.subtask_params_json = json.dumps(subtask_params)
        try:
            with self._kill_switch:
                reply = await self._golem_app.Compute(request)
        except Exception as e:
            print('TODO: Set status / use finally or remove this try block')
            print('ERROR in Compute:', e)
            raise
        await self._service.wait_until_shutdown_complete()
        return Path(reply.output_filepath)

    async def run_benchmark(self) -> float:
        request = RunBenchmarkRequest()
        try:
            with self._kill_switch:
                reply = await self._golem_app.RunBenchmark(request)
        except Exception as e:
            print('TODO: Set status / use finally or remove this try block')
            print('ERROR in RunBenchmark:', e)
            raise
        await self._service.wait_until_shutdown_complete()
        return reply.score

    async def shutdown(self) -> None:
        if not self._kill_switch.cancelled:
            self._kill_switch.cancel(ShutdownException("Shutdown requested"))
        if not self._service.running():
            return
        request = ShutdownRequest()
        await self._golem_app.Shutdown(request)
        await self._service.wait_until_shutdown_complete()

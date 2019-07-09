import abc
import asyncio
import json
from typing import ClassVar, List, NamedTuple, Tuple
from pathlib import Path

from grpclib.client import Channel

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


class AppCallbacks(abc.ABC):
    @abc.abstractmethod
    def spawn_server(self, command: str, port: int) -> Tuple[str, int]:
        """
        This method is supposed to pass the command argument to the entrypoint
        which will asynchronously spawn the server and should return a tuple
        (host, port) where one can connect to this server.
        E.g. for Docker app this could be implemented as:
        `docker run --detach <command>`
        """
        pass

    @abc.abstractmethod
    async def wait_after_shutdown(self) -> None:
        """
        After sending the Shutdown request one should wait for the server to
        finish it's cleanup and shutdown completely.
        E.g. for Docker app this should wait for the container to exit
        """
        pass


class RequestorAppClient:
    DEFAULT_PORT: ClassVar[int] = 50005

    def __init__(
            self,
            app_callbacks: AppCallbacks,
            port: int = DEFAULT_PORT,
    ) -> None:
        self._app_callbacks = app_callbacks
        host, port = app_callbacks.spawn_server(f'requestor {port}', port)
        self._golem_app = RequestorAppStub(
            Channel(host, port, loop=asyncio.get_event_loop()),
        )

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
        await self._app_callbacks.wait_after_shutdown()


class ProviderAppClient:
    DEFAULT_PORT: ClassVar[int] = 50006

    @classmethod
    def _spawn_server(
            cls,
            app_callbacks: AppCallbacks,
    ) -> None:
        host, port = app_callbacks.spawn_server(
            f'provider {cls.DEFAULT_PORT}',
            cls.DEFAULT_PORT,
        )
        return ProviderAppStub(
            Channel(host, port, loop=asyncio.get_event_loop()),
        )

    @classmethod
    async def compute(
            cls,
            app_callbacks: AppCallbacks,
            task_id: str,
            subtask_id: str,
            subtask_params: dict,
    ) -> Path:
        golem_app = cls._spawn_server(app_callbacks)
        request = ComputeRequest()
        request.task_id = task_id
        request.subtask_id = subtask_id
        request.subtask_params_json = json.dumps(subtask_params)
        reply = await golem_app.Compute(request)
        await app_callbacks.wait_after_shutdown()
        return reply.output_filepath

    @classmethod
    async def run_benchmark(
            cls,
            app_callbacks: AppCallbacks,
    ) -> float:
        golem_app = cls._spawn_server(app_callbacks)
        request = RunBenchmarkRequest()
        reply = await golem_app.RunBenchmark(request)
        await app_callbacks.wait_after_shutdown()
        return reply.score

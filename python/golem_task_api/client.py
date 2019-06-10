import abc
import asyncio
import json
from typing import Tuple
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
    RunBenchmarkRequest,
    RunBenchmarkReply,
    ShutdownRequest,
)
from golem_task_api.proto.golem_task_api_grpc import (
    RequestorAppStub,
)


class RequestorAppCallbacks(abc.ABC):
    @abc.abstractmethod
    def spawn_server(self, command: str, port: int) -> Tuple[str, int]:
        """
        This method is supposed to pass the command argument to the entrypoint
        which will spawn requestor's server and should return a tuple
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


class ProviderAppCallbacks(abc.ABC):
    @abc.abstractmethod
    async def run_command(self, command: str) -> None:
        """
        Similarly to the RequestorAppCallbacks this is supposed to pass the
        command to the entrypoint, but should wait for it's execution to end.
        E.g. for Docker app this could be implemented as:
        `docker run <command>`
        """
        pass


class RequestorAppClient:
    def __init__(
            self,
            app_callbacks: RequestorAppCallbacks,
            port: int,
    ) -> None:
        host, port = app_callbacks.spawn_server(f'start {port}', port)
        self._golem_app = RequestorAppStub(
            Channel(host, port, loop=asyncio.get_event_loop()),
        )

    async def create_task(
            self,
            task_id: str,
            task_params: dict,
    ) -> None:
        request = CreateTaskRequest()
        request.task_id = task_id
        request.task_params_json = json.dumps(task_params)
        await self._golem_app.CreateTask(request)

    async def next_subtask(
            self,
            task_id: str,
    ) -> Tuple[str, dict]:
        request = NextSubtaskRequest()
        request.task_id = task_id
        reply = await self._golem_app.NextSubtask(request)
        return reply.subtask_id, json.loads(reply.subtask_params_json)

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

    async def run_benchmark(self) -> float:
        request = RunBenchmarkRequest()
        reply = await self._golem_app.RunBenchmark(request)
        return reply.score

    async def shutdown(self) -> None:
        request = ShutdownRequest()
        await self._golem_app.Shutdown(request)


class ProviderAppClient:
    @staticmethod
    async def compute(
            app_callbacks: ProviderAppCallbacks,
            work_dir: Path,
            task_id: str,
            subtask_id: str,
            subtask_params: dict,
    ) -> None:
        request = ComputeRequest()
        request.task_id = task_id
        request.subtask_id = subtask_id
        request.subtask_params_json = json.dumps(subtask_params)
        request_filepath = f'{subtask_id}.request'
        with open(work_dir / request_filepath, 'wb') as f:
            f.write(request.SerializeToString())
        await app_callbacks.run_command(f'compute {request_filepath}')

    @staticmethod
    async def run_benchmark(
            app_callbacks: ProviderAppCallbacks,
            work_dir: Path,
    ) -> float:
        await app_callbacks.run_command('benchmark')
        with open(work_dir / 'benchmark.reply', 'rb') as f:
            reply = RunBenchmarkReply.ParseFromString(f.read())
        return reply.score

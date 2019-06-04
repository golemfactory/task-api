import abc
import asyncio
import json
from pathlib import Path
from typing import Tuple

from grpclib.server import Server

from golem_task_api.proto.golem_task_api_grpc import (
    RequestorGolemAppBase,
    ProviderGolemAppBase,
)
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
)


class RequestorGolemAppHandler:
    @abc.abstractmethod
    async def create_task(
            self,
            task_work_dir: Path,
            task_params: dict) -> None:
        pass

    @abc.abstractmethod
    async def next_subtask(
            self,
            task_work_dir: Path) -> Tuple[str, dict]:
        pass

    @abc.abstractmethod
    async def verify(
            self,
            task_work_dir: Path,
            subtask_id: str) -> bool:
        pass

    @abc.abstractmethod
    async def run_benchmark(self, work_dir: Path) -> float:
        pass


class ProviderGolemAppHandler:
    @abc.abstractmethod
    async def compute(
            self,
            task_work_dir: Path,
            subtask_id: str,
            subtask_params: dict) -> None:
        pass

    @abc.abstractmethod
    async def run_benchmark(self, work_dir: Path) -> float:
        pass


class RequestorGolemApp(RequestorGolemAppBase):

    def __init__(
            self,
            work_dir: Path,
            handler: RequestorGolemAppHandler) -> None:
        self._work_dir = work_dir
        self._handler = handler

    async def CreateTask(self, stream):
        request: CreateTaskRequest = await stream.recv_message()
        task_id = request.task_id
        task_work_dir = self._work_dir / task_id
        task_params = json.loads(request.task_params_json)
        await self._handler.create_task(task_work_dir, task_params)
        reply = CreateTaskReply()
        await stream.send_message(reply)

    async def NextSubtask(self, stream):
        request: NextSubtaskRequest = await stream.recv_message()
        task_id = request.task_id
        task_work_dir = self._work_dir / task_id
        subtask_id, subtask_params = \
            await self._handler.next_subtask(task_work_dir)
        reply = NextSubtaskReply()
        reply.subtask_id = subtask_id
        reply.subtask_params_json = json.dumps(subtask_params)
        await stream.send_message(reply)

    async def Verify(self, stream):
        request: VerifyRequest = await stream.recv_message()
        task_id = request.task_id
        subtask_id = request.subtask_id
        task_work_dir = self._work_dir / task_id
        success = await self._handler.verify(task_work_dir, subtask_id)
        reply = VerifyReply()
        reply.success = success
        await stream.send_message(reply)

    async def RunBenchmark(self, stream):
        request: RunBenchmarkRequest = await stream.recv_message()
        score = await self._handler.run_benchmark(self._work_dir)
        reply = RunBenchmarkReply()
        reply.score = score
        await stream.send_message(reply)


class ProviderGolemApp(ProviderGolemAppBase):

    def __init__(
            self,
            work_dir: Path,
            handler: ProviderGolemAppHandler) -> None:
        self._work_dir = work_dir
        self._handler = handler

    async def Compute(self, stream):
        request: ComputeRequest = await stream.recv_message()
        task_id = request.task_id
        subtask_id = request.subtask_id
        task_work_dir = self._work_dir / task_id
        subtask_params = json.loads(request.subtask_params_json)
        await self._handler.compute(task_work_dir, subtask_id, subtask_params)
        reply = ComputeReply()
        await stream.send_message(reply)

    async def RunBenchmark(self, stream):
        request: RunBenchmarkRequest = await stream.recv_message()
        score = await self._handler.run_benchmark(self._work_dir)
        reply = RunBenchmarkReply()
        reply.score = score
        await stream.send_message(reply)


class RequestorGolemAppServer:
    def __init__(
            self,
            work_dir: Path,
            port: int,
            handler: RequestorGolemAppHandler) -> None:
        golem_app = RequestorGolemApp(work_dir, handler)
        loop = asyncio.get_event_loop()
        self._server = Server(handlers=[golem_app], loop=loop)
        self._port = port

    async def start(self):
        print(f'Starting server at port {self._port}')
        await self._server.start('', self._port, ssl=None)

    async def stop(self):
        print("Stopping server...")
        self._server.close()
        await self._server.wait_closed()


class ProviderGolemAppServer:
    def __init__(
            self,
            work_dir: Path,
            port: int,
            handler: ProviderGolemAppHandler) -> None:
        golem_app = ProviderGolemApp(work_dir, handler)
        loop = asyncio.get_event_loop()
        self._server = Server(handlers=[golem_app], loop=loop)
        self._port = port

    async def start(self):
        print(f'Starting server at port {self._port}')
        await self._server.start('', self._port, ssl=None)

    async def stop(self):
        print("Stopping server...")
        self._server.close()
        await self._server.wait_closed()

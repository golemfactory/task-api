import asyncio
import json
from typing import Tuple

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
)
from golem_task_api.proto.golem_task_api_grpc import (
    GolemAppStub,
)


class GolemAppClient:
    def __init__(self, host: str, port: int) -> None:
        self._golem_app = GolemAppStub(
            Channel(host, port, loop=asyncio.get_event_loop()),
        )

    async def create_task(
            self,
            task_id: str,
            task_params: dict) -> None:
        request = CreateTaskRequest()
        request.task_id = task_id
        request.task_params_json = json.dumps(task_params)
        await self._golem_app.CreateTask(request)

    async def next_subtask(
            self,
            task_id: str) -> Tuple[str, dict]:
        request = NextSubtaskRequest()
        request.task_id = task_id
        reply = await self._golem_app.NextSubtask(request)
        return reply.subtask_id, json.loads(reply.subtask_params_json)

    async def compute(
            self,
            task_id: str,
            subtask_id: str,
            subtask_params: dict) -> None:
        request = ComputeRequest()
        request.task_id = task_id
        request.subtask_id = subtask_id
        request.subtask_params_json = json.dumps(subtask_params)
        await self._golem_app.Compute(request)

    async def verify(
            self,
            task_id: str,
            subtask_id: str) -> bool:
        request = VerifyRequest()
        request.task_id = task_id
        request.subtask_id = subtask_id
        reply = await self._golem_app.Verify(request)
        return reply.success

    async def run_benchmark(self) -> float:
        request = RunBenchmarkRequest()
        reply = await self._golem_app.RunBenchmark(request)
        return reply.score

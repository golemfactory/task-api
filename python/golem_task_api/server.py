import asyncio
import functools
import json
import traceback
from pathlib import Path

from grpclib import const
from grpclib import server

from golem_task_api.proto.golem_task_api_grpc import (
    ProviderAppBase,
    RequestorAppBase,
)
from golem_task_api.handlers import (
    ProviderAppHandler,
    RequestorAppHandler,
)
from golem_task_api.messages import (
    CreateTaskRequest,
    CreateTaskReply,
    ComputeRequest,
    ComputeReply,
    NextSubtaskRequest,
    NextSubtaskReply,
    VerifyRequest,
    VerifyReply,
    DiscardSubtasksRequest,
    DiscardSubtasksReply,
    RunBenchmarkRequest,
    RunBenchmarkReply,
    HasPendingSubtasksRequest,
    HasPendingSubtasksReply,
    ShutdownRequest,
    ShutdownReply,
)


def forward_exceptions():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(self, stream):
            try:
                await func(self, stream)
            except Exception as e:
                print(traceback.format_exc())
                await stream.send_trailing_metadata(
                    status=const.Status.INTERNAL,
                    status_message=str(e),
                )
        return wrapped
    return wrapper


class RequestorApp(RequestorAppBase):
    def __init__(
            self,
            work_dir: Path,
            handler: RequestorAppHandler,
            shutdown_future: asyncio.Future,
    ) -> None:
        self._shutdown_future = shutdown_future
        self._work_dir = work_dir
        self._handler = handler

    @forward_exceptions()
    async def CreateTask(self, stream):
        request: CreateTaskRequest = await stream.recv_message()
        task_id = request.task_id
        task_work_dir = self._work_dir / task_id
        max_subtasks_count = request.max_subtasks_count
        task_params = json.loads(request.task_params_json)
        await self._handler.create_task(
            task_work_dir,
            max_subtasks_count,
            task_params,
        )
        reply = CreateTaskReply()
        await stream.send_message(reply)

    @forward_exceptions()
    async def NextSubtask(self, stream):
        request: NextSubtaskRequest = await stream.recv_message()
        task_id = request.task_id
        task_work_dir = self._work_dir / task_id
        subtask_id, subtask_params, resources = \
            await self._handler.next_subtask(task_work_dir)
        reply = NextSubtaskReply()
        reply.subtask_id = subtask_id
        reply.subtask_params_json = json.dumps(subtask_params)
        reply.resources.extend(resources)
        await stream.send_message(reply)

    @forward_exceptions()
    async def Verify(self, stream):
        request: VerifyRequest = await stream.recv_message()
        task_id = request.task_id
        subtask_id = request.subtask_id
        task_work_dir = self._work_dir / task_id
        success = await self._handler.verify(task_work_dir, subtask_id)
        reply = VerifyReply()
        reply.success = success
        await stream.send_message(reply)

    @forward_exceptions()
    async def DiscardSubtasks(self, stream):
        request: DiscardSubtasksRequest = await stream.recv_message()
        task_id = request.task_id
        subtask_ids = request.subtask_ids
        task_work_dir = self._work_dir / task_id
        discarded_subtask_ids = \
            await self._handler.discard_subtasks(task_work_dir, subtask_ids)
        reply = DiscardSubtasksReply()
        reply.discarded_subtask_ids.extend(discarded_subtask_ids)
        await stream.send_message(reply)

    @forward_exceptions()
    async def RunBenchmark(self, stream):
        await stream.recv_message()
        score = await self._handler.run_benchmark(self._work_dir)
        reply = RunBenchmarkReply()
        reply.score = score
        await stream.send_message(reply)

    @forward_exceptions()
    async def HasPendingSubtasks(self, stream):
        request: HasPendingSubtasksRequest = await stream.recv_message()
        task_work_dir = self._work_dir / request.task_id
        has_pending_subtasks = \
            await self._handler.has_pending_subtasks(task_work_dir)
        reply = HasPendingSubtasksReply()
        reply.has_pending_subtasks = has_pending_subtasks
        await stream.send_message(reply)

    @forward_exceptions()
    async def Shutdown(self, stream):
        await stream.recv_message()
        self._shutdown_future.set_result(None)
        reply = ShutdownReply()
        await stream.send_message(reply)


class ProviderApp(ProviderAppBase):
    def __init__(
            self,
            work_dir: Path,
            handler: ProviderAppHandler,
            shutdown_future: asyncio.Future,
    ) -> None:
        self._shutdown_future = shutdown_future
        self._work_dir = work_dir
        self._handler = handler

    @forward_exceptions()
    async def RunBenchmark(self, stream):
        await stream.recv_message()
        score = await self._handler.run_benchmark(self._work_dir)
        reply = RunBenchmarkReply()
        reply.score = score
        await stream.send_message(reply)
        self._shutdown_future.set_result(None)

    @forward_exceptions()
    async def Compute(self, stream):
        request: ComputeRequest = await stream.recv_message()
        output_filepath = await self._handler.compute(
            self._work_dir,
            request.subtask_id,
            json.loads(request.subtask_params_json),
        )
        reply = ComputeReply()
        reply.output_filepath = output_filepath
        await stream.send_message(reply)
        self._shutdown_future.set_result(None)


class AppServer:
    def __init__(self, golem_app, port: int, shutdown_future) -> None:
        self._server = server.Server(
            handlers=[golem_app],
            loop=asyncio.get_event_loop(),
        )
        self._port = port
        self._shutdown_future = shutdown_future

    async def start(self):
        print(f'Starting server at port {self._port}')
        await self._server.start('', self._port, ssl=None)

    async def wait_until_shutdown(self):
        await self._shutdown_future

    async def stop(self):
        print("Stopping server...")
        self._server.close()
        await self._server.wait_closed()


class RequestorAppServer(AppServer):
    def __init__(
            self,
            work_dir: Path,
            port: int,
            handler: RequestorAppHandler,
    ) -> None:
        shutdown_future = asyncio.get_event_loop().create_future()
        golem_app = RequestorApp(work_dir, handler, shutdown_future)
        super().__init__(golem_app, port, shutdown_future)


class ProviderAppServer(AppServer):
    def __init__(
            self,
            work_dir: Path,
            port: int,
            handler: ProviderAppHandler,
    ) -> None:
        shutdown_future = asyncio.get_event_loop().create_future()
        golem_app = ProviderApp(work_dir, handler, shutdown_future)
        super().__init__(golem_app, port, shutdown_future)

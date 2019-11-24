import asyncio
import functools
import json
import ssl
import traceback
from pathlib import Path
from typing import Optional

from golem_task_api.ssl import create_server_ssl_context
from grpclib import const
from grpclib import server
from grpclib.health.service import Health

from golem_task_api.dirutils import ProviderTaskDir, RequestorDir
from golem_task_api.proto.golem_task_api_grpc import (
    ProviderAppBase,
    RequestorAppBase,
)
from golem_task_api.handlers import (
    AppLifecycleHandler,
    ProviderAppHandler,
    RequestorAppHandler,
)
from golem_task_api.messages import (
    AbortSubtaskRequest,
    AbortSubtaskReply,
    AbortTaskRequest,
    AbortTaskReply,
    CreateTaskRequest,
    CreateTaskReply,
    ComputeRequest,
    ComputeReply,
    Infrastructure,
    NextSubtaskRequest,
    NextSubtaskReply,
    SubtaskReply,
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
                # TODO: use non private property to check for closed status
                if stream._stream.closable:
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
            lifecycle: AppLifecycleHandler,
    ) -> None:
        self._work_dir = RequestorDir(work_dir)
        self._handler = handler
        self._lifecycle = lifecycle

    @forward_exceptions()
    async def CreateTask(self, stream):
        request: CreateTaskRequest = await stream.recv_message()
        task_work_dir = self._work_dir.task_dir(request.task_id)
        max_subtasks_count = request.max_subtasks_count
        task_params = json.loads(request.task_params_json)
        task = await self._handler.create_task(
            task_work_dir,
            max_subtasks_count,
            task_params,
        )

        inf_requirements = Infrastructure()
        inf_requirements.min_memory_mib = task.inf_requirements.min_memory_mib

        reply = CreateTaskReply()
        reply.env_id = task.env_id
        reply.prerequisites_json = json.dumps(task.prerequisites)
        reply.inf_requirements.CopyFrom(inf_requirements)

        await stream.send_message(reply)

    @forward_exceptions()
    async def NextSubtask(self, stream):
        request: NextSubtaskRequest = await stream.recv_message()
        task_work_dir = self._work_dir.task_dir(request.task_id)
        reply = NextSubtaskReply()
        subtask = await self._handler.next_subtask(
            task_work_dir,
            request.subtask_id,
            request.opaque_node_id)
        if subtask:
            subtask_reply = SubtaskReply()
            subtask_reply.subtask_params_json = json.dumps(subtask.params)
            subtask_reply.resources.extend(subtask.resources)
            reply.subtask.MergeFrom(subtask_reply)
        await stream.send_message(reply)

    @forward_exceptions()
    async def Verify(self, stream):
        request: VerifyRequest = await stream.recv_message()
        task_work_dir = self._work_dir.task_dir(request.task_id)
        subtask_id = request.subtask_id
        result, reason = await self._handler.verify(task_work_dir, subtask_id)
        reply = VerifyReply()
        reply.result = result.value
        if reason:
            reply.reason = reason
        await stream.send_message(reply)

    @forward_exceptions()
    async def DiscardSubtasks(self, stream):
        request: DiscardSubtasksRequest = await stream.recv_message()
        task_work_dir = self._work_dir.task_dir(request.task_id)
        subtask_ids = request.subtask_ids
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
        task_work_dir = self._work_dir.task_dir(request.task_id)
        has_pending_subtasks = \
            await self._handler.has_pending_subtasks(task_work_dir)
        reply = HasPendingSubtasksReply()
        reply.has_pending_subtasks = has_pending_subtasks
        await stream.send_message(reply)

    @forward_exceptions()
    async def AbortTask(self, stream):
        request: AbortTaskRequest = await stream.recv_message()
        task_work_dir = self._work_dir.task_dir(request.task_id)
        await self._handler.abort_task(task_work_dir)
        reply = AbortTaskReply()
        await stream.send_message(reply)

    @forward_exceptions()
    async def AbortSubtask(self, stream):
        request: AbortSubtaskRequest = await stream.recv_message()
        task_work_dir = self._work_dir.task_dir(request.task_id)
        subtask_id = request.subtask_id
        await self._handler.abort_subtask(task_work_dir, subtask_id)
        reply = AbortSubtaskReply()
        await stream.send_message(reply)

    @forward_exceptions()
    async def Shutdown(self, stream):
        await stream.recv_message()
        reply = ShutdownReply()
        await stream.send_message(reply)
        self._lifecycle.request_shutdown()


class ProviderApp(ProviderAppBase):
    def __init__(
            self,
            work_dir: Path,
            handler: ProviderAppHandler,
            lifecycle: AppLifecycleHandler,
    ) -> None:
        self._work_dir = ProviderTaskDir(work_dir)
        self._handler = handler
        self._lifecycle = lifecycle

    @forward_exceptions()
    async def RunBenchmark(self, stream):
        try:
            await stream.recv_message()
            score = await self._handler.run_benchmark(self._work_dir)
            reply = RunBenchmarkReply()
            reply.score = score
            await stream.send_message(reply)
        finally:
            self._lifecycle.request_shutdown()

    @forward_exceptions()
    async def Compute(self, stream):
        try:
            request: ComputeRequest = await stream.recv_message()
            output_filepath = await self._handler.compute(
                self._work_dir,
                request.subtask_id,
                json.loads(request.subtask_params_json),
            )
            reply = ComputeReply()
            reply.output_filepath = str(output_filepath)
            await stream.send_message(reply)
        finally:
            self._lifecycle.request_shutdown()

    @forward_exceptions()
    async def Shutdown(self, stream):
        await stream.recv_message()
        reply = ShutdownReply()
        await stream.send_message(reply)
        self._lifecycle.request_shutdown()


class AppServer:
    def __init__(
            self,
            golem_app,
            port: int,
            lifecycle: AppLifecycleHandler,
            ssl_context: Optional[ssl.SSLContext] = None,
    ) -> None:
        self._server = server.Server(
            handlers=[golem_app, Health()],
            loop=asyncio.get_event_loop(),
        )
        self._port = port
        self._lifecycle = lifecycle
        self._ssl_context = ssl_context

    async def start(self):
        print(f'Starting server at port {self._port}', flush=True)
        await self._lifecycle.on_before_startup()
        await self._server.start(
            host='',
            port=self._port,
            ssl=self._ssl_context)
        await self._lifecycle.on_after_startup()

    async def wait_until_shutdown(self):
        await self._lifecycle.shutdown_future

    async def stop(self):
        await self._lifecycle.on_before_shutdown()
        print("Stopping server...", flush=True)
        self._server.close()
        await self._server.wait_closed()
        await self._lifecycle.on_after_shutdown()


class RequestorAppServer(AppServer):
    def __init__(
            self,
            work_dir: Path,
            port: int,
            handler: RequestorAppHandler,
            lifecycle: AppLifecycleHandler,
    ) -> None:
        ssl_context = create_server_ssl_context(work_dir)
        golem_app = RequestorApp(work_dir, handler, lifecycle)
        super().__init__(golem_app, port, lifecycle, ssl_context=ssl_context)


class ProviderAppServer(AppServer):
    def __init__(
            self,
            work_dir: Path,
            port: int,
            handler: ProviderAppHandler,
            lifecycle: AppLifecycleHandler,
    ) -> None:
        ssl_context = create_server_ssl_context(work_dir)
        golem_app = ProviderApp(work_dir, handler, lifecycle)
        super().__init__(golem_app, port, lifecycle, ssl_context=ssl_context)

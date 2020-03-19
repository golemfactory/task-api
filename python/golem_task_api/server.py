import asyncio
import functools
import json
import logging
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
    RunBenchmarkReply,
    HasPendingSubtasksRequest,
    HasPendingSubtasksReply,
    ShutdownReply,
)


logger = logging.getLogger(__name__)


def forward_exceptions():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(self, stream):
            try:
                await func(self, stream)
            except Exception as e:
                logger.exception(traceback.format_exc())
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
        logger.debug('CreateTask()')
        request: CreateTaskRequest = await stream.recv_message()
        task_work_dir = self._work_dir.task_dir(request.task_id)
        max_subtasks_count = request.max_subtasks_count
        task_params = json.loads(request.task_params_json)
        logger.debug(
            'calling create_task on handler. dir=%s, subtasks=%d, params=%r',
            task_work_dir,
            max_subtasks_count,
            task_params,
        )
        task = await self._handler.create_task(
            task_work_dir,
            max_subtasks_count,
            task_params,
        )

        logger.debug('got create_task result. task=%r', task)
        inf_requirements = Infrastructure()
        inf_requirements.min_memory_mib = task.inf_requirements.min_memory_mib

        reply = CreateTaskReply()
        reply.env_id = task.env_id
        reply.prerequisites_json = json.dumps(task.prerequisites)
        reply.inf_requirements.CopyFrom(inf_requirements)

        await stream.send_message(reply)
        logger.debug('CreateTask() - done')

    @forward_exceptions()
    async def NextSubtask(self, stream):
        logger.debug('NextSubtask()')
        request: NextSubtaskRequest = await stream.recv_message()
        task_work_dir = self._work_dir.task_dir(request.task_id)
        reply = NextSubtaskReply()
        logger.debug(
            'calling next_subtask on handler. dir=%s, subtask_id=%s, node=%s',
            task_work_dir,
            request.subtask_id,
            request.opaque_node_id,
        )
        subtask = await self._handler.next_subtask(
            task_work_dir,
            request.subtask_id,
            request.opaque_node_id)

        logger.debug('got next_subtask result. subtask=%r', subtask)
        if subtask:
            subtask_reply = SubtaskReply()
            subtask_reply.subtask_params_json = json.dumps(subtask.params)
            subtask_reply.resources.extend(subtask.resources)
            reply.subtask.MergeFrom(subtask_reply)
        else:
            logger.debug('No more subtask available')
        await stream.send_message(reply)
        logger.debug('NextSubtask() - done')

    @forward_exceptions()
    async def Verify(self, stream):
        logger.debug('Verify()')
        request: VerifyRequest = await stream.recv_message()
        task_work_dir = self._work_dir.task_dir(request.task_id)
        subtask_id = request.subtask_id
        reply = NextSubtaskReply()
        logger.debug(
            'calling verify on handler. dir=%s, subtask_id=%s',
            task_work_dir,
            subtask_id,
        )
        result, reason = await self._handler.verify(task_work_dir, subtask_id)
        logger.debug('got verify result. result=%r, reason=%r', result, reason)
        reply = VerifyReply()
        reply.result = result.value
        if reason:
            reply.reason = reason
        await stream.send_message(reply)
        logger.debug('Verify() - done')

    @forward_exceptions()
    async def DiscardSubtasks(self, stream):
        logger.debug('DiscardSubtasks()')
        request: DiscardSubtasksRequest = await stream.recv_message()
        task_work_dir = self._work_dir.task_dir(request.task_id)
        subtask_ids = request.subtask_ids
        logger.debug(
            'calling discard_subtasks on handler. dir=%s, subtask_ids=%r',
            task_work_dir,
            subtask_ids,
        )
        discarded_subtask_ids = \
            await self._handler.discard_subtasks(task_work_dir, subtask_ids)
        logger.debug(
            'got discard_subtasks result. discarded=%r',
            discarded_subtask_ids
        )
        reply = DiscardSubtasksReply()
        reply.discarded_subtask_ids.extend(discarded_subtask_ids)
        await stream.send_message(reply)
        logger.debug('DiscardSubtasks() - done')

    @forward_exceptions()
    async def RunBenchmark(self, stream):
        logger.debug('RunBenchmark()')
        await stream.recv_message()
        logger.debug(
            'calling run_benchmark on handler. dir=%s',
            self._work_dir,
        )
        score = await self._handler.run_benchmark(self._work_dir)
        logger.debug('got run_benchmark result. score=%r', score)
        reply = RunBenchmarkReply()
        reply.score = score
        await stream.send_message(reply)
        logger.debug('RunBenchmark() - done')

    @forward_exceptions()
    async def HasPendingSubtasks(self, stream):
        logger.debug('HasPendingSubtasks()')
        request: HasPendingSubtasksRequest = await stream.recv_message()
        task_work_dir = self._work_dir.task_dir(request.task_id)
        logger.debug(
            'calling has_pending_subtasks on handler. dir=%s',
            task_work_dir,
        )
        has_pending_subtasks = \
            await self._handler.has_pending_subtasks(task_work_dir)
        logger.debug(
            'got has_pending_subtasks result. has_pending_subtasks=%r',
            has_pending_subtasks
        )
        reply = HasPendingSubtasksReply()
        reply.has_pending_subtasks = has_pending_subtasks
        await stream.send_message(reply)
        logger.debug('HasPendingSubtasks() - done')

    @forward_exceptions()
    async def AbortTask(self, stream):
        logger.debug('AbortTask()')
        request: AbortTaskRequest = await stream.recv_message()
        task_work_dir = self._work_dir.task_dir(request.task_id)
        logger.debug(
            'calling abort_task on handler. dir=%s',
            task_work_dir,
        )
        await self._handler.abort_task(task_work_dir)
        logger.debug('abort_task finished')
        reply = AbortTaskReply()
        await stream.send_message(reply)
        logger.debug('AbortTask() - done')

    @forward_exceptions()
    async def AbortSubtask(self, stream):
        logger.debug('AbortSubtask()')
        request: AbortSubtaskRequest = await stream.recv_message()
        task_work_dir = self._work_dir.task_dir(request.task_id)
        subtask_id = request.subtask_id
        logger.debug(
            'calling abort_subtask on handler. dir=%s, subtask_id=%r',
            task_work_dir,
            subtask_id,
        )
        await self._handler.abort_subtask(task_work_dir, subtask_id)
        logger.debug('abort_subtask finished')
        reply = AbortSubtaskReply()
        await stream.send_message(reply)
        logger.debug('AbortSubtask() - done')

    @forward_exceptions()
    async def Shutdown(self, stream):
        logger.debug('Shutdown()')
        await stream.recv_message()
        reply = ShutdownReply()
        await stream.send_message(reply)
        logger.debug('calling request_shutdown on lifecycle')
        self._lifecycle.request_shutdown()
        logger.debug('Shutdown() - done')


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
        logger.debug('RunBenchmark()')
        try:
            await stream.recv_message()
            logger.debug(
                'calling run_benchmark on handler. dir=%s',
                self._work_dir,
            )
            score = await self._handler.run_benchmark(self._work_dir)
            logger.debug('got run_benchmark result. score=%r', score)
            reply = RunBenchmarkReply()
            reply.score = score
            await stream.send_message(reply)
        finally:
            self._lifecycle.request_shutdown()
        logger.debug('RunBenchmark() - done')

    @forward_exceptions()
    async def Compute(self, stream):
        logger.debug('Compute()')
        try:
            request: ComputeRequest = await stream.recv_message()
            logger.debug(
                'calling compute on handler. dir=%s, subtask_id=%s, params=%r',
                self._work_dir,
                request.subtask_id,
                request.subtask_params_json,
            )
            output_filepath = await self._handler.compute(
                self._work_dir,
                request.subtask_id,
                json.loads(request.subtask_params_json),
            )
            logger.debug(
                'got compute result. output_filepath=%s',
                output_filepath
            )
            reply = ComputeReply()
            reply.output_filepath = str(output_filepath)
            await stream.send_message(reply)
        finally:
            self._lifecycle.request_shutdown()
        logger.debug('Compute() - done')

    @forward_exceptions()
    async def Shutdown(self, stream):
        logger.debug('Shutdown()')
        await stream.recv_message()
        reply = ShutdownReply()
        await stream.send_message(reply)
        self._lifecycle.request_shutdown()
        logger.debug('Shutdown() - done')


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
        logger.info(f'Starting server at port %r', self._port)
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
        logger.info("Stopping server...")
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

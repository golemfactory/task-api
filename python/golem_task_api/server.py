import asyncio
import json
from pathlib import Path
from typing import List, Optional, Tuple

from grpclib.server import Server

from golem_task_api.proto.golem_task_api_grpc import (
    RequestorAppBase,
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
    HasPendingSubtasksRequest,
    HasPendingSubtasksReply,
    ShutdownRequest,
    ShutdownReply,
)
from golem_task_api.handlers import (
    ProviderAppHandler,
    RequestorAppHandler,
)


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

    async def HasPendingSubtasks(self, stream):
        request: HasPendingSubtasksRequest = await stream.recv_message()
        task_work_dir = self._work_dir / request.task_id
        has_pending_subtasks = \
            await self._handler.has_pending_subtasks(task_work_dir)
        reply = HasPendingSubtasksReply()
        reply.has_pending_subtasks = has_pending_subtasks
        await stream.send_message(reply)

    async def Shutdown(self, stream):
        _ = await stream.recv_message()
        self._shutdown_future.set_result(None)
        reply = ShutdownReply()
        await stream.send_message(reply)


class RequestorAppServer:
    def __init__(
            self,
            work_dir: Path,
            port: int,
            handler: RequestorAppHandler,
    ) -> None:
        loop = asyncio.get_event_loop()
        self._shutdown_future = loop.create_future()
        golem_app = RequestorApp(work_dir, handler, self._shutdown_future)
        self._server = Server(handlers=[golem_app], loop=loop)
        self._port = port

    async def start(self):
        await self._server.start('', self._port, ssl=None)
        print(f'Starting server at port {self._port}')

    async def wait_until_shutdown(self):
        await self._shutdown_future

    async def stop(self):
        print("Stopping server...")
        self._server.close()
        await self._server.wait_closed()


async def entrypoint(
        work_dir: Path,
        argv: List[str],
        requestor_handler: Optional[RequestorAppHandler] = None,
        provider_handler: Optional[ProviderAppHandler] = None,
):
    cmd = argv[0]
    argv = argv[1:]
    if cmd == 'start':
        server = RequestorAppServer(
            work_dir,
            int(argv[0]),
            requestor_handler,
        )
        await server.start()
        await server.wait_until_shutdown()
        print('Shutting down server...')
        await server.stop()
    elif cmd == 'compute':
        params_filepath = argv[0]
        request = ComputeRequest()
        with open(work_dir / f'{params_filepath}', 'rb') as f:
            request.ParseFromString(f.read())
        await provider_handler.compute(
            work_dir,
            request.subtask_id,
            json.loads(request.subtask_params_json),
        )
    elif cmd == 'benchmark':
        score = await provider_handler.run_benchmark(
            work_dir,
        )
        reply = RunBenchmarkReply()
        reply.score = score
        with open(work_dir / 'benchmark.reply', 'wb') as f:
            f.write(reply.SerializeToString())
    else:
        raise Exception(f'Unknown command: {cmd}')

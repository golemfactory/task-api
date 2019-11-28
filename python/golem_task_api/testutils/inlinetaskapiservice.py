import asyncio
import multiprocessing
import signal
from pathlib import Path
from typing import Optional, Tuple

from golem_task_api import (
    TaskApiService,
    entrypoint,
    AppLifecycleHandler,
    ProviderAppHandler,
    RequestorAppHandler,
)


class InlineTaskApiService(TaskApiService):
    def __init__(
            self,
            work_dir: Path,
            requestor_handler: Optional[RequestorAppHandler] = None,
            requestor_lifecycle_handler: Optional[AppLifecycleHandler] = None,
            provider_handler: Optional[ProviderAppHandler] = None,
            provider_lifecycle_handler: Optional[AppLifecycleHandler] = None,
    ) -> None:
        self._work_dir = work_dir
        self._requestor_handler = requestor_handler
        self._requestor_lifecycle_handler = requestor_lifecycle_handler
        self._provider_handler = provider_handler
        self._provider_lifecycle_handler = provider_lifecycle_handler

        self._server_process: Optional[multiprocessing.Process] = None

    def _spawn(self, command: str) -> None:
        loop = asyncio.new_event_loop()
        loop.add_signal_handler(signal.SIGTERM, loop.stop)
        asyncio.set_event_loop(loop)
        loop.run_until_complete(entrypoint(
            self._work_dir,
            command.split(' '),
            requestor_handler=self._requestor_handler,
            requestor_lifecycle_handler=self._requestor_lifecycle_handler,
            provider_handler=self._provider_handler,
            provider_lifecycle_handler=self._provider_lifecycle_handler
        ))

    def _join(self) -> None:
        assert self._server_process is not None
        self._server_process.join(timeout=5)
        exit_code = self._server_process.exitcode
        if exit_code != 0:
            raise ChildProcessError(f'Server exited with code {exit_code}')

    async def running(self) -> bool:
        assert self._server_process is not None
        return self._server_process.is_alive()

    async def start(self, command: str, port: int) -> Tuple[str, int]:
        self._server_process = multiprocessing.Process(
            target=self._spawn,
            args=(command,),
            daemon=True,
        )
        self._server_process.start()
        return '127.0.0.1', port

    async def stop(self) -> None:
        assert self._server_process is not None
        self._server_process.terminate()

    async def wait_until_shutdown_complete(self) -> None:
        if not await self.running():
            print('Service no longer running')
            return
        await asyncio.get_event_loop().run_in_executor(None, self._join)

from pathlib import Path
import asyncio
import threading

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
        # get_child_watcher enables event loops in child threads
        asyncio.get_child_watcher()
        self._work_dir = work_dir
        self._requestor_handler = requestor_handler
        self._requestor_lifecycle_handler = requestor_lifecycle_handler
        self._provider_handler = provider_handler
        self._provider_lifecycle_handler = provider_lifecycle_handler
        self._thread = None

    def _spawn(self, command: str):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(entrypoint(
            self._work_dir,
            command.split(' '),
            requestor_handler=self._requestor_handler,
            provider_handler=self._provider_handler,
        ))

    def running(self) -> bool:
        return self._thread.is_alive()

    async def start(self, command: str, port: int) -> Tuple[str, int]:
        self._thread = threading.Thread(
            target=self._spawn,
            args=(command,),
            daemon=True,
        )
        self._thread.start()
        host = '127.0.0.1'
        return host, port

    async def wait_until_shutdown_complete(self) -> None:
        if not self.running():
            print('Service no longer running')
            return
        self._thread.join(timeout=3)

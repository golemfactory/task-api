from pathlib import Path
import asyncio
import contextlib
import socket
import threading
import time

from typing import Optional, Tuple

from golem_task_api import (
    TaskApiService,
    entrypoint,
    ProviderAppHandler,
    RequestorAppHandler,
)


def wait_until_socket_open(host: str, port: int, timeout: float = 3.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with contextlib.closing(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex((host, port)) == 0:
                return
        time.sleep(0.05)
    raise Exception(f'Could not connect to socket ({host}, {port})')


class InlineTaskApiService(TaskApiService):
    def __init__(
            self,
            work_dir: Path,
            provider_handler: Optional[ProviderAppHandler]=None,
            requestor_handler: Optional[RequestorAppHandler]=None,
    ) -> None:
        # get_child_watcher enables event loops in child threads
        asyncio.get_child_watcher()
        self._work_dir = work_dir
        self._provider_handler = provider_handler
        self._requestor_handler = requestor_handler
        self._thread = None

    def _spawn(self, command: str):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(entrypoint(
            self._work_dir,
            command.split(' '),
            provider_handler=self._provider_handler,
            requestor_handler=self._requestor_handler,
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
        wait_until_socket_open(host, port)
        return host, port

    async def wait_until_shutdown_complete(self) -> None:
        if not self.running():
            print('Service no longer running')
            return
        self._thread.join(timeout=3)

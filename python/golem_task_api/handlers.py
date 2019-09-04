import abc
import asyncio

from pathlib import Path
from typing import List, Tuple, Optional

from golem_task_api import threading
from golem_task_api.structs import Subtask


class AppLifecycleHandler:

    def __init__(self) -> None:
        self.shutdown_future = asyncio.get_event_loop().create_future()

    async def on_before_startup(self) -> None:
        threading.Executor.initialize()

    async def on_after_startup(self) -> None:
        pass

    async def on_before_shutdown(self) -> None:
        await threading.Executor.wait_for_shutdown()

    async def on_after_shutdown(self) -> None:
        pass

    def request_shutdown(self) -> None:
        # Do not call shutdown multiple times, this can happen in case of errors
        if not self.shutdown_future.done():
            print('Triggering shutdown', flush=True)
            threading.Executor.request_shutdown()
            self.shutdown_future.set_result(None)
        else:
            print('Shutdown already triggered', flush=True)


class RequestorAppHandler:
    @abc.abstractmethod
    async def create_task(
            self,
            task_work_dir: Path,
            max_subtasks_count: int,
            task_params: dict,
    ) -> None:
        pass

    @abc.abstractmethod
    async def next_subtask(
            self,
            task_work_dir: Path,
    ) -> Subtask:
        pass

    @abc.abstractmethod
    async def verify(
            self,
            task_work_dir: Path,
            subtask_id: str,
    ) -> Tuple[bool, Optional[str]]:
        pass

    @abc.abstractmethod
    async def discard_subtasks(
            self,
            task_work_dir: Path,
            subtask_ids: List[str],
    ) -> List[str]:
        pass

    @abc.abstractmethod
    async def run_benchmark(self, work_dir: Path) -> float:
        pass

    @abc.abstractmethod
    async def has_pending_subtasks(self, task_work_dir: Path) -> bool:
        pass


class ProviderAppHandler:
    @abc.abstractmethod
    async def compute(
            self,
            task_work_dir: Path,
            subtask_id: str,
            subtask_params: dict,
    ) -> Path:
        pass

    @abc.abstractmethod
    async def run_benchmark(self, work_dir: Path) -> float:
        pass

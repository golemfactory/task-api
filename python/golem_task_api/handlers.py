from pathlib import Path
from typing import List, Tuple, Optional
import abc

from golem_task_api.structs import Subtask


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

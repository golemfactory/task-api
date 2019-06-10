from pathlib import Path
from typing import Tuple
import abc


class RequestorAppHandler:
    @abc.abstractmethod
    async def create_task(
            self,
            task_work_dir: Path,
            task_params: dict,
    ) -> None:
        pass

    @abc.abstractmethod
    async def next_subtask(
            self,
            task_work_dir: Path,
    ) -> Tuple[str, dict]:
        pass

    @abc.abstractmethod
    async def verify(
            self,
            task_work_dir: Path,
            subtask_id: str,
    ) -> bool:
        pass

    @abc.abstractmethod
    async def run_benchmark(self, work_dir: Path) -> float:
        pass


class ProviderAppHandler:
    @abc.abstractmethod
    async def compute(
            self,
            task_work_dir: Path,
            subtask_id: str,
            subtask_params: dict,
    ) -> None:
        pass

    @abc.abstractmethod
    async def run_benchmark(self, work_dir: Path) -> float:
        pass

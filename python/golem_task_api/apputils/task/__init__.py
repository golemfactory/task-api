import enum

from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Tuple


class SubtaskStatus(enum.Enum):
    WAITING = None
    COMPUTING = 'computing'
    VERIFYING = 'verifying'
    FINISHED = 'finished'
    FAILED = 'failed'
    ABORTED = 'aborted'

    @classmethod
    def default(cls) -> 'SubtaskStatus':
        return cls.WAITING

    def is_computable(self) -> bool:
        return self in (self.WAITING, self.FAILED, self.ABORTED)


class TaskManager(ABC):

    @abstractmethod
    def create_task(
            self,
            part_count: int
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def abort_task(
            self,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_part(
            self,
            part_num: int
    ) -> Optional[object]:
        raise NotImplementedError

    @abstractmethod
    def get_part_num(
            self,
            subtask_id: str
    ) -> Optional[int]:
        raise NotImplementedError

    @abstractmethod
    def get_subtask(
            self,
            subtask_id: str
    ) -> Optional[object]:
        raise NotImplementedError

    @abstractmethod
    def start_subtask(
            self,
            part_num: int,
            subtask_id: str
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_subtask_status(
        self,
        subtask_id: str,
        status: SubtaskStatus,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_subtasks_statuses(
            self,
            part_nums: List[int],
    ) -> Dict[int, Tuple[SubtaskStatus, str]]:
        raise NotImplementedError

    @abstractmethod
    def get_next_pending_subtask(
            self,
    ) -> Optional[int]:
        raise NotImplementedError

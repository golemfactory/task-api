import enum

from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Tuple


class SubtaskStatus(enum.Enum):
    WAITING = None
    COMPUTING = 'computing'
    VERIFYING = 'verifying'
    SUCCESS = 'success'
    FAILURE = 'failure'
    ABORTED = 'aborted'

    @classmethod
    def default(cls) -> 'SubtaskStatus':
        return cls.WAITING

    def is_computable(self) -> bool:
        return self in (self.WAITING, self.FAILURE, self.ABORTED)


class TaskManager(ABC):
    """ Responsible for managing the internal task state.

        Based on a concept of a:

        - part

          An outcome of splitting a task into separate units of work. There
          usually exists a constant number of parts.

        - subtask

          A clone of a chosen task part that will be assigned to a
          computing node.

          Each subtask is given a unique identifier in order to distinguish
          computation attempts of the same part, which may fail due to
          unexpected errors or simply time out.

          A successful subtask computation concludes the computation of the
          corresponding part.

        This class is responsible for correlating subtasks with task parts and
        managing their status.
    """

    @abstractmethod
    def create_task(
            self,
            part_count: int
    ) -> None:
        """ Persist a "part_count" number of task parts and other necessary
            task information """
        raise NotImplementedError

    @abstractmethod
    def abort_task(
            self,
    ) -> None:
        """ Change the statuses of currently assigned subtasks to ABORTED.
            Subtasks must have a computable or COMPUTING status """
        raise NotImplementedError

    @abstractmethod
    def get_part(
            self,
            part_num: int
    ) -> Optional[object]:
        """ Return a task part object with the given part_num, if exists """
        raise NotImplementedError

    @abstractmethod
    def get_part_num(
            self,
            subtask_id: str
    ) -> Optional[int]:
        """ Return a task part object's number for the given subtask_id,
            if exists """
        raise NotImplementedError

    @abstractmethod
    def get_subtask(
            self,
            subtask_id: str
    ) -> Optional[object]:
        """ Return a subtask object with the given subtask_id, if exists """
        raise NotImplementedError

    @abstractmethod
    def start_subtask(
            self,
            part_num: int,
            subtask_id: str
    ) -> None:
        """ Persist a new subtask with the given subtask_id and a COMPUTING
            status. Assign that subtask to a task part object with the given
            part_num """
        raise NotImplementedError

    @abstractmethod
    def update_subtask_status(
        self,
        subtask_id: str,
        status: SubtaskStatus,
    ) -> None:
        """ Update the status of a subtask with the given subtask_id """
        raise NotImplementedError

    @abstractmethod
    def get_subtasks_statuses(
            self,
            part_nums: List[int],
    ) -> Dict[int, Tuple[SubtaskStatus, Optional[str]]]:
        """ Return (subtask status, subtask id) tuples mapped to part numbers
            with assigned subtasks or (WAITING, None) tuples otherwise.
            Task parts are chosen from the "part_nums" pool """
        raise NotImplementedError

    @abstractmethod
    def get_next_computable_part_num(
            self,
    ) -> Optional[int]:
        """ Return the next computable task part's number, if exists """
        raise NotImplementedError

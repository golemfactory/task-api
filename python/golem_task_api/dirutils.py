from pathlib import Path
from typing import TYPE_CHECKING

from golem_task_api import constants

if TYPE_CHECKING:
    FlavouredPath = Path
else:
    # Concrete path type appropriate for the platform (WindowsPath or PosixPath)
    FlavouredPath = type(Path())


class RequestorTaskDir(FlavouredPath):

    @property
    def task_inputs_dir(self) -> Path:
        return Path(self / constants.TASK_INPUTS_DIR)

    @property
    def task_outputs_dir(self) -> Path:
        return Path(self / constants.TASK_OUTPUTS_DIR)

    @property
    def subtask_inputs_dir(self) -> Path:
        return Path(self / constants.SUBTASK_INPUTS_DIR)

    @property
    def subtask_outputs_top_dir(self) -> Path:
        return Path(self / constants.SUBTASK_OUTPUTS_DIR)

    def subtask_outputs_dir(self, subtask_id: str) -> Path:
        return self.subtask_outputs_top_dir / subtask_id

    def prepare(self) -> None:
        self.mkdir()
        self.task_inputs_dir.mkdir()
        self.task_outputs_dir.mkdir()
        self.subtask_inputs_dir.mkdir()
        self.subtask_outputs_top_dir.mkdir()


class RequestorDir(FlavouredPath):

    def task_dir(self, task_id: str) -> RequestorTaskDir:
        return RequestorTaskDir(self / task_id)

    def subtask_outputs_dir(self, task_id: str, subtask_id: str) -> Path:
        return self.task_dir(task_id).subtask_outputs_dir(subtask_id)


class ProviderTaskDir(FlavouredPath):

    @property
    def subtask_inputs_dir(self) -> Path:
        return Path(self / constants.SUBTASK_INPUTS_DIR)

    def subtask_dir(self, subtask_id: str) -> Path:
        return Path(self / subtask_id)

    def prepare(self) -> None:
        self.mkdir()
        self.subtask_inputs_dir.mkdir()


class ProviderDir(FlavouredPath):

    def task_dir(self, task_id: str) -> ProviderTaskDir:
        return ProviderTaskDir(self / task_id)

    def subtask_dir(self, task_id: str, subtask_id: str) -> Path:
        return self.task_dir(task_id).subtask_dir(subtask_id)

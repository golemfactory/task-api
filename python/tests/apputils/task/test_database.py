# pylint: disable=redefined-outer-name
import shutil
from pathlib import Path

import pytest

from golem_task_api.apputils.database import database
from golem_task_api.apputils.task.database import DBTaskManager
from tests.apputils.task.base import TaskManagerTestBase


class TestDBTaskManager(TaskManagerTestBase):

    @staticmethod
    @pytest.yield_fixture
    def task_manager(tmpdir):
        manager = DBTaskManager(Path(tmpdir))
        try:
            yield manager
        finally:
            database.close()
            shutil.rmtree(tmpdir)

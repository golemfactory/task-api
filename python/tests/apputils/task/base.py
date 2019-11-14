# pylint: disable=redefined-outer-name
import peewee
import pytest

from golem_task_api.apputils.task import SubtaskStatus


class TaskManagerTestBase:

    def test_create_task(self, task_manager):
        subtask_count = 4
        task_manager.create_task(subtask_count)

        statuses = task_manager.get_subtasks_statuses(
            list(range(subtask_count)))
        assert all(
            statuses[i] == (SubtaskStatus.WAITING, None)
            for i in range(subtask_count))

    def test_abort_task(self, task_manager):
        subtask_count = 10
        task_manager.create_task(subtask_count)

        for i in range(subtask_count):
            task_manager.start_subtask(i, f'subtask_{i}')
            status = task_manager.get_subtasks_statuses([i])[i]
            assert status == (SubtaskStatus.COMPUTING, f'subtask_{i}')

        task_manager.abort_task()

        for i in range(subtask_count):
            status = task_manager.get_subtasks_statuses([i])[i]
            assert status == (SubtaskStatus.ABORTED, f'subtask_{i}')

    def test_get_part(self, task_manager):
        assert task_manager.get_part(0) is None

        task_manager.create_task(2)

        assert task_manager.get_part(0)
        assert task_manager.get_part(1)
        assert task_manager.get_part(2) is None

    def test_get_part_num(self, task_manager):
        task_manager.create_task(2)

        task_manager.start_subtask(0, 'subtask_0')
        task_manager.start_subtask(1, 'subtask_1')

        assert task_manager.get_part_num('subtask_0') == 0
        assert task_manager.get_part_num('subtask_1') == 1

        task_manager.update_subtask_status(
            'subtask_0',
            SubtaskStatus.ABORTED)
        task_manager.update_subtask_status(
            'subtask_1',
            SubtaskStatus.ABORTED)

        task_manager.start_subtask(0, 'subtask_2')
        task_manager.start_subtask(1, 'subtask_3')

        assert task_manager.get_part_num('subtask_2') == 0
        assert task_manager.get_part_num('subtask_3') == 1

    def test_get_subtask(self, task_manager):
        task_manager.create_task(1)
        assert task_manager.get_subtask('subtask') is None

        task_manager.start_subtask(0, 'subtask')
        assert task_manager.get_subtask('subtask')

    def test_start_subtask(self, task_manager):
        subtask_id = 'subtask'
        task_manager.create_task(1)

        task_manager.start_subtask(0, subtask_id)
        statuses = task_manager.get_subtasks_statuses([0])

        assert statuses == {0: (SubtaskStatus.COMPUTING, subtask_id)}
        assert task_manager.get_next_computable_part_num() is None

    def test_start_subtask_twice(self, task_manager):
        task_manager.create_task(1)
        task_manager.start_subtask(0, 'subtask')

        with pytest.raises(RuntimeError):
            task_manager.start_subtask(0, 'subtask_2')

    def test_start_subtask_duplicate_id(self, task_manager):
        task_manager.create_task(2)
        task_manager.start_subtask(0, 'subtask')

        with pytest.raises(peewee.PeeweeException):
            task_manager.start_subtask(1, 'subtask')

    def test_start_discarded_subtask(self, task_manager):
        task_manager.create_task(1)

        task_manager.start_subtask(0, 'subtask_1')
        task_manager.update_subtask_status(
            'subtask_1',
            SubtaskStatus.ABORTED)
        task_manager.start_subtask(0, 'subtask_2')

        statuses = task_manager.get_subtasks_statuses([0])
        assert statuses == {0: (SubtaskStatus.COMPUTING, 'subtask_2')}

    def test_abort_subtask(self, task_manager):
        subtask_id = 'subtask'
        task_manager.create_task(1)

        statuses = task_manager.get_subtasks_statuses([0])
        assert statuses == {0: (SubtaskStatus.WAITING, None)}
        assert task_manager.get_next_computable_part_num() == 0

        task_manager.start_subtask(0, subtask_id)
        statuses = task_manager.get_subtasks_statuses([0])
        assert statuses == {0: (SubtaskStatus.COMPUTING, subtask_id)}
        assert task_manager.get_next_computable_part_num() is None

        task_manager.update_subtask_status(
            subtask_id,
            SubtaskStatus.ABORTED)
        statuses = task_manager.get_subtasks_statuses([0])
        assert statuses == {0: (SubtaskStatus.ABORTED, subtask_id)}
        assert task_manager.get_next_computable_part_num() == 0

    def test_get_next_pending_subtask(self, task_manager):
        subtask_id = 'subtask'
        task_manager.create_task(1)

        assert task_manager.get_next_computable_part_num() == 0

        task_manager.start_subtask(0, subtask_id)  # SubtaskStatus.COMPUTING
        assert task_manager.get_next_computable_part_num() is None

        task_manager.update_subtask_status(
            subtask_id,
            SubtaskStatus.VERIFYING)
        assert task_manager.get_next_computable_part_num() is None

        task_manager.update_subtask_status(
            subtask_id,
            SubtaskStatus.SUCCESS)
        assert task_manager.get_next_computable_part_num() is None

        task_manager.update_subtask_status(
            subtask_id,
            SubtaskStatus.ABORTED)
        assert task_manager.get_next_computable_part_num() == 0

        task_manager.update_subtask_status(
            subtask_id,
            SubtaskStatus.FAILURE)
        assert task_manager.get_next_computable_part_num() == 0

    def test_get_next_pending_subtask_twice(self, task_manager):
        task_manager.create_task(1)

        assert task_manager.get_next_computable_part_num() == 0
        assert task_manager.get_next_computable_part_num() == 0

    def test_get_subtasks_statuses(self, task_manager):
        subtask_count = 4
        task_manager.create_task(subtask_count)

        nums = list(range(subtask_count))
        statuses = task_manager.get_subtasks_statuses(nums)

        assert len(statuses) == subtask_count
        for i in range(subtask_count):
            assert i in statuses
            assert statuses[i] == (SubtaskStatus.WAITING, None)

    def test_get_subtasks_statuses_invalid_nums(self, task_manager):
        subtask_count = 4
        task_manager.create_task(subtask_count)

        nums = [9, 10, 11]
        statuses = task_manager.get_subtasks_statuses(nums)
        assert not statuses

    def test_update_subtask(self, task_manager):
        subtask_id = 'subtask_0'
        task_manager.create_task(1)

        task_manager.start_subtask(0, subtask_id)
        statuses = task_manager.get_subtasks_statuses([0])
        assert statuses == {0: (SubtaskStatus.COMPUTING, subtask_id)}

        task_manager.update_subtask_status(
            subtask_id,
            SubtaskStatus.VERIFYING)
        statuses = task_manager.get_subtasks_statuses([0])
        assert statuses == {0: (SubtaskStatus.VERIFYING, subtask_id)}

        task_manager.update_subtask_status(
            subtask_id,
            SubtaskStatus.SUCCESS)
        statuses = task_manager.get_subtasks_statuses([0])
        assert statuses == {0: (SubtaskStatus.SUCCESS, subtask_id)}

    def test_update_subtask_without_starting(self, task_manager):
        subtask_id = 'subtask'
        task_manager.create_task(2)

        task_manager.update_subtask_status(
            subtask_id,
            SubtaskStatus.VERIFYING)
        statuses = task_manager.get_subtasks_statuses([1])
        assert statuses[1] == (SubtaskStatus.WAITING, None)

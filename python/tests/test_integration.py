from unittest import mock
from pathlib import Path

import pytest

from golem_task_api import (
    ProviderAppHandler,
    RequestorAppHandler,
    structs,
)
from golem_task_api.testutils import TaskLifecycleUtil


class AsyncMock(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


@pytest.mark.asyncio
async def test_e2e_flow(tmpdir):
    task_lifecycle_util = TaskLifecycleUtil(Path(tmpdir))
    requestor_handler = AsyncMock(spec_set=RequestorAppHandler)
    provider_handler = AsyncMock(spec_set=ProviderAppHandler)

    task_id = 'test_task_id123'
    max_subtasks_count = 1
    resources = []
    task_params = {'test_param': 'test_value'}

    async with task_lifecycle_util.init_requestor_with_handler(
            requestor_handler):
        await task_lifecycle_util.create_task(
            task_id,
            max_subtasks_count,
            resources,
            task_params,
        )
        requestor_handler.create_task.assert_called_once_with(
            mock.ANY,
            max_subtasks_count,
            task_params,
        )
        task_lifecycle_util.init_provider_with_handler(
            provider_handler,
            task_id,
        )
        requestor_handler.has_pending_subtasks.return_value = True
        requestor_handler.next_subtask.return_value = \
            structs.Subtask('subtask_id', {}, [])
        result_path = Path('result')
        (task_lifecycle_util.prov_task_work_dir / result_path).touch()
        provider_handler.compute.return_value = result_path
        requestor_handler.verify.return_value = (True, None)
        subtask_id, verdict = \
            await task_lifecycle_util.compute_next_subtask(task_id)
        assert verdict

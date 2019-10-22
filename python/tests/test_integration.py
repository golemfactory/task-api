from unittest import mock
from pathlib import Path

import pytest

from golem_task_api import (
    ProviderAppHandler,
    RequestorAppHandler,
    enums,
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

    task_struct = structs.Task(
        env_id='test_env',
        prerequisites={}
    )
    task_id = 'test_task_id123'
    max_subtasks_count = 1
    resources = []
    task_params = {'test_param': 'test_value'}
    result_path = Path('result')

    # Mocks have to be configured before calling init_requestor_with_handler
    # because it creates copies of these objects when spawning server process.
    requestor_handler.create_task.return_value = task_struct
    requestor_handler.has_pending_subtasks.return_value = True
    requestor_handler.next_subtask.return_value = \
        structs.Subtask('subtask_id', {}, [])
    provider_handler.compute.return_value = result_path
    requestor_handler.verify.return_value = (enums.VerifyResult.SUCCESS, None)

    async with task_lifecycle_util.init_requestor_with_handler(
            requestor_handler):
        created_task = await task_lifecycle_util.create_task(
            task_id,
            max_subtasks_count,
            resources,
            task_params,
        )
        assert created_task == task_struct
        provider_task_dir = task_lifecycle_util.init_provider_with_handler(
            provider_handler,
            task_id
        )
        (provider_task_dir / result_path).touch()
        node_id = '0xdead'
        subtask_id, verdict = await task_lifecycle_util.compute_next_subtask(
            task_id, node_id)
        assert verdict is enums.VerifyResult.SUCCESS

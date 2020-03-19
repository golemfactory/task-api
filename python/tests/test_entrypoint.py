import logging
from pathlib import Path
import pytest
from mock import Mock, MagicMock

from golem_task_api import entrypoint


class AsyncMock(MagicMock):
    """
    Extended MagicMock to keep async calls async
    """
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class TestEntrypoint():

    @pytest.mark.asyncio
    @pytest.fixture(autouse=True)
    async def test_entrypoint(self, monkeypatch):

        mock_server = AsyncMock()

        def mock_create(*_args, **_kwargs):
            return mock_server

        monkeypatch.setattr(
            'golem_task_api.entrypoint.RequestorAppServer',
            mock_create
        )
        await entrypoint.entrypoint(
            Path('a'),
            ['requestor', 1],
            Mock(),
            None,
            None,
            None,
            'DEBUG',
        )
        assert entrypoint.logger.getEffectiveLevel() == logging.DEBUG
        assert logging.getLogger().getEffectiveLevel() == logging.DEBUG

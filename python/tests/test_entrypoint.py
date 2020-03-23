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
    async def test_main(self, monkeypatch):

        mock_server = AsyncMock()
        mock_create = Mock(return_value=mock_server)

        monkeypatch.setattr(
            'golem_task_api.entrypoint.RequestorAppServer',
            mock_create
        )
        await entrypoint.main(
            Path('a'),
            ['requestor', 1],
            Mock(),
            None,
            None,
            None,
        )
        mock_create.assert_called_once()
        mock_server.start.assert_called_once_with()
        mock_server.wait_until_shutdown.assert_called_once_with()
        mock_server.stop.assert_called_once_with()

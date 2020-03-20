import logging
from golem_task_api.apputils import start_logging


class TestLogger:
    def test_from_arg_defaults(self):
        start_logging.from_arg()
        assert logging.getLogger().getEffectiveLevel() \
            == start_logging.DEFAULT_LEVEL

    def test_from_arg_debug_arg(self):
        start_logging.from_arg(log_level_arg='DEBUG')
        assert logging.getLogger().getEffectiveLevel() == logging.DEBUG

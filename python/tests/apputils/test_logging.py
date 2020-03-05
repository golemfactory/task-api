import logging
from golem_task_api.apputils import logging as log_util


class TestLogger:
    def test_init_logger_defaults(self):
        log_util.init_logging()
        assert logging.getLogger().getEffectiveLevel() == log_util.DEFAULT_LEVEL

    def test_init_logger_debug_arg(self):
        log_util.init_logging(log_level_arg='DEBUG')
        assert logging.getLogger().getEffectiveLevel() == logging.DEBUG

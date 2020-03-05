import logging
import logging.config

from typing import Dict, List, Optional, Union

# consts
DEFAULT_CONFIG = {'version': 1}
DEFAULT_LEVEL = logging.INFO
DEFAUTL_EXTERNAL_LOGGERS = ['hpack', 'peewee']
LOG_LEVEL_VALUES = [
    'CRITICAL',
    'ERROR',
    'INFO',
    'WARNING',
    'DEBUG',
]
# types
LogLevelArg = Union[str, int]
# vars
logger = logging.getLogger(__name__)


def init_logging(
    log_config: Dict = DEFAULT_CONFIG,
    log_level_arg: Optional[LogLevelArg] = None,
    log_level_default: int = DEFAULT_LEVEL,
    external_loggers: List[str] = DEFAUTL_EXTERNAL_LOGGERS,
    log_level_external: List[LogLevelArg] = DEFAULT_LEVEL
):
    level = log_level_arg or log_level_default
    logging.config.dictConfig(log_config)
    try:
        logging.getLogger().setLevel(level)
    except (ValueError, TypeError) as e:
        logger.warning(
            'WARNING: --log-level value not valid, no level is set.'
            ' value=%r, error=%r',
            level,
            e
        )
    for logger_name in external_loggers:
        logging.getLogger(logger_name).setLevel(log_level_external)

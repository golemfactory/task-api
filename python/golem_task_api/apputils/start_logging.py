import logging

from typing import List, Optional, Union

# consts
DEFAULT_LEVEL = logging.INFO
DEFAULT_EXTERNAL_LOGGERS = ['hpack', 'peewee']
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


def from_arg(
    log_level_arg: Optional[LogLevelArg] = None,
    log_level_default: int = DEFAULT_LEVEL,
    external_loggers: List[str] = DEFAULT_EXTERNAL_LOGGERS,
    external_log_level: LogLevelArg = DEFAULT_LEVEL
):
    """
    Configure simple python logging.
    For more options use logging.config.dictConfig()
    """
    level = log_level_arg or log_level_default
    logging.basicConfig(level=level)

    root_logger = logging.getLogger()
    try:
        logger.debug('setting root logger. level=%r', level)
        root_logger.setLevel(level)
    except (ValueError, TypeError) as e:
        logger.warning(
            'WARNING: --log-level value not valid, no level is set.'
            ' value=%r, error=%r',
            level,
            e
        )
    logger.debug('root logger level=%r', root_logger.getEffectiveLevel())
    logger.debug(
        '3rd party loggers level=%r, loggers=%r',
        external_log_level,
        external_loggers,
    )
    for logger_name in external_loggers:
        logging.getLogger(logger_name).setLevel(external_log_level)

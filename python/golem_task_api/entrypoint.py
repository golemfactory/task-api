import logging

from pathlib import Path
from typing import List, Optional

from golem_task_api.handlers import (
    AppLifecycleHandler,
    ProviderAppHandler,
    RequestorAppHandler,
)

from golem_task_api.server import (
    AppServer,
    ProviderAppServer,
    RequestorAppServer,
)

logger = logging.getLogger(__name__)


async def entrypoint(
        work_dir: Path,
        argv: List[str],
        requestor_handler: Optional[RequestorAppHandler] = None,
        requestor_lifecycle_handler: Optional[AppLifecycleHandler] = None,
        provider_handler: Optional[ProviderAppHandler] = None,
        provider_lifecycle_handler: Optional[AppLifecycleHandler] = None,
        log_level: str = None,
):
    level = log_level or logging.INFO
    logging.basicConfig()
    logging.getLogger().setLevel(level)
    external_loggers = ['hpack', 'peewee']
    for logger_name in external_loggers:
        logging.getLogger(logger_name).setLevel(logging.INFO)
    logger.debug('entrypoint(%r, %r, ..., %r)', work_dir, argv, log_level)

    cmd = argv[0]
    argv = argv[1:]
    if cmd == 'requestor':
        assert requestor_handler is not None
        server: AppServer = RequestorAppServer(
            work_dir,
            port=int(argv[0]),
            handler=requestor_handler,
            lifecycle=requestor_lifecycle_handler or AppLifecycleHandler(),
        )
    elif cmd == 'provider':
        assert provider_handler is not None
        server = ProviderAppServer(
            work_dir,
            port=int(argv[0]),
            handler=provider_handler,
            lifecycle=provider_lifecycle_handler or AppLifecycleHandler(),
        )
    else:
        raise Exception(f'Unknown command: {cmd}')

    await server.start()
    await server.wait_until_shutdown()
    logger.info('Shutting down server...')
    await server.stop()
    logger.info('Shutdown completed')

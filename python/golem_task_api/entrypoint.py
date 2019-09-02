from pathlib import Path
from typing import List, Optional

from golem_task_api.handlers import (
    AppLifecycleHandler,
    ProviderAppHandler,
    RequestorAppHandler,
)

from golem_task_api.server import (
    ProviderAppServer,
    RequestorAppServer,
)


async def entrypoint(
        work_dir: Path,
        argv: List[str],
        requestor_handler: Optional[RequestorAppHandler] = None,
        requestor_lifecycle_handler: Optional[AppLifecycleHandler] = None,
        provider_handler: Optional[ProviderAppHandler] = None,
        provider_lifecycle_handler: Optional[AppLifecycleHandler] = None,
):
    cmd = argv[0]
    argv = argv[1:]
    if cmd == 'requestor':
        server = RequestorAppServer(
            work_dir,
            port=int(argv[0]),
            handler=requestor_handler,
            lifecycle=requestor_lifecycle_handler or AppLifecycleHandler(),
        )
    elif cmd == 'provider':
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
    print('Shutting down server...')
    await server.stop()

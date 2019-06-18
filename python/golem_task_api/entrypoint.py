from pathlib import Path
from typing import List, Optional

from golem_task_api.handlers import (
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
        provider_handler: Optional[ProviderAppHandler] = None,
):
    cmd = argv[0]
    argv = argv[1:]
    if cmd == 'requestor':
        server = RequestorAppServer(
            work_dir,
            int(argv[0]),
            requestor_handler,
        )
    elif cmd == 'provider':
        server = ProviderAppServer(
            work_dir,
            int(argv[0]),
            provider_handler,
        )
    else:
        raise Exception(f'Unknown command: {cmd}')

    await server.start()
    await server.wait_until_shutdown()
    print('Shutting down server...')
    await server.stop()

import os
import shlex
import sys
import uuid
from pathlib import Path
from typing import Tuple, Optional

from aiodocker import Docker
from aiodocker.docker import DockerContainer
from golem_task_api import constants, TaskApiService
from golem_task_api.apputils.process import exec_cmd_output


async def is_docker_available():
    """ Check the connection with Docker daemon """
    docker = Docker()
    try:
        await docker.system.info()
        return True
    except Exception:  # pylint: disable=broad-except
        return False
    finally:
        await docker.close()


async def run_container(
        image: str,
        work_dir: Path,
        command: str,
        port: int
) -> DockerContainer:
    """" Start a detached container """
    ports = {}
    if sys.platform != 'linux':
        ports[f'{port}/tcp'] = port

    config = dict(
        Image=image,
        Cmd=shlex.split(command),
        Volumes={
            str(work_dir): {
                'bind': f'/{constants.WORK_DIR}',
                'mode': 'rw',
            }
        },
        User=str(os.getuid()),
        HostConfig={
            'Binds': [f'/{work_dir}:/{constants.WORK_DIR}'],
            'PortBindings': {
                f'{port}/tcp': [{
                    'HostIp': '',
                    'HostPort': f'{port}'
                }]
            },
        },
        ExposedPorts={
            f'{port}/tcp': {}
        },
        Detach=True,
    )

    return await Docker().containers.run(config, name=str(uuid.uuid4()))


async def get_docker_container_state(
        container: DockerContainer,
) -> str:
    """ Retrieve container state """
    container_config = await container.show()
    return container_config['State']


async def get_docker_container_id(
        container: DockerContainer,
) -> str:
    """ Retrieve container id """
    container_id = getattr(container, '_id', None)
    if container_id:
        return container_id
    container_config = await container.show()
    return container_config['Id']


async def get_container_port_mapping(
        container: DockerContainer,
        port: int,
        vm_name: str,
) -> Tuple[str, int]:
    """ Retrieve running container's IP address and port """

    container_config = await container.show()
    net_config = container_config['NetworkSettings']

    if sys.platform == 'darwin':
        ip_address = '127.0.0.1'
    elif sys.platform == 'win32':
        stdout, _ = await exec_cmd_output(['docker-machine', 'ip', vm_name])
        ip_address = stdout.decode('utf-8').strip()
    else:
        ip_address = net_config['Networks']['bridge']['IPAddress']

    if net_config['Ports']:
        port = int(net_config['Ports'][f'{port}/tcp'][0]['HostPort'])

    if not ip_address:
        container_id = await get_docker_container_id(container)
        raise RuntimeError(f'Unable to read the IP address of {container_id}')

    return ip_address, port


class DockerTaskApiService(TaskApiService):

    def __init__(
            self,
            image: str,
            work_dir: Path,
            vm_name: Optional[str] = 'default'
    ) -> None:
        self._image = image
        self._work_dir = work_dir
        self._vm_name: Optional[str] = vm_name
        self._container: Optional[DockerContainer] = None

    async def start(
            self,
            command: str,
            port: int,
    ) -> Tuple[str, int]:
        self._container = await run_container(
            self._image,
            self._work_dir,
            command,
            port)

        return await get_container_port_mapping(
            self._container,
            port,
            self._vm_name)

    async def stop(self) -> None:
        if not self._container:
            return
        if await self.running():
            await self._container.stop()
            await self._container.delete()

    async def running(self) -> bool:
        try:
            status = await get_docker_container_state(self._container)
        except Exception:  # pylint: disable=broad-except
            return False
        return status not in ['exited', 'error']

    async def wait_until_shutdown_complete(self) -> None:
        if not await self.running():
            return

        logs = await self._container.log(stdout=True, stderr=True)
        logs = "\n".join(logs)

        try:
            await self.stop()
        finally:
            print(logs)

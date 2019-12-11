import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple, Optional, Dict

import docker
from golem_task_api import constants, TaskApiService


def is_docker_available():
    """ Check the connection with Docker daemon """
    try:
        client = docker.from_env()
        client.ping()
    except Exception:
        return False
    return True


def run_docker_container(
        image: str,
        work_dir: Path,
        command: str,
        port: int
) -> docker.models.containers.Container:
    """" Start a detached container """
    if sys.platform == 'linux':
        ports: Dict[int, int] = {}
    else:
        ports = {port: port}

    client = docker.from_env()
    return client.containers.run(
        image=image,
        command=command,
        volumes={
            str(work_dir): {
                'bind': f'/{constants.WORK_DIR}',
                'mode': 'rw',
            }
        },
        user=os.getuid(),
        ports=ports,
        detach=True,
    )


def get_docker_container_port_mapping(
        container_id: str,
        port: int,
        vm_name: Optional[str],
) -> Tuple[str, int]:
    """ Retrieve running container's IP address and port """

    client = docker.APIClient()
    container_config = client.inspect_container(container_id)
    net_config = container_config['NetworkSettings']

    if sys.platform == 'darwin':
        ip_address = '127.0.0.1'
    elif sys.platform == 'win32':
        assert isinstance(vm_name, str)
        ip_address = subprocess.check_output(['docker-machine', 'ip', vm_name])
        ip_address = ip_address.decode('utf-8').strip()
    else:
        ip_address = net_config['Networks']['bridge']['IPAddress']

    if sys.platform != 'linux':
        port = int(net_config['Ports'][f'{port}/tcp'][0]['HostPort'])

    if not ip_address:
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
        self._vm_name = vm_name
        self._container: Optional[docker.models.containers.Container] = None

    async def start(
            self,
            command: str,
            port: int
    ) -> Tuple[str, int]:
        self._container = run_docker_container(
            self._image,
            self._work_dir,
            command,
            port)
        assert isinstance(self._container, docker.models.containers.Container)

        return get_docker_container_port_mapping(
            self._container.id,
            port,
            self._vm_name)

    async def stop(self) -> None:
        assert isinstance(self._container, docker.models.containers.Container)
        if not self.running():
            return
        self._container.stop()

    def running(self) -> bool:
        assert isinstance(self._container, docker.models.containers.Container)
        try:
            self._container.reload()
        except (AttributeError, docker.errors.APIError):
            return False
        return self._container.status not in ['exited', 'error']

    async def wait_until_shutdown_complete(self) -> None:
        assert isinstance(self._container, docker.models.containers.Container)
        print(f'Shutting down container with status: {self._container.status}')
        if not self.running():
            return

        logs = self._container.logs()
        logs = logs.decode('utf-8')

        try:
            self._container.remove(force=True)
        finally:
            print(logs)

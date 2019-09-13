import shutil
from pathlib import Path
from typing import Callable, List, Tuple

from async_generator import asynccontextmanager

from golem_task_api import (
    TaskApiService,
    constants,
    ProviderAppClient,
    RequestorAppClient,
    AppLifecycleHandler,
    ProviderAppHandler,
    RequestorAppHandler,
)
from golem_task_api.testutils import InlineTaskApiService


class TaskLifecycleUtil:
    def __init__(self, work_dir: Path) -> None:
        self.work_dir = work_dir
        self.req_work_dir = work_dir / 'requestor'
        self.req_work_dir.mkdir()
        self.prov_work_dir = work_dir / 'provider'
        self.prov_work_dir.mkdir()

    def init_provider(
            self,
            get_task_api_service: Callable[[Path], TaskApiService],
            task_id: str,
    ) -> None:
        self.mkdir_provider_task(task_id)
        self._provider_service = get_task_api_service(self.prov_task_work_dir)

    def init_provider_with_handler(
            self,
            provider_handler: ProviderAppHandler,
            lifecycle_handler: AppLifecycleHandler,
            task_id: str,
    ) -> None:
        def get_task_api_service(work_dir: Path):
            return InlineTaskApiService(
                work_dir,
                provider_handler=provider_handler,
                provider_lifecycle_handler=lifecycle_handler,
            )
        self.init_provider(get_task_api_service, task_id)

    async def start_provider(self) -> None:
        self.provider_client = \
            await ProviderAppClient.create(self._provider_service)
        # No need to finally shutdown for provider, it does this by default

    @asynccontextmanager
    async def init_requestor(
            self,
            get_task_api_service: Callable[[Path], TaskApiService],
            port: int = 50005,
    ):
        task_api_service = get_task_api_service(self.req_work_dir)
        self.requestor_client = \
            await RequestorAppClient.create(task_api_service, port)
        try:
            yield self.requestor_client
        finally:
            await self.requestor_client.shutdown()

    @asynccontextmanager
    async def init_requestor_with_handler(
            self,
            requestor_handler: RequestorAppHandler,
            lifecycle_handler: AppLifecycleHandler,
            port: int = 50005,
    ):
        def get_task_api_service(work_dir: Path):
            return InlineTaskApiService(
                work_dir,
                requestor_handler=requestor_handler,
                requestor_lifecycle_handler=lifecycle_handler,
            )
        async with self.init_requestor(get_task_api_service, port):
            yield self.requestor_client

    async def simulate_task(
            self,
            get_task_api_service: Callable[[Path], TaskApiService],
            max_subtasks_count: int,
            task_params: dict,
            resources: List[Path],
    ):
        async with self.init_requestor(get_task_api_service):
            task_id = 'test_task_id123'
            opaque_node_id = 'node_id123'
            await self.create_task(
                task_id,
                max_subtasks_count,
                resources,
                task_params,
            )
            self.init_provider(get_task_api_service, task_id)
            subtask_ids = await self.compute_remaining_subtasks(
                task_id, opaque_node_id)
            assert len(subtask_ids) <= max_subtasks_count

            assert not await self.requestor_client.has_pending_subtasks(task_id)

    def mkdir_requestor(self, task_id: str) -> None:
        self.req_task_work_dir = self.req_work_dir / task_id
        self.req_task_work_dir.mkdir()
        self.req_task_inputs_dir = \
            self.req_task_work_dir / constants.TASK_INPUTS_DIR
        self.req_task_inputs_dir.mkdir()
        self.req_subtask_inputs_dir = \
            self.req_task_work_dir / constants.SUBTASK_INPUTS_DIR
        self.req_subtask_inputs_dir.mkdir()
        self.req_task_outputs_dir = \
            self.req_task_work_dir / constants.TASK_OUTPUTS_DIR
        self.req_task_outputs_dir.mkdir()
        self.req_subtask_outputs_dir = \
            self.req_task_work_dir / constants.SUBTASK_OUTPUTS_DIR
        self.req_subtask_outputs_dir.mkdir()

    def mkdir_provider_task(self, task_id: str) -> None:
        self.prov_task_work_dir = self.prov_work_dir / task_id
        self.prov_task_work_dir.mkdir()
        self.prov_subtask_inputs_dir = \
            self.prov_task_work_dir / constants.SUBTASK_INPUTS_DIR
        self.prov_subtask_inputs_dir.mkdir()

    def mkdir_provider_subtask(self, subtask_id: str) -> None:
        prov_subtask_work_dir = self.prov_task_work_dir / subtask_id
        prov_subtask_work_dir.mkdir()

    def put_resources_to_requestor(self, resources: List[Path]) -> None:
        for resource in resources:
            shutil.copy2(resource, self.req_task_inputs_dir)

    def copy_resources_from_requestor(self, resources: List[str]) -> None:
        for resource_id in resources:
            network_resource = self.req_subtask_inputs_dir / resource_id
            assert network_resource.exists()
            shutil.copy2(network_resource, self.prov_subtask_inputs_dir)

    def copy_result_from_provider(
            self,
            output_filepath: Path,
            subtask_id: str,
    ) -> None:
        result = self.prov_task_work_dir / output_filepath
        assert result.exists()
        shutil.copy2(
            result,
            self.req_subtask_outputs_dir / f'{result.name}',
        )

    async def create_task(
            self,
            task_id: str,
            max_subtasks_count: int,
            resources: List[Path],
            task_params: dict,
    ) -> None:
        self.mkdir_requestor(task_id)

        self.put_resources_to_requestor(resources)

        await self.requestor_client.create_task(
            task_id,
            max_subtasks_count,
            task_params,
        )

    async def compute_remaining_subtasks(
            self,
            task_id: str,
            opaque_node_id: str,
    ) -> List[str]:
        """ Returns list of subtask IDs """
        subtask_ids = []
        while await self.requestor_client.has_pending_subtasks(task_id):
            subtask_id, verdict = await self.compute_next_subtask(
                task_id, opaque_node_id)
            assert verdict
            subtask_ids.append(subtask_id)
        return subtask_ids

    async def compute_next_subtask(
            self,
            task_id: str,
            opaque_node_id: str,
    ) -> Tuple[str, bool]:
        """ Returns (subtask_id, verification result) """
        assert await self.requestor_client.has_pending_subtasks(task_id)
        subtask = await self.requestor_client.next_subtask(
            task_id,
            opaque_node_id)

        self.copy_resources_from_requestor(subtask.resources)
        self.mkdir_provider_subtask(subtask.subtask_id)

        await self.start_provider()
        output_filepath = await self.provider_client.compute(
            task_id,
            subtask.subtask_id,
            subtask.params,
        )
        self.copy_result_from_provider(output_filepath, subtask.subtask_id)

        verdict = \
            await self.requestor_client.verify(task_id, subtask.subtask_id)
        return (subtask.subtask_id, verdict)

    async def run_provider_benchmark(self) -> float:
        await self.start_provider()
        return await self.provider_client.run_benchmark()

    async def shutdown_provider(self) -> None:
        return await self.provider_client.shutdown()

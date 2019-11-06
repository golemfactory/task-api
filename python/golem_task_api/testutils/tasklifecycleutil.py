import shutil
import uuid
from pathlib import Path
from typing import Callable, List, Tuple, Optional

from async_generator import asynccontextmanager

from golem_task_api import (
    enums,
    TaskApiService,
    ProviderAppClient,
    RequestorAppClient,
    AppLifecycleHandler,
    ProviderAppHandler,
    RequestorAppHandler,
    structs
)
from golem_task_api.dirutils import (
    ProviderDir,
    ProviderTaskDir,
    RequestorDir,
    RequestorTaskDir
)
from golem_task_api.testutils import InlineTaskApiService


class TaskLifecycleUtil:

    def __init__(self, work_dir: Path) -> None:
        self.work_dir = work_dir
        self.req_dir = RequestorDir(work_dir / 'requestor')
        self.req_dir.mkdir()
        self.prov_dir = ProviderDir(work_dir / 'provider')
        self.prov_dir.mkdir()

    def init_provider(
            self,
            get_task_api_service: Callable[[Path], TaskApiService],
            task_id: str,
    ) -> ProviderTaskDir:
        task_dir = self.prov_dir.task_dir(task_id)
        task_dir.prepare()
        self._provider_service = get_task_api_service(task_dir)
        return task_dir

    def init_provider_with_handler(
            self,
            provider_handler: ProviderAppHandler,
            task_id: str,
            lifecycle_handler: Optional[AppLifecycleHandler] = None,
    ) -> ProviderTaskDir:
        def get_task_api_service(work_dir: Path):
            return InlineTaskApiService(
                work_dir,
                provider_handler=provider_handler,
                provider_lifecycle_handler=lifecycle_handler,
            )
        return self.init_provider(get_task_api_service, task_id)

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
        task_api_service = get_task_api_service(self.req_dir)
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
            lifecycle_handler: Optional[AppLifecycleHandler] = None,
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
    ) -> RequestorTaskDir:
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
            return self.req_dir.task_dir(task_id)

    def put_resources_to_requestor(
            self,
            resources: List[Path],
            task_id: str
    ) -> None:
        task_inputs_dir = self.req_dir.task_dir(task_id).task_inputs_dir
        for resource in resources:
            shutil.copy2(resource, task_inputs_dir)

    def copy_resources_from_requestor(
            self,
            resources: List[str],
            task_id: str
    ) -> None:
        req_dir = self.req_dir.task_dir(task_id).subtask_inputs_dir
        prov_dir = self.prov_dir.task_dir(task_id).subtask_inputs_dir
        for resource_id in resources:
            network_resource = req_dir / resource_id
            assert network_resource.exists()
            shutil.copy2(network_resource, prov_dir)

    def copy_result_from_provider(
            self,
            output_filepath: Path,
            task_id: str,
            subtask_id: str
    ) -> None:
        result = self.prov_dir.task_dir(task_id) / output_filepath
        outputs_dir = self.req_dir.subtask_outputs_dir(task_id, subtask_id)
        outputs_dir.mkdir()
        assert result.exists()
        shutil.copy2(
            result,
            outputs_dir / result.name,
        )

    async def create_task(
            self,
            task_id: str,
            max_subtasks_count: int,
            resources: List[Path],
            task_params: dict,
    ) -> structs.Task:
        self.req_dir.task_dir(task_id).prepare()

        self.put_resources_to_requestor(resources, task_id)

        return await self.requestor_client.create_task(
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
            assert verdict is enums.VerifyResult.SUCCESS
            subtask_ids.append(subtask_id)
        return subtask_ids

    async def compute_next_subtask(
            self,
            task_id: str,
            opaque_node_id: str,
    ) -> Tuple[str, enums.VerifyResult]:
        """ Returns (subtask_id, verification result) """
        assert await self.requestor_client.has_pending_subtasks(task_id)
        subtask_id = str(uuid.uuid4())
        subtask = await self.requestor_client.next_subtask(
            task_id,
            subtask_id,
            opaque_node_id
        )

        self.copy_resources_from_requestor(subtask.resources, task_id)
        self.prov_dir.subtask_dir(task_id, subtask_id).mkdir()

        await self.start_provider()
        output_filepath = await self.provider_client.compute(
            task_id,
            subtask_id,
            subtask.params,
        )
        self.copy_result_from_provider(output_filepath, task_id, subtask_id)

        result, reason = await self.requestor_client.verify(
            task_id,
            subtask_id
        )
        return subtask_id, result

    async def run_provider_benchmark(self) -> float:
        await self.start_provider()
        return await self.provider_client.run_benchmark()

    async def shutdown_provider(self) -> None:
        return await self.provider_client.shutdown()

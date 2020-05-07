import abc
import asyncio
import json
import logging
import ssl
import time
from typing import ClassVar, List, Tuple, Optional
from pathlib import Path

from grpclib.client import Channel
from grpclib.exceptions import StreamTerminatedError
from grpclib.health.v1.health_grpc import HealthStub
from grpclib.health.v1.health_pb2 import HealthCheckRequest, HealthCheckResponse
from grpclib.utils import Wrapper

from golem_task_api.enums import VerifyResult
from golem_task_api.messages import (
    AbortSubtaskRequest,
    AbortSubtaskReply,
    AbortTaskRequest,
    AbortTaskReply,
    CreateTaskRequest,
    CreateTaskReply,
    NextSubtaskRequest,
    NextSubtaskReply,
    ComputeRequest,
    ComputeReply,
    VerifyRequest,
    VerifyReply,
    DiscardSubtasksRequest,
    DiscardSubtasksReply,
    RunBenchmarkRequest,
    RunBenchmarkReply,
    HasPendingSubtasksRequest,
    HasPendingSubtasksReply,
    ShutdownRequest,
)
from golem_task_api.proto.golem_task_api_grpc import (
    ProviderAppStub,
    RequestorAppStub,
)
from golem_task_api.structs import Subtask, Task, Infrastructure

CONNECTION_TIMEOUT = 15.0  # seconds
logger = logging.getLogger(__name__)


async def _wait_for_channel(
        host: str,
        port: int,
        timeout: float = CONNECTION_TIMEOUT,
        ssl_context: Optional[ssl.SSLContext] = None,
) -> Channel:
    logger.debug('Starting service health check')
    request = HealthCheckRequest()
    request.service = ''  # empty service name for a server check

    deadline = time.time() + timeout
    while time.time() < deadline:
        channel = Channel(
            host,
            port,
            ssl=ssl_context,
            loop=asyncio.get_event_loop())
        client = HealthStub(channel)
        try:
            response = await client.Check(request)
            if response.status == HealthCheckResponse.SERVING:
                logger.debug('Service health check completed with success')
                return channel
        except (StreamTerminatedError, ConnectionError):
            pass
        channel.close()
        sleep_time = 0.1
        logger.debug(
            'Service health check failed, will try again in %fs. deadline=%r',
            sleep_time,
            deadline,
        )
        await asyncio.sleep(sleep_time)

    raise TimeoutError


class ShutdownException(Exception):
    pass


class TaskApiService(abc.ABC):

    @abc.abstractmethod
    def running(self) -> bool:
        """
        Checks if the service is still running.
        E.g. For inline this would be implemented as:
        `thread.is_alive()`
        """
        pass

    @abc.abstractmethod
    async def start(self, command: str, port: int) -> Tuple[str, int]:
        """
        This method is supposed to pass the command argument to the entrypoint
        which will asynchronously spawn the server and should return a tuple
        (host, port) where one can connect to this server. The method **should
        not** use the event loop in which it is being called to run the service
        (but rather spawn a new thread or process).
        E.g. for Docker app this could be implemented as:
        `docker run --detach <command>`
        """
        pass

    @abc.abstractmethod
    async def stop(self) -> None:
        """ Force service shutdown. E.g. by calling `docker stop` """

    async def open_channel(
            self,
            command: str,
            port: int,
            ssl_context: Optional[ssl.SSLContext] = None,
    ) -> Channel:
        """
        Start the service and wait for it to start listening. Return GRPC
        channel for connecting to the service. In case any exception is raised
        stop the service to avoid orphaned processes.
        """
        try:
            host, port = await self.start(command, port)
            return await _wait_for_channel(
                host,
                port,
                ssl_context=ssl_context)
        except Exception:
            if self.running():
                await self.stop()
            raise

    @abc.abstractmethod
    async def wait_until_shutdown_complete(self) -> None:
        """
        After sending the Shutdown request one should wait for the server to
        finish it's cleanup and shutdown completely.
        E.g. for Docker app this should wait for the container to exit
        """
        pass


class AppClient(abc.ABC):
    SOFT_SHUTDOWN_TIMEOUT: ClassVar[float] = 5.0  # seconds

    def __init__(self, service: TaskApiService) -> None:
        self._service = service
        self._kill_switch = Wrapper()
        self._shutdown_future = asyncio.get_event_loop().create_future()

    async def shutdown(self, timeout: float = SOFT_SHUTDOWN_TIMEOUT) -> None:
        logger.debug('shutdown(%r) called', timeout)
        if self._kill_switch.cancelled:
            logger.debug('kill_switch already cancelled.')
            await self._shutdown_future
            return
        logger.debug('triggering kill switch')
        self._kill_switch.cancel(ShutdownException("Shutdown requested"))
        if not self._service.running():
            logger.debug('service already stopped, early exit')
            return
        try:
            logger.debug('waiting for service to stop')
            await asyncio.wait_for(self._soft_shutdown(), timeout=timeout)
        except (
                asyncio.TimeoutError,
                StreamTerminatedError,
                ConnectionRefusedError
        ):
            # Catching StreamTerminatedError and ConnectionRefusedError
            # because server might have stopped between calling
            # self._service.running() and self._soft_shutdown()
            if self._service.running():
                await self._service.stop()
                await self._service.wait_until_shutdown_complete()
        finally:
            self._shutdown_future.set_result(None)
            logger.debug('finished shutdown')

    @abc.abstractmethod
    async def _soft_shutdown(self) -> None:
        raise NotImplementedError


class RequestorAppClient(AppClient):
    DEFAULT_PORT: ClassVar[int] = 50005

    @classmethod
    async def create(
            cls,
            service: TaskApiService,
            port: int = DEFAULT_PORT,
            ssl_context: Optional[ssl.SSLContext] = None,
    ) -> 'RequestorAppClient':
        channel = await service.open_channel(
            f'requestor {port}',
            port,
            ssl_context)
        app_stub = RequestorAppStub(channel)
        return cls(service, app_stub)

    def __init__(
            self,
            service: TaskApiService,
            app_stub: RequestorAppStub,
    ) -> None:
        super().__init__(service)
        self._golem_app = app_stub

    async def create_task(
            self,
            task_id: str,
            max_subtasks_count: int,
            task_params: dict,
    ) -> Task:
        logger.debug(
            'Creating task. task_id=%r, max_subtasks=%r, task_params=%r',
            task_id,
            max_subtasks_count,
            task_params,
        )
        request = CreateTaskRequest()
        request.task_id = task_id
        request.max_subtasks_count = max_subtasks_count
        request.task_params_json = json.dumps(task_params)
        reply = await self._golem_app.CreateTask(request)

        inf_requirements = Infrastructure()
        inf_requirements.min_memory_mib = reply.inf_requirements.min_memory_mib

        task = Task(
            env_id=reply.env_id,
            prerequisites=json.loads(reply.prerequisites_json),
            inf_requirements=inf_requirements)

        logger.debug(
            'Task created. '
            'task_id=%r, env_id=%r, prerequisites=%r, inf_requirements=%r',
            task_id,
            task.env_id,
            task.prerequisites,
            task.inf_requirements,
        )
        return task

    async def next_subtask(
            self,
            task_id: str,
            subtask_id: str,
            opaque_node_id: str,
    ) -> Optional[Subtask]:
        logger.debug(
            'Preparing next subtask. task_id=%r, subtask_id=%r, node_id=%r',
            task_id,
            subtask_id,
            opaque_node_id,
        )
        request = NextSubtaskRequest()
        request.task_id = task_id
        request.subtask_id = subtask_id
        request.opaque_node_id = opaque_node_id
        reply = await self._golem_app.NextSubtask(request)
        if not reply.HasField('subtask'):
            logger.debug('No next subtask given')
            return None
        subtask = Subtask(
            params=json.loads(reply.subtask.subtask_params_json),
            resources=reply.subtask.resources,
        )
        logger.debug(
            'Next subtask ready! subtask_id=%r, params=%r, resources=%r',
            subtask_id,
            subtask.params,
            subtask.resources,
        )
        return subtask

    async def verify(
            self,
            task_id: str,
            subtask_id: str,
    ) -> Tuple[VerifyResult, str]:
        request = VerifyRequest()
        request.task_id = task_id
        request.subtask_id = subtask_id
        reply = await self._golem_app.Verify(request)
        return VerifyResult(reply.result), reply.reason

    async def discard_subtasks(
            self,
            task_id: str,
            subtask_ids: List[str],
    ) -> List[str]:
        request = DiscardSubtasksRequest()
        request.task_id = task_id
        request.subtask_ids.extend(subtask_ids)
        reply = await self._golem_app.DiscardSubtasks(request)
        return reply.discarded_subtask_ids

    async def run_benchmark(self) -> float:
        request = RunBenchmarkRequest()
        reply = await self._golem_app.RunBenchmark(request)
        return reply.score

    async def has_pending_subtasks(self, task_id: str) -> bool:
        request = HasPendingSubtasksRequest()
        request.task_id = task_id
        reply = await self._golem_app.HasPendingSubtasks(request)
        return reply.has_pending_subtasks

    async def abort_task(self, task_id: str) -> None:
        request = AbortTaskRequest()
        request.task_id = task_id
        await self._golem_app.AbortTask(request)

    async def abort_subtask(self, task_id: str, subtask_id: str) -> None:
        request = AbortSubtaskRequest()
        request.task_id = task_id
        request.subtask_id = subtask_id
        await self._golem_app.AbortSubtask(request)

    async def _soft_shutdown(self) -> None:
        request = ShutdownRequest()
        await self._golem_app.Shutdown(request)
        await self._service.wait_until_shutdown_complete()


class ProviderAppClient(AppClient):
    DEFAULT_PORT: ClassVar[int] = 50006

    @classmethod
    async def create(
            cls,
            service: TaskApiService,
            port: int = DEFAULT_PORT,
            ssl_context: Optional[ssl.SSLContext] = None,
    ) -> 'ProviderAppClient':
        channel = await service.open_channel(
            f'provider {port}',
            port,
            ssl_context)
        app_stub = ProviderAppStub(channel)
        return cls(service, app_stub)

    def __init__(
            self,
            service: TaskApiService,
            app_stub: ProviderAppStub,
    ) -> None:
        super().__init__(service)
        self._golem_app = app_stub

    async def compute(
            self,
            task_id: str,
            subtask_id: str,
            subtask_params: dict,
    ) -> Path:
        request = ComputeRequest()
        request.task_id = task_id
        request.subtask_id = subtask_id
        request.subtask_params_json = json.dumps(subtask_params)
        try:
            with self._kill_switch:
                reply = await self._golem_app.Compute(request)
        except Exception:
            await self.shutdown()
            raise
        finally:
            await self._service.wait_until_shutdown_complete()
        return Path(reply.output_filepath)

    async def run_benchmark(self) -> float:
        request = RunBenchmarkRequest()
        try:
            with self._kill_switch:
                reply = await self._golem_app.RunBenchmark(request)
        except Exception:
            await self.shutdown()
            raise
        finally:
            await self._service.wait_until_shutdown_complete()
        return reply.score

    async def _soft_shutdown(self) -> None:
        request = ShutdownRequest()
        await self._golem_app.Shutdown(request)
        await self._service.wait_until_shutdown_complete()

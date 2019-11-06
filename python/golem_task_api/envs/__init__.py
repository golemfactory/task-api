from google.protobuf.json_format import MessageToDict

from golem_task_api.envs.constants import DOCKER_CPU_ENV_ID, DOCKER_GPU_ENV_ID
from golem_task_api.proto.envs_pb2 import DockerPrerequisites
from golem_task_api.structs import Task, Infrastructure


def _create_docker_task(
        env_id: str,
        image: str,
        tag: str,
        inf: Infrastructure,
) -> Task:
    prerequisites = DockerPrerequisites()
    prerequisites.image = image
    prerequisites.tag = tag
    prerequisites_dict = MessageToDict(
        prerequisites,
        preserving_proto_field_name=True)

    return Task(
        env_id=env_id,
        prerequisites=prerequisites_dict,
        inf_requirements=inf)


def create_docker_cpu_task(image: str, tag: str, inf: Infrastructure) -> Task:
    return _create_docker_task(DOCKER_CPU_ENV_ID, image, tag, inf)


def create_docker_gpu_task(image: str, tag: str, inf: Infrastructure) -> Task:
    return _create_docker_task(DOCKER_GPU_ENV_ID, image, tag, inf)

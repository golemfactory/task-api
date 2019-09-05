from google.protobuf.json_format import MessageToJson

from golem_task_api.envs.constants import DOCKER_CPU_ENV_ID, DOCKER_GPU_ENV_ID
from golem_task_api.proto.envs_pb2 import DockerPrerequisites
from golem_task_api.proto.golem_task_api_pb2 import CreateTaskReply


def _create_docker_task_reply(
        env_id: str,
        image: str,
        tag: str
) -> CreateTaskReply:
    prerequisites = DockerPrerequisites()
    prerequisites.image = image
    prerequisites.tag = tag
    prerequisites_json = MessageToJson(prerequisites)

    reply = CreateTaskReply()
    reply.env_id = env_id
    reply.prerequisites_json = prerequisites_json
    return reply


def create_docker_cpu_task_reply(image: str, tag: str) -> CreateTaskReply:
    return _create_docker_task_reply(DOCKER_CPU_ENV_ID, image, tag)


def create_docker_gpu_task_reply(image: str, tag: str) -> CreateTaskReply:
    return _create_docker_task_reply(DOCKER_GPU_ENV_ID, image, tag)

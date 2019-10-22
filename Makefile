.PHONY: python
python:
	  python -m grpc_tools.protoc --proto_path=. --python_out=python/ --python_grpc_out=python/ golem_task_api/proto/*.proto
	  python python/gen_enums.py python/golem_task_api/proto/golem_task_api_pb2.py python/golem_task_api/enums.py
	  python python/gen_constants.py golem_task_api.proto.constants_pb2 python/golem_task_api/constants.py
	  python python/gen_constants.py golem_task_api.proto.envs_pb2 python/golem_task_api/envs/constants.py

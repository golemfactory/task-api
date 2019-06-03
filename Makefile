.PHONY: python
python:
	  python -m grpc_tools.protoc --proto_path=. --python_out=python/ --python_grpc_out=python/ golem_task_api/proto/*.proto

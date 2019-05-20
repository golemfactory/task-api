.PHONY: python
python:
	  python -m grpc_tools.protoc --proto_path=proto --python_out=python/ --python_grpc_out=python/ proto/golem_task_api/*.proto

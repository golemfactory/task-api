# Golem task-api Python module

This is the python module to use as super class for your task_api implementation.

## Running generator

After updating the `*.proto` files you need to re-generate the python code and commit the changes together.

### Install requirements
To install the requirements for the generator you run:

```
cd <task-api-git-root>/
python python/setup.py develop
pip install -r requirements-build.txt
```

### Run the generator
To generate the updated python code run:
```
make python
```

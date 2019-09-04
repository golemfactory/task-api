from setuptools import setup

setup(
    name='Golem-Task-Api',
    version='0.14.0',
    url='https://github.com/golemfactory/golem/task-api/python',
    maintainer='The Golem team',
    maintainer_email='tech@golem.network',
    packages=[
        'golem_task_api',
        'golem_task_api.proto',
        'golem_task_api.testutils',
    ],
    python_requires='>=3.6',
    install_requires=[
        'async-generator==1.10',
        'grpclib==0.2.4',
        'protobuf==3.7.1',
    ],
)

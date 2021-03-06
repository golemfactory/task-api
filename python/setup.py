from setuptools import setup


setup(
    name='Golem-Task-Api',
    version='0.24.7',
    url='https://github.com/golemfactory/golem/task-api/python',
    maintainer='The Golem team',
    maintainer_email='tech@golem.network',
    packages=[
        'golem_task_api',
        'golem_task_api.envs',
        'golem_task_api.proto',
        'golem_task_api.apputils',
        'golem_task_api.apputils.database',
        'golem_task_api.apputils.task',
        'golem_task_api.testutils',
    ],
    python_requires='>=3.6',
    install_requires=[
        'async-generator==1.10',
        'dataclasses==0.6',
        'dataclasses-json==0.3.0',
        'grpclib==0.2.4',
        'protobuf==3.7.1',
    ]
)

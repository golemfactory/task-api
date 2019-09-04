import asyncio
import functools
from collections import Callable
from typing import Any


class Executor:
    _tasks = set()
    _shutting_down = asyncio.Event()

    @classmethod
    def initialize(cls) -> None:
        cls._shutting_down.clear()

    @classmethod
    async def run(
            cls,
            func: Callable,
            *args,
            **kwargs
    ) -> Any:
        func = functools.partial(func, **kwargs)
        loop = asyncio.get_event_loop()
        task = loop.run_in_executor(None, func, *args)

        cls._tasks.add(task)
        try:
            return await task
        finally:
            cls._tasks.remove(task)

    @classmethod
    def request_shutdown(cls) -> None:
        cls._shutting_down.set()

    @classmethod
    async def wait_for_shutdown(cls, timeout: float = 5.) -> None:
        if not cls._tasks:
            return

        tasks = list(cls._tasks)
        cls._tasks = None
        await asyncio.wait(tasks, timeout=timeout)

    @classmethod
    def is_shutting_down(cls) -> bool:
        return cls._shutting_down.is_set()

import asyncio
import time
from typing import Tuple

from dataclasses import dataclass
from golem_task_api.threading import Executor


@dataclass
class Usage:
    mem_peak: float = 0.  # bytes
    cpu_time: float = 0.
    real_time: float = 0.


def _monitor_pid(
        pid: int,
        usage: Usage,
        interval: float = 0.5
) -> None:
    from psutil import Process

    proc = Process(pid)
    while proc.is_running() and not Executor.is_shutting_down():
        usage.cpu_time = sum(proc.cpu_times())
        usage.mem_peak = max(usage.mem_peak, proc.memory_info().vms)
        time.sleep(interval)


async def exec_and_monitor_cmd(cmd) -> Tuple[int, Usage]:
    usage = Usage()
    time_started = time.time()

    process = await asyncio.create_subprocess_exec(*cmd)
    future = Executor.run(_monitor_pid, process.pid, usage)
    asyncio.ensure_future(future)

    try:
        return_code = await process.wait()
    except asyncio.CancelledError:
        process.terminate()
        raise

    usage.real_time = time.time() - time_started
    return return_code, usage


async def exec_cmd(cmd) -> int:
    process = await asyncio.create_subprocess_exec(*cmd)
    try:
        return await process.wait()
    except asyncio.CancelledError:
        process.terminate()
        raise


async def exec_cmd_output(cmd) -> Tuple[bytes, bytes]:
    process = await asyncio.create_subprocess_exec(*cmd)
    try:
        return await process.communicate()
    except asyncio.CancelledError:
        process.terminate()
        raise

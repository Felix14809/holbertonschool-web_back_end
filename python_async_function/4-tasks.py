#!/usr/bin/env python3
"""
program that calls wait_random using returned asyncio task
from task_wait_random
"""
import asyncio
from typing import List
get_task = __import__('3-tasks').task_wait_random


async def task_wait_n(n: int, max_delay: int) -> List[float]:
    """
    runs wait_random n times through get_task
    and returns a list of the waits
    """
    delays = []
    coroutines = [get_task(max_delay) for _ in range(n)]
    for task in asyncio.as_completed(coroutines):
        delays.append(await task)
    return delays

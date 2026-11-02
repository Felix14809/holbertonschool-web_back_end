#!/usr/bin/env python3
"""A simple program showing basic asyncio syntax"""
import asyncio
from typing import List
wait_random = __import__('0-basic_async_syntax').wait_random


async def wait_n(n: int, max_delay: int) -> List[float]:
    """runs wait_random n times and returns a list of the waits"""
    delays = []
    coroutines = [wait_random(max_delay) for i in range(n)]
    for task in asyncio.as_completed(coroutines):
        delays.append(await task)
    return delays

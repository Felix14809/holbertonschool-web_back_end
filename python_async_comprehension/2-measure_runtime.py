#!/usr/bin/env python3
"""
Simple demonstration of async comprehension
"""
import asyncio
import time
async_comprehension = __import__('1-async_comprehension').async_comprehension


async def measure_runtime() -> float:
    """
    Runs async comprehension 4 times and returns time taken
    """

    start = time.perf_counter()
    coroutines = [async_comprehension() for _ in range(4)]
    await asyncio.gather(*coroutines)
    return (time.perf_counter() - start)

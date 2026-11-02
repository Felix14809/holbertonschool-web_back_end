#!/usr/bin/env python3
"""
simple syntax for an async generator
"""
import asyncio
import random
from typing import AsyncGenerator


async def async_generator() -> AsyncGenerator[float, None]:
    """
    generator that yields a random number per iteration 10 times
    """

    for _ in range(10):
        await asyncio.sleep(1)
        yield random.uniform(0, 10)

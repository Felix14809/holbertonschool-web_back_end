#!/usr/bin/env python3
"""
Simple demonstration of async comprehension
"""
import asyncio
from typing import Generator, List
async_generator = __import__('0-async_generator').async_generator


async def async_comprehension() -> List[float]:
    """
    Runs async_generators and returns a list of its returns
    """
    return [x async for x in async_generator()]

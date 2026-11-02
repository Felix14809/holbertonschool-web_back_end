#!/usr/bin/env python3
"""A simple program showing basic asyncio syntax"""
import asyncio
import random


async def wait_random(max_delay: int = 10) -> float:
    """takes an input and waits a random amount of time"""
    rand_delay = random.uniform(0, max_delay)
    await asyncio.sleep(rand_delay)
    return rand_delay

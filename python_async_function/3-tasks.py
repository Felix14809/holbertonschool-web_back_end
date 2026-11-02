#!/usr/bin/env python3
"""A simple program showing basic asyncio syntax"""
import asyncio
from typing import List
wait_random = __import__('0-basic_async_syntax').wait_random


def task_wait_random(max_delay: int) -> float:
    """
    creates and returns an asyncio task
    """

    return asyncio.create_task(wait_random(max_delay))

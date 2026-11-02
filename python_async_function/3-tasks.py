#!/usr/bin/env python3
"""A simple program showing basic asyncio syntax"""
import asyncio
wait_random = __import__('0-basic_async_syntax').wait_random


def task_wait_random(max_delay: int) -> asyncio.Task:
    """
    creates and returns an asyncio task
    """
    return asyncio.create_task(wait_random(max_delay))

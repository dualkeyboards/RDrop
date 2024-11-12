#main.py
import asyncio
import os
import signal
from loguru import logger
from _includes.connect import connect
from _includes.status_bar import StickyStatusBar
from _includes.interrupt import interrupt_handler
import collections

async def main():
    user_id = input('Please Enter your user ID: ')
    try:
        with open('local_proxies.txt', 'r') as file:
            local_proxies = file.read().splitlines()
    except FileNotFoundError:
        logger.error("local_proxies.txt not found. Create a file with your proxies.")
        return

    if not local_proxies:
        logger.error("local_proxies.txt is empty. Please add proxies.")
        return

    status_bar = StickyStatusBar("ACTIVE: 0 | PING: 0 | PONG: 0 | DROP: 0")
    interrupt_handler(status_bar)

    async def update_status_bar(tasks, stats):
        while True:
            active_tasks = sum(1 for task in tasks if not task.done())
            status_bar.update(f"ACTIVE: {active_tasks} | PING: {stats['pings']} | PONG: {stats['pongs']} | DROP: {stats['dropped']}")
            await asyncio.sleep(0.25)

    async def connect_with_stats(proxy, user_id, stats):
        try:
            await connect(proxy, user_id, stats)
        except Exception as e:
            if not isinstance(e, asyncio.CancelledError):
                 logger.exception(f"Proxy {proxy} dropped: {e}")
                 stats['dropped'] += 1


    stats = collections.defaultdict(int)
    tasks = [asyncio.create_task(connect_with_stats(proxy, user_id, stats)) for proxy in local_proxies]
    status_task = asyncio.create_task(update_status_bar(tasks, stats))

    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        if not isinstance(e, asyncio.CancelledError):
            logger.exception(f"An error occurred: {e}")
    finally:
        status_bar.clear()
        logger.info("Shutdown complete (if reached).")


if __name__ == '__main__':
    asyncio.run(main())
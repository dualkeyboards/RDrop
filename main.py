# main.py
import asyncio
from loguru import logger
from _includes.connect import connect

async def main():
    user_id = input('Please Enter your user ID: ')
    try:
        with open('local_proxies.txt', 'r') as file:
            local_proxies = file.read().splitlines()
    except FileNotFoundError:
        logger.error("local_proxies.txt not found.  Create a file containing your proxies, one per line.")
        return

    tasks = [asyncio.create_task(connect(proxy, user_id)) for proxy in local_proxies]

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        for task in tasks:
            task.cancel()
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError:
            pass  # Suppress CancelledError during shutdown
        logger.info("Shutdown complete.")


if __name__ == '__main__':
    asyncio.run(main())
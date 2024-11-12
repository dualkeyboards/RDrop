#main.py
import asyncio
import os
import signal
import sys
from loguru import logger
from _includes.connect import connect
from _includes.status_bar import StickyStatusBar
from _includes.interrupt import interrupt_handler
import collections
import time
import re

# Helper function to get background color based on log level
def _get_background_color(level_name):
    color_mapping = {
        "ERROR": "41",  # Red
        "INFO": "47",  # White
        "SUCCESS": "42",  # Green
        "WARNING": "43", # Yellow
    }
    return color_mapping.get(level_name, "0")  # Default to no background

# Helper function to get custom prefix based on level
def _get_prefix(level_name):
    prefix_mapping = {
        "INFO": "     ",  # 6 spaces
        "WARNING": "  ",  # 3 spaces
        "SUCCESS": "  ",  # 3 spaces
        "ERROR": "    ",  # 5 spaces
    }
    return prefix_mapping.get(level_name, "")  # Default to empty prefix

# Helper function to format IP address
def format_ip(ip_address):
    if ip_address:  # Check if ip_address is not None
        parts = ip_address.split(".")
        formatted_parts = []
        for part in parts:
            part = part.rjust(3)  # Pad with spaces to 3 characters
            formatted_parts.append(part)
        return ".".join(formatted_parts)
    return ""  # Return empty string if ip_address is None

def colored_sink(message):
    record = message.record
    formatted_message = " {time}{level: <8}{message}" # {name}:{function}:{line}

    # Apply color to the entire level section:
    colored_level = f"\033[30m\033[{_get_background_color(record['level'].name)}m{_get_prefix(record['level'].name)} {record['level'].name} \033[0m"

    # Colorize the timestamp background in cyan and text in black:
    colored_time = f"\033[46m\033[30m {record['time'].strftime('%Y-%m-%d %H:%M:%S')} \033[0m"  # 46 for cyan background, 30 for black text

    styled_message = formatted_message.format(
        time=colored_time,  # Use colored time
        level=colored_level,  # Use colored level
        name=record["name"],
        function=record["function"],
        line=record["line"],
        message=record["message"]
    )
    print(styled_message)


logger.configure(
    patcher=lambda record: record["extra"].update(time=record["time"].strftime("%Y-%m-%d %H:%M:%S")),
    handlers=[{"sink": colored_sink}]
)

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

    num_devices = len(local_proxies)
    logger.info(f"\033[44m CONNECTING     \033[42;37m {num_devices} devices\033[0m")  # Log the connection message

    status_bar = StickyStatusBar("\033[30m")
    interrupt_handler(status_bar)

    async def update_status_bar(tasks, stats):
        while True:
            active_tasks = sum(1 for task in tasks if not task.done())
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")  # Get current time
            styled_text = f" \033[46m\033[30m {current_time} \033[0m\033[47m\033[30m    ACTIVE \033[0m\033[102m\033[30m {active_tasks} \033[0m\033[47m\033[30m PING \033[0m\033[102m\033[30m {stats['pings']} \033[0m\033[47m\033[30m PONG \033[0m\033[102m\033[30m {stats['pongs']} \033[0m"
            print(f"\0337{styled_text}\r\0338", end="", flush=True)
            await asyncio.sleep(0.25)

    async def connect_with_stats(proxy, user_id, stats):
        # Extract components from the proxy string using urlparse (more reliable)
        try:
            from urllib.parse import urlparse  # Python 3
        except ImportError:
            from urlparse import urlparse  # Python 2

        parsed_proxy = urlparse(proxy)
        proxy_ip = format_ip(parsed_proxy.hostname)
        protocol = parsed_proxy.scheme
        port = parsed_proxy.port
        if parsed_proxy.username:
            username_password = f"{parsed_proxy.username}:{parsed_proxy.password}@"
        else:
            username_password = "" # or None if you prefer

        try:
            await connect(proxy, user_id, stats, proxy_ip, protocol, username_password, port) # Pass proxy_ip to connect
        except Exception as e:
            if not isinstance(e, asyncio.CancelledError):
                logger.exception(f"Proxy {formatted_ip} dropped: {e}")
                stats['dropped'] += 1

    stats = collections.defaultdict(int)
    tasks = [asyncio.create_task(connect_with_stats(proxy, user_id, stats)) for proxy in local_proxies]
    status_task = asyncio.create_task(update_status_bar(tasks, stats))

    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        if not isinstance(e, asyncio.CancelledError):
            logger.exception(f"An error occurred: {e}") # Log other exceptions
    finally:
        status_bar.clear()
        logger.info("\033[41;37m Shutting down ...\033[0m")



if __name__ == '__main__':
    asyncio.run(main())
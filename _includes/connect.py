#_includes/connect.py
import asyncio
import random
import ssl
import uuid

from loguru import logger
from fake_useragent import UserAgent
from websockets_proxy import Proxy, proxy_connect
from .ping import ping
from .response import response

URILIST = ["wss://proxy.wynd.network:4444/", "wss://proxy.wynd.network:4650/"]
SERVER_HOSTNAME = "proxy.wynd.network"

async def connect(socks5_proxy, user_id, stats, proxy_ip, protocol, username_password, port, max_retries=2):  # Added stats parameter
    """Connects to the websocket and handles interaction with retry logic."""
    retries = 0
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, socks5_proxy))

    while retries < max_retries:
        try:
            random_user_agent = UserAgent(os=['windows', 'macos', 'linux'], browsers='chrome').random
            custom_headers = {"User-Agent": random_user_agent}
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            uri = random.choice(URILIST)
            proxy = Proxy.from_url(socks5_proxy)

            async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname=SERVER_HOSTNAME,
                                     extra_headers=custom_headers) as websocket:
                asyncio.create_task(ping(websocket, stats, proxy_ip))  # Pass socks5_proxy
                await response(websocket, device_id, user_id, random_user_agent, stats, proxy_ip)  # Pass socks5_proxy

        except asyncio.CancelledError:
            logger.info(f"Connection task cancelled for proxy: \033[47m\033[30m {proxy_ip}\033[0m")
            break

        except Exception as e:
            retries += 1
            logger.error(f"\033[43;30m {retries}/{max_retries} RETRIES    \033[47;30m {proxy_ip}\033[0m")
            if retries >= max_retries:
                stats['dropped'] += 1  # Increment dropped count if max retries reached
                logger.error(f"\033[43;30m MAX RETRIES    \033[47;30m {proxy_ip}\033[0m")
            await asyncio.sleep(5)
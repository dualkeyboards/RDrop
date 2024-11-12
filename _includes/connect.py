# _includes/connect.py
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

async def connect(socks5_proxy, user_id, max_retries=2):
    """Connects to the websocket and handles interaction with retry logic."""
    retries = 0
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, socks5_proxy))

    while retries < max_retries:
        try:
            # Instantiate UserAgent inside the loop to ensure uniqueness
            random_user_agent = UserAgent(os=['windows', 'macos', 'linux'], browsers='chrome').random
            custom_headers = {"User-Agent": random_user_agent}
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            uri = random.choice(URILIST)
            proxy = Proxy.from_url(socks5_proxy)

            logger.info(f"Connecting with device ID: {device_id}")

            async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname=SERVER_HOSTNAME,
                                     extra_headers=custom_headers) as websocket:
                asyncio.create_task(ping(websocket))
                await response(websocket, device_id, user_id, random_user_agent)

        except asyncio.CancelledError:
            logger.info(f"Connection task cancelled for proxy: {socks5_proxy}")
            break  # Exit the loop gracefully on cancellation

        except Exception as e:
            retries += 1
            logger.error(f"Error with proxy {socks5_proxy}: {e}. Retry attempt {retries}/{max_retries}")
            await asyncio.sleep(5)  # Wait before retrying

        if retries >= max_retries:
            logger.error(f"Max retries reached for proxy {socks5_proxy}. Giving up.")
            break

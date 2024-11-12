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

USER_AGENT = UserAgent(os=['windows', 'macos', 'linux'], browsers='chrome')
URILIST = ["wss://proxy.wynd.network:4444/", "wss://proxy.wynd.network:4650/"]
SERVER_HOSTNAME = "proxy.wynd.network"

async def connect(socks5_proxy, user_id, progress):
    """Connects to the websocket and handles interaction."""
    global ip_count, error_count

    random_user_agent = USER_AGENT.random
    try:
        device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, socks5_proxy))
        logger.info(f"Connecting with device ID: {device_id}")

        while True:
            try:
                await asyncio.sleep(random.uniform(0.1, 1))
                custom_headers = {"User-Agent": random_user_agent}
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False  # SECURITY RISK: Address this in a production setting.
                ssl_context.verify_mode = ssl.CERT_NONE  # SECURITY RISK: Address this!
                uri = random.choice(URILIST)

                try:  # Inner try-except for proxy errors
                    proxy = Proxy.from_url(socks5_proxy)
                    ip_count += 1  # Increment ip_count only after successful proxy creation
                except ValueError as ve:
                    logger.error(f"Invalid proxy format: {socks5_proxy}. Error: {ve}")
                    error_count += 1
                    break  # Or try the next proxy if available

                async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname=SERVER_HOSTNAME,
                                        extra_headers=custom_headers) as websocket:
                    asyncio.create_task(ping(websocket, progress))  # Pass progress to ping
                    await response(websocket, device_id, user_id, random_user_agent, progress)  # Pass progress

            except (OSError, asyncio.TimeoutError, ConnectionRefusedError, ConnectionResetError) as ce:
                logger.error(f"Connection error with proxy {socks5_proxy}: {ce}")
                error_count += 1
                await asyncio.sleep(5)  # Wait before retrying

            except asyncio.CancelledError:
                logger.info(f"Connection task cancelled for proxy: {socks5_proxy}")
                break  # Exit the loop gracefully

            except Exception as e:
                logger.error(f"Unexpected error during websocket interaction: {e}")
                error_count += 1
                break  # Stop the loop for this proxy and move on

    except ValueError as ve:
        logger.error(f"Invalid proxy format (outer): {socks5_proxy}. Error: {ve}")
        error_count += 1

    except Exception as e:
        logger.error(f"Unexpected error during setup: {e}")
        error_count += 1

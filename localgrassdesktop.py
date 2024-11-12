import asyncio
import random
import ssl
import json
import time
import uuid
import requests
import shutil
from loguru import logger
from websockets_proxy import Proxy, proxy_connect
from fake_useragent import UserAgent

USER_AGENT = UserAgent(os=['windows', 'macos', 'linux'], browsers='chrome')
URILIST = ["wss://proxy.wynd.network:4444/", "wss://proxy.wynd.network:4650/"]
SERVER_HOSTNAME = "proxy.wynd.network"

async def send_ping(websocket):
    """Sends ping messages to the websocket."""
    while True:
        send_message = json.dumps(
            {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}})
        logger.debug(send_message)
        await websocket.send(send_message)
        await asyncio.sleep(5)

async def handle_messages(websocket, device_id, user_id, user_agent):
    """Handles incoming websocket messages."""
    while True:
        response = await websocket.recv()
        message = json.loads(response)
        logger.info(message)

        if message.get("action") == "AUTH":
            auth_response = {
                "id": message["id"],
                "origin_action": "AUTH",
                "result": {
                    "browser_id": device_id,
                    "user_id": user_id,
                    "user_agent": user_agent,
                    "timestamp": int(time.time()),
                    "device_type": "desktop",
                    "version": "4.28.2",
                }
            }
            logger.debug(auth_response)
            await websocket.send(json.dumps(auth_response))

        elif message.get("action") == "PONG":
            pong_response = {"id": message["id"], "origin_action": "PONG"}
            logger.debug(pong_response)
            await websocket.send(json.dumps(pong_response))

async def connect_and_interact(socks5_proxy, user_id):
    """Connects to the websocket and handles interaction."""
    random_user_agent = USER_AGENT.random
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, socks5_proxy))
    logger.info(device_id)

    while True:
        try:
            await asyncio.sleep(random.uniform(0.1, 1))  # More even distribution
            custom_headers = {"User-Agent": random_user_agent}
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            uri = random.choice(URILIST)
            proxy = Proxy.from_url(socks5_proxy)

            async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname=SERVER_HOSTNAME,
                                     extra_headers=custom_headers) as websocket:

                asyncio.create_task(send_ping(websocket))
                await handle_messages(websocket, device_id, user_id, random_user_agent)

        except Exception as e:
            logger.error(f"Error with proxy {socks5_proxy}: {e}")

async def main():
    """Main function to gather user ID and start connections."""
    user_id = input('Please Enter your user ID: ')
    with open('local_proxies.txt', 'r') as file:
        local_proxies = file.read().splitlines()

    tasks = [connect_and_interact(proxy, user_id) for proxy in local_proxies]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
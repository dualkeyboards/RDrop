#_includes/response.py
import asyncio
import json
from loguru import logger
from .auth import auth
from .pong import pong
from websockets_proxy import Proxy

async def response(websocket, device_id, user_id, user_agent, stats, proxy_ip):  # Add socks5_proxy
    """Handles incoming websocket responses."""
    while True:
        try:
            response_data = await websocket.recv()
            message = json.loads(response_data)
            logger.success(f"\033[42;30m PONGED         \033[47;30m {proxy_ip}\033[0m")  # Log the received message

            if message.get("action") == "AUTH":
                await auth(websocket, device_id, user_id, user_agent, message, proxy_ip) # Pass socks5_proxy to auth
            elif message.get("action") == "PONG":
                await pong(websocket, message)
                stats['pongs'] += 1  # Increment pong counter

        except asyncio.CancelledError:
            logger.info("Response handling task cancelled.")
            break  # Exit loop on cancellation

        except Exception as receive_error:
            logger.error(f"\033[41m PROCESSING     \033[47;30m {receive_error}\033[0m")
            break  # Break out of the loop on error
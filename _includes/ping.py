#_includes/ping.py
import asyncio
import json
import uuid
from websockets_proxy import Proxy
from loguru import logger

async def ping(websocket, stats, proxy_ip):  # Add socks5_proxy
    """Sends ping messages to the websocket, with error handling."""
    while True:
        try:
            send_message = json.dumps(
                {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}})
            logger.info(f"\033[44m PINGING        \033[47;30m {proxy_ip}\033[0m") # Changed to info
            await websocket.send(send_message)
            stats['pings'] += 1  # Increment ping counter
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            logger.info(f"\033[44m PINGING        \033[41m CANCELLED \033[47;30m {proxy_ip}\033[0m")
            break
        except Exception as e:
            logger.error(f"\033[41m PINGING        \033[47;30m {e}\033[0m")
            break  # Stop the ping loop on error
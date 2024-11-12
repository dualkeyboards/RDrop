# _includes/ping.py
import asyncio
import json
import uuid
from loguru import logger

async def ping(websocket, stats):  # Takes the stats dictionary as an argument
    """Sends ping messages to the websocket, with error handling."""
    while True:
        try:
            send_message = json.dumps(
                {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}})
            logger.info(f"Sending ping: {send_message}") # Changed to info
            await websocket.send(send_message)
            stats['pings'] += 1  # Increment ping counter
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            logger.info("Ping task cancelled.")
            break
        except Exception as e:
            logger.error(f"Error sending ping: {e}")
            break  # Stop the ping loop on error
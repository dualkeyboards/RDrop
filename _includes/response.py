import asyncio
import json
from loguru import logger
from .auth import auth
from .pong import pong

async def response(websocket, device_id, user_id, user_agent, stats):  # stats parameter added
    """Handles incoming websocket responses."""
    while True:
        try:
            response_data = await websocket.recv()
            message = json.loads(response_data)
            logger.info(message)  # Log the received message

            if message.get("action") == "AUTH":
                await auth(websocket, device_id, user_id, user_agent, message)
            elif message.get("action") == "PONG":
                await pong(websocket, message)
                stats['pongs'] += 1  # Increment pong counter

        except asyncio.CancelledError:
            logger.info("Response handling task cancelled.")
            break  # Exit loop on cancellation

        except Exception as receive_error:
            logger.error(f"Error during receive or message processing: {receive_error}")
            break  # Break out of the loop on error
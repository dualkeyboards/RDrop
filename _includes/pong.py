#_includes/pong.py
import json
from loguru import logger

async def pong(websocket, message):
    """Handles incoming PONG response."""
    pong_response = {"id": message["id"], "origin_action": "PONG"}
    await websocket.send(json.dumps(pong_response))
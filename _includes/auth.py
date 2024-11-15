#_includes/auth.py
import json
import time
from loguru import logger

async def auth(websocket, device_id, user_id, user_agent, message, proxy_ip):
    """Handles incoming AUTH response."""
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
    logger.info(f"\033[45m AUTHENTICATION \033[47;30m {proxy_ip}\033[0m")  # Use socks5_proxy in logging
    await websocket.send(json.dumps(auth_response))
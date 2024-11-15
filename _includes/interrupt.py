#_includes/interrupt.py
import os
import signal
from loguru import logger

def interrupt_handler(status_bar):
    def signal_handler(sig, frame):
        logger.info(f"\033[41;30m CANCELLED       EXITING \033[0m \n")
        status_bar.clear()
        os._exit(1)

    signal.signal(signal.SIGINT, signal_handler)  # Register for Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Register for termination signals (or SIGBREAK on Windows)
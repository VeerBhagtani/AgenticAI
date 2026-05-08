import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")

class AgentLogger:
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        log_file = os.path.join(LOG_DIR, f"agent_{datetime.now().strftime('%Y%m%d')}.log")

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.log = logging.getLogger("PCAgent")

    def info(self, msg):  self.log.info(msg)
    def error(self, msg): self.log.error(msg)
    def warn(self, msg):  self.log.warning(msg)

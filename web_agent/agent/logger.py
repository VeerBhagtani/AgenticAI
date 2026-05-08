import logging, os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")

class Logger:
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        log_file = os.path.join(LOG_DIR, f"webagent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
        )
        self.log = logging.getLogger("WebAgent")

    def info(self, msg):  self.log.info(msg)
    def warn(self, msg):  self.log.warning(msg)
    def error(self, msg): self.log.error(msg)
    def step(self, n, msg): self.log.info(f"[STEP {n}] {msg}")

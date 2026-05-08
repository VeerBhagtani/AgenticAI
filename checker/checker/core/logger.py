import logging, os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")

class Logger:
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        log_file = os.path.join(LOG_DIR, f"checker_{datetime.now().strftime('%Y%m%d')}.log")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
        )
        self.log = logging.getLogger("Checker")

    def info(self, m):  self.log.info(m)
    def warn(self, m):  self.log.warning(m)
    def error(self, m): self.log.error(m)

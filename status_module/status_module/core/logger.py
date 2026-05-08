import logging, os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")

class Logger:
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(os.path.join(LOG_DIR, f"status_{ts}.log")),
                logging.StreamHandler()
            ]
        )
        self.log = logging.getLogger("StatusModule")

    def info(self, m):  self.log.info(m)
    def warn(self, m):  self.log.warning(m)
    def error(self, m): self.log.error(m)

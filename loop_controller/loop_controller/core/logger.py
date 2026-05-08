import logging, os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")

class Logger:
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(LOG_DIR, f"loop_{ts}.log")
        fmt = "%(asctime)s [%(levelname)s] %(message)s"
        logging.basicConfig(
            level=logging.INFO,
            format=fmt,
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
        )
        self.log = logging.getLogger("LoopController")

    def info(self, m):    self.log.info(m)
    def warn(self, m):    self.log.warning(m)
    def error(self, m):   self.log.error(m)
    def success(self, m): self.log.info(f"✅ {m}")
    def fail(self, m):    self.log.warning(f"❌ {m}")
    def retry(self, n, m):self.log.warning(f"🔁 [RETRY {n}] {m}")
    def section(self, m): self.log.info(f"{'─'*50}\n{m}")

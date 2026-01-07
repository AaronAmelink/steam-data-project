import logging
import os
import sys
from datetime import datetime

LOG_DIRECTORY = f"/app/log/{datetime.now().year}/{datetime.now().month}/{datetime.now().day}/"

os.makedirs(LOG_DIRECTORY, exist_ok=True)
# Clear existing handlers (optional, useful if script is reloaded in some environments)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

def configure_logger(name: str | None = None) -> logging.Logger:
    """Configure and return a logger for the given name."""
    if name is None:
        name = 'cron' if '--cron' in sys.argv else 'manual'
    log_file = LOG_DIRECTORY + name + '.log'

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),  # write logs to file
            logging.StreamHandler()         # also print logs to console
        ]
    )
    return logging.getLogger(name)

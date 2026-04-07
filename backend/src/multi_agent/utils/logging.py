
# ═══════════════════════════════════════════════════════════════════════════════
# multi_agent/utils/logging.py
# ═══════════════════════════════════════════════════════════════════════════════
import logging
import sys
from ..config import settings


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        ))
        logger.addHandler(h)
    logger.setLevel(settings.LOG_LEVEL)
    return logger


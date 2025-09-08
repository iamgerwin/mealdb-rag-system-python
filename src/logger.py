from __future__ import annotations
from loguru import logger
from .config import settings

# Configure logger once on import
logger.remove()
logger.add(settings.log_file, level=settings.log_level, rotation="10 MB", retention="10 days")
logger.add(lambda msg: print(msg, end=""), level=settings.log_level)

__all__ = ["logger"]

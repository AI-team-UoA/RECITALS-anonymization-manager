from loguru import logger

from .config import AnonymizationConfig
from .core import AnonymizationManager

# Doesn't log when used as a library.
logger.disable("anonymization_manager")

__all__ = ["AnonymizationManager", "AnonymizationConfig"]

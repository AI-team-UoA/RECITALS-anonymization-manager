"""
Logging setup for the Anonymization Manager.

The package uses loguru. Logging is disabled by default when the package is imported
as a library. Entry points (CLI and REST API) call `setup_logging` to turn it on.

Logs are written only to a file, kept as an audit trail. The file location and level
can be set with environment variables:
    ANONYMIZATION_MANAGER_LOG_FILE  (default: logs/anonymization_manager.log)
    ANONYMIZATION_MANAGER_LOG_LEVEL (default: INFO)

Dataset contents are never logged, only paths, parameters and outcomes.
"""

import os
from pathlib import Path

from loguru import logger

LOG_FILE_ENV = "ANONYMIZATION_MANAGER_LOG_FILE"
LOG_LEVEL_ENV = "ANONYMIZATION_MANAGER_LOG_LEVEL"
DEFAULT_LOG_FILE = "logs/anonymization_manager.log"
DEFAULT_LOG_LEVEL = "INFO"

_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS ZZ} | {level: <8} | "
    "{name}:{function}:{line} - {message}"
)

def setup_logging() -> None:
    """Sends all package logs to the audit log file."""
    path = Path(os.getenv(LOG_FILE_ENV, DEFAULT_LOG_FILE))
    level = os.getenv(LOG_LEVEL_ENV, DEFAULT_LOG_LEVEL).upper()

    # Only the owner can read the log directory.
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    logger.remove()
    logger.add(
        path,
        level=level,
        format=_FORMAT,
        rotation="10 MB",
        retention="90 days",
        compression="gz",
        enqueue=True, # safe with several worker threads
        backtrace=False,
        diagnose=False, # don't write variable values into tracebacks
    )
    logger.enable("anonymization_manager")
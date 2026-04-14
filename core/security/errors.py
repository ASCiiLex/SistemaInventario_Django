import logging
from .error_protection import ErrorProtector

logger = logging.getLogger("inventory.domain")

protector = ErrorProtector()


def safe_log_error(error_type: str, message: str, context: str = ""):
    if protector.should_log(error_type, context):
        logger.error(message, extra={
            "error_type": error_type,
            "context": context,
        })
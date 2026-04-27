import logging
import sys
import json
from datetime import datetime
import os


class JSONFormatter(logging.Formatter):
    def format(self, record):
        from core.observability.tracing import get_trace_id

        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": get_trace_id(),
        }

        if hasattr(record, "product_id"):
            log_record["product_id"] = record.product_id
        if hasattr(record, "org_id"):
            log_record["organization_id"] = record.org_id
        if hasattr(record, "movement_id"):
            log_record["movement_id"] = record.movement_id
        if hasattr(record, "type"):
            log_record["movement_type"] = record.type
        if hasattr(record, "qty"):
            log_record["quantity"] = record.qty
        if hasattr(record, "errors"):
            log_record["errors"] = record.errors

        return json.dumps(log_record)


IS_DEV = os.getenv("DJANGO_ENV") != "prod"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": JSONFormatter},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "json",
        },
    },
    "loggers": {
        "inventory.domain": {
            "handlers": ["console"],
            "level": "WARNING" if IS_DEV else "INFO",
            "propagate": False,
        },
        "inventory.metrics": {
            "handlers": ["console"],
            "level": "WARNING" if IS_DEV else "INFO",  # 🔥 clave
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
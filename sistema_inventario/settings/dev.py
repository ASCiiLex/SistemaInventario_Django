from .base import *

SECRET_KEY = 'django-insecure-dev-key'

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ============================
# 🔥 OBSERVABILIDAD OFF EN DEV
# ============================

OBSERVABILITY_ENABLED = False
OBSERVABILITY_TRACE_ENABLED = False
OBSERVABILITY_METRICS_ENABLED = False

# ============================
# LOGGING OPTIMIZADO DEV
# ============================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "inventory.metrics": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    },
}

# ============================
# DEV PERFORMANCE BOOST
# ============================

DATABASES["default"]["CONN_MAX_AGE"] = 0

SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = "SAMEORIGIN"
from .base import *

SECRET_KEY = 'django-insecure-dev-key'

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ============================
# LOGGING OPTIMIZADO DEV
# ============================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "inventory.metrics": {
            "handlers": ["console"],
            "level": "WARNING",  # 🔥 elimina ruido y mejora rendimiento
        },
    },
}

# ============================
# DEV PERFORMANCE BOOST
# ============================

# 🔥 evita latencias en queries largas
DATABASES["default"]["CONN_MAX_AGE"] = 0

# 🔥 desactiva seguridad innecesaria en local
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = "SAMEORIGIN"
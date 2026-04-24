from .base import *

SECRET_KEY = 'django-insecure-dev-key'

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ============================
# LOGGING (simple en dev)
# ============================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
}
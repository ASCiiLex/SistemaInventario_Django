from .base import *
import os

# ============================
# CORE
# ============================

SECRET_KEY = os.getenv("SECRET_KEY") or "unsafe-secret-key"

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ============================
# HOSTS
# ============================

raw_hosts = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(",") if h.strip()]

if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

# ============================
# SECURITY
# ============================

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host != "*"
]

# ============================
# LOGGING
# ============================

from .logging import LOGGING
from .base import *
import os

# ============================
# CORE
# ============================

SECRET_KEY = os.getenv("SECRET_KEY") or "unsafe-secret-key"

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ============================
# HOSTS (FIX REAL)
# ============================

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".railway.app",
]

# permitir override desde env (sin romper local)
extra_hosts = os.getenv("ALLOWED_HOSTS")
if extra_hosts:
    ALLOWED_HOSTS += [h.strip() for h in extra_hosts.split(",") if h.strip()]

# ============================
# SECURITY
# ============================

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

CSRF_TRUSTED_ORIGINS = [
    f"https://{host.replace('.', '')}" if host.startswith(".") else f"https://{host}"
    for host in ALLOWED_HOSTS
    if host not in ["127.0.0.1", "localhost"]
]

# ============================
# LOGGING
# ============================

from .logging import LOGGING
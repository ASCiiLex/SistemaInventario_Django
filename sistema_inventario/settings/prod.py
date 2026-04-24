from .base import *
import os

# ============================
# CORE
# ============================

SECRET_KEY = os.getenv("SECRET_KEY") or "unsafe-secret-key"

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ============================
# HOSTS (ROBUSTO Y PORTABLE)
# ============================

DEFAULT_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".railway.app",
    "sistemainventario.up.railway.app",  # 🔥 fix definitivo
]

env_hosts = os.getenv("ALLOWED_HOSTS")

if env_hosts:
    ALLOWED_HOSTS = DEFAULT_HOSTS + [
        h.strip() for h in env_hosts.split(",") if h.strip()
    ]
else:
    ALLOWED_HOSTS = DEFAULT_HOSTS

# eliminar duplicados (por limpieza)
ALLOWED_HOSTS = list(set(ALLOWED_HOSTS))

# ============================
# SECURITY
# ============================

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

CSRF_TRUSTED_ORIGINS = [
    f"https://{host.lstrip('.')}"
    for host in ALLOWED_HOSTS
    if host not in ["127.0.0.1", "localhost"]
]

# ============================
# LOGGING
# ============================

from .logging import LOGGING
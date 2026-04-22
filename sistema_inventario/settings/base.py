from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Solo cargar .env en local (evita conflictos en Railway)
if os.getenv("DJANGO_ENV") != "prod":
    load_dotenv(BASE_DIR / ".env")

# ============================
# APPS
# ============================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    'core.apps.CoreConfig',

    'accounts',
    'organizations',

    'products.apps.ProductsConfig',
    'suppliers',
    'categories',
    'dashboard',
    'notifications.apps.NotificationsConfig',
    'inventory',
    'observability',

    'channels',
]

# ============================
# MIDDLEWARE (REORDENADO Y AISLADO)
# ============================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # 🔐 control de acceso primero
    'accounts.middleware.LoginRequiredMiddleware',

    # 🏢 multi-tenant solo con usuario autenticado
    'organizations.middleware.OrganizationMiddleware',

    # 🔍 observabilidad al final (no rompe flujo)
    'core.observability.middleware.ObservabilityMiddleware',

    # ⚠️ rate limit fuera del flujo crítico (opcional reintroducir después)
    # 'core.security.middleware.RateLimitMiddleware',

    "inventory.middleware.audit_middleware.AuditUserMiddleware",

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================
# URLS / WSGI / ASGI
# ============================

ROOT_URLCONF = 'sistema_inventario.urls'
WSGI_APPLICATION = 'sistema_inventario.wsgi.application'
ASGI_APPLICATION = 'sistema_inventario.asgi.application'

# ============================
# TEMPLATES
# ============================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notifications.context_processors.notifications_unread',
                "accounts.context_processors.permissions_context",
                'organizations.context_processors.organization',
            ],
        },
    },
]

# ============================
# DATABASE
# ============================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}

# ============================
# REDIS
# ============================

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")

# ============================
# CACHE
# ============================

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# ============================
# PASSWORDS
# ============================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================
# I18N
# ============================

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

# ============================
# STATIC
# ============================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================
# EMAIL
# ============================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ============================
# CHANNELS
# ============================

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

# ============================
# GENERAL
# ============================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
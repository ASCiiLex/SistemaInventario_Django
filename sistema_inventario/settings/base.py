from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

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
# MIDDLEWARE
# ============================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'core.security.middleware.RateLimitMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.observability.middleware.ObservabilityMiddleware',

    'accounts.middleware.LoginRequiredMiddleware',
    'organizations.middleware.OrganizationMiddleware',

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
        "NAME": os.getenv("DB_NAME", "inventario"),
        "USER": os.getenv("DB_USER", "inventario_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "inventario_pass"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 0,
    }
}

# ============================
# CACHE
# ============================

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CACHE_TTL = {
    "metrics": 15,
    "low_stock": 15,
    "charts": 30,
    "notifications": 10,
    "activity": 5,
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
            "hosts": [("127.0.0.1", 6379)],
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
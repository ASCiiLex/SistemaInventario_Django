from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ============================
# ENTORNO
# ============================

DJANGO_ENV = os.getenv("DJANGO_ENV", "dev")
IS_DEV = DJANGO_ENV != "prod"

# Solo cargar .env en local
if IS_DEV:
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
# MIDDLEWARE
# ============================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'accounts.middleware.LoginRequiredMiddleware',
    'organizations.middleware.OrganizationMiddleware',

    'core.observability.middleware.ObservabilityMiddleware',

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
# DATABASE (SEPARACIÓN REAL DEV/PROD)
# ============================

if IS_DEV:
    DATABASE_URL = None
else:
    DATABASE_URL = (
        os.getenv("DATABASE_URL")
        or os.getenv("DATABASE_PUBLIC_URL")
    )

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
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
# REDIS / CACHE
# ============================

REDIS_URL = (
    os.getenv("REDIS_PUBLIC_URL")
    or os.getenv("REDIS_URL")
)

if REDIS_URL and not IS_DEV:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SOCKET_CONNECT_TIMEOUT": 2,
                "SOCKET_TIMEOUT": 2,
            }
        }
    }

    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
            },
        },
    }

else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-dev",
        }
    }

    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
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
# GENERAL
# ============================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# ============================
# HOSTS
# ============================

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost,.railway.app"
).split(",")

# ============================
# CACHE TTL
# ============================

CACHE_TTL = {
    "charts": 60 if not IS_DEV else 1,
}
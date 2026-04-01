from pathlib import Path

# BASE DIR
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================
# SEGURIDAD
# ============================

SECRET_KEY = 'django-insecure-3*sfsynq@f9ef+8h6$holq(cpei*68s^u(rdml=kzulgaeruj='

DEBUG = True

ALLOWED_HOSTS = []  # En producción añadir dominio o IP


# ============================
# APPS
# ============================

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Core
    'accounts',
    'organizations',

    # Apps del proyecto
    'products.apps.ProductsConfig',
    'suppliers',
    'categories',
    'dashboard',
    'notifications',
    'inventory',

    # WebSockets
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

    # 🔐 LOGIN GLOBAL
    'accounts.middleware.LoginRequiredMiddleware',
    'organizations.middleware.OrganizationMiddleware',

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

                # Notificaciones
                'notifications.context_processors.notifications_unread',

                # Permisos
                'accounts.context_processors.permissions',
                'organizations.context_processors.organization',
            ],
        },
    },
]


# ============================
# BASE DE DATOS
# ============================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ============================
# CACHE
# ============================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-saas-cache",
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
# VALIDACIÓN DE PASSWORDS
# ============================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================
# INTERNACIONALIZACIÓN
# ============================

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True


# ============================
# ARCHIVOS ESTÁTICOS
# ============================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

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
# CONFIG GENERAL
# ============================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
import os

# 🔥 prioridad absoluta: variable estándar Django
settings_module = os.getenv("DJANGO_SETTINGS_MODULE")

if settings_module:
    # Django ya sabe qué módulo usar → no interferimos
    pass
else:
    # fallback automático limpio
    env = os.getenv("DJANGO_ENV", "prod")

    if env == "prod":
        from .prod import *
    else:
        from .dev import *
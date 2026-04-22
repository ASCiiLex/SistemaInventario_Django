import os

env = os.getenv("DJANGO_ENV")

# default seguro para entornos tipo Railway
if env == "prod":
    from .prod import *
else:
    # si no está definido, asumimos producción (evita usar dev sin querer)
    from .prod import *
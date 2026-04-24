import os

env = os.getenv("DJANGO_ENV")

if env == "prod":
    from .prod import *
else:
    from .dev import *
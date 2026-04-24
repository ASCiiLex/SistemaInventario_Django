"""
WSGI config for sistema_inventario project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "sistema_inventario.settings.prod")
)

application = get_wsgi_application()
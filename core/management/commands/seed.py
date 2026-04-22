from django.core.management.base import BaseCommand
from django.db import connection
from scripts.seed_demo import run


class Command(BaseCommand):
    help = "Seed inicial de datos (idempotente)"

    def handle(self, *args, **kwargs):
        connection.ensure_connection()

        # 🔥 ejecutar SIEMPRE (idempotente)
        run()

        self.stdout.write(self.style.SUCCESS("✅ Seed ejecutado correctamente"))
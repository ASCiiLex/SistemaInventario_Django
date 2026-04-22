from django.core.management.base import BaseCommand
from django.db import connection
import sys

from scripts.seed_demo import run


class Command(BaseCommand):
    help = "Seed inicial de datos (idempotente)"

    def handle(self, *args, **kwargs):
        print("🔥 SEED: inicio", flush=True)

        try:
            connection.ensure_connection()
            print("🔥 SEED: DB conectada", flush=True)
        except Exception as e:
            print(f"❌ SEED: error DB {e}", flush=True)
            sys.exit(1)

        try:
            run()
            print("🔥 SEED: run() ejecutado", flush=True)
        except Exception as e:
            print(f"❌ SEED: error en run {e}", flush=True)
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS("✅ Seed ejecutado correctamente"))
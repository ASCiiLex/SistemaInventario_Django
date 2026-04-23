from django.core.management.base import BaseCommand
from django.db import connection
import sys


class Command(BaseCommand):
    help = "Seed de datos (base | demo)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode",
            type=str,
            default="base",
            choices=["base", "demo"],
            help="Modo de seed"
        )

    def handle(self, *args, **options):
        mode = options["mode"]

        print(f"🔥 SEED ({mode}): inicio", flush=True)

        try:
            connection.ensure_connection()
            print("🔥 SEED: DB conectada", flush=True)
        except Exception as e:
            print(f"❌ SEED: error DB {e}", flush=True)
            sys.exit(1)

        try:
            if mode == "base":
                from scripts.seed_base import run
            else:
                from scripts.seed_demo import run

            run()

        except Exception as e:
            print(f"❌ SEED: error en run {e}", flush=True)
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS(f"✅ Seed {mode} ejecutado correctamente"))
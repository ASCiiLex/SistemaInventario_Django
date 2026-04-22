from django.core.management.base import BaseCommand
from scripts.seed_demo import run


class Command(BaseCommand):
    help = "Seed inicial de datos (idempotente)"

    def handle(self, *args, **kwargs):
        run()
        self.stdout.write(self.style.SUCCESS("✅ Seed ejecutado correctamente"))
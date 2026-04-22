from django.apps import AppConfig
import os


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # 🔥 SOLO en producción
        if os.getenv("DJANGO_ENV") != "prod":
            return

        # 🔥 evitar múltiples ejecuciones (gunicorn workers)
        if os.getenv("RUN_MAIN") != "true":
            return

        try:
            from django.contrib.auth.models import User

            # 🔥 idempotencia real
            if User.objects.filter(username="admin").exists():
                return

            from scripts.seed_demo import run
            run()

            print("🔥 SEED ejecutado automáticamente en arranque")

        except Exception as e:
            print(f"❌ Error en seed automático: {e}")
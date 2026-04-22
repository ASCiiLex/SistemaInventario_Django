from django.apps import AppConfig
import os


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # 🔥 Ejecutar seed SOLO en producción y una vez
        if os.getenv("DJANGO_ENV") != "prod":
            return

        if os.getenv("RUN_MAIN") != "true":
            return

        try:
            from django.contrib.auth.models import User

            # Si ya existe el admin, no hacer nada
            if User.objects.filter(username="admin").exists():
                return

            from scripts.seed_demo import run
            run()

            print("✅ Seed ejecutado automáticamente en producción")

        except Exception as e:
            print(f"❌ Error ejecutando seed: {e}")
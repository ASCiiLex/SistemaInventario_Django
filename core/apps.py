from django.apps import AppConfig
import os


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # 🔥 Solo ejecutar en comando explícito de seed
        if os.getenv("RUN_SEED") != "true":
            return

        try:
            from scripts.seed_demo import run
            run()
            print("✅ Seed ejecutado desde AppConfig (RUN_SEED=true)")
        except Exception as e:
            print(f"❌ Error ejecutando seed: {e}")
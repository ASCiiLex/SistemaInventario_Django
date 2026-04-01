from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"

    def ready(self):
        # 🔥 IMPORTA LOS HANDLERS (esto registra los eventos)
        import notifications.services
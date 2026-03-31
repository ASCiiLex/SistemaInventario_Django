from django.urls import path
from .views import notification_preferences

urlpatterns = [
    path("settings/notifications/", notification_preferences, name="notification_preferences"),
]
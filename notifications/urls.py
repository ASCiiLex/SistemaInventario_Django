from django.urls import path
from .views import (
    notifications_list,
    notifications_mark_all_read,
    notification_mark_read,
    notifications_counter,
)

urlpatterns = [
    path("", notifications_list, name="notifications_list"),
    path("leer-todas/", notifications_mark_all_read, name="notifications_mark_all_read"),
    path("leer/<int:pk>/", notification_mark_read, name="notification_mark_read"),
    path("contador/", notifications_counter, name="notifications_counter"),
]
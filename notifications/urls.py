from django.urls import path
from .views import (
    notifications_list,
    notifications_mark_all_read,
    notifications_counter,
)

urlpatterns = [
    path("", notifications_list, name="notifications_list"),
    path("leer-todas/", notifications_mark_all_read, name="notifications_mark_all_read"),
    path("contador/", notifications_counter, name="notifications_counter"),
]
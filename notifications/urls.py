from django.urls import path
from .views import (
    notifications_list,
    notifications_mark_all_read,
    notification_mark_read,
    notification_mark_unread,
    notifications_counter,
    notifications_panel,
    notifications_panel_mark_all,
    notifications_panel_mark_one,
    notifications_panel_mark_unread,

)

urlpatterns = [
    path("", notifications_list, name="notifications_list"),
    path("leer-todas/", notifications_mark_all_read, name="notifications_mark_all_read"),
    path("leer/<int:pk>/", notification_mark_read, name="notification_mark_read"),
    path("contador/", notifications_counter, name="notifications_counter"),

    path("panel/", notifications_panel, name="notifications_panel"),
    path("panel/leer-todas/", notifications_panel_mark_all, name="notifications_panel_mark_all"),
    path("panel/leer/<int:pk>/", notifications_panel_mark_one, name="notifications_panel_mark_one"),
    path("panel/no-leida/<int:pk>/", notifications_panel_mark_unread, name="notifications_panel_mark_unread"),
    path("no-leida/<int:pk>/", notification_mark_unread, name="notification_mark_unread"),
]
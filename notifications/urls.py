from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("lista/", views.notifications_list, name="notifications_list"),

    path("marcar-todas/", views.notifications_mark_all_read, name="notifications_mark_all_read"),
    path("marcar-leida/<int:pk>/", views.notification_mark_read, name="notification_mark_read"),
    path("marcar-no-leida/<int:pk>/", views.notification_mark_unread, name="notification_mark_unread"),

    path("toggle-all/", views.notifications_toggle_all, name="notifications_toggle_all"),
    path("panel/toggle-all/", views.notifications_toggle_all, name="notifications_panel_toggle_all"),

    path("panel/", views.notifications_panel, name="notifications_panel"),
    path("panel/marcar-todas/", views.notifications_panel_mark_all, name="notifications_panel_mark_all"),
    path("panel/marcar-una/<int:pk>/", views.notifications_panel_mark_one, name="notifications_panel_mark_one"),
    path("panel/marcar-no-leida/<int:pk>/", views.notifications_panel_mark_unread, name="notifications_panel_mark_unread"),

    path("bulk/", views.notifications_bulk_action, name="notifications_bulk_action"),

    path("dashboard/resumen/", views.notifications_summary, name="dashboard_notifications_summary"),
    path("dashboard/graficos/", views.notifications_chart, name="dashboard_notifications_chart"),
    path("dashboard/recientes/", views.notifications_recent, name="dashboard_notifications_recent"),

    path("contador/", views.notifications_counter, name="notifications_counter"),
]
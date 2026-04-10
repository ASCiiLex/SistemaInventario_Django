from django.urls import path

from .views.main import dashboard_view
from .views.metrics import dashboard_totals, dashboard_low_stock, dashboard_system_metrics
from .views.charts import dashboard_chart, dashboard_chart_data
from .views.activity import (
    dashboard_recent_movements,
    dashboard_recent_stock_movements,
)
from .views.notifications import (
    dashboard_notifications_recent,
    dashboard_notifications_summary,
)

urlpatterns = [
    path("", dashboard_view, name="dashboard"),

    path("totales/", dashboard_totals, name="dashboard_totals"),
    path("bajo-minimo/", dashboard_low_stock, name="dashboard_low_stock"),
    path("system-metrics/", dashboard_system_metrics, name="dashboard_system_metrics"),

    path(
        "notificaciones-resumen/",
        dashboard_notifications_summary,
        name="dashboard_notifications_summary",
    ),

    path(
        "notificaciones-recientes/",
        dashboard_notifications_recent,
        name="dashboard_notifications_recent",
    ),

    path("movimientos-recientes/", dashboard_recent_movements, name="dashboard_recent_movements"),
    path("movimientos-stock/", dashboard_recent_stock_movements, name="dashboard_recent_stock_movements"),

    path("grafico/", dashboard_chart, name="dashboard_chart"),
    path("grafico/<str:tipo>/", dashboard_chart_data, name="dashboard_chart_data"),
]
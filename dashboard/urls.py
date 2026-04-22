from django.urls import path

from .views import (
    dashboard_view,
    dashboard_totals,
    dashboard_low_stock,
    dashboard_system_metrics,
    dashboard_notifications_recent,
    dashboard_notifications_summary,
    dashboard_recent_movements,
    dashboard_recent_stock_movements,
    dashboard_chart,
    dashboard_chart_data,
)
from .views import observability

urlpatterns = [
    path("", dashboard_view, name="dashboard"),

    path("totales/", dashboard_totals, name="dashboard_totals"),
    path("bajo-minimo/", dashboard_low_stock, name="dashboard_low_stock"),
    path("system-metrics/", dashboard_system_metrics, name="dashboard_system_metrics"),

    # 🆕 NUEVA PÁGINA
    path("observability/", observability.observability_dashboard_view, name="observability_dashboard"),
    path("observability/slow-requests/", observability.slow_requests_view, name="slow_requests"),

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
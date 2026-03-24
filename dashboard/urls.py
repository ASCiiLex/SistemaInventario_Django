from django.urls import path
from .views import (
    dashboard_view,
    dashboard_totals,
    dashboard_low_stock,
    dashboard_recent_movements,
    dashboard_recent_stock_movements,
    dashboard_chart,
    dashboard_notifications_recent,
)

urlpatterns = [
    path("", dashboard_view, name="dashboard"),

    # KPIs
    path("totales/", dashboard_totals, name="dashboard_totals"),

    # Bajo mínimo
    path("bajo-minimo/", dashboard_low_stock, name="dashboard_low_stock"),

    # Notificaciones recientes (HTMX)
    path("notificaciones-recientes/", dashboard_notifications_recent, name="dashboard_notifications_recent"),

    # Movimientos
    path("movimientos-recientes/", dashboard_recent_movements, name="dashboard_recent_movements"),
    path("movimientos-stock/", dashboard_recent_stock_movements, name="dashboard_recent_stock_movements"),

    # Gráfico
    path("grafico/", dashboard_chart, name="dashboard_chart"),
]
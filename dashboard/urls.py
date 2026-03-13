from django.urls import path
from .views import (
    dashboard_view,
    dashboard_totals,
    dashboard_low_stock,
    dashboard_recent_movements,
    dashboard_recent_stock_movements,
    dashboard_chart,
)

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("totales/", dashboard_totals, name="dashboard_totals"),
    path("bajo-minimo/", dashboard_low_stock, name="dashboard_low_stock"),
    path("movimientos-recientes/", dashboard_recent_movements, name="dashboard_recent_movements"),
    path("movimientos-stock/", dashboard_recent_stock_movements, name="dashboard_recent_stock_movements"),
    path("grafico/", dashboard_chart, name="dashboard_chart"),
]
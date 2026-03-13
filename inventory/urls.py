from django.urls import path
from . import views

urlpatterns = [
    path("locations/", views.location_list, name="location_list"),
    path("orders/", views.order_list, name="order_list"),
    path("stock-movements/", views.stockmovement_list, name="stockmovement_list"),
    path("stock-movements/nuevo/", views.stockmovement_create, name="stockmovement_create"),
    path("stock-movements/transferencia/", views.stock_transfer_create, name="stock_transfer_create"),

    # NUEVO: Importación CSV de stock inicial
    path("importar-stock/", views.import_stock_view, name="import_stock"),
    path("importar-stock/confirmar/", views.import_stock_confirm_view, name="import_stock_confirm"),
]
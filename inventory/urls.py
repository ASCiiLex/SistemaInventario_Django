from django.urls import path
from . import views

urlpatterns = [
    path("locations/", views.location_list, name="location_list"),
    path("orders/", views.order_list, name="order_list"),
    path("stock-movements/", views.stockmovement_list, name="stockmovement_list"),
    path("stock-movements/nuevo/", views.stockmovement_create, name="stockmovement_create"),
    path("stock-movements/transferencia/", views.stock_transfer_create, name="stock_transfer_create"),

    # Importación CSV
    path("importar-stock/", views.import_stock_view, name="import_stock"),
    path("importar-stock/confirmar/", views.import_stock_confirm_view, name="import_stock_confirm"),

    # ---------------------------------------------------------
    # NUEVO — MÓDULO DE TRANSFERENCIAS PROFESIONALES
    # ---------------------------------------------------------
    path("transferencias/", views.transfer_list, name="transfer_list"),
    path("transferencias/nueva/", views.transfer_create, name="transfer_create"),
    path("transferencias/<int:pk>/", views.transfer_detail, name="transfer_detail"),
    path("transferencias/<int:pk>/confirmar/", views.transfer_confirm, name="transfer_confirm"),
    path("transferencias/<int:pk>/cancelar/", views.transfer_cancel, name="transfer_cancel"),
]
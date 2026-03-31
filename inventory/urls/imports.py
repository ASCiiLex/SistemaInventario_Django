from django.urls import path
from ..views.imports import import_stock_view, import_stock_confirm_view

urlpatterns = [
    path("importar-stock/", import_stock_view, name="import_stock"),
    path("importar-stock/confirmar/", import_stock_confirm_view, name="import_stock_confirm"),
]
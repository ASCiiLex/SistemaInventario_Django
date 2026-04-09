from django.urls import path

from ..views.stock import (
    stockmovement_list,
    stockmovement_create,
    export_stockmovements_csv,
)

urlpatterns = [
    path("stock-movements/", stockmovement_list, name="stockmovement_list"),
    path("stock-movements/nuevo/", stockmovement_create, name="stockmovement_create"),
    path("stock-movements/exportar/", export_stockmovements_csv, name="export_stockmovements_csv"),
]
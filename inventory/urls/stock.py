from django.urls import path
from ..views import stockmovement_list, stockmovement_create, transfer_create

urlpatterns = [
    path("stock-movements/", stockmovement_list, name="stockmovement_list"),
    path("stock-movements/nuevo/", stockmovement_create, name="stockmovement_create"),
# Compatibilidad temporal con la ruta antigua
    path("stock-movements/transferencia/", transfer_create),
]
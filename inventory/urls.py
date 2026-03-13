from django.urls import path
from . import views

urlpatterns = [
    path("locations/", views.location_list, name="location_list"),
    path("orders/", views.order_list, name="order_list"),
    path("stock-movements/", views.stockmovement_list, name="stockmovement_list"),
    path("stock-movements/nuevo/", views.stockmovement_create, name="stockmovement_create"),
    path("stock-movements/transferencia/", views.stock_transfer_create, name="stock_transfer_create"),
]
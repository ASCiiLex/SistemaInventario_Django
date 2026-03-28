from django.urls import path
from .views import (
    product_list,
    product_detail,
    product_create,
    product_edit,
    product_delete,
    export_products_csv,
    lowstock_counter,
    stockitem_counter
)

urlpatterns = [
    path("", product_list, name="product_list"),
    path("<int:pk>/", product_detail, name="product_detail"),
    path("crear/", product_create, name="product_create"),
    path("editar/<int:pk>/", product_edit, name="product_edit"),
    path("eliminar/<int:pk>/", product_delete, name="product_delete"),
    path("exportar/", export_products_csv, name="export_products_csv"),
    path("low-stock-counter/", lowstock_counter, name="lowstock_counter"),
    path("stockitem-counter/", stockitem_counter, name="stockitem_counter"),
]
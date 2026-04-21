from django.urls import path
from .views import (
    supplier_list,
    supplier_create,
    supplier_edit,
    supplier_delete,
    supplier_products,
)

urlpatterns = [
    path('', supplier_list, name='supplier_list'),
    path('crear/', supplier_create, name='supplier_create'),
    path('editar/<int:pk>/', supplier_edit, name='supplier_edit'),
    path('eliminar/<int:pk>/', supplier_delete, name='supplier_delete'),
    path("<int:pk>/products/", supplier_products, name="supplier_products"),
]
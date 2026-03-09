from django.urls import path
from .views import (
    supplier_list,
    supplier_create,
    supplier_edit,
    supplier_delete
)

urlpatterns = [
    path('', supplier_list, name='supplier_list'),
    path('crear/', supplier_create, name='supplier_create'),
    path('editar/<int:pk>/', supplier_edit, name='supplier_edit'),
    path('eliminar/<int:pk>/', supplier_delete, name='supplier_delete'),
]
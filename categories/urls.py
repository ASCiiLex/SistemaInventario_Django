from django.urls import path
from .views import (
    category_list,
    category_create,
    category_edit,
    category_delete,
)

urlpatterns = [
    path("", category_list, name="category_list"),
    path("crear/", category_create, name="category_create"),
    path("editar/<int:pk>/", category_edit, name="category_edit"),
    path("eliminar/<int:pk>/", category_delete, name="category_delete"),
]
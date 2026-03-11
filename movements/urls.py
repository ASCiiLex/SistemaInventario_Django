from django.urls import path
from .views import (
    movement_list,
    movement_create,
    export_movements_csv,
)

urlpatterns = [
    path("", movement_list, name="movement_list"),
    path("crear/", movement_create, name="movement_create"),
    path("exportar/", export_movements_csv, name="export_movements_csv"),
]
from django.urls import path
from .views import (
    movement_list,
    movement_create
)

urlpatterns = [
    path('', movement_list, name='movement_list'),
    path('crear/', movement_create, name='movement_create'),
]
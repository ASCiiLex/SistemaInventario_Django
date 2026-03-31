from django.urls import path
from ..views.transfers import (
    transfer_list,
    transfer_create,
    transfer_detail,
    transfer_confirm,
    transfer_cancel,
)

urlpatterns = [
    path("transferencias/", transfer_list, name="transfer_list"),
    path("transferencias/nueva/", transfer_create, name="transfer_create"),
    path("transferencias/<int:pk>/", transfer_detail, name="transfer_detail"),
    path("transferencias/<int:pk>/confirmar/", transfer_confirm, name="transfer_confirm"),
    path("transferencias/<int:pk>/cancelar/", transfer_cancel, name="transfer_cancel"),
]
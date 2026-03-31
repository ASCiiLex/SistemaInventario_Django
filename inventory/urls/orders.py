from django.urls import path
from ..views.orders import (
    order_list,
    order_create,
    order_detail,
    order_edit,
    order_send,
    order_receive,
    order_cancel,
    orders_counter,
)

urlpatterns = [
    path("orders/", order_list, name="order_list"),
    path("orders/nuevo/", order_create, name="order_create"),
    path("orders/<int:pk>/", order_detail, name="order_detail"),
    path("orders/<int:pk>/editar/", order_edit, name="order_edit"),
    path("orders/<int:pk>/enviar/", order_send, name="order_send"),
    path("orders/<int:pk>/recibir/", order_receive, name="order_receive"),
    path("orders/<int:pk>/cancelar/", order_cancel, name="order_cancel"),
    path("counter/", orders_counter, name="orders_counter"),
]
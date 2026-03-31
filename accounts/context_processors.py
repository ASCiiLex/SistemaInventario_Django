from .permissions import (
    can_manage_products,
    can_manage_orders,
    can_view_dashboard,
)


def permissions(request):
    user = request.user

    return {
        "can_manage_products": can_manage_products(user),
        "can_manage_orders": can_manage_orders(user),
        "can_view_dashboard": can_view_dashboard(user),
    }
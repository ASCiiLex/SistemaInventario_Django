from .permissions import (
    can_manage_products,
    can_manage_orders,
    can_view_dashboard,

    # 🔥 granular
    can_view_products,
    can_create_products,
    can_edit_products,
    can_delete_products,
    can_export_products,
)


def permissions(request):
    user = request.user

    return {
        # legacy
        "can_manage_products": can_manage_products(user),
        "can_manage_orders": can_manage_orders(user),
        "can_view_dashboard": can_view_dashboard(user),

        # 🔥 nuevos granular
        "can_view_products": can_view_products(user),
        "can_create_products": can_create_products(user),
        "can_edit_products": can_edit_products(user),
        "can_delete_products": can_delete_products(user),
        "can_export_products": can_export_products(user),
    }
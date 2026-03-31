from .permissions import (
    can_manage_products,
    can_manage_orders,
    can_view_dashboard,

    can_view_products,
    can_create_products,
    can_edit_products,
    can_delete_products,
    can_export_products,

    # 🔥 INVENTORY
    can_view_inventory,
    can_create_inventory,
    can_edit_inventory,
    can_delete_inventory,
    can_confirm_inventory,
)


def permissions(request):
    user = request.user

    return {
        # legacy
        "can_manage_products": can_manage_products(user),
        "can_manage_orders": can_manage_orders(user),
        "can_view_dashboard": can_view_dashboard(user),

        # products
        "can_view_products": can_view_products(user),
        "can_create_products": can_create_products(user),
        "can_edit_products": can_edit_products(user),
        "can_delete_products": can_delete_products(user),
        "can_export_products": can_export_products(user),

        # inventory
        "can_view_inventory": can_view_inventory(user),
        "can_create_inventory": can_create_inventory(user),
        "can_edit_inventory": can_edit_inventory(user),
        "can_delete_inventory": can_delete_inventory(user),
        "can_confirm_inventory": can_confirm_inventory(user),
    }
from accounts.permissions import *


def permissions_context(request):
    user = request.user

    perm = {
        # PRODUCTS
        "view_products": can_view_products(user),
        "create_products": can_create_products(user),
        "edit_products": can_edit_products(user),
        "delete_products": can_delete_products(user),
        "export_products": can_export_products(user),

        # CATEGORIES
        "view_categories": can_view_categories(user),
        "manage_categories": can_manage_categories(user),

        # SUPPLIERS
        "view_suppliers": can_view_suppliers(user),
        "manage_suppliers": can_manage_suppliers(user),

        # LOCATIONS
        "view_locations": can_view_locations(user),
        "manage_locations": can_manage_locations(user),

        # INVENTORY
        "view_inventory": can_view_inventory(user),
        "create_inventory": can_create_inventory(user),
        "edit_inventory": can_edit_inventory(user),
        "confirm_inventory": can_confirm_inventory(user),

        # TRANSFERS
        "view_transfers": can_view_transfers(user),
        "create_transfer": can_create_transfer(user),
        "confirm_transfer": can_confirm_transfer(user),

        # ORDERS
        "view_orders": can_view_orders(user),
        "create_order": can_create_order(user),
        "edit_order": can_edit_order(user),
        "send_order": can_send_order(user),
        "cancel_order": can_cancel_order(user),
        "receive_order": can_receive_order(user),

        # AUDIT
        "view_audit": can_view_audit(user),

        # NOTIFICATIONS
        "manage_notifications": can_manage_notifications(user),
    }

    return {
        "perm": perm
    }
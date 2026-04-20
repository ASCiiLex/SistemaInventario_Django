from accounts import permissions as perms


def permissions_context(request):
    user = getattr(request, "user", None)
    org = getattr(request, "organization", None)

    # 🔒 Usuario no autenticado
    if not user or not user.is_authenticated:
        return {"perm": {}}

    perm = {
        # PRODUCTS
        "view_products": perms.can_view_products(user, org),
        "create_products": perms.can_create_products(user, org),
        "edit_products": perms.can_edit_products(user, org),
        "delete_products": perms.can_delete_products(user, org),
        "export_products": perms.can_export_products(user, org),

        # CATEGORIES
        "view_categories": perms.can_view_categories(user, org),
        "manage_categories": perms.can_manage_categories(user, org),

        # SUPPLIERS
        "view_suppliers": perms.can_view_suppliers(user, org),
        "manage_suppliers": perms.can_manage_suppliers(user, org),

        # LOCATIONS
        "view_locations": perms.can_view_locations(user, org),
        "manage_locations": perms.can_manage_locations(user, org),

        # INVENTORY
        "view_inventory": perms.can_view_inventory(user, org),
        "create_inventory": perms.can_create_inventory(user, org),
        "edit_inventory": perms.can_edit_inventory(user, org),
        "confirm_inventory": perms.can_confirm_inventory(user, org),

        # TRANSFERS
        "view_transfers": perms.can_view_transfers(user, org),
        "create_transfer": perms.can_create_transfer(user, org),
        "confirm_transfer": perms.can_confirm_transfer(user, org),

        # ORDERS
        "view_orders": perms.can_view_orders(user, org),
        "create_order": perms.can_create_order(user, org),
        "edit_order": perms.can_edit_order(user, org),
        "send_order": perms.can_send_order(user, org),
        "cancel_order": perms.can_cancel_order(user, org),
        "receive_order": perms.can_receive_order(user, org),

        # AUDIT
        "view_audit": perms.can_view_audit(user, org),

        # NOTIFICATIONS
        "manage_notifications": perms.can_manage_notifications(user, org),

        # METRICS
        "can_view_system_metrics": perms.can_view_system_metrics(user, org),
    }

    return {
        "perm": perm
    }
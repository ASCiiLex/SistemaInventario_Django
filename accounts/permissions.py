from organizations.models import Membership


# ==========================================
# 🔥 CORE HELPERS
# ==========================================

def _get_membership(user):
    if not user or not user.is_authenticated:
        return None

    return (
        user.memberships
        .select_related("organization")
        .filter(is_active=True)
        .first()
    )


def _has_role(user, roles):
    membership = _get_membership(user)
    if not membership:
        return False
    return membership.role in roles


def _is_owner(user):
    return _has_role(user, [Membership.Roles.OWNER])


def _is_admin(user):
    return _has_role(user, [Membership.Roles.OWNER, Membership.Roles.ADMIN])


def _is_manager(user):
    return _has_role(user, [
        Membership.Roles.OWNER,
        Membership.Roles.ADMIN,
        Membership.Roles.MANAGER
    ])


def _is_staff(user):
    return _has_role(user, [
        Membership.Roles.OWNER,
        Membership.Roles.ADMIN,
        Membership.Roles.MANAGER,
        Membership.Roles.STAFF
    ])


# ==========================================
# PRODUCTS
# ==========================================

def can_view_products(user):
    return _is_staff(user)


def can_create_products(user):
    return _is_manager(user)


def can_edit_products(user):
    return _is_manager(user)


def can_delete_products(user):
    return _is_admin(user)


def can_export_products(user):
    return _is_manager(user)


# ==========================================
# CATEGORIES
# ==========================================

def can_view_categories(user):
    return _is_staff(user)


def can_manage_categories(user):
    return _is_manager(user)


# ==========================================
# SUPPLIERS
# ==========================================

def can_view_suppliers(user):
    return _is_staff(user)


def can_manage_suppliers(user):
    return _is_manager(user)


# ==========================================
# LOCATIONS
# ==========================================

def can_view_locations(user):
    return _is_staff(user)


def can_manage_locations(user):
    return _is_admin(user)


# ==========================================
# INVENTORY
# ==========================================

def can_view_inventory(user):
    return _is_staff(user)


def can_create_inventory(user):
    return _is_staff(user)


def can_edit_inventory(user):
    return _is_manager(user)


def can_confirm_inventory(user):
    return _is_manager(user)


# ==========================================
# TRANSFERS
# ==========================================

def can_view_transfers(user):
    return _is_staff(user)


def can_create_transfer(user):
    return _is_staff(user)


def can_confirm_transfer(user):
    return _is_manager(user)


# ==========================================
# ORDERS
# ==========================================

def can_view_orders(user):
    return _is_staff(user)


def can_create_order(user):
    return _is_manager(user)


def can_edit_order(user):
    return _is_manager(user)


def can_send_order(user):
    return _is_manager(user)


def can_cancel_order(user):
    return _is_manager(user)


def can_receive_order(user):
    return _is_staff(user)


# ==========================================
# AUDIT
# ==========================================

def can_view_audit(user):
    return _is_manager(user)


# ==========================================
# NOTIFICATIONS
# ==========================================

def can_manage_notifications(user):
    return _is_manager(user)
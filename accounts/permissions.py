from organizations.models import Membership


def _get_membership(user):
    if not user.is_authenticated:
        return None

    return (
        Membership.objects
        .filter(user=user, is_active=True)
        .select_related("organization")
        .first()
    )


def is_owner(user):
    membership = _get_membership(user)
    return membership and membership.role == Membership.Roles.OWNER


def is_admin(user):
    membership = _get_membership(user)
    return membership and membership.role in [
        Membership.Roles.OWNER,
        Membership.Roles.ADMIN
    ]


def is_manager(user):
    membership = _get_membership(user)
    return membership and membership.role in [
        Membership.Roles.OWNER,
        Membership.Roles.ADMIN,
        Membership.Roles.MANAGER
    ]


def is_staff(user):
    membership = _get_membership(user)
    return membership and membership.role == Membership.Roles.STAFF


# 🔹 PRODUCTS

def can_view_products(user):
    return user.is_authenticated


def can_create_products(user):
    return is_manager(user) or is_staff(user)


def can_edit_products(user):
    return is_manager(user)


def can_delete_products(user):
    return is_admin(user)


def can_export_products(user):
    return can_create_products(user)


# 🔹 INVENTORY

def can_view_inventory(user):
    return user.is_authenticated


def can_create_inventory(user):
    return is_manager(user)


def can_edit_inventory(user):
    return is_manager(user)


def can_delete_inventory(user):
    return is_admin(user)


def can_confirm_inventory(user):
    return is_manager(user)


def can_send_orders(user):
    return user.is_authenticated


# 🔹 LEGACY

def can_manage_products(user):
    return is_manager(user)


def can_manage_orders(user):
    return is_manager(user)


def can_view_dashboard(user):
    return user.is_authenticated
from organizations.models import Membership


# ==========================================
# CORE HELPERS (CON CONTEXTO DE ORGANIZACIÓN)
# ==========================================

def _get_membership(user, organization=None):
    if not user or not user.is_authenticated:
        return None

    if organization:
        return (
            user.memberships
            .filter(organization=organization, is_active=True)
            .first()
        )

    request = getattr(user, "_request", None)

    if request and hasattr(request, "organization"):
        return (
            user.memberships
            .filter(organization=request.organization, is_active=True)
            .first()
        )

    return user.memberships.filter(is_active=True).first()


def _has_role(user, roles, organization=None):
    membership = _get_membership(user, organization)
    if not membership:
        return False
    return membership.role in roles


def _is_owner(user, organization=None):
    return _has_role(user, [Membership.Roles.OWNER], organization)


def _is_admin(user, organization=None):
    return _has_role(user, [Membership.Roles.OWNER, Membership.Roles.ADMIN], organization)


def _is_manager(user, organization=None):
    return _has_role(
        user,
        [
            Membership.Roles.OWNER,
            Membership.Roles.ADMIN,
            Membership.Roles.MANAGER
        ],
        organization
    )


def _is_staff(user, organization=None):
    return _has_role(
        user,
        [
            Membership.Roles.OWNER,
            Membership.Roles.ADMIN,
            Membership.Roles.MANAGER,
            Membership.Roles.STAFF
        ],
        organization
    )


# ==========================================
# PRODUCTS
# ==========================================

def can_view_products(user, organization=None):
    return _is_staff(user, organization)


def can_create_products(user, organization=None):
    return _is_manager(user, organization)


def can_edit_products(user, organization=None):
    return _is_manager(user, organization)


def can_delete_products(user, organization=None):
    return _is_admin(user, organization)


def can_export_products(user, organization=None):
    return _is_manager(user, organization)


# ==========================================
# CATEGORIES
# ==========================================

def can_view_categories(user, organization=None):
    return _is_staff(user, organization)


def can_manage_categories(user, organization=None):
    return _is_manager(user, organization)


# ==========================================
# SUPPLIERS
# ==========================================

def can_view_suppliers(user, organization=None):
    return _is_staff(user, organization)


def can_manage_suppliers(user, organization=None):
    return _is_manager(user, organization)


# ==========================================
# LOCATIONS
# ==========================================

def can_view_locations(user, organization=None):
    return _is_staff(user, organization)


def can_manage_locations(user, organization=None):
    return _is_admin(user, organization)


# ==========================================
# INVENTORY
# ==========================================

def can_view_inventory(user, organization=None):
    return _is_staff(user, organization)


def can_create_inventory(user, organization=None):
    return _is_staff(user, organization)


def can_edit_inventory(user, organization=None):
    return _is_manager(user, organization)


def can_confirm_inventory(user, organization=None):
    return _is_manager(user, organization)


# ==========================================
# TRANSFERS
# ==========================================

def can_view_transfers(user, organization=None):
    return _is_staff(user, organization)


def can_create_transfer(user, organization=None):
    return _is_staff(user, organization)


def can_confirm_transfer(user, organization=None):
    return _is_manager(user, organization)


# ==========================================
# ORDERS
# ==========================================

def can_view_orders(user, organization=None):
    return _is_staff(user, organization)


def can_create_order(user, organization=None):
    return _is_manager(user, organization)


def can_edit_order(user, organization=None):
    return _is_manager(user, organization)


def can_send_order(user, organization=None):
    return _is_manager(user, organization)


def can_cancel_order(user, organization=None):
    return _is_manager(user, organization)


def can_receive_order(user, organization=None):
    return _is_staff(user, organization)


# ==========================================
# AUDIT
# ==========================================

def can_view_audit(user, organization=None):
    return _is_manager(user, organization)


# ==========================================
# NOTIFICATIONS
# ==========================================

def can_manage_notifications(user, organization=None):
    return _is_manager(user, organization)


# ==========================================
# METRICS
# ==========================================

def can_view_system_metrics(user, organization=None):
    return _is_admin(user, organization)
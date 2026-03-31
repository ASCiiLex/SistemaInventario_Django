def is_admin(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return hasattr(user, "profile") and user.profile.role == "ADMIN"


def is_manager(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return hasattr(user, "profile") and user.profile.role in ["ADMIN", "MANAGER"]


def is_staff(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return hasattr(user, "profile") and user.profile.role == "STAFF"


# GRANULARIDAD PRODUCTOS

def can_view_products(user):
    return user.is_authenticated


def can_create_products(user):
    return is_admin(user) or is_manager(user) or is_staff(user)


def can_edit_products(user):
    return is_admin(user) or is_manager(user)


def can_delete_products(user):
    return is_admin(user) or is_manager(user)


def can_export_products(user):
    return can_create_products(user)


# OTROS

def can_manage_products(user):
    return is_manager(user)


def can_manage_orders(user):
    return is_manager(user)


def can_view_dashboard(user):
    return user.is_authenticated
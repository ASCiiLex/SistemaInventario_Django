def is_admin(user):
    if not user.is_authenticated:
        return False

    # 🔥 SUPERUSER = ADMIN SIEMPRE
    if user.is_superuser:
        return True

    return hasattr(user, "profile") and user.profile.role == "ADMIN"


def is_manager(user):
    if not user.is_authenticated:
        return False

    # 🔥 SUPERUSER = ACCESO TOTAL
    if user.is_superuser:
        return True

    return hasattr(user, "profile") and user.profile.role in ["ADMIN", "MANAGER"]


def can_manage_products(user):
    return is_manager(user)


def can_manage_orders(user):
    return is_manager(user)


def can_view_dashboard(user):
    return user.is_authenticated
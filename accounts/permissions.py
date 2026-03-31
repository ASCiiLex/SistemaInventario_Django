def is_admin(user):
    return hasattr(user, "profile") and user.profile.role == "ADMIN"


def is_manager(user):
    return hasattr(user, "profile") and user.profile.role in ["ADMIN", "MANAGER"]


def can_manage_products(user):
    return is_manager(user)


def can_manage_orders(user):
    return is_manager(user)


def can_view_dashboard(user):
    return user.is_authenticated
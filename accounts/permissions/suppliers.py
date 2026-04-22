from .core import is_staff, is_manager


def can_view_suppliers(user, organization=None):
    return is_staff(user, organization)


def can_manage_suppliers(user, organization=None):
    return is_manager(user, organization)
from .core import is_staff, is_manager, is_admin


def can_view_products(user, organization=None):
    return is_staff(user, organization)


def can_create_products(user, organization=None):
    return is_manager(user, organization)


def can_edit_products(user, organization=None):
    return is_manager(user, organization)


def can_delete_products(user, organization=None):
    return is_admin(user, organization)


def can_export_products(user, organization=None):
    return is_manager(user, organization)
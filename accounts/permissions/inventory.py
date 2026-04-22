from .core import is_staff, is_manager


def can_view_inventory(user, organization=None):
    return is_staff(user, organization)


def can_create_inventory(user, organization=None):
    return is_staff(user, organization)


def can_edit_inventory(user, organization=None):
    return is_manager(user, organization)


def can_confirm_inventory(user, organization=None):
    return is_manager(user, organization)
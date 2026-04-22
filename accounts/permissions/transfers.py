from .core import is_staff, is_manager


def can_view_transfers(user, organization=None):
    return is_staff(user, organization)


def can_create_transfer(user, organization=None):
    return is_staff(user, organization)


def can_confirm_transfer(user, organization=None):
    return is_manager(user, organization)
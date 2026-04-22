from .core import is_staff, is_manager


def can_view_orders(user, organization=None):
    return is_staff(user, organization)


def can_create_order(user, organization=None):
    return is_manager(user, organization)


def can_edit_order(user, organization=None):
    return is_manager(user, organization)


def can_send_order(user, organization=None):
    return is_manager(user, organization)


def can_cancel_order(user, organization=None):
    return is_manager(user, organization)


def can_receive_order(user, organization=None):
    return is_staff(user, organization)
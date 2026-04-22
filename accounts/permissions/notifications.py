from .core import is_manager


def can_manage_notifications(user, organization=None):
    return is_manager(user, organization)
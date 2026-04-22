from .core import is_manager


def can_view_audit(user, organization=None):
    return is_manager(user, organization)
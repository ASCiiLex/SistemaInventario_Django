from .core import is_admin


def can_view_system_metrics(user, organization=None):
    return is_admin(user, organization)
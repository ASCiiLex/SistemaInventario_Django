from .core import is_staff, is_admin


def can_view_locations(user, organization=None):
    return is_staff(user, organization)


def can_manage_locations(user, organization=None):
    return is_admin(user, organization)
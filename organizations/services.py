from .models import Membership


def get_user_memberships(user):
    return Membership.objects.select_related("organization").filter(user=user, is_active=True)


def get_user_organizations(user):
    return [m.organization for m in get_user_memberships(user)]


def get_user_role(user, organization):
    membership = (
        Membership.objects
        .filter(user=user, organization=organization, is_active=True)
        .first()
    )
    return membership.role if membership else None


def is_admin(user, organization):
    return get_user_role(user, organization) == "admin"


def is_manager(user, organization):
    return get_user_role(user, organization) in ["admin", "manager"]
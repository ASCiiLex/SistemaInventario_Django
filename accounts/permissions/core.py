from organizations.models import Membership


def get_membership(user, organization=None):
    if not user or not user.is_authenticated:
        return None

    if organization:
        return (
            user.memberships
            .filter(organization=organization, is_active=True)
            .first()
        )

    request = getattr(user, "_request", None)

    if request and hasattr(request, "organization"):
        return (
            user.memberships
            .filter(organization=request.organization, is_active=True)
            .first()
        )

    return user.memberships.filter(is_active=True).first()


def has_role(user, roles, organization=None):
    membership = get_membership(user, organization)
    if not membership:
        return False
    return membership.role in roles


def is_owner(user, organization=None):
    return has_role(user, [Membership.Roles.OWNER], organization)


def is_admin(user, organization=None):
    return has_role(user, [Membership.Roles.OWNER, Membership.Roles.ADMIN], organization)


def is_manager(user, organization=None):
    return has_role(
        user,
        [
            Membership.Roles.OWNER,
            Membership.Roles.ADMIN,
            Membership.Roles.MANAGER
        ],
        organization
    )


def is_staff(user, organization=None):
    return has_role(
        user,
        [
            Membership.Roles.OWNER,
            Membership.Roles.ADMIN,
            Membership.Roles.MANAGER,
            Membership.Roles.STAFF
        ],
        organization
    )
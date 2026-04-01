from .models import Organization, Membership


def create_organization_with_owner(user, name, slug):
    organization = Organization.objects.create(
        name=name,
        slug=slug
    )

    Membership.objects.create(
        user=user,
        organization=organization,
        role=Membership.Roles.OWNER
    )

    return organization
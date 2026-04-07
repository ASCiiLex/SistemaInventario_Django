from .models import Membership


def organization(request):
    user = getattr(request, "user", None)

    if not user or not user.is_authenticated:
        return {
            "organization": None,
            "organizations": [],
        }

    memberships = (
        Membership.objects
        .select_related("organization")
        .filter(user=user, is_active=True)
        .order_by("organization__name")
    )

    return {
        "organization": getattr(request, "organization", None),
        "organizations": memberships,
    }
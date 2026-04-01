from .models import Membership, Organization


class OrganizationMiddleware:
    """
    Inyecta organization activa en request
    + bootstrap automático para usuarios legacy
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None

        if request.user.is_authenticated:

            membership = (
                Membership.objects
                .select_related("organization")
                .filter(user=request.user, is_active=True)
                .first()
            )

            # 🔥 BOOTSTRAP AUTOMÁTICO (clave)
            if not membership:
                organization, _ = Organization.objects.get_or_create(
                    slug="default",
                    defaults={"name": "Default Organization"}
                )

                membership = Membership.objects.create(
                    user=request.user,
                    organization=organization,
                    role=Membership.Roles.OWNER
                )

            request.organization = membership.organization

        return self.get_response(request)
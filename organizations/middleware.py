from .models import Membership, Organization


class OrganizationMiddleware:
    """
    🔥 Middleware multi-tenant definitivo

    - Inyecta:
        request.organization
        request.membership

    - Bootstrap automático seguro (owner obligatorio)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None
        request.membership = None

        user = request.user

        if user.is_authenticated:

            membership = (
                Membership.objects
                .select_related("organization")
                .filter(user=user, is_active=True)
                .order_by("id")
                .first()
            )

            # 🔥 BOOTSTRAP correcto (con owner obligatorio)
            if not membership:
                organization, created = Organization.objects.get_or_create(
                    slug="default",
                    defaults={
                        "name": "Default Organization",
                        "owner": user,  # 🔥 clave para evitar IntegrityError
                    }
                )

                # si existía sin owner (edge case)
                if not organization.owner:
                    organization.owner = user
                    organization.save(update_fields=["owner"])

                membership = Membership.objects.create(
                    user=user,
                    organization=organization,
                    role=Membership.Roles.OWNER
                )

            request.organization = membership.organization
            request.membership = membership

        return self.get_response(request)
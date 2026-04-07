from .models import Membership, Organization


class OrganizationMiddleware:
    """
    🔥 Middleware multi-tenant PRO

    - Soporta múltiples organizaciones por usuario
    - Permite selección activa vía sesión
    - Fallback automático seguro
    """

    SESSION_KEY = "active_organization_id"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None
        request.membership = None

        user = request.user

        if user.is_authenticated:

            memberships = (
                Membership.objects
                .select_related("organization")
                .filter(user=user, is_active=True)
                .order_by("id")
            )

            membership = None

            # 🔥 1. Intentar desde sesión
            org_id = request.session.get(self.SESSION_KEY)

            if org_id:
                membership = memberships.filter(organization_id=org_id).first()

            # 🔥 2. Fallback → primera activa
            if not membership:
                membership = memberships.first()

            # 🔥 3. Bootstrap seguro
            if not membership:
                organization, _ = Organization.objects.get_or_create(
                    slug="default",
                    defaults={
                        "name": "Default Organization",
                        "owner": user,
                    }
                )

                if not organization.owner:
                    organization.owner = user
                    organization.save(update_fields=["owner"])

                membership = Membership.objects.create(
                    user=user,
                    organization=organization,
                    role=Membership.Roles.OWNER
                )

            # 🔥 Persistir en sesión
            request.session[self.SESSION_KEY] = membership.organization_id

            request.organization = membership.organization
            request.membership = membership

        return self.get_response(request)
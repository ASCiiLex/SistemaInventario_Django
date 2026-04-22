from .models import Membership, Organization


class OrganizationMiddleware:
    """
    🔥 Middleware multi-tenant robusto (no rompe login / errores DB)
    """

    SESSION_KEY = "active_organization_id"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None
        request.membership = None

        user = getattr(request, "user", None)

        # 🔥 CRÍTICO: si no hay usuario o no está autenticado → no tocar DB
        if not user or not user.is_authenticated:
            return self.get_response(request)

        try:
            memberships = (
                Membership.objects
                .select_related("organization")
                .filter(user=user, is_active=True)
                .order_by("id")
            )

            membership = None

            # 1. sesión
            org_id = request.session.get(self.SESSION_KEY)
            if org_id:
                membership = memberships.filter(organization_id=org_id).first()

            # 2. fallback
            if not membership:
                membership = memberships.first()

            # 3. bootstrap seguro
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

            request.session[self.SESSION_KEY] = membership.organization_id

            request.organization = membership.organization
            request.membership = membership

        except Exception:
            # 🔥 nunca romper request (login incluido)
            request.organization = None
            request.membership = None

        return self.get_response(request)
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse

from organizations.models import Membership


@login_required
def switch_organization(request, org_id):
    membership = get_object_or_404(
        Membership,
        user=request.user,
        organization_id=org_id,
        is_active=True
    )

    request.session["active_organization_id"] = membership.organization_id

    if request.headers.get("HX-Request"):
        response = HttpResponse()
        response["HX-Redirect"] = reverse("dashboard")
        return response

    return redirect("dashboard")
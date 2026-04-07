from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Membership
from .forms import InviteUserForm, UpdateRoleForm
from inventory.utils.listing import ListViewMixin


# ==========================================
# 🔐 PERMISOS
# ==========================================

def _can_manage(request):
    membership = request.membership
    return membership and membership.role in ["owner", "admin"]


# ==========================================
# 📋 LISTADO DE MIEMBROS
# ==========================================

@login_required
def members_list(request):
    if not _can_manage(request):
        return render(request, "403.html", status=403)

    view = ListViewMixin()
    view.allowed_sort_fields = [
        "user__username",
        "user__email",
        "role",
        "is_active",
    ]
    view.default_ordering = "user__username"

    qs = Membership.objects.select_related("user").filter(
        organization=request.organization
    )

    qs = view.apply_ordering(request, qs)
    page_obj = view.paginate_queryset(request, qs)

    invite_form = InviteUserForm(organization=request.organization)

    context = {
        "members": page_obj,
        "page_obj": page_obj,
        "invite_form": invite_form,
        **view.get_ordering_context(request),
    }

    if view.is_htmx(request):
        return render(request, "organizations/members/partials/table.html", context)

    return render(request, "organizations/members/list.html", context)


# ==========================================
# ➕ INVITAR USUARIO
# ==========================================

@login_required
def invite_member(request):
    if not _can_manage(request):
        return render(request, "403.html", status=403)

    if request.method == "POST":
        form = InviteUserForm(request.POST, organization=request.organization)

        if form.is_valid():
            user = form.cleaned_data["user_instance"]

            Membership.objects.get_or_create(
                user=user,
                organization=request.organization,
                defaults={
                    "role": form.cleaned_data["role"],
                },
            )

    return redirect("members_list")


# ==========================================
# 🔁 CAMBIAR ROL
# ==========================================

@login_required
def update_role(request, pk):
    if not _can_manage(request):
        return render(request, "403.html", status=403)

    membership = get_object_or_404(
        Membership,
        pk=pk,
        organization=request.organization
    )

    # 🔒 No tocar owner
    if membership.role == Membership.Roles.OWNER:
        return redirect("members_list")

    if request.method == "POST":
        form = UpdateRoleForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()

    return redirect("members_list")


# ==========================================
# 🔄 ACTIVAR / DESACTIVAR
# ==========================================

@login_required
def toggle_member(request, pk):
    if not _can_manage(request):
        return render(request, "403.html", status=403)

    membership = get_object_or_404(
        Membership,
        pk=pk,
        organization=request.organization
    )

    # 🔒 No tocar owner
    if membership.role == Membership.Roles.OWNER:
        return redirect("members_list")

    membership.is_active = not membership.is_active
    membership.save(update_fields=["is_active"])

    return redirect("members_list")


# ==========================================
# 🔥 SWITCH ORGANIZATION (NUEVO)
# ==========================================

@login_required
def switch_organization(request, org_id):
    """
    Cambia organización activa (session-based)
    """
    request.session["active_organization_id"] = org_id
    return redirect(request.META.get("HTTP_REFERER", "dashboard"))
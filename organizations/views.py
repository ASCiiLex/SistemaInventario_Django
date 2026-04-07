from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Membership
from .forms import InviteUserForm, UpdateRoleForm
from inventory.utils.listing import ListViewMixin


def _can_manage(request):
    membership = request.membership
    return membership and membership.role in ["owner", "admin"]


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


@login_required
def invite_member(request):
    if not _can_manage(request):
        return render(request, "403.html", status=403)

    if request.method == "POST":
        form = InviteUserForm(request.POST, organization=request.organization)

        if form.is_valid():
            user = form.cleaned_data["user_instance"]

            Membership.objects.create(
                user=user,
                organization=request.organization,
                role=form.cleaned_data["role"],
            )

    return redirect("members_list")


@login_required
def update_role(request, pk):
    if not _can_manage(request):
        return render(request, "403.html", status=403)

    membership = get_object_or_404(
        Membership,
        pk=pk,
        organization=request.organization
    )

    if membership.role == "owner":
        return redirect("members_list")

    if request.method == "POST":
        form = UpdateRoleForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()

    return redirect("members_list")


@login_required
def toggle_member(request, pk):
    if not _can_manage(request):
        return render(request, "403.html", status=403)

    membership = get_object_or_404(
        Membership,
        pk=pk,
        organization=request.organization
    )

    if membership.role == "owner":
        return redirect("members_list")

    membership.is_active = not membership.is_active
    membership.save()

    return redirect("members_list")
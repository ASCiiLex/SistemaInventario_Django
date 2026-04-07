from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Membership
from .forms import InviteUserForm, UpdateRoleForm, ToggleMembershipForm


def _can_manage(request):
    membership = request.membership
    return membership and membership.role in ["owner", "admin"]


@login_required
def members_list(request):
    if not _can_manage(request):
        return render(request, "403.html", status=403)

    members = Membership.objects.select_related("user").filter(
        organization=request.organization
    )

    invite_form = InviteUserForm(organization=request.organization)

    return render(request, "organizations/members/list.html", {
        "members": members,
        "invite_form": invite_form,
    })


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
from django.urls import path
from .views import (
    members_list,
    invite_member,
    update_role,
    toggle_member,
    switch_organization,
)

urlpatterns = [
    path("members/", members_list, name="members_list"),
    path("members/invite/", invite_member, name="invite_member"),
    path("members/<int:pk>/role/", update_role, name="update_role"),
    path("members/<int:pk>/toggle/", toggle_member, name="toggle_member"),

    # 🔥 selector organización
    path("switch/<int:org_id>/", switch_organization, name="switch_organization"),
]
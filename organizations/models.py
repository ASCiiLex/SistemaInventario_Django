from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_organizations"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    # 🔥 helper clave
    def get_owner_membership(self):
        return self.memberships.filter(
            user=self.owner,
            role=Membership.Roles.OWNER
        ).first()


class Membership(models.Model):

    class Roles(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        STAFF = "staff", "Staff"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.STAFF
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "organization")
        indexes = [
            models.Index(fields=["user", "organization"]),
        ]

    def __str__(self):
        return f"{self.user.username} @ {self.organization.name} ({self.role})"

    # 🔥 helpers PRO
    def is_owner(self):
        return self.role == self.Roles.OWNER

    def is_admin(self):
        return self.role in [self.Roles.OWNER, self.Roles.ADMIN]

    def is_manager(self):
        return self.role in [self.Roles.OWNER, self.Roles.ADMIN, self.Roles.MANAGER]


# ==========================================
# 🔥 USER HELPERS (clave para todo el sistema)
# ==========================================

def get_user_active_membership(user):
    return (
        user.memberships
        .select_related("organization")
        .filter(is_active=True)
        .first()
    )


def get_user_organization(user):
    membership = get_user_active_membership(user)
    return membership.organization if membership else None


def get_user_role(user):
    membership = get_user_active_membership(user)
    return membership.role if membership else None
from django import forms
from django.contrib.auth.models import User
from .models import Membership


class InviteUserForm(forms.Form):
    email = forms.EmailField(label="Email")
    role = forms.ChoiceField(choices=Membership.Roles.choices)

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        user, _ = User.objects.get_or_create(
            username=email,
            defaults={"email": email},
        )

        if Membership.objects.filter(
            user=user,
            organization=self.organization,
            is_active=True
        ).exists():
            raise forms.ValidationError("El usuario ya pertenece a la organización.")

        self.cleaned_data["user_instance"] = user
        return email


class UpdateRoleForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ["role"]


class ToggleMembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ["is_active"]
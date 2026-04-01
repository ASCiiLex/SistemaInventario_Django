from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Supplier
        fields = ["name", "contact_name", "email", "phone", "address"]

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.organization:
            instance.organization = self.organization
        if commit:
            instance.save()
        return instance
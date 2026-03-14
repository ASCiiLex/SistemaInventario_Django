from django import forms
from ..models import Location


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "address", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
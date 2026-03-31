from django import forms
from inventory.models.audit import AuditLog


class AuditFilterForm(forms.Form):
    model = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Modelo"
        })
    )

    user = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Usuario"
        })
    )

    action = forms.ChoiceField(
        required=False,
        choices=[("", "Acción")] + list(AuditLog.ACTION_CHOICES),
        widget=forms.Select(attrs={"class": "form-select"})
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control",
            "placeholder": "Desde"
        })
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control",
            "placeholder": "Hasta"
        })
    )
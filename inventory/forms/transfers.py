from django import forms

from products.models import Product
from ..models import StockTransfer, Location


class StockTransferCreateForm(forms.ModelForm):
    class Meta:
        model = StockTransfer
        fields = ["product", "origin", "destination", "quantity", "note"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-control select2"}),
            "origin": forms.Select(attrs={"class": "form-control select2"}),
            "destination": forms.Select(attrs={"class": "form-control select2"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor que cero.")
        return qty

    def clean(self):
        cleaned = super().clean()
        origin = cleaned.get("origin")
        destination = cleaned.get("destination")

        if origin and destination and origin == destination:
            raise forms.ValidationError("El origen y destino no pueden ser iguales.")

        return cleaned


class StockTransferConfirmForm(forms.Form):
    confirmar = forms.BooleanField(
        required=True,
        initial=True,
        widget=forms.HiddenInput()
    )


class StockTransferFilterForm(forms.Form):
    STATUS_CHOICES = [
        ("", "Todos los estados"),
    ] + list(StockTransfer.STATUS_CHOICES)

    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select select2",
            "data-placeholder": "Producto"}),
        label="Producto",
    )
    origin = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select select2",
            "data-placeholder": "Origen"}),
        label="Origen",
    )
    destination = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select select2",
            "data-placeholder": "Destino"}),
        label="Destino",
    )
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Estado",
    )
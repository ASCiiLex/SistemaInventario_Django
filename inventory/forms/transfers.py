from django import forms
from ..models import StockTransfer


class StockTransferCreateForm(forms.ModelForm):
    class Meta:
        model = StockTransfer
        fields = ["product", "origin", "destination", "quantity", "note"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-control"}),
            "origin": forms.Select(attrs={"class": "form-control"}),
            "destination": forms.Select(attrs={"class": "form-control"}),
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
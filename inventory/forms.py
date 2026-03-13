from django import forms

from .models import (
    StockMovement,
    Location,
    StockTransfer,   # NUEVO
)

from products.models import Product


# ---------------------------------------------------------
# FORMULARIO EXISTENTE — NO SE TOCA
# ---------------------------------------------------------
class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ["product", "movement_type", "origin", "destination", "quantity", "note"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-control"}),
            "movement_type": forms.Select(attrs={"class": "form-control"}),
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


# ---------------------------------------------------------
# FORMULARIO EXISTENTE — SE MANTIENE POR COMPATIBILIDAD
# ---------------------------------------------------------
class StockTransferForm(forms.ModelForm):
    movement_type = forms.CharField(widget=forms.HiddenInput(), initial="TRANSFER")

    class Meta:
        model = StockMovement
        fields = ["product", "origin", "destination", "quantity", "note", "movement_type"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-control"}),
            "origin": forms.Select(attrs={"class": "form-control"}),
            "destination": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        origin = cleaned_data.get("origin")
        destination = cleaned_data.get("destination")

        if origin and destination and origin == destination:
            raise forms.ValidationError("El origen y destino no pueden ser iguales.")

        return cleaned_data

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor que cero.")
        return qty


# ---------------------------------------------------------
# NUEVO — FORMULARIO PARA CREAR TRANSFERENCIA PENDIENTE
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# NUEVO — FORMULARIO PARA CONFIRMAR RECEPCIÓN
# ---------------------------------------------------------
class StockTransferConfirmForm(forms.Form):
    """Formulario vacío: solo sirve para confirmar la recepción."""
    confirmar = forms.BooleanField(
        required=True,
        initial=True,
        widget=forms.HiddenInput()
    )


# ---------------------------------------------------------
# FORMULARIO EXISTENTE — NO SE TOCA
# ---------------------------------------------------------
class StockImportForm(forms.Form):
    csv_file = forms.FileField(label="Archivo CSV")
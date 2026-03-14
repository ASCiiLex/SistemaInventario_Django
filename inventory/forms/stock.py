from django import forms

from products.models import Product
from ..models import StockMovement, Location


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ["product", "movement_type", "origin", "destination", "quantity", "note"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-control select2"}),
            "movement_type": forms.Select(attrs={"class": "form-control"}),
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


class StockMovementFilterForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select select2"}),
        label="Producto",
    )

    movement_type = forms.ChoiceField(
        required=False,
        choices=[("", "Todos los tipos")] + list(
            StockMovement._meta.get_field("movement_type").choices
        ),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Tipo",
    )

    origin = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select select2"}),
        label="Origen",
    )

    destination = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select select2"}),
        label="Destino",
    )
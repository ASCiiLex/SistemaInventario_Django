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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TRANSFER se gestiona por StockTransfer
        self.fields["movement_type"].choices = [
            ("IN", "Entrada"),
            ("OUT", "Salida"),
        ]
        self.fields["origin"].queryset = Location.objects.all()
        self.fields["destination"].queryset = Location.objects.all()

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor que cero.")
        return qty


class StockMovementFilterForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select select2",
            "data-placeholder": "Producto"}),
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

    q = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Buscar producto..."}
        ),
    )

    date_from = forms.DateField(
        required=False,
        label="Desde",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    date_to = forms.DateField(
        required=False,
        label="Hasta",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
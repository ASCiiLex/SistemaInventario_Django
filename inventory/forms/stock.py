from django import forms

from products.models import Product
from ..models import StockMovement, Location


class StockMovementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        self.fields["movement_type"].choices = [
            ("IN", "Entrada"),
            ("OUT", "Salida"),
        ]

        if self.organization:
            self.fields["product"].queryset = Product.objects.filter(organization=self.organization)
            self.fields["origin"].queryset = Location.objects.filter(organization=self.organization)
            self.fields["destination"].queryset = Location.objects.filter(organization=self.organization)

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

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.organization:
            instance.organization = self.organization
        if commit:
            instance.save()
        return instance


class StockMovementFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        if organization:
            self.fields["product"].queryset = Product.objects.filter(organization=organization)
            self.fields["origin"].queryset = Location.objects.filter(organization=organization)
            self.fields["destination"].queryset = Location.objects.filter(organization=organization)

    product = forms.ModelChoiceField(queryset=Product.objects.none(), required=False)
    movement_type = forms.ChoiceField(
        required=False,
        choices=[("", "Todos")] + list(StockMovement._meta.get_field("movement_type").choices),
    )
    origin = forms.ModelChoiceField(queryset=Location.objects.none(), required=False)
    destination = forms.ModelChoiceField(queryset=Location.objects.none(), required=False)
    q = forms.CharField(required=False)
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)
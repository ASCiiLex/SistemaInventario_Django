from django import forms

from products.models import Product
from ..models import StockTransfer, Location


class StockTransferCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        if self.organization:
            self.fields["product"].queryset = Product.objects.filter(organization=self.organization)
            self.fields["origin"].queryset = Location.objects.filter(organization=self.organization)
            self.fields["destination"].queryset = Location.objects.filter(organization=self.organization)

    class Meta:
        model = StockTransfer
        fields = ["product", "origin", "destination", "quantity", "note"]

    def clean(self):
        cleaned = super().clean()
        origin = cleaned.get("origin")
        destination = cleaned.get("destination")

        if origin and destination and origin == destination:
            raise forms.ValidationError("El origen y destino no pueden ser iguales.")

        return cleaned

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


class StockTransferConfirmForm(forms.Form):
    confirmar = forms.BooleanField(required=True, initial=True, widget=forms.HiddenInput())


class StockTransferFilterForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.none(), required=False)
    origin = forms.ModelChoiceField(queryset=Location.objects.none(), required=False)
    destination = forms.ModelChoiceField(queryset=Location.objects.none(), required=False)
    status = forms.ChoiceField(
        required=False,
        choices=[("", "Todos")] + list(StockTransfer.STATUS_CHOICES),
    )

    def __init__(self, *args, **kwargs):
        organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        if organization:
            self.fields["product"].queryset = Product.objects.filter(organization=organization)
            self.fields["origin"].queryset = Location.objects.filter(organization=organization)
            self.fields["destination"].queryset = Location.objects.filter(organization=organization)
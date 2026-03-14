from django import forms
from django.forms import inlineformset_factory

from ..models import Order, OrderItem
from suppliers.models import Supplier
from .locations import Location
from products.models import Product


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["supplier", "location", "estimated_arrival", "status"]
        widgets = {
            "supplier": forms.Select(attrs={"class": "form-select select2"}),
            "location": forms.Select(attrs={"class": "form-select select2"}),
            "estimated_arrival": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "cost_price"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select select2"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "cost_price": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def clean_quantity(self):
        qty = self.cleaned_data.get("quantity")
        if qty is None or qty <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor que cero.")
        return qty


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
)


class OrderFilterForm(forms.Form):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select select2"}),
        label="Proveedor",
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select select2"}),
        label="Almacén",
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "Todos los estados")] + list(Order.STATUS_CHOICES),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Estado",
    )


class OrderReceiveForm(forms.Form):
    confirmar = forms.BooleanField(
        required=True,
        initial=True,
        widget=forms.HiddenInput(),
    )
from django import forms
from django.forms import inlineformset_factory

from ..models import Order, OrderItem, Location
from suppliers.models import Supplier
from products.models import Product


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        if self.organization:
            self.fields["supplier"].queryset = Supplier.objects.filter(organization=self.organization)
            self.fields["location"].queryset = Location.objects.filter(organization=self.organization)

    class Meta:
        model = Order
        fields = ["supplier", "location", "estimated_arrival", "status"]
        widgets = {
            "supplier": forms.Select(attrs={"class": "form-select select2"}),
            "location": forms.Select(attrs={"class": "form-select select2"}),
            "estimated_arrival": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.organization:
            instance.organization = self.organization
        if commit:
            instance.save()
        return instance


class OrderItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        if self.organization:
            self.fields["product"].queryset = Product.objects.filter(organization=self.organization)

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


class BaseOrderItemFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        for form in self.forms:
            form.organization = self.organization
            if self.organization:
                form.fields["product"].queryset = Product.objects.filter(organization=self.organization)


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    formset=BaseOrderItemFormSet,
    extra=1,
    can_delete=True,
)


class OrderFilterForm(forms.Form):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select select2", "data-placeholder": "Proveedor"}),
    )

    location = forms.ModelChoiceField(
        queryset=Location.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select select2", "data-placeholder": "Almacén"}),
    )

    status = forms.ChoiceField(
        required=False,
        choices=[("", "Estado")] + list(Order.STATUS_CHOICES),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        if organization:
            self.fields["supplier"].queryset = Supplier.objects.filter(organization=organization)
            self.fields["location"].queryset = Location.objects.filter(organization=organization)
from django import forms
from .models import Product
from categories.models import Category
from suppliers.models import Supplier


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        if self.organization:
            self.fields["category"].queryset = Category.objects.filter(organization=self.organization)
            self.fields["supplier"].queryset = Supplier.objects.filter(organization=self.organization)

    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "category",
            "supplier",
            "min_stock",
            "cost_price",
            "sale_price",
            "image",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "sku": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control select2"}),
            "supplier": forms.Select(attrs={"class": "form-control select2"}),
            "min_stock": forms.NumberInput(attrs={"class": "form-control"}),
            "cost_price": forms.NumberInput(attrs={"class": "form-control"}),
            "sale_price": forms.NumberInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_sku(self):
        return self.cleaned_data["sku"].upper()

    def clean_min_stock(self):
        value = self.cleaned_data.get("min_stock")
        if value is not None and value < 0:
            raise forms.ValidationError("El mínimo no puede ser negativo.")
        return value

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.organization:
            instance.organization = self.organization
        if commit:
            instance.save()
        return instance
from django import forms
from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "category",
            "supplier",
            "stock",
            "min_stock",
            "image",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del producto"}),
            "sku": forms.TextInput(attrs={"class": "form-control", "placeholder": "Código SKU"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "supplier": forms.Select(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "min_stock": forms.NumberInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }

    def clean_sku(self):
        sku = self.cleaned_data["sku"].upper()
        return sku
from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ["name", "description", "parent"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de la categoría"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "parent": forms.Select(attrs={"class": "form-control"}),
        }
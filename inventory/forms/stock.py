from django import forms

from products.models import Product
from ..models import StockMovement, Location


class StockMovementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        # 🔥 IN / OUT
        self.fields["movement_type"].choices = [
            ("IN", "Entrada"),
            ("OUT", "Salida"),
        ]

        # 🔥 Campo virtual
        self.fields["location"] = forms.ModelChoiceField(
            queryset=Location.objects.none(),
            required=True,
            label="Almacén",
            widget=forms.Select(attrs={"class": "form-control select2"})
        )

        self.fields.pop("destination", None)
        self.fields.pop("origin", None)

        if self.organization:
            self.fields["product"].queryset = Product.objects.filter(
                organization=self.organization
            )
            self.fields["location"].queryset = Location.objects.filter(
                organization=self.organization
            )

    class Meta:
        model = StockMovement
        fields = ["product", "movement_type", "quantity", "note"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-control select2"}),
            "movement_type": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()

        if self.instance and self.organization:
            self.instance.organization = self.organization

        return cleaned

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor que cero.")
        return qty

    def save(self, commit=True):
        instance = super().save(commit=False)

        location = self.cleaned_data.get("location")

        if instance.movement_type == "IN":
            instance.destination = location
            instance.origin = None

        elif instance.movement_type == "OUT":
            instance.origin = location
            instance.destination = None

        if commit:
            instance.save()

        return instance


# 🔥 NUEVO FORM (EL QUE FALTABA)
class StockMovementFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        self.fields["product"].queryset = Product.objects.none()
        self.fields["location"].queryset = Location.objects.none()

        if self.organization:
            self.fields["product"].queryset = Product.objects.filter(
                organization=self.organization
            )
            self.fields["location"].queryset = Location.objects.filter(
                organization=self.organization
            )

    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control select2"})
    )

    movement_type = forms.ChoiceField(
        required=False,
        choices=[
            ("", "---------"),
            ("IN", "Entrada"),
            ("OUT", "Salida"),
        ],
        widget=forms.Select(attrs={"class": "form-control"})
    )

    location = forms.ModelChoiceField(
        queryset=Location.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control select2"})
    )

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Buscar producto..."})
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
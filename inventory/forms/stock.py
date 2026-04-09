from django import forms

from products.models import Product
from ..models import StockMovement, Location


class StockMovementForm(forms.ModelForm):
    # 🔥 Campo virtual declarado correctamente (fuera de Meta)
    location = forms.ModelChoiceField(
        queryset=Location.objects.none(),
        required=True,
        label="Almacén",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = StockMovement
        fields = ["product", "movement_type", "quantity", "note"]  # ⚠️ NO incluir location

    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        self.fields["movement_type"].choices = [
            ("IN", "Entrada"),
            ("OUT", "Salida"),
        ]

        if self.organization:
            self.fields["product"].queryset = Product.objects.filter(
                organization=self.organization
            )
            self.fields["location"].queryset = Location.objects.filter(
                organization=self.organization
            )

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned = super().clean()

        location = cleaned.get("location")
        movement_type = cleaned.get("movement_type")

        if location and movement_type:
            if movement_type == "IN":
                self.instance.destination = location
                self.instance.origin = None
            elif movement_type == "OUT":
                self.instance.origin = location
                self.instance.destination = None

        if self.organization:
            self.instance.organization = self.organization

        return cleaned

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor que cero.")
        return qty

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

        return instance


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
        widget=forms.Select(attrs={"class": "form-control"})
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
        widget=forms.Select(attrs={"class": "form-control"})
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
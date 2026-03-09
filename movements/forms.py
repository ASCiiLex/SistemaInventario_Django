from django import forms
from .models import Movement

class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ['product', 'movement_type', 'quantity', 'note']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'movement_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
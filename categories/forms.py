from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        if self.organization:
            self.fields["parent"].queryset = Category.objects.filter(organization=self.organization)

    class Meta:
        model = Category
        fields = ["name", "description", "parent"]

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.organization:
            instance.organization = self.organization
        if commit:
            instance.save()
        return instance
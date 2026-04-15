from django import forms


class StockImportForm(forms.Form):
    csv_file = forms.FileField(label="Archivo CSV")

    def clean_csv_file(self):
        file = self.cleaned_data["csv_file"]

        if not file.name.endswith(".csv"):
            raise forms.ValidationError("El archivo debe ser CSV.")

        if file.size > 2 * 1024 * 1024:
            raise forms.ValidationError("El archivo es demasiado grande (max 2MB).")

        return file
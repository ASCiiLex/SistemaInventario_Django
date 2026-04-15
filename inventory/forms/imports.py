from django import forms


class StockImportForm(forms.Form):
    csv_file = forms.FileField(label="Archivo CSV")

    def clean_csv_file(self):
        file = self.cleaned_data["csv_file"]
        if not file.name.endswith(".csv"):
            raise forms.ValidationError("El archivo debe ser CSV.")
        return file
from django import forms


class StockImportForm(forms.Form):
    csv_file = forms.FileField(label="Archivo CSV")
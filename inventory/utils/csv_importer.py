import csv
from io import TextIOWrapper


REQUIRED_HEADERS = {"sku", "name", "location", "stock_current"}


def read_csv(file):
    wrapper = TextIOWrapper(file, encoding="utf-8-sig")
    reader = csv.DictReader(wrapper)

    headers = set(reader.fieldnames or [])

    missing = REQUIRED_HEADERS - headers
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(missing)}")

    return list(reader)
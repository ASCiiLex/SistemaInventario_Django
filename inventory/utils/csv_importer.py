import csv
from io import TextIOWrapper

def read_csv(file):
    wrapper = TextIOWrapper(file, encoding="utf-8")
    reader = csv.DictReader(wrapper)
    return list(reader)
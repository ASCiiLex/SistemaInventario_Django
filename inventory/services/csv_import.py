from django.db import transaction
from django.core.exceptions import ValidationError

from products.models import Product
from inventory.models import StockItem, Location


REQUIRED_FIELDS = ["product_code", "location_code", "quantity"]


def validate_row(row, organization):
    errors = []

    # Campos requeridos
    for field in REQUIRED_FIELDS:
        if not row.get(field):
            errors.append(f"Falta campo: {field}")

    if errors:
        return None, errors

    product_code = row.get("product_code")
    location_code = row.get("location_code")

    # Validación quantity
    try:
        quantity = int(row.get("quantity", 0))
        if quantity < 0:
            errors.append("Cantidad negativa")
    except Exception:
        errors.append("Cantidad inválida")
        quantity = 0

    # Validación product
    try:
        product = Product.objects.get(
            sku=product_code,
            organization=organization
        )
    except Product.DoesNotExist:
        errors.append(f"Producto no encontrado: {product_code}")
        product = None

    # Validación location
    try:
        location = Location.objects.get(
            code=location_code,
            organization=organization
        )
    except Location.DoesNotExist:
        errors.append(f"Ubicación no encontrada: {location_code}")
        location = None

    if errors:
        return None, errors

    return {
        "product": product,
        "location": location,
        "quantity": quantity,
    }, []


def validate_rows(rows, organization):
    validated = []
    errors = []

    for idx, row in enumerate(rows, start=1):
        data, row_errors = validate_row(row, organization)

        if row_errors:
            errors.append({
                "row": idx,
                "errors": row_errors,
                "data": row
            })
        else:
            validated.append(data)

    return validated, errors


def execute_import(validated_rows, organization):
    """
    🔥 IMPORT ATÓMICO
    """
    processed = 0

    with transaction.atomic():
        for item in validated_rows:
            stock_item, created = StockItem.objects.get_or_create(
                product=item["product"],
                location=item["location"],
                organization=organization,
                defaults={"quantity": item["quantity"]},
            )

            if not created:
                stock_item.quantity = item["quantity"]
                stock_item.save(update_fields=["quantity"])

            processed += 1

    return processed
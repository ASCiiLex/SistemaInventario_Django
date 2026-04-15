from dataclasses import dataclass
from typing import List, Dict, Any

from django.db import transaction

from products.models import Product
from inventory.models import Location, StockMovement


@dataclass
class NormalizedRow:
    sku: str
    name: str
    location: Location
    stock_min: int
    stock_current: int


class CSVImportValidator:

    REQUIRED_FIELDS = ["sku", "name", "location", "stock_current"]

    def __init__(self, organization):
        self.organization = organization
        self._location_cache = {}

    def _get_location(self, name: str):
        if name in self._location_cache:
            return self._location_cache[name]

        location = Location.objects.filter(
            name=name,
            organization=self.organization
        ).first()

        self._location_cache[name] = location
        return location

    def validate_row(self, row: Dict[str, Any], index: int):
        errors = []

        for field in self.REQUIRED_FIELDS:
            if not row.get(field):
                errors.append(f"Falta campo: {field}")

        if errors:
            return None, errors

        try:
            stock_current = int(row.get("stock_current", 0))
            if stock_current < 0:
                errors.append("Stock negativo")
        except Exception:
            errors.append("Stock inválido")
            stock_current = 0

        try:
            stock_min = int(row.get("stock_min", 0))
            if stock_min < 0:
                errors.append("Stock mínimo negativo")
        except Exception:
            stock_min = 0

        location_name = row["location"]
        location = self._get_location(location_name)

        if not location:
            errors.append(f"Ubicación no existe: {location_name}")

        if errors:
            return None, errors

        return NormalizedRow(
            sku=row["sku"],
            name=row["name"],
            location=location,
            stock_min=stock_min,
            stock_current=stock_current,
        ), []

    def validate(self, rows: List[Dict[str, Any]]):
        validated = []
        errors = []

        seen = set()

        for idx, row in enumerate(rows, start=1):
            normalized, row_errors = self.validate_row(row, idx)

            if row_errors:
                errors.append({
                    "row": idx,
                    "errors": row_errors,
                    "data": row
                })
                continue

            key = (normalized.sku, normalized.location.id)
            if key in seen:
                errors.append({
                    "row": idx,
                    "errors": ["Duplicado en CSV"],
                    "data": row
                })
                continue

            seen.add(key)
            validated.append(normalized)

        return validated, errors


class CSVImportExecutor:

    def __init__(self, organization, user):
        self.organization = organization
        self.user = user

    def _generate_idempotency_key(self, row: NormalizedRow):
        return f"csv:{self.organization.id}:{row.sku}:{row.location.id}:{row.stock_current}"

    def _upsert_product(self, row: NormalizedRow):
        product, _ = Product.objects.update_or_create(
            sku=row.sku,
            organization=self.organization,
            defaults={
                "name": row.name,
                "min_stock": row.stock_min,
            }
        )
        return product

    def _apply_stock(self, product, location, target_quantity, row: NormalizedRow):
        from inventory.models import StockItem

        stock = StockItem.objects.filter(
            product=product,
            location=location,
            organization=self.organization
        ).first()

        current = stock.quantity if stock else 0
        delta = target_quantity - current

        if delta == 0:
            return {
                "action": "noop",
                "delta": 0
            }

        idempotency_key = self._generate_idempotency_key(row)

        if delta > 0:
            movement = StockMovement(
                organization=self.organization,
                product=product,
                movement_type="IN",
                source_type="manual",
                destination=location,
                quantity=delta,
                note="CSV import adjustment",
                idempotency_key=idempotency_key
            )
        else:
            movement = StockMovement(
                organization=self.organization,
                product=product,
                movement_type="OUT",
                source_type="manual",
                origin=location,
                quantity=abs(delta),
                note="CSV import adjustment",
                idempotency_key=idempotency_key
            )

        movement.save()

        return {
            "action": "adjust",
            "delta": delta
        }

    @transaction.atomic
    def execute(self, rows: List[NormalizedRow]):
        processed = 0
        report = []

        for row in rows:
            product = self._upsert_product(row)
            result = self._apply_stock(product, row.location, row.stock_current, row)

            report.append({
                "sku": row.sku,
                "location": row.location.name,
                "action": result["action"],
                "delta": result["delta"]
            })

            processed += 1

        return processed, report
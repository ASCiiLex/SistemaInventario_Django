from django.http import HttpResponse
import csv

from products.models import Product
from accounts.permissions import can_export_products
from accounts.decorators import permission_required_custom


@permission_required_custom(can_export_products)
def export_products_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=productos.csv"

    writer = csv.writer(response)
    writer.writerow([
        "Nombre",
        "SKU",
        "Categoría",
        "Proveedor",
        "Stock",
        "Mínimo",
        "Coste",
        "Precio venta",
        "Margen",
        "Valor inventario",
    ])

    products = Product.objects.select_related("category", "supplier").filter(
        organization=request.organization
    )

    for p in products:
        writer.writerow([
            p.name,
            p.sku,
            p.category.name if p.category else "",
            p.supplier.name if p.supplier else "",
            p.total_stock,
            p.total_min_stock,
            f"{p.cost_price:.2f}",
            f"{p.sale_price:.2f}",
            f"{p.margin:.2f}",
            f"{p.inventory_value:.2f}",
        ])

    return response
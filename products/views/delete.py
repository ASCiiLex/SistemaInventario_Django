from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from products.models import Product
from accounts.permissions import can_delete_products
from accounts.decorators import permission_required_custom


@permission_required_custom(can_delete_products)
def product_delete(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        organization=request.organization
    )
    product.delete()
    return redirect(reverse("product_list"))
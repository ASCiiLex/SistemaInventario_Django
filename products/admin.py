from django.contrib import admin
from django.utils.html import format_html
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'sku',
        'category',
        'supplier',
        'total_stock',
        'total_min_stock',
        'cost_price',
        'sale_price',
        'margin_display',
        'inventory_value_display',
        'below_minimum',
        'image_tag',
    )
    search_fields = ('name', 'sku')
    list_filter = ('category', 'supplier')

    def below_minimum(self, obj):
        return "⚠️ Sí" if obj.is_below_minimum else "No"
    below_minimum.short_description = "Bajo mínimo"

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="40" height="40"/>', obj.image.url)
        return "-"

    def margin_display(self, obj):
        return f"{obj.margin:.2f}"
    margin_display.short_description = "Margen"

    def inventory_value_display(self, obj):
        return f"{obj.inventory_value:.2f}"
    inventory_value_display.short_description = "Valor inventario"
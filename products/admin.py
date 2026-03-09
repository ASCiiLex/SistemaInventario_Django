from django.contrib import admin
from django.utils.html import format_html
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'supplier', 'stock', 'min_stock', 'below_minimum', 'image_tag')
    search_fields = ('name', 'sku')
    list_filter = ('category', 'supplier')

    def below_minimum(self, obj):
        return "⚠️ Sí" if obj.is_below_minimum else "No"
    below_minimum.short_description = "Bajo mínimo"

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="40" height="40"/>', obj.image.url)
        return "-"
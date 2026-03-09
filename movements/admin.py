from django.contrib import admin
from .models import Movement

@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'created_at')
    list_filter = ('movement_type', 'created_at')
    search_fields = ('product__name', 'product__sku')
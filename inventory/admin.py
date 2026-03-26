from django.contrib import admin
from .models import Location, StockItem, StockMovement, Order, OrderItem


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "is_active")
    search_fields = ("name",)
    list_per_page = 20


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("product", "location", "quantity", "is_below_minimum")
    list_filter = ("location", "product")
    search_fields = ("product__name", "location__name")
    list_per_page = 20


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "movement_type", "origin", "destination", "quantity", "created_at")
    list_filter = ("movement_type", "origin", "destination")
    search_fields = ("product__name",)
    list_per_page = 20


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "supplier", "location", "status", "created_at", "estimated_arrival")
    list_filter = ("status", "supplier", "location")
    inlines = [OrderItemInline]
    list_per_page = 20
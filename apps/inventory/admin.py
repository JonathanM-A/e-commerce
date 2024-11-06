from django.contrib import admin
from .models import (
    InventoryItem,FacilityInventory, Transfer, TransferDetails,
    WarehouseInventory, Inbound, InboundDetails)

# Register your models here.
admin.site.register(TransferDetails)

from django.contrib import admin
from .models import Transfer, TransferDetails


class InventoryItemInline(admin.TabularInline):
    model = InventoryItem
    extra = 0
    readonly_fields = (
        "product_id",
        "product_name",
        "cost_price_pack",
        "selling_price_pack",
    )


# @admin.register(FacilityInventory)
# class FacilityInventoryAdmin(admin.ModelAdmin):
#     list_display = ("facility", "inventory_item", "quantity")
#     inlines = [InventoryItemInline]


class TransferDetailsInline(admin.TabularInline):
    model = TransferDetails
    extra = 0
    readonly_fields = (
        "inventory_item",
        "quantity",
    )


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("transfer_id", "source", "destination", "transfer_date", "status")
    inlines = [TransferDetailsInline]


class WarehouseInventoryInline(admin.TabularInline):
    model = WarehouseInventory
    extra = 0
    readonly_fields = (
        "inventory_item",
        "quantity",
        "batch_no",
        "expiry_date",
    )
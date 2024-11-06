from rest_framework import serializers
from .models import (
    InventoryItem,
    FacilityInventory,
    TransferDetails,
    Transfer,
    WarehouseInventory,
    Inbound,
    InboundDetails
)


class InventoryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = ["product_id", "product_name", "cost_price_pack", "selling_price_pack"]


class WarehouseInventorySerializer:
    inventory_item = InventoryItemSerializer()

    class Meta:
        model = WarehouseInventory
        fields = ["inventory_item", "quantity", "batch_no", "expiry_date"]


class FacilityInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityInventory
        fields = ["facility", "inventory_item", "quantity"]


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ["transfer_id", "source", "destination", "transfer_date", "status"]


class TransferDetailsSerializer(serializers.ModelSerializer):
    inventory_item = InventoryItemSerializer()

    class Meta:
        model = TransferDetails
        fields = ["transfer_id", "inventory_item"]


class InboundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inbound
        fields = ["inbound_id", "supplier", "invoice_no", "invoice_date"]


class InboundDetailsSerializer(serializers.ModelSerializer):
    warehouse_item = WarehouseInventorySerializer()

    class Meta:
        model = InboundDetails
        fields = ["inbound_id", "warehouse_item", "quantity"]

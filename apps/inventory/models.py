from django.db import models
from django.utils import timezone
from rest_framework.serializers import ValidationError


class InventoryItem(models.Model):
    """
    List of items in the company inventory
    """
    product_id = models.CharField(max_length=5, unique=True)
    generic_name = models.CharField(max_length=255)
    brand_name = models.CharField(max_length=255, null=True)
    strength = models.CharField(max_length=255, null=False)
    product_form = models.CharField(max_length=100, null=False)
    cost_price_pack = models.DecimalField(max_digits=7, decimal_places=2)
    selling_price_pack = models.DecimalField(max_digits=7, decimal_places=2)
    pack_size = models.IntegerField()

    class Meta:
        unique_together = ["generic_name", "brand_name", "strength", "product_form"]

    def __str__(self):
        return self.product_name

    @property
    def product_name(self):
        parts = [self.generic_name]
        if self.brand_name:
            parts.append(f"({self.brand_name})")
        parts.append(self.strength)
        parts.append(self.product_form.title())
        parts.append(f"x{self.pack_size}")
        return " ".join(parts)

    @property
    def uint_selling_price(self):
        return round((self.selling_price_pack / self.quantity), 2)

    def save(self, *args, **kwargs):
        # Read on SKUs to generate a more meaningful product ID
        if not self.product_id:
            last_item = InventoryItem.objects.order_by("-product_id").first()
            if not last_item:
                new_id = 1
            else:
                new_id = int(last_item.product_id) + 1
            self.product_id = f"{new_id:05}"
        super().save(*args, **kwargs)


# IDEA
# preload facility inventory with all items in main inventory
# then transfers will be made for required quantities
class FacilityInventory(models.Model):
    """
    Inventory of items in a facility
    """
    facility = models.ForeignKey("facilities.Facility", on_delete=models.CASCADE)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    class Meta:
        db_table = "facility_inventory"
        unique_together = ["facility", "inventory_item"]


class WarehouseInventory(models.Model):
    """
    Inventory of items in the warehouse
    """
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=5, editable=False)
    batch_no = models.CharField(max_length=20)
    expiry_date = models.DateField()
    quantity = models.IntegerField(default=0)

    class Meta:
        db_table = "warehouse"
        unique_together = ["inventory_item", "batch_no"]

    # Ensure batch number always have the same expiry date
    def save(self, *args, **kwargs):
        if self.inventory_item:
            self.product_id = self.inventory_item.product_id
        existing_record = (
            WarehouseInventory.objects.filter(
                inventory_item=self.inventory_item, batch_no=self.batch_no
            )
            .exclude(id=self.id)
            .first()
        )

        if existing_record and existing_record.expiry_date != self.expiry_date:
            raise ValidationError(
                f"The batch number '{self.batch_no}' for item '{self.inventory_item}' "
                f"must have the expiry date '{existing_record.expiry_date}'"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.inventory_item}, Quantity: {self.quantity}, Batch No.: {self.batch_no}, "
            f"Expiry: {self.expiry_date}"
        )


class Transfer(models.Model):
    """
    Record of Inventory transfer between facilities
    """
    STATUS_PENDING = "Pending"
    STATUS_IN_PROGRESS = "In progress"
    STATUS_COMPLETED = "Completed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
    ]

    transfer_id = models.CharField(max_length=5, primary_key=True, editable=False)
    source = models.ForeignKey(
        "facilities.Facility", on_delete=models.CASCADE, related_name="transfers_source"
    )
    destination = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.CASCADE,
        related_name="transfers_destination",
    )
    transfer_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(default=STATUS_PENDING, choices=STATUS_CHOICES)

    class Meta:
        db_table = "transfers"

    def __str__(self):
        return f"ID: {self.transfer_id}, From: {self.source.name}, Date: {self.transfer_date.date()}"

    def save(self, *args, **kwargs):
        if not self.transfer_id:
            last_transfer = Transfer.objects.order_by("-transfer_id").first()
            if last_transfer:
                new_id = int(last_transfer.transfer_id) + 1
            else:
                new_id = 1
            self.transfer_id = f"{new_id:05}"
        super().save(*args, **kwargs)


class TransferDetails(models.Model):
    """
    Details of inventory transfer between facilities
    """
    transfer_id = models.ForeignKey(
        Transfer, on_delete=models.CASCADE, related_name="details"
    )
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        db_table = "transfer_details"


class Inbound(models.Model):
    """
    Record of products received from suppliers
    """
    inbound_id = models.CharField(max_length=5, primary_key=True)
    supplier = models.CharField(max_length=255)
    invoice_no = models.CharField(max_length=20)
    invoice_date = models.DateField()
    inbound_date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "warehouse_inbound"

    def save(self, *args, **kwargs):
        if not self.inbound_id:
            last_inbound = Inbound.objects.order_by("-inbound_id").first()
            if last_inbound:
                new_id = int(last_inbound.inbound_id) + 1
            else:
                new_id =  1
            self.inbound_id = f"{new_id:05}"
        super().save(*args, **kwargs)


class InboundDetails(models.Model):
    """
    Details of products received from suppliers
    """
    inbound_id = models.ForeignKey(Inbound, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=5, editable=False)
    warehouse_item = models.ForeignKey(WarehouseInventory, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def save(self, *args, **kwargs):
        self.product_id = self.warehouse_item.product_id
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = "warehouse_inbound_details"

 
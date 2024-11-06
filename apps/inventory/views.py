from django.db import transaction
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    InventoryItemSerializer,
    FacilityInventorySerializer,
    TransferDetailsSerializer,
    TransferSerializer,
    WarehouseInventorySerializer,
    InboundDetailsSerializer,
    InboundSerializer
)
from .models import (
    InventoryItem,
    FacilityInventory,
    Transfer,
    TransferDetails,
    WarehouseInventory,
    Inbound, InboundDetails
)
from apps.users.permissions import IsSuperUser, IsWarehouse, IsAdminUser
from apps.facilities.models import Facility


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsSuperUser]

    filterset_fields = ["generic_name", "brand_name"]
    search_fields = ["generic_name", "brand_name"]


class WarehouseInventoryViewSet(viewsets.ModelViewSet):
    queryset = WarehouseInventory.objects.all()
    serializer_class = WarehouseInventorySerializer
    permission_classes = [IsWarehouse]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.has_perm("IsWarehouse"):
            return self.queryset
        return WarehouseInventory.objects.none()
    
    @action(
            detail=False, methods=["POST"], permission_classes=[IsWarehouse | IsSuperUser])
    def inbound(self, request):
        supplier = request.data.get("supplier")
        invoice_no = request.data.get("invoice_no")
        invoice_date = request.data.get("invoice_date")
        items = request.data.get("items")

        if not any([supplier, invoice_no, invoice_date]):
            raise ValidationError(
                "'Supplier', 'Invoice Number' and 'Invoice Date' are required")

        if not items or not isinstance(items, list):
            raise ValidationError("A valid list of inventory items must be provided")
        
        with transaction.atomic():
            inbound = Inbound.objects.create(
                supplier = supplier,
                invoice_no = invoice_no,
                invoice_date = invoice_date
            )
            for item in items:
                product_id = item.get("product_id")
                batch_no = item.get("batch_no")
                expiry_date = item.get("expiry_date")
                quantity = int(item.get("quantity"))

                if not all([product_id, batch_no, expiry_date, quantity]):
                    raise ValidationError(
                        "Each item must have a 'product id', 'batch no', 'expiry date' and 'quantity'."
                    )
                
                inventory_item = get_object_or_404(InventoryItem, product_id=product_id)

                warehouse_item, created = WarehouseInventory.objects.get_or_create(
                    inventory_item = inventory_item,
                    batch_no = batch_no,
                    expiry_date = expiry_date
                )
                warehouse_item.quantity = F("quantity") + quantity
                warehouse_item.save()

                InboundDetails.objects.create(
                    inbound_id = inbound,
                    warehouse_item = warehouse_item,
                    quantity = quantity
                )
        return Response("Inbound successful.", status=201)

    # IDEA
    # Consider adding batch_no so facilities can track expiries
    @action(
        detail=False, methods=["POST"], permission_classes=[IsWarehouse | IsSuperUser])
    def supply(self, request):
        destination_id = request.data.get("facility")
        items = request.data.get("items")

        destination = get_object_or_404(Facility, id = destination_id)

        if not items or not isinstance(items, list):
            raise ValidationError("A valid list of inventory items must be provided")

        with transaction.atomic():
            transfer = Transfer.objects.create(
                source=request.user.facility, destination=destination
            )
            for item in items:
                product_id = item.get("product_id")
                quantity = int(item.get("quantity"))

                if product_id is None or quantity is None:
                    raise ValidationError(
                        "Each item must have a 'product_id' and 'quantity'."
                    )

                inventory_item = get_object_or_404(InventoryItem, product_id = product_id)

                warehouse_item = get_object_or_404(
                    WarehouseInventory, inventory_item=inventory_item.id,
                )
                # quantity__gte=quantity may work above in place of statement below

                if warehouse_item.quantity < quantity:
                    raise ValidationError(
                        f"Insufficient stock. {warehouse_item.quantity} packs available."
                    )

                facility_item, created = FacilityInventory.objects.get_or_create(
                    facility = destination,
                    inventory_item = inventory_item.id,
                )
                # use F() to avoid race conditions
                facility_item.quantity = F("quantity") + quantity
                warehouse_item.quantity = F("quantity") - quantity
                facility_item.save()
                warehouse_item.save()

                TransferDetails.objects.create(
                    transfer_id = transfer,
                    inventory_item = inventory_item,
                    quantity = quantity
                )

        return Response("Transfer successful", status=200)


class FacilityInventoryViewSet(viewsets.ModelViewSet):
    queryset = FacilityInventory.objects.all()
    serializer_class = FacilityInventorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsSuperUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return FacilityInventory.objects.filter(
            Q(facility=user.facility)
        )
    # add a view to allow stock transfer between facilities
    
    @action(detail=False, methods=["POST"], permission_classes=[IsAdminUser|IsSuperUser])
    def transfer(self, request):
        destination_id = request.data.get("facility")
        items = request.data.get("items")

        destination = get_object_or_404(Facility, id = destination_id)

        if not items or not isinstance(items, list):
            raise ValidationError("A valid list of inventory items must be provided")
        
        with transaction.atomic():
            transfer = Transfer.objects.create(
                source=request.user.facility, destination=destination
            )
            for item in items:
                product_id = item.get("product_id")
                quantity = int(item.get("quantity"))

                if product_id is None or quantity is None:
                    raise ValidationError(
                        "Each item must have a 'product_id' and 'quantity'."
                    )

                inventory_item = get_object_or_404(InventoryItem, product_id = product_id)

                facility_item = get_object_or_404(
                    FacilityInventory, facility=request.user.facility, inventory_item=inventory_item.id
                )

                if facility_item.quantity < quantity:
                    raise ValidationError(
                        f"Insufficient stock. {facility_item.quantity} packs available."
                    )

                destination_item, created = FacilityInventory.objects.get_or_create(
                    facility = destination,
                    inventory_item = inventory_item.id
                )
                destination_item.quantity = F("quantity") + quantity
                facility_item.quantity = F("quantity") - quantity
                destination_item.save()
                facility_item.save()

                TransferDetails.objects.create(
                    transfer_id = transfer,
                    inventory_item = inventory_item,
                    quantity = quantity
                )
        
        return Response("Transfer successful", status=200)


class TransferViewSet(viewsets.ModelViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return Transfer.objects.filter(
            Q(destination = user.facility) | Q(source = user.facility)
        )

    def get_permissions(self):
        if self.request.user.is_superuser:
            return super().get_permissions()
        if self.action == "partial_update":
            permission_classes = [IsAdminUser]
        elif self.action == "retrieve":
            permission_classes = [IsAuthenticated | IsAdminUser]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        transfer = self.get_object()
        transfer_details = TransferDetails.objects.filter(transfer_id=transfer)
        serializer = TransferDetailsSerializer(transfer_details, many=True)
        return Response(serializer.data, status=200)

    @action(detail=True, methods=["PATCH"], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        user = request.user
        transfer = self.get_object()
        if request.user.facility != transfer.destination:
            return Response("Not authorized")
        new_status = request.data.get("status")

        valid_status = [choice[0] for choice in TransferHistory.STATUS_CHOICES]
        if new_status not in valid_status:
            raise ValidationError("Invalid status")

        transfer.status = new_status
        transfer.save()

        return Response("Status updated succesfully", status=200)


class InboundViewSet(viewsets.ModelViewSet):
    queryset = Inbound.objects.all()
    serializer_class = InboundSerializer
    permission_classes = [IsSuperUser]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsWarehouse|IsSuperUser]
        return [permission() for permission in permission_classes]
    
    def retrieve(self, request, *args, **kwargs):
        inbound = self.get_object()
        inbound_details = InboundDetails.objects.filter(inbound_id=inbound)
        serializer = InboundDetailsSerializer(inbound_details, many=True)
        return Response(serializer.data, status=200)

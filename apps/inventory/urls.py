from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InventoryItemViewSet,
    FacilityInventoryViewSet,
    TransferViewSet,
    WarehouseInventoryViewSet,
    InboundViewSet,
)

router = DefaultRouter()
router.register(r"inventory", InventoryItemViewSet)
router.register(r"facility-inventory", FacilityInventoryViewSet)
router.register(r"transfer", TransferViewSet, basename="transfer")
router.register(r"warehouse", WarehouseInventoryViewSet)
router.register(r"inbound", InboundViewSet)

app_name = "inventory"
urlpatterns = [
    path("", include(router.urls)),
]

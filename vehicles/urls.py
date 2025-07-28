from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    dashboard, VehicleViewSet, TripViewSet, FuelRecordViewSet,
    ServiceRecordViewSet, TrackingDeviceViewSet
)

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet)
router.register(r'trips', TripViewSet)
router.register(r'fuel-records', FuelRecordViewSet)
router.register(r'service-records', ServiceRecordViewSet)
router.register(r'tracking-devices', TrackingDeviceViewSet)

app_name = 'vehicles'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('api/', include(router.urls)),
]
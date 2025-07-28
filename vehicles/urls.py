from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    dashboard, vehicles_list, trips_list, VehicleViewSet, TripViewSet, FuelRecordViewSet,
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
    path('vehicles/', vehicles_list, name='list'),
    path('trips/', trips_list, name='trips_list'),
    path('api/', include(router.urls)),
]
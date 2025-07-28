from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Vehicle, TrackingDevice, Trip, FuelRecord, ServiceRecord

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'user_type']


class TrackingDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingDevice
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    tracking_device = TrackingDeviceSerializer(read_only=True)
    assigned_driver = UserSerializer(read_only=True)
    assigned_driver_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Vehicle
        fields = '__all__'
    
    def validate_assigned_driver_id(self, value):
        if value:
            try:
                user = User.objects.get(id=value, user_type='driver')
                return value
            except User.DoesNotExist:
                raise serializers.ValidationError("Motorista não encontrado ou usuário não é motorista.")
        return value


class TripSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    driver = UserSerializer(read_only=True)
    vehicle_id = serializers.IntegerField(write_only=True)
    driver_id = serializers.IntegerField(write_only=True)
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = Trip
        fields = '__all__'
    
    def validate_vehicle_id(self, value):
        try:
            Vehicle.objects.get(id=value)
            return value
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError("Veículo não encontrado.")
    
    def validate_driver_id(self, value):
        try:
            User.objects.get(id=value, user_type='driver')
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Motorista não encontrado.")


class FuelRecordSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    vehicle_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FuelRecord
        fields = '__all__'
    
    def validate_vehicle_id(self, value):
        try:
            Vehicle.objects.get(id=value)
            return value
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError("Veículo não encontrado.")


class ServiceRecordSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    vehicle_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ServiceRecord
        fields = '__all__'
    
    def validate_vehicle_id(self, value):
        try:
            Vehicle.objects.get(id=value)
            return value
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError("Veículo não encontrado.")


class VehicleSummarySerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagens"""
    assigned_driver_name = serializers.CharField(source='assigned_driver.get_full_name', read_only=True)
    last_location = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = ['id', 'plate', 'brand', 'model', 'year', 'status', 'assigned_driver_name', 'last_location']
    
    def get_last_location(self, obj):
        if hasattr(obj, 'tracking_device') and obj.tracking_device:
            last_location = obj.tracking_device.location_data.first()
            if last_location:
                return {
                    'latitude': float(last_location.latitude),
                    'longitude': float(last_location.longitude),
                    'timestamp': last_location.timestamp
                }
        return None
from django.contrib import admin
from .models import LocationData, GeofenceArea, GeofenceAlert, SpeedAlert, MaintenanceAlert


@admin.register(LocationData)
class LocationDataAdmin(admin.ModelAdmin):
    list_display = ('device', 'timestamp', 'latitude', 'longitude', 'speed', 'ignition')
    list_filter = ('device', 'timestamp', 'ignition', 'engine_running')
    search_fields = ('device__vehicle__plate', 'device__device_id')
    ordering = ('-timestamp',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Localização', {
            'fields': ('device', 'timestamp', 'latitude', 'longitude', 'altitude', 'accuracy')
        }),
        ('Movimento', {
            'fields': ('speed', 'heading')
        }),
        ('Status do Veículo', {
            'fields': ('ignition', 'engine_running', 'fuel_level', 'battery_voltage', 'temperature', 'odometer')
        }),
    )


@admin.register(GeofenceArea)
class GeofenceAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'area_type', 'is_active', 'created_at')
    list_filter = ('area_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    filter_horizontal = ('vehicles',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'area_type', 'description', 'is_active')
        }),
        ('Coordenadas', {
            'fields': ('coordinates', 'radius')
        }),
        ('Veículos Monitorados', {
            'fields': ('vehicles',)
        }),
    )


@admin.register(GeofenceAlert)
class GeofenceAlertAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'geofence_area', 'alert_type', 'status', 'created_at')
    list_filter = ('alert_type', 'status', 'created_at', 'geofence_area__area_type')
    search_fields = ('vehicle__plate', 'geofence_area__name', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def save_model(self, request, obj, form, change):
        if obj.status == 'acknowledged' and not obj.acknowledged_by:
            obj.acknowledged_by = request.user
            from django.utils import timezone
            obj.acknowledged_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(SpeedAlert)
class SpeedAlertAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'actual_speed', 'speed_limit', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('vehicle__plate',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def save_model(self, request, obj, form, change):
        if obj.status == 'acknowledged' and not obj.acknowledged_by:
            obj.acknowledged_by = request.user
            from django.utils import timezone
            obj.acknowledged_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(MaintenanceAlert)
class MaintenanceAlertAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'title', 'alert_type', 'priority', 'status', 'due_date', 'created_at')
    list_filter = ('alert_type', 'priority', 'status', 'created_at', 'due_date')
    search_fields = ('vehicle__plate', 'title', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('vehicle', 'alert_type', 'title', 'description')
        }),
        ('Prioridade e Status', {
            'fields': ('priority', 'status', 'due_date')
        }),
        ('Reconhecimento', {
            'fields': ('acknowledged_by', 'acknowledged_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if obj.status == 'acknowledged' and not obj.acknowledged_by:
            obj.acknowledged_by = request.user
            from django.utils import timezone
            obj.acknowledged_at = timezone.now()
        super().save_model(request, obj, form, change)

from django.contrib import admin
from .models import Vehicle, TrackingDevice, Trip, FuelRecord, ServiceRecord


class TrackingDeviceInline(admin.StackedInline):
    model = TrackingDevice
    extra = 0
    max_num = 1


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate', 'brand', 'model', 'year', 'status', 'assigned_driver', 'created_at')
    list_filter = ('status', 'fuel_type', 'brand', 'year')
    search_fields = ('plate', 'brand', 'model')
    ordering = ('plate',)
    inlines = [TrackingDeviceInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('plate', 'brand', 'model', 'year', 'color')
        }),
        ('Especificações', {
            'fields': ('fuel_type', 'fuel_capacity')
        }),
        ('Status e Atribuição', {
            'fields': ('status', 'assigned_driver')
        }),
    )


@admin.register(TrackingDevice)
class TrackingDeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'vehicle', 'device_type', 'status', 'last_communication')
    list_filter = ('device_type', 'status')
    search_fields = ('device_id', 'imei', 'vehicle__plate')
    ordering = ('device_id',)


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'driver', 'origin', 'destination', 'status', 'planned_start_time')
    list_filter = ('status', 'planned_start_time', 'vehicle')
    search_fields = ('vehicle__plate', 'driver__username', 'origin', 'destination')
    ordering = ('-planned_start_time',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('vehicle', 'driver', 'origin', 'destination', 'purpose')
        }),
        ('Horários Planejados', {
            'fields': ('planned_start_time', 'planned_end_time')
        }),
        ('Horários Reais', {
            'fields': ('actual_start_time', 'actual_end_time')
        }),
        ('Dados da Viagem', {
            'fields': ('status', 'distance_km', 'fuel_consumed', 'notes')
        }),
    )


@admin.register(FuelRecord)
class FuelRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'date', 'quantity', 'cost', 'fuel_station', 'created_by')
    list_filter = ('date', 'vehicle', 'fuel_station')
    search_fields = ('vehicle__plate', 'fuel_station')
    ordering = ('-date',)
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo registro
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ServiceRecord)
class ServiceRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'service_type', 'date', 'cost', 'service_provider', 'created_by')
    list_filter = ('service_type', 'date', 'vehicle')
    search_fields = ('vehicle__plate', 'service_provider', 'description')
    ordering = ('-date',)
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo registro
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

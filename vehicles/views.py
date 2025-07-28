from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from .models import Vehicle, TrackingDevice, Trip, FuelRecord, ServiceRecord
from .serializers import (
    VehicleSerializer, VehicleSummarySerializer, TrackingDeviceSerializer,
    TripSerializer, FuelRecordSerializer, ServiceRecordSerializer
)

User = get_user_model()


@login_required
def dashboard(request):
    """Dashboard principal do sistema"""
    user = request.user
    
    # Filtrar dados baseado no tipo de usuário
    if user.user_type == 'driver':
        vehicles = Vehicle.objects.filter(assigned_driver=user)
        trips = Trip.objects.filter(driver=user)
    else:
        vehicles = Vehicle.objects.all()
        trips = Trip.objects.all()
    
    # Estatísticas gerais
    stats = {
        'total_vehicles': vehicles.count(),
        'active_vehicles': vehicles.filter(status='active').count(),
        'total_trips': trips.count(),
        'active_trips': trips.filter(status='in_progress').count(),
        'total_drivers': User.objects.filter(user_type='driver').count() if user.can_manage_users() else 0,
        'fuel_records': FuelRecord.objects.filter(vehicle__in=vehicles).count(),
    }
    
    # Viagens recentes
    recent_trips = trips.select_related('vehicle', 'driver').order_by('-created_at')[:5]
    
    # Alertas (placeholder - implementar quando o sistema de alertas estiver pronto)
    alerts = {
        'maintenance': 0,
        'fuel_low': 0,
        'speed_violations': 0,
    }
    
    context = {
        'stats': stats,
        'recent_trips': recent_trips,
        'alerts': alerts,
        'user': user,
    }
    
    return render(request, 'vehicles/dashboard.html', context)


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Vehicle.objects.all()
        user = self.request.user
        
        # Filtros baseados no tipo de usuário
        if user.user_type == 'driver':
            queryset = queryset.filter(assigned_driver=user)
        
        # Filtros por parâmetros de query
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        brand_filter = self.request.query_params.get('brand')
        if brand_filter:
            queryset = queryset.filter(brand__icontains=brand_filter)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(plate__icontains=search) |
                Q(brand__icontains=search) |
                Q(model__icontains=search)
            )
        
        return queryset.select_related('assigned_driver', 'tracking_device')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VehicleSummarySerializer
        return VehicleSerializer
    
    @action(detail=True, methods=['get'])
    def location_history(self, request, pk=None):
        """Retorna histórico de localização do veículo"""
        vehicle = self.get_object()
        
        if not hasattr(vehicle, 'tracking_device'):
            return Response(
                {'error': 'Veículo não possui dispositivo de rastreamento'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Parâmetros de data
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        from tracking.models import LocationData
        locations = LocationData.objects.filter(device=vehicle.tracking_device)
        
        if from_date:
            locations = locations.filter(timestamp__gte=from_date)
        if to_date:
            locations = locations.filter(timestamp__lte=to_date)
        
        locations = locations.order_by('-timestamp')[:100]  # Limita a 100 registros
        
        data = []
        for location in locations:
            data.append({
                'latitude': float(location.latitude),
                'longitude': float(location.longitude),
                'speed': location.speed,
                'timestamp': location.timestamp,
                'ignition': location.ignition
            })
        
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def current_location(self, request, pk=None):
        """Retorna localização atual do veículo"""
        vehicle = self.get_object()
        
        if not hasattr(vehicle, 'tracking_device'):
            return Response(
                {'error': 'Veículo não possui dispositivo de rastreamento'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from tracking.models import LocationData
        last_location = LocationData.objects.filter(
            device=vehicle.tracking_device
        ).order_by('-timestamp').first()
        
        if not last_location:
            return Response(
                {'error': 'Nenhuma localização encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = {
            'latitude': float(last_location.latitude),
            'longitude': float(last_location.longitude),
            'speed': last_location.speed,
            'timestamp': last_location.timestamp,
            'ignition': last_location.ignition,
            'fuel_level': last_location.fuel_level,
            'battery_voltage': last_location.battery_voltage
        }
        
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def trips(self, request, pk=None):
        """Retorna viagens do veículo"""
        vehicle = self.get_object()
        trips = Trip.objects.filter(vehicle=vehicle).order_by('-planned_start_time')
        
        # Filtro por status
        status_filter = request.query_params.get('status')
        if status_filter:
            trips = trips.filter(status=status_filter)
        
        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data)


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Trip.objects.all()
        user = self.request.user
        
        # Filtros baseados no tipo de usuário
        if user.user_type == 'driver':
            queryset = queryset.filter(driver=user)
        
        # Filtros por parâmetros
        vehicle_id = self.request.query_params.get('vehicle')
        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related('vehicle', 'driver').order_by('-planned_start_time')
    
    def perform_create(self, serializer):
        # Define o motorista como o usuário atual se for um motorista
        if self.request.user.user_type == 'driver':
            serializer.save(driver=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def start_trip(self, request, pk=None):
        """Inicia uma viagem"""
        trip = self.get_object()
        
        if trip.status != 'planned':
            return Response(
                {'error': 'Viagem não pode ser iniciada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        trip.status = 'in_progress'
        trip.actual_start_time = timezone.now()
        trip.save()
        
        serializer = self.get_serializer(trip)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def end_trip(self, request, pk=None):
        """Finaliza uma viagem"""
        trip = self.get_object()
        
        if trip.status != 'in_progress':
            return Response(
                {'error': 'Viagem não está em andamento'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        trip.status = 'completed'
        trip.actual_end_time = timezone.now()
        
        # Dados opcionais do request
        trip.distance_km = request.data.get('distance_km', trip.distance_km)
        trip.fuel_consumed = request.data.get('fuel_consumed', trip.fuel_consumed)
        trip.notes = request.data.get('notes', trip.notes)
        
        trip.save()
        
        serializer = self.get_serializer(trip)
        return Response(serializer.data)


class FuelRecordViewSet(viewsets.ModelViewSet):
    queryset = FuelRecord.objects.all()
    serializer_class = FuelRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = FuelRecord.objects.all()
        user = self.request.user
        
        # Filtros baseados no tipo de usuário
        if user.user_type == 'driver':
            queryset = queryset.filter(vehicle__assigned_driver=user)
        
        # Filtros por parâmetros
        vehicle_id = self.request.query_params.get('vehicle')
        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)
        
        return queryset.select_related('vehicle', 'created_by').order_by('-date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ServiceRecordViewSet(viewsets.ModelViewSet):
    queryset = ServiceRecord.objects.all()
    serializer_class = ServiceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ServiceRecord.objects.all()
        user = self.request.user
        
        # Filtros baseados no tipo de usuário
        if user.user_type == 'driver':
            queryset = queryset.filter(vehicle__assigned_driver=user)
        
        # Filtros por parâmetros
        vehicle_id = self.request.query_params.get('vehicle')
        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)
        
        service_type = self.request.query_params.get('service_type')
        if service_type:
            queryset = queryset.filter(service_type=service_type)
        
        return queryset.select_related('vehicle', 'created_by').order_by('-date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TrackingDeviceViewSet(viewsets.ModelViewSet):
    queryset = TrackingDevice.objects.all()
    serializer_class = TrackingDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = TrackingDevice.objects.all()
        user = self.request.user
        
        # Apenas admins e gestores podem ver todos os dispositivos
        if user.user_type == 'driver':
            queryset = queryset.filter(vehicle__assigned_driver=user)
        
        return queryset.select_related('vehicle')
    
    @action(detail=True, methods=['post'])
    def sync_data(self, request, pk=None):
        """Sincroniza dados do dispositivo com a API Flespi"""
        device = self.get_object()
        
        from tracking.services import TelemetryProcessor
        processor = TelemetryProcessor()
        
        try:
            success = processor.process_device_data(device.device_id)
            if success:
                return Response({'message': 'Dados sincronizados com sucesso'})
            else:
                return Response(
                    {'error': 'Falha na sincronização'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@login_required
def vehicles_list(request):
    """Lista todos os veículos"""
    user = request.user
    
    # Filtrar veículos baseado no tipo de usuário
    if user.user_type == 'driver':
        vehicles = Vehicle.objects.filter(assigned_driver=user)
    else:
        vehicles = Vehicle.objects.all()
    
    # Filtros opcionais
    status_filter = request.GET.get('status')
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)
    
    search = request.GET.get('search')
    if search:
        vehicles = vehicles.filter(
            Q(plate__icontains=search) |
            Q(brand__icontains=search) |
            Q(model__icontains=search)
        )
    
    vehicles = vehicles.select_related('assigned_driver').order_by('plate')
    
    context = {
        'vehicles': vehicles,
        'status_choices': Vehicle.STATUS_CHOICES,
        'current_status': status_filter,
        'search_query': search,
    }
    
    return render(request, 'vehicles/list.html', context)


@login_required 
def trips_list(request):
    """Lista todas as viagens"""
    user = request.user
    
    # Filtrar viagens baseado no tipo de usuário
    if user.user_type == 'driver':
        trips = Trip.objects.filter(driver=user)
    else:
        trips = Trip.objects.all()
    
    # Filtros opcionais
    status_filter = request.GET.get('status')
    if status_filter:
        trips = trips.filter(status=status_filter)
    
    vehicle_filter = request.GET.get('vehicle')
    if vehicle_filter:
        trips = trips.filter(vehicle_id=vehicle_filter)
    
    trips = trips.select_related('vehicle', 'driver').order_by('-planned_start_time')
    
    # Obter veículos para o filtro
    if user.user_type == 'driver':
        vehicles_for_filter = Vehicle.objects.filter(assigned_driver=user)
    else:
        vehicles_for_filter = Vehicle.objects.all()
    
    context = {
        'trips': trips,
        'status_choices': Trip.STATUS_CHOICES,
        'vehicles': vehicles_for_filter,
        'current_status': status_filter,
        'current_vehicle': vehicle_filter,
    }
    
    return render(request, 'vehicles/trips_list.html', context)

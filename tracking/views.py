from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import LocationData, GeofenceAlert, SpeedAlert, MaintenanceAlert
from vehicles.models import Vehicle


@login_required
def tracking_dashboard(request):
    """Dashboard principal de rastreamento"""
    user = request.user
    
    # Filtrar veículos baseado no tipo de usuário
    if user.user_type == 'driver':
        vehicles = Vehicle.objects.filter(assigned_driver=user)
    else:
        vehicles = Vehicle.objects.all()
    
    # Alertas ativos
    active_alerts = {
        'geofence': GeofenceAlert.objects.filter(status='active').count(),
        'speed': SpeedAlert.objects.filter(status='active').count(),
        'maintenance': MaintenanceAlert.objects.filter(status='active').count(),
    }
    
    context = {
        'vehicles': vehicles,
        'active_alerts': active_alerts,
        'total_vehicles': vehicles.count(),
        'active_vehicles': vehicles.filter(status='active').count(),
    }
    
    return render(request, 'tracking/dashboard.html', context)


@login_required
def live_map(request):
    """Mapa em tempo real dos veículos"""
    user = request.user
    
    # Filtrar veículos baseado no tipo de usuário
    if user.user_type == 'driver':
        vehicles = Vehicle.objects.filter(assigned_driver=user)
    else:
        vehicles = Vehicle.objects.all()
    
    # Se for uma requisição AJAX, retornar JSON
    if request.headers.get('Content-Type') == 'application/json' or request.path.endswith('/api/live-locations/'):
        vehicles_data = []
        for vehicle in vehicles:
            vehicle_data = {
                'id': vehicle.id,
                'plate': vehicle.plate,
                'brand': vehicle.brand,
                'model': vehicle.model,
                'status': vehicle.status,
                'status_display': vehicle.get_status_display(),
                'assigned_driver': vehicle.assigned_driver.get_full_name() if vehicle.assigned_driver else None,
                'last_location': None
            }
            
            # Obter última localização
            if hasattr(vehicle, 'tracking_device') and vehicle.tracking_device:
                last_location = LocationData.objects.filter(
                    device=vehicle.tracking_device
                ).order_by('-timestamp').first()
                
                if last_location:
                    vehicle_data['last_location'] = {
                        'latitude': float(last_location.latitude),
                        'longitude': float(last_location.longitude),
                        'speed': last_location.speed,
                        'timestamp': last_location.timestamp.isoformat(),
                        'ignition': last_location.ignition
                    }
            
            vehicles_data.append(vehicle_data)
        
        return JsonResponse(vehicles_data, safe=False)
    
    # Renderizar template HTML - Obter última localização de cada veículo
    vehicles_data = []
    for vehicle in vehicles:
        if hasattr(vehicle, 'tracking_device'):
            last_location = LocationData.objects.filter(
                device=vehicle.tracking_device
            ).order_by('-timestamp').first()
            
            if last_location:
                vehicles_data.append({
                    'id': vehicle.id,
                    'plate': vehicle.plate,
                    'brand': vehicle.brand,
                    'model': vehicle.model,
                    'status': vehicle.status,
                    'latitude': float(last_location.latitude),
                    'longitude': float(last_location.longitude),
                    'speed': last_location.speed,
                    'timestamp': last_location.timestamp.isoformat(),
                    'ignition': last_location.ignition,
                    'fuel_level': last_location.fuel_level,
                })
    
    context = {
        'vehicles': vehicles,
        'vehicles_data': vehicles_data,
    }
    
    return render(request, 'tracking/live_map.html', context)

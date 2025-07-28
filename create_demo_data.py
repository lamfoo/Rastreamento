#!/usr/bin/env python
"""
Script para criar dados de demonstração para o sistema de monitoramento veicular
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_monitoring.settings')
django.setup()

from django.contrib.auth import get_user_model
from vehicles.models import Vehicle, TrackingDevice, Trip, FuelRecord, ServiceRecord
from tracking.models import LocationData, GeofenceArea

User = get_user_model()

def create_users():
    """Criar usuários de demonstração"""
    print("Criando usuários...")
    
    # Gestor
    manager, created = User.objects.get_or_create(
        username='gestor',
        defaults={
            'email': 'gestor@vehicletrack.com',
            'first_name': 'João',
            'last_name': 'Silva',
            'user_type': 'manager',
            'phone': '+258 84 123 4567',
            'nuit': '123456789',
        }
    )
    if created:
        manager.set_password('gestor123')
        manager.save()
        print(f"✓ Gestor criado: {manager.username}")
    
    # Motoristas
    drivers_data = [
        {
            'username': 'motorista1',
            'email': 'motorista1@vehicletrack.com',
            'first_name': 'Carlos',
            'last_name': 'Machado',
            'phone': '+258 84 234 5678',
            'nuit': '234567890',
            'driving_license': 'MOZ123456',
        },
        {
            'username': 'motorista2',
            'email': 'motorista2@vehicletrack.com',
            'first_name': 'Maria',
            'last_name': 'Santos',
            'phone': '+258 84 345 6789',
            'nuit': '345678901',
            'driving_license': 'MOZ234567',
        },
        {
            'username': 'motorista3',
            'email': 'motorista3@vehicletrack.com',
            'first_name': 'António',
            'last_name': 'Fernandes',
            'phone': '+258 84 456 7890',
            'nuit': '456789012',
            'driving_license': 'MOZ345678',
        }
    ]
    
    drivers = []
    for driver_data in drivers_data:
        driver, created = User.objects.get_or_create(
            username=driver_data['username'],
            defaults={
                **driver_data,
                'user_type': 'driver',
                'is_active_driver': True,
            }
        )
        if created:
            driver.set_password('motorista123')
            driver.save()
            print(f"✓ Motorista criado: {driver.username}")
        drivers.append(driver)
    
    return manager, drivers

def create_vehicles(drivers):
    """Criar veículos de demonstração"""
    print("Criando veículos...")
    
    vehicles_data = [
        {
            'plate': 'MPM-001-MZ',
            'brand': 'Toyota',
            'model': 'Hilux',
            'year': 2022,
            'color': 'Branco',
            'fuel_type': 'diesel',
            'fuel_capacity': 80.0,
            'assigned_driver': drivers[0] if drivers else None,
        },
        {
            'plate': 'MPM-002-MZ',
            'brand': 'Nissan',
            'model': 'Navara',
            'year': 2021,
            'color': 'Prata',
            'fuel_type': 'diesel',
            'fuel_capacity': 75.0,
            'assigned_driver': drivers[1] if len(drivers) > 1 else None,
        },
        {
            'plate': 'MPM-003-MZ',
            'brand': 'Ford',
            'model': 'Ranger',
            'year': 2023,
            'color': 'Azul',
            'fuel_type': 'diesel',
            'fuel_capacity': 85.0,
            'assigned_driver': drivers[2] if len(drivers) > 2 else None,
        },
        {
            'plate': 'MPM-004-MZ',
            'brand': 'Isuzu',
            'model': 'D-Max',
            'year': 2020,
            'color': 'Vermelho',
            'fuel_type': 'diesel',
            'fuel_capacity': 76.0,
            'assigned_driver': None,
        },
        {
            'plate': 'MPM-005-MZ',
            'brand': 'Mitsubishi',
            'model': 'L200',
            'year': 2022,
            'color': 'Preto',
            'fuel_type': 'diesel',
            'fuel_capacity': 73.0,
            'assigned_driver': None,
        }
    ]
    
    vehicles = []
    for vehicle_data in vehicles_data:
        vehicle, created = Vehicle.objects.get_or_create(
            plate=vehicle_data['plate'],
            defaults=vehicle_data
        )
        if created:
            print(f"✓ Veículo criado: {vehicle.plate}")
        vehicles.append(vehicle)
    
    return vehicles

def create_tracking_devices(vehicles):
    """Criar dispositivos de rastreamento"""
    print("Criando dispositivos de rastreamento...")
    
    devices = []
    for i, vehicle in enumerate(vehicles):
        device, created = TrackingDevice.objects.get_or_create(
            device_id=f'COBAN_{i+1:03d}',
            defaults={
                'device_type': 'coban_gps303f',
                'imei': f'86012345678901{i}',
                'vehicle': vehicle,
                'status': 'active',
            }
        )
        if created:
            print(f"✓ Dispositivo criado: {device.device_id} para {vehicle.plate}")
        devices.append(device)
    
    return devices

def create_sample_locations(devices):
    """Criar dados de localização de exemplo"""
    print("Criando dados de localização...")
    
    # Coordenadas de exemplo em Maputo
    base_coordinates = [
        (-25.9664, 32.5832),  # Centro de Maputo
        (-25.9692, 32.5731),  # Baixa
        (-25.9553, 32.5906),  # Polana
        (-25.9445, 32.6058),  # Sommerschield
        (-25.9789, 32.5654),  # Malhangalene
    ]
    
    for i, device in enumerate(devices):
        base_lat, base_lng = base_coordinates[i % len(base_coordinates)]
        
        # Criar 10 pontos de localização para cada dispositivo
        for j in range(10):
            # Pequenas variações na localização
            lat_offset = (j - 5) * 0.001
            lng_offset = (j - 5) * 0.001
            
            timestamp = datetime.now() - timedelta(hours=j)
            
            location, created = LocationData.objects.get_or_create(
                device=device,
                timestamp=timestamp,
                defaults={
                    'latitude': Decimal(str(base_lat + lat_offset)),
                    'longitude': Decimal(str(base_lng + lng_offset)),
                    'speed': 45.0 + (j * 2),
                    'heading': j * 36,
                    'ignition': True,
                    'engine_running': True,
                    'fuel_level': 80.0 - (j * 2),
                    'battery_voltage': 12.5,
                    'temperature': 25.0,
                    'odometer': 15000.0 + (j * 10),
                }
            )
            if created and j == 0:  # Só imprimir o primeiro
                print(f"✓ Localização criada para {device.device_id}")

def create_trips(vehicles, drivers):
    """Criar viagens de exemplo"""
    print("Criando viagens...")
    
    trips_data = [
        {
            'vehicle': vehicles[0] if vehicles else None,
            'driver': drivers[0] if drivers else None,
            'origin': 'Centro de Maputo',
            'destination': 'Aeroporto Internacional de Maputo',
            'status': 'completed',
            'distance_km': 8.5,
            'fuel_consumed': 1.2,
            'purpose': 'Transporte de passageiros',
        },
        {
            'vehicle': vehicles[1] if len(vehicles) > 1 else None,
            'driver': drivers[1] if len(drivers) > 1 else None,
            'origin': 'Polana Shopping',
            'destination': 'Universidade Eduardo Mondlane',
            'status': 'in_progress',
            'distance_km': None,
            'fuel_consumed': None,
            'purpose': 'Entrega de documentos',
        },
        {
            'vehicle': vehicles[2] if len(vehicles) > 2 else None,
            'driver': drivers[2] if len(drivers) > 2 else None,
            'origin': 'Mercado Central',
            'destination': 'Costa do Sol',
            'status': 'planned',
            'distance_km': None,
            'fuel_consumed': None,
            'purpose': 'Transporte de mercadorias',
        }
    ]
    
    now = datetime.now()
    
    for i, trip_data in enumerate(trips_data):
        if not trip_data['vehicle'] or not trip_data['driver']:
            continue
            
        planned_start = now - timedelta(hours=i*2)
        
        trip, created = Trip.objects.get_or_create(
            vehicle=trip_data['vehicle'],
            driver=trip_data['driver'],
            planned_start_time=planned_start,
            defaults={
                'origin': trip_data['origin'],
                'destination': trip_data['destination'],
                'status': trip_data['status'],
                'distance_km': trip_data['distance_km'],
                'fuel_consumed': trip_data['fuel_consumed'],
                'purpose': trip_data['purpose'],
                'planned_end_time': planned_start + timedelta(hours=2),
                'actual_start_time': planned_start if trip_data['status'] != 'planned' else None,
                'actual_end_time': planned_start + timedelta(hours=1.5) if trip_data['status'] == 'completed' else None,
            }
        )
        if created:
            print(f"✓ Viagem criada: {trip.origin} → {trip.destination}")

def create_fuel_records(vehicles, manager):
    """Criar registros de combustível"""
    print("Criando registros de combustível...")
    
    for i, vehicle in enumerate(vehicles[:3]):  # Só para os primeiros 3 veículos
        for j in range(3):  # 3 registros por veículo
            date = datetime.now() - timedelta(days=j*7)
            
            fuel_record, created = FuelRecord.objects.get_or_create(
                vehicle=vehicle,
                date=date,
                defaults={
                    'quantity': 50.0 + (j * 5),
                    'cost': Decimal('3500.00') + (j * 200),
                    'fuel_station': f'Posto Petromoc {i+1}',
                    'odometer_reading': 15000.0 + (j * 500),
                    'created_by': manager,
                    'notes': f'Abastecimento de rotina #{j+1}',
                }
            )
            if created and j == 0:  # Só imprimir o primeiro
                print(f"✓ Registro de combustível criado para {vehicle.plate}")

def create_service_records(vehicles, manager):
    """Criar registros de serviços"""
    print("Criando registros de serviços...")
    
    service_types = ['maintenance', 'oil_change', 'tire_change', 'inspection']
    
    for i, vehicle in enumerate(vehicles[:3]):
        service_type = service_types[i % len(service_types)]
        date = datetime.now() - timedelta(days=i*10)
        
        service_record, created = ServiceRecord.objects.get_or_create(
            vehicle=vehicle,
            date=date,
            service_type=service_type,
            defaults={
                'description': f'Serviço de {service_type} realizado conforme cronograma',
                'cost': Decimal('2500.00') + (i * 500),
                'service_provider': f'Oficina Técnica {i+1}',
                'odometer_reading': 15000.0 + (i * 200),
                'created_by': manager,
                'next_service_date': (date + timedelta(days=90)).date(),
            }
        )
        if created:
            print(f"✓ Registro de serviço criado para {vehicle.plate}")

def create_geofence_areas(vehicles):
    """Criar áreas de geofence"""
    print("Criando áreas de geofence...")
    
    geofence_data = [
        {
            'name': 'Centro de Maputo',
            'area_type': 'allowed',
            'description': 'Área central de Maputo permitida para circulação',
            'coordinates': [[-25.9664, 32.5832], [-25.9700, 32.5800], [-25.9700, 32.5864], [-25.9628, 32.5864]],
            'radius': 1000.0,
        },
        {
            'name': 'Aeroporto Internacional',
            'area_type': 'restricted',
            'description': 'Área restrita do aeroporto',
            'coordinates': [[-25.9208, 32.5726], [-25.9250, 32.5700], [-25.9250, 32.5752], [-25.9166, 32.5752]],
            'radius': 500.0,
        },
        {
            'name': 'Depósito Principal',
            'area_type': 'depot',
            'description': 'Depósito principal da empresa',
            'coordinates': [[-25.9553, 32.5906], [-25.9570, 32.5890], [-25.9570, 32.5922], [-25.9536, 32.5922]],
            'radius': 200.0,
        }
    ]
    
    for area_data in geofence_data:
        area, created = GeofenceArea.objects.get_or_create(
            name=area_data['name'],
            defaults={
                'area_type': area_data['area_type'],
                'description': area_data['description'],
                'coordinates': area_data['coordinates'],
                'radius': area_data['radius'],
                'is_active': True,
            }
        )
        if created:
            # Associar alguns veículos à área
            area.vehicles.set(vehicles[:2])
            print(f"✓ Área de geofence criada: {area.name}")

def main():
    """Função principal"""
    print("🚗 Criando dados de demonstração para o Sistema de Monitoramento Veicular")
    print("=" * 70)
    
    try:
        # Criar usuários
        manager, drivers = create_users()
        
        # Criar veículos
        vehicles = create_vehicles(drivers)
        
        # Criar dispositivos de rastreamento
        devices = create_tracking_devices(vehicles)
        
        # Criar dados de localização
        create_sample_locations(devices)
        
        # Criar viagens
        create_trips(vehicles, drivers)
        
        # Criar registros de combustível
        create_fuel_records(vehicles, manager)
        
        # Criar registros de serviços
        create_service_records(vehicles, manager)
        
        # Criar áreas de geofence
        create_geofence_areas(vehicles)
        
        print("\n" + "=" * 70)
        print("✅ Dados de demonstração criados com sucesso!")
        print("\n📋 Credenciais de acesso:")
        print("👨‍💼 Administrador: admin / admin123")
        print("👨‍💼 Gestor: gestor / gestor123")
        print("🚗 Motorista 1: motorista1 / motorista123")
        print("🚗 Motorista 2: motorista2 / motorista123")
        print("🚗 Motorista 3: motorista3 / motorista123")
        print("\n🌐 Acesse o sistema em: http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados de demonstração: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
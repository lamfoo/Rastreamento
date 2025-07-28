import requests
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import LocationData, GeofenceAlert, SpeedAlert, MaintenanceAlert
from vehicles.models import TrackingDevice

logger = logging.getLogger(__name__)


class FlespiService:
    """Serviço para integração com a API Flespi"""
    
    def __init__(self):
        self.base_url = settings.FLESPI_BASE_URL
        self.token = settings.FLESPI_TOKEN
        self.headers = {
            'Authorization': f'FlespiToken {self.token}',
            'Content-Type': 'application/json'
        }
    
    def get_device_data(self, device_id, from_time=None, to_time=None):
        """
        Obtém dados de telemetria de um dispositivo específico
        """
        if not from_time:
            from_time = timezone.now() - timedelta(hours=1)
        if not to_time:
            to_time = timezone.now()
        
        # Converte para timestamp Unix
        from_timestamp = int(from_time.timestamp())
        to_timestamp = int(to_time.timestamp())
        
        url = f"{self.base_url}/{device_id}/messages"
        params = {
            'from': from_timestamp,
            'to': to_timestamp,
            'fields': 'timestamp,position.latitude,position.longitude,position.altitude,position.speed,position.direction,engine.ignition.status,fuel.level,battery.voltage,temperature,odometer'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter dados do dispositivo {device_id}: {e}")
            return None
    
    def get_all_devices(self):
        """
        Obtém lista de todos os dispositivos
        """
        url = self.base_url
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter lista de dispositivos: {e}")
            return None
    
    def create_device(self, device_data):
        """
        Cria um novo dispositivo na plataforma Flespi
        """
        url = self.base_url
        
        try:
            response = requests.post(url, headers=self.headers, json=device_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao criar dispositivo: {e}")
            return None


class TelemetryProcessor:
    """Processador de dados de telemetria"""
    
    def __init__(self):
        self.flespi_service = FlespiService()
    
    def process_device_data(self, device_id):
        """
        Processa dados de telemetria para um dispositivo específico
        """
        try:
            device = TrackingDevice.objects.get(device_id=device_id)
        except TrackingDevice.DoesNotExist:
            logger.error(f"Dispositivo {device_id} não encontrado")
            return False
        
        # Obtém dados da API Flespi
        data = self.flespi_service.get_device_data(device_id)
        if not data or 'result' not in data:
            logger.warning(f"Nenhum dado encontrado para o dispositivo {device_id}")
            return False
        
        messages = data['result']
        processed_count = 0
        
        for message in messages:
            if self._save_location_data(device, message):
                processed_count += 1
        
        # Atualiza última comunicação do dispositivo
        if processed_count > 0:
            device.last_communication = timezone.now()
            device.status = 'active'
            device.save()
        
        logger.info(f"Processadas {processed_count} mensagens para o dispositivo {device_id}")
        return True
    
    def _save_location_data(self, device, message):
        """
        Salva dados de localização no banco de dados
        """
        try:
            # Extrai dados da mensagem
            timestamp = datetime.fromtimestamp(message.get('timestamp', 0), tz=timezone.utc)
            position = message.get('position', {})
            
            # Verifica se já existe um registro para este timestamp
            if LocationData.objects.filter(device=device, timestamp=timestamp).exists():
                return False
            
            location_data = LocationData(
                device=device,
                timestamp=timestamp,
                latitude=position.get('latitude', 0),
                longitude=position.get('longitude', 0),
                altitude=position.get('altitude'),
                speed=position.get('speed'),
                heading=position.get('direction'),
                ignition=message.get('engine', {}).get('ignition', {}).get('status', False),
                fuel_level=message.get('fuel', {}).get('level'),
                battery_voltage=message.get('battery', {}).get('voltage'),
                temperature=message.get('temperature'),
                odometer=message.get('odometer')
            )
            
            location_data.save()
            
            # Processa alertas
            self._process_alerts(location_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados de localização: {e}")
            return False
    
    def _process_alerts(self, location_data):
        """
        Processa alertas baseados nos dados de localização
        """
        # Alerta de velocidade
        self._check_speed_alerts(location_data)
        
        # Alerta de geofence
        self._check_geofence_alerts(location_data)
        
        # Alerta de manutenção
        self._check_maintenance_alerts(location_data)
    
    def _check_speed_alerts(self, location_data):
        """
        Verifica alertas de velocidade
        """
        if not location_data.speed:
            return
        
        # Limite de velocidade padrão (pode ser configurável por veículo)
        speed_limit = 80  # km/h
        
        if location_data.speed > speed_limit:
            # Verifica se já existe um alerta ativo para este veículo
            existing_alert = SpeedAlert.objects.filter(
                vehicle=location_data.device.vehicle,
                status='active'
            ).first()
            
            if not existing_alert:
                SpeedAlert.objects.create(
                    vehicle=location_data.device.vehicle,
                    location_data=location_data,
                    speed_limit=speed_limit,
                    actual_speed=location_data.speed
                )
                logger.info(f"Alerta de velocidade criado para {location_data.device.vehicle.plate}")
    
    def _check_geofence_alerts(self, location_data):
        """
        Verifica alertas de geofence
        """
        from .models import GeofenceArea
        import math
        
        vehicle = location_data.device.vehicle
        vehicle_lat = float(location_data.latitude)
        vehicle_lng = float(location_data.longitude)
        
        # Verifica todas as áreas de geofence ativas para este veículo
        geofence_areas = GeofenceArea.objects.filter(
            is_active=True,
            vehicles=vehicle
        )
        
        for area in geofence_areas:
            is_inside = self._is_point_inside_geofence(
                vehicle_lat, vehicle_lng, area
            )
            
            # Lógica para detectar entrada/saída
            # (Implementação simplificada - pode ser melhorada)
            if area.area_type == 'restricted' and is_inside:
                GeofenceAlert.objects.create(
                    geofence_area=area,
                    vehicle=vehicle,
                    location_data=location_data,
                    alert_type='violation',
                    message=f"Veículo {vehicle.plate} entrou em área restrita: {area.name}"
                )
    
    def _is_point_inside_geofence(self, lat, lng, geofence_area):
        """
        Verifica se um ponto está dentro de uma área de geofence
        """
        # Implementação simplificada para áreas circulares
        if geofence_area.radius and len(geofence_area.coordinates) >= 1:
            center = geofence_area.coordinates[0]
            center_lat, center_lng = center[0], center[1]
            
            # Calcula distância usando fórmula de Haversine
            distance = self._calculate_distance(lat, lng, center_lat, center_lng)
            return distance <= geofence_area.radius
        
        # Para polígonos complexos, implementar algoritmo ray casting
        return False
    
    def _calculate_distance(self, lat1, lng1, lat2, lng2):
        """
        Calcula distância entre dois pontos usando fórmula de Haversine
        """
        import math
        
        R = 6371000  # Raio da Terra em metros
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _check_maintenance_alerts(self, location_data):
        """
        Verifica alertas de manutenção
        """
        vehicle = location_data.device.vehicle
        
        # Alerta de combustível baixo
        if location_data.fuel_level and location_data.fuel_level < 20:
            existing_alert = MaintenanceAlert.objects.filter(
                vehicle=vehicle,
                alert_type='fuel_low',
                status='active'
            ).first()
            
            if not existing_alert:
                MaintenanceAlert.objects.create(
                    vehicle=vehicle,
                    alert_type='fuel_low',
                    title='Combustível Baixo',
                    description=f'Nível de combustível: {location_data.fuel_level}%',
                    priority='high'
                )
        
        # Alerta de bateria baixa
        if location_data.battery_voltage and location_data.battery_voltage < 11.5:
            existing_alert = MaintenanceAlert.objects.filter(
                vehicle=vehicle,
                alert_type='battery_low',
                status='active'
            ).first()
            
            if not existing_alert:
                MaintenanceAlert.objects.create(
                    vehicle=vehicle,
                    alert_type='battery_low',
                    title='Bateria Baixa',
                    description=f'Voltagem da bateria: {location_data.battery_voltage}V',
                    priority='medium'
                )


def sync_all_devices():
    """
    Sincroniza dados de todos os dispositivos ativos
    """
    processor = TelemetryProcessor()
    devices = TrackingDevice.objects.filter(status='active')
    
    for device in devices:
        try:
            processor.process_device_data(device.device_id)
        except Exception as e:
            logger.error(f"Erro ao processar dispositivo {device.device_id}: {e}")
    
    logger.info(f"Sincronização concluída para {devices.count()} dispositivos")
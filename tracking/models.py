from django.db import models
from django.contrib.auth import get_user_model
from vehicles.models import Vehicle, TrackingDevice

User = get_user_model()


class LocationData(models.Model):
    device = models.ForeignKey(
        TrackingDevice,
        on_delete=models.CASCADE,
        related_name='location_data',
        verbose_name='Dispositivo'
    )
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        verbose_name='Latitude'
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        verbose_name='Longitude'
    )
    altitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Altitude (m)'
    )
    speed = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Velocidade (km/h)'
    )
    heading = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Direção (graus)'
    )
    accuracy = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Precisão (m)'
    )
    timestamp = models.DateTimeField(
        verbose_name='Data/Hora'
    )
    ignition = models.BooleanField(
        default=False,
        verbose_name='Ignição Ligada'
    )
    engine_running = models.BooleanField(
        default=False,
        verbose_name='Motor Funcionando'
    )
    fuel_level = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Nível de Combustível (%)'
    )
    battery_voltage = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Voltagem da Bateria (V)'
    )
    temperature = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Temperatura (°C)'
    )
    odometer = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Odômetro (km)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Dados de Localização'
        verbose_name_plural = 'Dados de Localização'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', '-timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return f"{self.device.vehicle.plate} - {self.timestamp.strftime('%d/%m/%Y %H:%M:%S')}"

    @property
    def coordinates(self):
        return [float(self.latitude), float(self.longitude)]


class GeofenceArea(models.Model):
    AREA_TYPE_CHOICES = [
        ('allowed', 'Área Permitida'),
        ('restricted', 'Área Restrita'),
        ('depot', 'Depósito'),
        ('fuel_station', 'Posto de Combustível'),
        ('service_center', 'Centro de Serviço'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='Nome da Área'
    )
    area_type = models.CharField(
        max_length=20,
        choices=AREA_TYPE_CHOICES,
        verbose_name='Tipo da Área'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
    )
    # Coordenadas do polígono (formato JSON)
    coordinates = models.JSONField(
        verbose_name='Coordenadas',
        help_text='Array de coordenadas [lat, lng] definindo o polígono'
    )
    radius = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Raio (metros)',
        help_text='Para áreas circulares'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    vehicles = models.ManyToManyField(
        Vehicle,
        blank=True,
        related_name='geofence_areas',
        verbose_name='Veículos Monitorados'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Área de Geofence'
        verbose_name_plural = 'Áreas de Geofence'

    def __str__(self):
        return f"{self.name} ({self.get_area_type_display()})"


class GeofenceAlert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('entered', 'Entrada na Área'),
        ('exited', 'Saída da Área'),
        ('violation', 'Violação de Área'),
    ]

    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('acknowledged', 'Reconhecido'),
        ('resolved', 'Resolvido'),
    ]

    geofence_area = models.ForeignKey(
        GeofenceArea,
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name='Área de Geofence'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='geofence_alerts',
        verbose_name='Veículo'
    )
    location_data = models.ForeignKey(
        LocationData,
        on_delete=models.CASCADE,
        verbose_name='Dados de Localização'
    )
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPE_CHOICES,
        verbose_name='Tipo de Alerta'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    message = models.TextField(
        verbose_name='Mensagem'
    )
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts',
        verbose_name='Reconhecido por'
    )
    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Reconhecido em'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Alerta de Geofence'
        verbose_name_plural = 'Alertas de Geofence'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vehicle.plate} - {self.get_alert_type_display()} - {self.geofence_area.name}"


class SpeedAlert(models.Model):
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('acknowledged', 'Reconhecido'),
        ('resolved', 'Resolvido'),
    ]

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='speed_alerts',
        verbose_name='Veículo'
    )
    location_data = models.ForeignKey(
        LocationData,
        on_delete=models.CASCADE,
        verbose_name='Dados de Localização'
    )
    speed_limit = models.FloatField(
        verbose_name='Limite de Velocidade (km/h)'
    )
    actual_speed = models.FloatField(
        verbose_name='Velocidade Registrada (km/h)'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_speed_alerts',
        verbose_name='Reconhecido por'
    )
    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Reconhecido em'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Alerta de Velocidade'
        verbose_name_plural = 'Alertas de Velocidade'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vehicle.plate} - {self.actual_speed}km/h (limite: {self.speed_limit}km/h)"


class MaintenanceAlert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('scheduled', 'Manutenção Agendada'),
        ('overdue', 'Manutenção Vencida'),
        ('mileage', 'Quilometragem Atingida'),
        ('fuel_low', 'Combustível Baixo'),
        ('battery_low', 'Bateria Baixa'),
        ('engine_fault', 'Falha no Motor'),
    ]

    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('acknowledged', 'Reconhecido'),
        ('resolved', 'Resolvido'),
    ]

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='maintenance_alerts',
        verbose_name='Veículo'
    )
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPE_CHOICES,
        verbose_name='Tipo de Alerta'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    description = models.TextField(
        verbose_name='Descrição'
    )
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Baixa'),
            ('medium', 'Média'),
            ('high', 'Alta'),
            ('critical', 'Crítica'),
        ],
        default='medium',
        verbose_name='Prioridade'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Vencimento'
    )
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_maintenance_alerts',
        verbose_name='Reconhecido por'
    )
    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Reconhecido em'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Alerta de Manutenção'
        verbose_name_plural = 'Alertas de Manutenção'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vehicle.plate} - {self.title}"

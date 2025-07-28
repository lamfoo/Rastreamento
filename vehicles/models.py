from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Vehicle(models.Model):
    FUEL_TYPE_CHOICES = [
        ('gasoline', 'Gasolina'),
        ('diesel', 'Diesel'),
        ('electric', 'Elétrico'),
        ('hybrid', 'Híbrido'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('maintenance', 'Manutenção'),
    ]

    plate = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Placa'
    )
    brand = models.CharField(
        max_length=50,
        verbose_name='Marca'
    )
    model = models.CharField(
        max_length=50,
        verbose_name='Modelo'
    )
    year = models.IntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2030)
        ],
        verbose_name='Ano'
    )
    color = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='Cor'
    )
    fuel_type = models.CharField(
        max_length=10,
        choices=FUEL_TYPE_CHOICES,
        default='gasoline',
        verbose_name='Tipo de Combustível'
    )
    fuel_capacity = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name='Capacidade do Tanque (L)'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    assigned_driver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'driver'},
        related_name='assigned_vehicles',
        verbose_name='Motorista Designado'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        ordering = ['plate']

    def __str__(self):
        return f"{self.plate} - {self.brand} {self.model}"

    @property
    def is_available(self):
        return self.status == 'active' and not self.current_trips.filter(status='in_progress').exists()


class TrackingDevice(models.Model):
    DEVICE_TYPE_CHOICES = [
        ('coban_gps303f', 'Coban GPS303-F'),
        ('other', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('error', 'Erro'),
    ]

    device_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='ID do Dispositivo'
    )
    device_type = models.CharField(
        max_length=20,
        choices=DEVICE_TYPE_CHOICES,
        default='coban_gps303f',
        verbose_name='Tipo do Dispositivo'
    )
    imei = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name='IMEI'
    )
    vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='tracking_device',
        verbose_name='Veículo'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    last_communication = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última Comunicação'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dispositivo de Rastreamento'
        verbose_name_plural = 'Dispositivos de Rastreamento'

    def __str__(self):
        return f"{self.device_id} - {self.vehicle.plate}"


class Trip(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planejada'),
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
    ]

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='trips',
        verbose_name='Veículo'
    )
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'driver'},
        related_name='trips',
        verbose_name='Motorista'
    )
    origin = models.CharField(
        max_length=200,
        verbose_name='Origem'
    )
    destination = models.CharField(
        max_length=200,
        verbose_name='Destino'
    )
    planned_start_time = models.DateTimeField(
        verbose_name='Horário Planejado de Início'
    )
    planned_end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Horário Planejado de Fim'
    )
    actual_start_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Horário Real de Início'
    )
    actual_end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Horário Real de Fim'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name='Status'
    )
    distance_km = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Distância (km)'
    )
    fuel_consumed = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Combustível Consumido (L)'
    )
    purpose = models.TextField(
        blank=True,
        null=True,
        verbose_name='Propósito da Viagem'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Viagem'
        verbose_name_plural = 'Viagens'
        ordering = ['-planned_start_time']

    def __str__(self):
        return f"{self.vehicle.plate} - {self.origin} → {self.destination}"

    @property
    def duration(self):
        if self.actual_start_time and self.actual_end_time:
            return self.actual_end_time - self.actual_start_time
        return None


class FuelRecord(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='fuel_records',
        verbose_name='Veículo'
    )
    date = models.DateTimeField(
        verbose_name='Data do Abastecimento'
    )
    quantity = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name='Quantidade (L)'
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Custo (MZN)'
    )
    odometer_reading = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Leitura do Odômetro (km)'
    )
    fuel_station = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Posto de Combustível'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Registrado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de Combustível'
        verbose_name_plural = 'Registros de Combustível'
        ordering = ['-date']

    def __str__(self):
        return f"{self.vehicle.plate} - {self.quantity}L em {self.date.strftime('%d/%m/%Y')}"


class ServiceRecord(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('maintenance', 'Manutenção Preventiva'),
        ('repair', 'Reparo'),
        ('inspection', 'Inspeção'),
        ('tire_change', 'Troca de Pneus'),
        ('oil_change', 'Troca de Óleo'),
        ('other', 'Outro'),
    ]

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='service_records',
        verbose_name='Veículo'
    )
    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_TYPE_CHOICES,
        verbose_name='Tipo de Serviço'
    )
    date = models.DateTimeField(
        verbose_name='Data do Serviço'
    )
    description = models.TextField(
        verbose_name='Descrição'
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Custo (MZN)'
    )
    service_provider = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Prestador de Serviço'
    )
    odometer_reading = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Leitura do Odômetro (km)'
    )
    next_service_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Próximo Serviço'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Registrado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de Serviço'
        verbose_name_plural = 'Registros de Serviços'
        ordering = ['-date']

    def __str__(self):
        return f"{self.vehicle.plate} - {self.get_service_type_display()} em {self.date.strftime('%d/%m/%Y')}"

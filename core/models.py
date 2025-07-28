from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    ADMIN = 'admin'
    MANAGER = 'manager'
    DRIVER = 'driver'
    USER_TYPE_CHOICES = [
        (ADMIN, 'Administrador'),
        (MANAGER, 'Gestor'),
        (DRIVER, 'Motorista'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

class Vehicle(models.Model):
    plate = models.CharField(max_length=10, unique=True)
    model = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    # device será relacionado depois

class Device(models.Model):
    identifier = models.CharField(max_length=50, unique=True)
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='device', null=True, blank=True)
    last_latitude = models.FloatField(null=True, blank=True)
    last_longitude = models.FloatField(null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nuit = models.CharField(max_length=20)
    license_number = models.CharField(max_length=20)
    contact = models.CharField(max_length=20)
    vehicles = models.ManyToManyField(Vehicle, blank=True)

class Trip(models.Model):
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

class Fuel(models.Model):
    date = models.DateField()
    quantity = models.FloatField()
    cost = models.FloatField()
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

class Service(models.Model):
    date = models.DateField()
    service_type = models.CharField(max_length=50)
    cost = models.FloatField()
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

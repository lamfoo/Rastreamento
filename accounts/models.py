from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Administrador'),
        ('manager', 'Gestor'),
        ('driver', 'Motorista'),
    ]
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='driver',
        verbose_name='Tipo de Usuário'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Telefone'
    )
    nuit = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name='NUIT'
    )
    driving_license = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Carta de Condução'
    )
    is_active_driver = models.BooleanField(
        default=False,
        verbose_name='Motorista Ativo'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    @property
    def is_admin(self):
        return self.user_type == 'admin'

    @property
    def is_manager(self):
        return self.user_type == 'manager'

    @property
    def is_driver(self):
        return self.user_type == 'driver'

    def can_manage_vehicles(self):
        return self.user_type in ['admin', 'manager']

    def can_manage_users(self):
        return self.user_type in ['admin', 'manager']

    def can_view_all_trips(self):
        return self.user_type in ['admin', 'manager']

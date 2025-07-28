from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ReportTemplate(models.Model):
    """Template para geração de relatórios"""
    REPORT_TYPE_CHOICES = [
        ('trips', 'Relatório de Viagens'),
        ('fuel', 'Relatório de Combustível'),
        ('services', 'Relatório de Serviços'),
        ('location', 'Relatório de Localização'),
        ('alerts', 'Relatório de Alertas'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nome do Template'
    )
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        verbose_name='Tipo de Relatório'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição'
    )
    fields = models.JSONField(
        verbose_name='Campos do Relatório',
        help_text='Lista dos campos a serem incluídos no relatório'
    )
    filters = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Filtros Padrão',
        help_text='Filtros padrão para o relatório'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Criado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Template de Relatório'
        verbose_name_plural = 'Templates de Relatórios'
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class GeneratedReport(models.Model):
    """Relatório gerado"""
    STATUS_CHOICES = [
        ('generating', 'Gerando'),
        ('completed', 'Concluído'),
        ('failed', 'Falha'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('excel', 'Excel'),
    ]
    
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        verbose_name='Template'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        verbose_name='Formato'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='generating',
        verbose_name='Status'
    )
    filters_used = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Filtros Utilizados'
    )
    file_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Caminho do Arquivo'
    )
    file_size = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Tamanho do Arquivo (bytes)'
    )
    records_count = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Número de Registros'
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensagem de Erro'
    )
    generated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Gerado por'
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Relatório Gerado'
        verbose_name_plural = 'Relatórios Gerados'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

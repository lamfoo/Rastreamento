from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from vehicles.models import Vehicle, Trip, FuelRecord, ServiceRecord
from tracking.models import LocationData


@login_required
def reports_dashboard(request):
    """Dashboard principal de relatórios"""
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
        'total_trips': trips.count(),
        'completed_trips': trips.filter(status='completed').count(),
        'in_progress_trips': trips.filter(status='in_progress').count(),
        'total_fuel_records': FuelRecord.objects.filter(vehicle__in=vehicles).count(),
        'total_service_records': ServiceRecord.objects.filter(vehicle__in=vehicles).count(),
    }
    
    # Dados para gráficos
    # Viagens por mês (últimos 6 meses)
    six_months_ago = timezone.now() - timedelta(days=180)
    trips_by_month = trips.filter(
        planned_start_time__gte=six_months_ago
    ).extra(
        select={'month': "strftime('%%Y-%%m', planned_start_time)"}
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Combustível por mês
    fuel_by_month = FuelRecord.objects.filter(
        vehicle__in=vehicles,
        date__gte=six_months_ago
    ).extra(
        select={'month': "strftime('%%Y-%%m', date)"}
    ).values('month').annotate(
        total_quantity=Sum('quantity'),
        total_cost=Sum('cost')
    ).order_by('month')
    
    context = {
        'stats': stats,
        'trips_by_month': list(trips_by_month),
        'fuel_by_month': list(fuel_by_month),
    }
    
    return render(request, 'reports/dashboard.html', context)


@login_required
def trips_report(request):
    """Relatório de viagens"""
    user = request.user
    
    # Filtros
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    vehicle_id = request.GET.get('vehicle')
    status = request.GET.get('status')
    
    # Query base
    if user.user_type == 'driver':
        trips = Trip.objects.filter(driver=user)
    else:
        trips = Trip.objects.all()
    
    # Aplicar filtros
    if start_date:
        trips = trips.filter(planned_start_time__gte=start_date)
    if end_date:
        trips = trips.filter(planned_start_time__lte=end_date)
    if vehicle_id:
        trips = trips.filter(vehicle_id=vehicle_id)
    if status:
        trips = trips.filter(status=status)
    
    trips = trips.select_related('vehicle', 'driver').order_by('-planned_start_time')
    
    # Estatísticas
    trip_stats = {
        'total': trips.count(),
        'completed': trips.filter(status='completed').count(),
        'in_progress': trips.filter(status='in_progress').count(),
        'planned': trips.filter(status='planned').count(),
        'cancelled': trips.filter(status='cancelled').count(),
        'total_distance': trips.filter(distance_km__isnull=False).aggregate(Sum('distance_km'))['distance_km__sum'] or 0,
        'total_fuel': trips.filter(fuel_consumed__isnull=False).aggregate(Sum('fuel_consumed'))['fuel_consumed__sum'] or 0,
    }
    
    # Veículos para filtro
    if user.user_type == 'driver':
        vehicles = Vehicle.objects.filter(assigned_driver=user)
    else:
        vehicles = Vehicle.objects.all()
    
    context = {
        'trips': trips,
        'trip_stats': trip_stats,
        'vehicles': vehicles,
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'vehicle_id': vehicle_id,
            'status': status,
        }
    }
    
    return render(request, 'reports/trips_report.html', context)


@login_required
def fuel_report(request):
    """Relatório de combustível"""
    user = request.user
    
    # Filtros
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    vehicle_id = request.GET.get('vehicle')
    
    # Query base
    if user.user_type == 'driver':
        fuel_records = FuelRecord.objects.filter(vehicle__assigned_driver=user)
        vehicles = Vehicle.objects.filter(assigned_driver=user)
    else:
        fuel_records = FuelRecord.objects.all()
        vehicles = Vehicle.objects.all()
    
    # Aplicar filtros
    if start_date:
        fuel_records = fuel_records.filter(date__gte=start_date)
    if end_date:
        fuel_records = fuel_records.filter(date__lte=end_date)
    if vehicle_id:
        fuel_records = fuel_records.filter(vehicle_id=vehicle_id)
    
    fuel_records = fuel_records.select_related('vehicle', 'created_by').order_by('-date')
    
    # Estatísticas
    fuel_stats = {
        'total_records': fuel_records.count(),
        'total_quantity': fuel_records.aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'total_cost': fuel_records.aggregate(Sum('cost'))['cost__sum'] or 0,
        'avg_quantity': fuel_records.aggregate(Avg('quantity'))['quantity__avg'] or 0,
        'avg_cost': fuel_records.aggregate(Avg('cost'))['cost__avg'] or 0,
    }
    
    context = {
        'fuel_records': fuel_records,
        'fuel_stats': fuel_stats,
        'vehicles': vehicles,
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'vehicle_id': vehicle_id,
        }
    }
    
    return render(request, 'reports/fuel.html', context)


@login_required
def services_report(request):
    """Relatório de serviços"""
    user = request.user
    
    # Filtros
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    vehicle_id = request.GET.get('vehicle')
    service_type = request.GET.get('service_type')
    
    # Query base
    if user.user_type == 'driver':
        service_records = ServiceRecord.objects.filter(vehicle__assigned_driver=user)
        vehicles = Vehicle.objects.filter(assigned_driver=user)
    else:
        service_records = ServiceRecord.objects.all()
        vehicles = Vehicle.objects.all()
    
    # Aplicar filtros
    if start_date:
        service_records = service_records.filter(date__gte=start_date)
    if end_date:
        service_records = service_records.filter(date__lte=end_date)
    if vehicle_id:
        service_records = service_records.filter(vehicle_id=vehicle_id)
    if service_type:
        service_records = service_records.filter(service_type=service_type)
    
    service_records = service_records.select_related('vehicle', 'created_by').order_by('-date')
    
    # Estatísticas
    service_stats = {
        'total_records': service_records.count(),
        'total_cost': service_records.aggregate(Sum('cost'))['cost__sum'] or 0,
        'avg_cost': service_records.aggregate(Avg('cost'))['cost__avg'] or 0,
    }
    
    # Estatísticas por tipo de serviço
    service_by_type = service_records.values('service_type').annotate(
        count=Count('id'),
        total_cost=Sum('cost')
    ).order_by('-count')
    
    context = {
        'service_records': service_records,
        'service_stats': service_stats,
        'service_by_type': service_by_type,
        'vehicles': vehicles,
        'service_types': ServiceRecord.SERVICE_TYPE_CHOICES,
        'filters': {
            'start_date': start_date,
            'end_date': end_date,
            'vehicle_id': vehicle_id,
            'service_type': service_type,
        }
    }
    
    return render(request, 'reports/services.html', context)


@login_required
def export_trips_report(request, format):
    """Exporta relatório de viagens"""
    # Aplicar os mesmos filtros da view trips_report
    user = request.user
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    vehicle_id = request.GET.get('vehicle')
    status = request.GET.get('status')
    
    if user.user_type == 'driver':
        trips = Trip.objects.filter(driver=user)
    else:
        trips = Trip.objects.all()
    
    if start_date:
        trips = trips.filter(planned_start_time__gte=start_date)
    if end_date:
        trips = trips.filter(planned_start_time__lte=end_date)
    if vehicle_id:
        trips = trips.filter(vehicle_id=vehicle_id)
    if status:
        trips = trips.filter(status=status)
    
    trips = trips.select_related('vehicle', 'driver').order_by('-planned_start_time')
    
    if format == 'csv':
        return _export_trips_csv(trips)
    elif format == 'pdf':
        return _export_trips_pdf(trips)
    else:
        return HttpResponse('Formato não suportado', status=400)


def _export_trips_csv(trips):
    """Exporta viagens para CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="relatorio_viagens.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Veículo', 'Motorista', 'Origem', 'Destino', 'Status',
        'Início Planejado', 'Fim Planejado', 'Início Real', 'Fim Real',
        'Distância (km)', 'Combustível (L)', 'Propósito'
    ])
    
    for trip in trips:
        writer.writerow([
            trip.vehicle.plate,
            trip.driver.get_full_name() or trip.driver.username,
            trip.origin,
            trip.destination,
            trip.get_status_display(),
            trip.planned_start_time.strftime('%d/%m/%Y %H:%M') if trip.planned_start_time else '',
            trip.planned_end_time.strftime('%d/%m/%Y %H:%M') if trip.planned_end_time else '',
            trip.actual_start_time.strftime('%d/%m/%Y %H:%M') if trip.actual_start_time else '',
            trip.actual_end_time.strftime('%d/%m/%Y %H:%M') if trip.actual_end_time else '',
            trip.distance_km or '',
            trip.fuel_consumed or '',
            trip.purpose or ''
        ])
    
    return response


def _export_trips_pdf(trips):
    """Exporta viagens para PDF"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_viagens.pdf"'
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Conteúdo do PDF
    story = []
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Relatório de Viagens", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Data de geração
    date_str = timezone.now().strftime('%d/%m/%Y %H:%M')
    date_para = Paragraph(f"Gerado em: {date_str}", styles['Normal'])
    story.append(date_para)
    story.append(Spacer(1, 12))
    
    # Tabela de dados
    data = [['Veículo', 'Motorista', 'Origem', 'Destino', 'Status', 'Início']]
    
    for trip in trips[:50]:  # Limita a 50 registros para o PDF
        data.append([
            trip.vehicle.plate,
            trip.driver.get_full_name() or trip.driver.username,
            trip.origin[:20] + '...' if len(trip.origin) > 20 else trip.origin,
            trip.destination[:20] + '...' if len(trip.destination) > 20 else trip.destination,
            trip.get_status_display(),
            trip.planned_start_time.strftime('%d/%m/%Y') if trip.planned_start_time else ''
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


@login_required
def export_fuel_report(request, format):
    """Exporta relatório de combustível"""
    # Similar ao export_trips_report, mas para combustível
    # Implementação similar...
    return HttpResponse('Funcionalidade em desenvolvimento')


@login_required
def export_services_report(request, format):
    """Exporta relatório de serviços"""
    # Similar ao export_trips_report, mas para serviços
    # Implementação similar...
    return HttpResponse('Funcionalidade em desenvolvimento')

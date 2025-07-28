from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('trips/', views.trips_report, name='trips'),
    path('fuel/', views.fuel_report, name='fuel'),
    path('services/', views.services_report, name='services'),
    path('export/trips/<str:format>/', views.export_trips_report, name='export_trips'),
    path('export/fuel/<str:format>/', views.export_fuel_report, name='export_fuel'),
    path('export/services/<str:format>/', views.export_services_report, name='export_services'),
]
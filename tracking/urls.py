from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Adicionar viewsets quando criados

app_name = 'tracking'

urlpatterns = [
    path('', views.tracking_dashboard, name='dashboard'),
    path('map/', views.live_map, name='live_map'),
    path('api/live-locations/', views.live_map, name='live_locations_api'),
    path('api/', include(router.urls)),
]
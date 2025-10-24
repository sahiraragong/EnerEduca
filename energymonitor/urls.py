# energymonitor/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/recibir/', views.recibir_dato, name='recibir_dato'),
    path('historial/', views.historial, name='historial'),
    path('graficas/', views.graficas, name='graficas'),
    path('exportar-excel/', views.exportar_excel, name='exportar_excel'),
    path('limpiar/', views.limpiar_datos, name='limpiar_datos'),
    path('emergencia/', views.emergencia, name='emergencia'),
]


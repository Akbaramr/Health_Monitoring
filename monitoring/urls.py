from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False), name='home'),

    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.custom_logout, name='logout'),
    path('devices/select/', views.device_select, name='device_select'),
    path('devices/add/', views.device_add, name='device_add'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('grafik/', views.grafik, name='grafik'),
    path('histori/', views.histori, name='histori'),
    path('api/iot/ingest/', views.api_iot_ingest, name='api_iot_ingest'),
    path('api/devices/active/latest/', views.api_latest, name='api_latest'),
    path('api/devices/active/save-latest/', views.api_save_latest, name='api_save_latest'),
    path('api/devices/active/records/', views.api_records, name='api_records'),
    path('api/devices/list/', views.api_devices_list, name='api_devices_list'),
    path('api/device/set-active/', views.api_device_set_active, name='api_device_set_active'),
]

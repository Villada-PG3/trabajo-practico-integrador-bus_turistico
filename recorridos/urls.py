from django.urls import path
from . import views

urlpatterns = [
    # Parte Pública
    path('', views.home, name='home'),
    path('recorridos/', views.recorridos_list, name='recorridos_list'),
    path('paradas/', views.paradas_list, name='paradas_list'),
    path('atractivos/', views.atractivos_list, name='atractivos_list'),

    # Panel Administrativo
    path('admin-panel/login/', views.admin_login, name='admin_login'),
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
]
from django.urls import path
from . import views
from .views import RecorridoListView, ParadaListView, ParadaDetailView

urlpatterns = [
    # Parte Pública
    path('', views.home, name='home'),
    path('recorridos/', RecorridoListView.as_view(), name='recorridos_list'),
    path('paradas/', ParadaListView.as_view(), name='paradas_list'),
    path('paradas/<int:pk>/', ParadaDetailView.as_view(), name='parada_detail'),
    path('atractivos/', views.atractivos_list, name='atractivos_list'),
    path('nosotros/', views.nosotros, name='nosotros'),

    # Panel Administrativo
    path('admin-panel/login/', views.admin_login, name='admin_login'),
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
]
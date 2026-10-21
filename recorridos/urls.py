from django.urls import path
from . import views
from .views import (
    HomeView,
    NosotrosView,
    RecorridoListView, 
    RecorridoDetailView, 
    ParadaListView, 
    ParadaDetailView,
    AtractivoListView,
    AtractivoDetailView,
)

urlpatterns = [
    # Parte Pública (CBVs)
    path('', HomeView.as_view(), name='home'),
    path('nosotros/', NosotrosView.as_view(), name='nosotros'),

    # Recorridos
    path('recorridos/', RecorridoListView.as_view(), name='recorridos_list'),
    path('recorridos/<int:pk>/', RecorridoDetailView.as_view(), name='recorrido_detail'),

    # Paradas
    path('paradas/', ParadaListView.as_view(), name='paradas_list'),
    path('paradas/<int:pk>/', ParadaDetailView.as_view(), name='parada_detail'),

    # Atractivos Turísticos
    path('atractivos/', AtractivoListView.as_view(), name='atractivos_list'),
    path('atractivos/<int:pk>/', AtractivoDetailView.as_view(), name='atractivo_detail'),

    # Panel Administrativo
    path('admin-panel/login/', views.admin_login, name='admin_login'),
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
]
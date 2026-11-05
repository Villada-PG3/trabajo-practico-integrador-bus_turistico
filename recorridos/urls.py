
from django.urls import path
from . import views

urlpatterns = [
    # Parte publica
    path(
        '',
        views.HomeView.as_view(),
        name='home'
    ),
    path(
        'nosotros/',
        views.NosotrosView.as_view(),
        name='nosotros'
    ),
    path(
        'recorridos/',
        views.RecorridoListView.as_view(),
        name='recorridos_list'
    ),
    path(
        'recorridos/<int:pk>/',
        views.RecorridoDetailView.as_view(),
        name='recorrido_detail'
    ),
    path(
        'paradas/',
        views.ParadaListView.as_view(),
        name='paradas_list'
    ),
    path(
        'paradas/<int:pk>/',
        views.ParadaDetailView.as_view(),
        name='parada_detail'
    ),
    path(
        'atractivos/',
        views.AtractivoListView.as_view(),
        name='atractivos_list'
    ),
    path(
        'atractivos/<int:pk>/',
        views.AtractivoDetailView.as_view(),
        name='atractivo_detail'
    ),

    # Panel administrativo
    path(
        'admin-panel/login/',
        views.PanelLoginView.as_view(),
        name='admin_login'
    ),
    path(
        'admin-panel/dashboard/',
        views.DashboardView.as_view(),
        name='admin_dashboard'
    ),
    path(
        'admin-panel/logout/',
        views.PanelLogoutView.as_view(),
        name='admin_logout'
    ),

    # Gestion de autobuses
    path(
        'admin-panel/autobuses/nuevo/',
        views.AutobusCreateView.as_view(),
        name='autobus_create'
    ),
    path(
        'admin-panel/autobuses/',
        views.AutobusListView.as_view(),
        name='autobus_list'
    ),
    path(
        'admin-panel/autobuses/<int:pk>/editar/',
        views.AutobusUpdateView.as_view(),
        name='autobus_update'
    ),

    # Gestion de viajes
    path(
        'admin-panel/viajes/',
        views.ViajeListView.as_view(),
        name='viaje_list'
    ),
    path(
        'admin-panel/viajes/<int:pk>/iniciar/',
        views.ViajeIniciarView.as_view(),
        name='viaje_iniciar'
    ),
    path(
        'admin-panel/viajes/<int:pk>/finalizar/',
        views.ViajeFinalizarView.as_view(),
        name='viaje_finalizar'
    ),
]


from django.urls import path
from . import views

urlpatterns = [
    # Parte publica
    path('', views.HomeView.as_view(), name='home'),
    path('nosotros/', views.NosotrosView.as_view(), name='nosotros'),
    path('recorridos/', views.RecorridoListView.as_view(), name='recorridos_list'),
    path('recorridos/<int:pk>/', views.RecorridoDetailView.as_view(), name='recorrido_detail'),
    path('paradas/', views.ParadaListView.as_view(), name='paradas_list'),
    path('paradas/<int:pk>/', views.ParadaDetailView.as_view(), name='parada_detail'),
    path('atractivos/', views.AtractivoListView.as_view(), name='atractivos_list'),
    path('atractivos/<int:pk>/', views.AtractivoDetailView.as_view(), name='atractivo_detail'),

    # Panel administrativo
    path('admin-panel/login/', views.PanelLoginView.as_view(), name='admin_login'),
    path('admin-panel/dashboard/', views.DashboardView.as_view(), name='admin_dashboard'),
    path('admin-panel/logout/', views.PanelLogoutView.as_view(), name='admin_logout'),

    # Gestion de autobuses
    path('admin-panel/autobuses/nuevo/', views.AutobusCreateView.as_view(), name='autobus_create'),
    path('admin-panel/autobuses/', views.AutobusListView.as_view(), name='autobus_list'),
    path('admin-panel/autobuses/<int:pk>/editar/', views.AutobusUpdateView.as_view(), name='autobus_update'),

    # Gestion de viajes
    path('admin-panel/viajes/', views.ViajeListView.as_view(), name='viaje_list'),
    path('admin-panel/viajes/<int:pk>/iniciar/', views.ViajeIniciarView.as_view(), name='viaje_iniciar'),
    path('admin-panel/viajes/<int:pk>/finalizar/', views.ViajeFinalizarView.as_view(), name='viaje_finalizar'),
    path('admin-panel/viajes/nuevo/', views.ViajeCreateView.as_view(), name='viaje_create'),

    # Gestion de choferes
    path('admin-panel/choferes/', views.ChoferListView.as_view(), name='chofer_list'),
    path('admin-panel/choferes/nuevo/', views.ChoferCreateView.as_view(), name='chofer_create'),
    path('admin-panel/choferes/<int:pk>/editar/', views.ChoferUpdateView.as_view(), name='chofer_update'),

    # Gestion de reparaciones
    path('admin-panel/reparaciones/', views.ReparacionListView.as_view(), name='reparacion_list'),
    path('admin-panel/reparaciones/nueva/', views.ReparacionCreateView.as_view(), name='reparacion_create'),
    path('admin-panel/reparaciones/<int:pk>/finalizar/', views.ReparacionFinalizarView.as_view(), name='reparacion_finalizar'),

    # Gestion de recorridos (panel administrativo)
    path('admin-panel/recorridos/', views.RecorridoListAdminView.as_view(), name='recorrido_admin_list'),
    path('admin-panel/recorridos/nuevo/', views.RecorridoCreateView.as_view(), name='recorrido_create'),
    path('admin-panel/recorridos/<int:pk>/editar/', views.RecorridoUpdateView.as_view(), name='recorrido_update'),

    # Gestion de paradas (panel administrativo)
    path('admin-panel/paradas/', views.ParadaListAdminView.as_view(), name='parada_admin_list'),
    path('admin-panel/paradas/nueva/', views.ParadaCreateView.as_view(), name='parada_create'),
    path('admin-panel/paradas/<int:pk>/editar/', views.ParadaUpdateView.as_view(), name='parada_update'),
    path('admin-panel/recorridos/asignar-parada/', views.RecorridoParadaCreateView.as_view(), name='recorrido_parada_create'),

    # Administracion de paradas asignadas
    path('admin-panel/recorridos/paradas/', views.RecorridoParadaListView.as_view(), name='recorrido_parada_list'),
    path('admin-panel/recorridos/paradas/<int:pk>/editar/', views.RecorridoParadaUpdateView.as_view(), name='recorrido_parada_update'),
    path('admin-panel/recorridos/paradas/<int:pk>/eliminar/', views.RecorridoParadaDeleteView.as_view(), name='recorrido_parada_delete'),

    # Gestion de atractivos turisticos
    path('admin-panel/atractivos/', views.AtractivoListAdminView.as_view(), name='atractivo_admin_list'),
    path('admin-panel/atractivos/nuevo/', views.AtractivoCreateView.as_view(), name='atractivo_create'),
    path('admin-panel/atractivos/<int:pk>/editar/', views.AtractivoUpdateView.as_view(), name='atractivo_update'),
    path('admin-panel/atractivos/asociar-parada/', views.ParadaAtractivoCreateView.as_view(), name='parada_atractivo_create'),

    # Administracion de asociaciones entre paradas y atractivos
    path('admin-panel/atractivos/asociaciones/', views.ParadaAtractivoListView.as_view(), name='parada_atractivo_list'),
    path('admin-panel/atractivos/asociaciones/<int:pk>/editar/', views.ParadaAtractivoUpdateView.as_view(), name='parada_atractivo_update'),
    path('admin-panel/atractivos/asociaciones/<int:pk>/eliminar/', views.ParadaAtractivoDeleteView.as_view(), name='parada_atractivo_delete'),

]

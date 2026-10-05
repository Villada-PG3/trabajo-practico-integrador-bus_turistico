from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recorridos/', views.recorridos_list, name='recorridos_list'),
    path('paradas/', views.paradas_list, name='paradas_list'),
    path('atractivos/', views.atractivos_list, name='atractivos_list'),
    path('admin-panel/login/', views.admin_login, name='admin_login'),
]
from django.contrib import admin
from .models import (
    Chofer,
    Autobus,
    Recorrido,
    Parada,
    Atractivo,
    RecorridoParada,
    ParadaAtractivo,
    Viaje,
    Reparacion,
)


@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    list_display = ('legajo', 'apellido', 'nombre')
    search_fields = ('apellido', 'nombre')


@admin.register(Autobus)
class AutobusAdmin(admin.ModelAdmin):
    list_display = ('id_bus', 'numero_unidad', 'patente', 'estado', 'fecha_compra')
    search_fields = ('patente', 'numero_unidad')
    list_filter = ('estado',)


@admin.register(Recorrido)
class RecorridoAdmin(admin.ModelAdmin):
    list_display = ('id_recorrido', 'color', 'frecuencia', 'duracion_aproximada')
    search_fields = ('color',)


@admin.register(Parada)
class ParadaAdmin(admin.ModelAdmin):
    list_display = ('id_parada', 'nombre', 'direccion')
    search_fields = ('nombre', 'direccion')


@admin.register(Atractivo)
class AtractivoAdmin(admin.ModelAdmin):
    list_display = ('id_atractivo', 'nombre', 'calificacion')
    search_fields = ('nombre',)


@admin.register(RecorridoParada)
class RecorridoParadaAdmin(admin.ModelAdmin):
    list_display = ('id_recorrido_parada', 'recorrido', 'parada', 'orden')
    list_filter = ('recorrido',)


@admin.register(ParadaAtractivo)
class ParadaAtractivoAdmin(admin.ModelAdmin):
    list_display = ('id_parada_atractivo', 'parada', 'atractivo')


@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ('id_viaje', 'recorrido', 'bus', 'chofer', 'fecha_hora_inicio_programada')
    list_filter = ('recorrido', 'bus')


@admin.register(Reparacion)
class ReparacionAdmin(admin.ModelAdmin):
    list_display = ('id_reparacion', 'bus', 'fecha_inicio', 'fecha_fin')
    list_filter = ('bus',)
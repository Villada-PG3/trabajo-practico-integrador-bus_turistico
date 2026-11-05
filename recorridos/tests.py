from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Autobus, Chofer, Recorrido, Viaje


class ViajeEstadoTests(TestCase):

    def setUp(self):
        # Datos de prueba
        self.bus = Autobus.objects.create(
            patente="TEST123",
            numero_unidad=999,
            fecha_compra=timezone.localdate(),
            estado="OPERATIVO"
        )

        self.chofer = Chofer.objects.create(
            nombre="Juan",
            apellido="Prueba",
            activo=True
        )

        self.recorrido = Recorrido.objects.create(
            color="Prueba",
            frecuencia_minutos=30,
            hora_inicio="08:00",
            hora_fin="18:00",
            duracion_aproximada=90
        )

        self.viaje = Viaje.objects.create(
            bus=self.bus,
            chofer=self.chofer,
            recorrido=self.recorrido,
            fecha_hora_inicio_programada=timezone.now()
            + timedelta(hours=1)
        )

    def test_iniciar_viaje(self):
        self.viaje.iniciar()

        self.viaje.refresh_from_db()

        self.assertEqual(self.viaje.estado, "EN_CURSO")
        self.assertIsNotNone(self.viaje.fecha_hora_inicio_real)

    def test_finalizar_viaje(self):
        self.viaje.iniciar()
        self.viaje.finalizar()

        self.viaje.refresh_from_db()

        self.assertEqual(self.viaje.estado, "FINALIZADO")
        self.assertIsNotNone(self.viaje.fecha_hora_fin_real)

    def test_no_iniciar_viaje_cancelado(self):
        self.viaje.estado = "CANCELADO"
        self.viaje.save(update_fields=["estado"])

        with self.assertRaises(ValidationError):
            self.viaje.iniciar()
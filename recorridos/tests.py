from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

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

class ViajeTicketTests(TestCase):

    def setUp(self):
        bus = Autobus.objects.create(
            patente="TEST123", numero_unidad=7,
            fecha_compra=timezone.localdate(), estado="OPERATIVO",
        )
        chofer = Chofer.objects.create(nombre="Ana", apellido="Gómez", activo=True)
        recorrido = Recorrido.objects.create(
            color="Verde", frecuencia_minutos=30, hora_inicio="10:00",
            hora_fin="18:00", duracion_aproximada=90,
        )
        self.viaje = Viaje.objects.create(
            bus=bus, chofer=chofer, recorrido=recorrido,
            fecha_hora_inicio_programada=timezone.now() + timedelta(hours=1),
        )
        self.staff = User.objects.create_user("dueno", password="clave12345", is_staff=True)
        self.url = reverse("viaje_ticket", args=[self.viaje.pk])

    def test_ticket_de_viaje_finalizado_muestra_los_datos(self):
        self.viaje.iniciar()
        self.viaje.finalizar()
        self.client.force_login(self.staff)

        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Recorrido Verde")
        self.assertContains(respuesta, "Gómez")
        self.assertContains(respuesta, str(self.viaje.chofer.legajo))

    def test_ticket_de_viaje_no_finalizado_redirige(self):
        self.client.force_login(self.staff)

        respuesta = self.client.get(self.url)

        self.assertRedirects(respuesta, reverse("viaje_list"))

    def test_ticket_requiere_staff(self):
        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("admin_login"), respuesta["Location"])

    def test_finalizar_redirige_al_ticket(self):
        self.viaje.iniciar()
        self.client.force_login(self.staff)

        respuesta = self.client.post(reverse("viaje_finalizar", args=[self.viaje.pk]))

        self.assertRedirects(respuesta, self.url)

class ReporteDiarioTests(TestCase):

    def setUp(self):
        self.bus = Autobus.objects.create(
            patente="TEST123", numero_unidad=7,
            fecha_compra=timezone.localdate(), estado="OPERATIVO",
        )
        self.chofer = Chofer.objects.create(nombre="Ana", apellido="Gómez", activo=True)
        self.recorrido = Recorrido.objects.create(
            color="Verde", frecuencia_minutos=30, hora_inicio="10:00",
            hora_fin="18:00", duracion_aproximada=90,
        )
        self.staff = User.objects.create_user("gerente", password="clave12345", is_staff=True)
        self.url = reverse("reporte_diario")
        self.base = timezone.localtime().replace(hour=10, minute=0, second=0, microsecond=0)

    def crear_viaje(self, programado, demora=None, duracion=None, estado="PROGRAMADO"):
        inicio_real = programado + timedelta(minutes=demora) if demora is not None else None
        fin_real = inicio_real + timedelta(minutes=duracion) if duracion is not None else None
        return Viaje.objects.create(
            bus=self.bus, chofer=self.chofer, recorrido=self.recorrido,
            fecha_hora_inicio_programada=programado,
            fecha_hora_inicio_real=inicio_real,
            fecha_hora_fin_real=fin_real,
            estado=estado,
        )

    def test_reporte_requiere_staff(self):
        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("admin_login"), respuesta["Location"])

    def test_calcula_promedios_de_duracion_y_demora(self):
        self.crear_viaje(self.base, demora=10, duracion=60, estado="FINALIZADO")
        self.crear_viaje(self.base + timedelta(hours=1), demora=20, duracion=90, estado="FINALIZADO")
        # Programado: cuenta en el total pero no en los promedios
        self.crear_viaje(self.base + timedelta(hours=2))
        # Otro día: no debe aparecer
        self.crear_viaje(self.base + timedelta(days=1), demora=50, duracion=30, estado="FINALIZADO")
        self.client.force_login(self.staff)

        respuesta = self.client.get(self.url, {"fecha": self.base.date().isoformat()})

        resumen = respuesta.context["resumen"]
        self.assertEqual(resumen["total"], 3)
        self.assertEqual(resumen["finalizados"], 2)
        self.assertEqual(resumen["programados"], 1)
        self.assertEqual(resumen["promedio_duracion"], 75.0)
        self.assertEqual(resumen["promedio_demora"], 15.0)

    def test_dia_sin_viajes_no_tiene_promedios(self):
        self.client.force_login(self.staff)

        respuesta = self.client.get(self.url, {"fecha": self.base.date().isoformat()})

        resumen = respuesta.context["resumen"]
        self.assertEqual(resumen["total"], 0)
        self.assertIsNone(resumen["promedio_duracion"])
        self.assertIsNone(resumen["promedio_demora"])
        self.assertContains(respuesta, "No hay viajes programados")

    def test_fecha_invalida_muestra_hoy_con_aviso(self):
        self.client.force_login(self.staff)

        respuesta = self.client.get(self.url, {"fecha": "no-es-una-fecha"})

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["fecha"], timezone.localdate())
        self.assertContains(respuesta, "La fecha ingresada no es válida")
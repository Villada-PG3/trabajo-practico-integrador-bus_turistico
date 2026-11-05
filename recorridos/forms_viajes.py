
from django import forms

from .models import Viaje


class ViajeForm(forms.ModelForm):

    class Meta:
        model = Viaje

        fields = [
            "recorrido",
            "bus",
            "chofer",
            "fecha_hora_inicio_programada",
        ]

        labels = {
            "recorrido": "Recorrido",
            "bus": "Autobús",
            "chofer": "Chofer",
            "fecha_hora_inicio_programada": "Fecha y hora programada",
        }

        widgets = {
            "recorrido": forms.Select(
                attrs={"class": "form-select"}
            ),
            "bus": forms.Select(
                attrs={"class": "form-select"}
            ),
            "chofer": forms.Select(
                attrs={"class": "form-select"}
            ),
            "fecha_hora_inicio_programada": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[
            "fecha_hora_inicio_programada"
        ].input_formats = ["%Y-%m-%dT%H:%M"]

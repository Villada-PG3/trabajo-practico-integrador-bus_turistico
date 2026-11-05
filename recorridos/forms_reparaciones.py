
from django import forms

from .models import Reparacion


class ReparacionForm(forms.ModelForm):

    class Meta:
        model = Reparacion

        fields = [
            "bus",
            "descripcion",
            "fecha_inicio",
            "costo",
        ]

        labels = {
            "bus": "Autobús",
            "descripcion": "Descripción de la reparación",
            "fecha_inicio": "Fecha y hora de inicio",
            "costo": "Costo de la reparación",
        }

        widgets = {
            "bus": forms.Select(
                attrs={"class": "form-select"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
            "fecha_inicio": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "costo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["fecha_inicio"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]

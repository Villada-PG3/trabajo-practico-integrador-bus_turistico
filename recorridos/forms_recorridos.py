
from django import forms

from .models import Recorrido


class RecorridoForm(forms.ModelForm):

    class Meta:
        model = Recorrido

        fields = [
            "color",
            "color_hex",
            "descripcion",
            "frecuencia_minutos",
            "hora_inicio",
            "hora_fin",
            "duracion_aproximada",
        ]

        labels = {
            "color": "Color del recorrido",
            "color_hex": "Color hexadecimal",
            "descripcion": "Descripción",
            "frecuencia_minutos": "Frecuencia (minutos)",
            "hora_inicio": "Hora de inicio",
            "hora_fin": "Hora de finalización",
            "duracion_aproximada": "Duración aproximada (minutos)",
        }

        widgets = {
            "color": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "color_hex": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "#16a34a",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
            "frecuencia_minutos": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            "hora_inicio": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                },
                format="%H:%M",
            ),
            "hora_fin": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                },
                format="%H:%M",
            ),
            "duracion_aproximada": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["hora_inicio"].input_formats = ["%H:%M"]
        self.fields["hora_fin"].input_formats = ["%H:%M"]

    def clean(self):
        cleaned_data = super().clean()

        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")

        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            self.add_error(
                "hora_fin",
                "La hora de finalización debe ser posterior a la de inicio."
            )

        return cleaned_data

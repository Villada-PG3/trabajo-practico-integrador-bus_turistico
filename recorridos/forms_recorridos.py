import re
from django import forms

from .models import Recorrido

COLORES_VALIDOS = {
    "rojo": "Rojo",
    "azul": "Azul",
    "azul marino": "Azul Marino",
    "celeste": "Celeste",
    "verde": "Verde",
    "verde oscuro": "Verde Oscuro",
    "amarillo": "Amarillo",
    "naranja": "Naranja",
    "violeta": "Violeta",
    "morado": "Morado",
    "rosa": "Rosa",
    "fucsia": "Fucsia",
    "turquesa": "Turquesa",
    "bordo": "Bordó",
    "bordó": "Bordó",
    "marron": "Marrón",
    "marrón": "Marrón",
    "gris": "Gris",
    "negro": "Negro",
    "dorado": "Dorado",
}


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
                attrs={
                    "class": "form-control",
                    "list": "lista-colores",
                    "autocomplete": "off",
                    "placeholder": "Escribí o elegí un color (ej: Rojo, Azul...)",
                }
            ),
            "color_hex": forms.TextInput(
                attrs={
                    "type": "color",
                    "class": "form-control form-control-color",
                    "title": "Elegí el tono del recorrido",
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

    def clean_color(self):
        valor = self.cleaned_data["color"].strip().lower()
        if valor not in COLORES_VALIDOS:
            raise forms.ValidationError(
                "Elegí un color válido de la lista (ej: Rojo, Azul, Verde, Amarillo, Violeta)."
            )

        nombre_oficial = COLORES_VALIDOS[valor]

        ya_existe = (
            Recorrido.objects
            .filter(color__iexact=nombre_oficial)
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if ya_existe:
            raise forms.ValidationError(
                f"Ya existe un recorrido con el color {nombre_oficial}. Elegí otro distinto."
            )

        return nombre_oficial

    def clean_color_hex(self):
        hex_val = self.cleaned_data["color_hex"].strip().lower()
        if not re.fullmatch(r"^#[0-9a-f]{6}$", hex_val):
            raise forms.ValidationError(
                "Seleccioná un código de color válido en la paleta."
            )

        hex_repetido = (
            Recorrido.objects
            .filter(color_hex__iexact=hex_val)
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if hex_repetido:
            raise forms.ValidationError(
                "Ese tono exacto de la paleta ya está en uso en otro recorrido."
            )

        return hex_val

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
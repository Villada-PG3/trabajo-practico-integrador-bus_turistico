from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Chofer
from .roles import CHOFER


class ChoferForm(forms.ModelForm):

    class Meta:
        model = Chofer

        fields = [
            "nombre",
            "apellido",
            "dni",
            "activo",
            "usuario",
        ]

        labels = {
            "nombre": "Nombre",
            "apellido": "Apellido",
            "dni": "DNI",
            "activo": "Chofer activo",
            "usuario": "Usuario del sistema",
        }

        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "apellido": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "dni": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "activo": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "usuario": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Solo se pueden vincular usuarios del grupo Chofer
        # (y el usuario ya vinculado, si lo hay).
        filtro = Q(groups__name=CHOFER)
        if self.instance.pk and self.instance.usuario_id:
            filtro |= Q(pk=self.instance.usuario_id)

        self.fields["usuario"].queryset = (
            get_user_model().objects.filter(filtro).distinct()
        )
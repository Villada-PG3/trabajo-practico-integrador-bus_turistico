from django.db import migrations

ROLES = [
    "Administrador",
    "Encargado de Operaciones",
    "Chofer",
    "Gerente de Operaciones",
]


def crear_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for nombre in ROLES:
        Group.objects.get_or_create(name=nombre)


def borrar_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=ROLES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("recorridos", "0006_chofer_usuario"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(crear_grupos, borrar_grupos),
    ]
# 🚌 Bus Turístico — Trabajo Práctico Integrador (Caso 7)

Aplicación web desarrollada con **Django** para administrar el servicio de bus turístico de Buenos Aires: recorridos, paradas, atractivos cercanos, flota de buses, choferes y control operativo de viajes.

Trabajo Práctico Integrador de Programación 2026.

## Tecnologías

- Python 3.12 o superior
- Django 6.0.7
- Pillow 12.3.0 (manejo de imágenes)
- SQLite (base de datos incluida con Python, sin instalación extra)
- Bootstrap 5 (se carga por CDN, hace falta conexión a internet)

## Funcionalidades

**Sitio público**

- Listado y detalle de **recorridos**, con su color, frecuencia, horarios y paradas en orden.
- Listado y detalle de **paradas**, con dirección, descripción, foto y atractivos cercanos.
- Listado y detalle de **atractivos turísticos**, con su calificación en estrellas.
- Buscadores en cada listado y página 404 personalizada.

**Panel de administración** (solo usuarios *staff*)

- Alta y edición de autobuses, choferes, reparaciones, recorridos, paradas y atractivos, con formularios validados. Se pueden agregar y quitar las paradas de cada recorrido y los atractivos de cada parada.
- **Viajes:** programar un viaje (bus + chofer + recorrido + horario), iniciarlo y finalizarlo. No se puede asignar un bus que esté en reparación.
- **Ticket de viaje:** se emite al finalizar el viaje, con los datos del viaje y la duración en minutos. Se puede imprimir.
- **Reporte diario:** viajes del día con duración y demora de inicio, y los promedios diarios de ambos valores.

## Requisitos previos

- [Python 3.12+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- Conexión a internet (para los estilos de Bootstrap)

Para verificar las versiones instaladas:

```bash
python3 --version
git --version
```

## Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone git@github.com:Villada-PG3/trabajo-practico-integrador-bus_turistico.git
cd trabajo-practico-integrador-bus_turistico
```

### 2. Crear el entorno virtual

Linux / macOS:

```bash
python3 -m venv venv
```

Windows:

```bash
python -m venv venv
```

### 3. Activar el entorno virtual

Linux / macOS:

```bash
source venv/bin/activate
```

Windows (PowerShell):

```powershell
venv\Scripts\Activate.ps1
```

Windows (CMD):

```bat
venv\Scripts\activate.bat
```

Cuando está activo, la terminal muestra `(venv)` al comienzo de la línea.

### 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 5. Crear la base de datos (migraciones)

```bash
python manage.py migrate
```

Esto crea el archivo `db.sqlite3` con todas las tablas. No hace falta configurar nada más.

### 6. Crear un superusuario

```bash
python manage.py createsuperuser
```

Ingresá un nombre de usuario, un email (opcional) y una contraseña. Con este usuario se accede al panel de administración.

### 7. Activar el modo desarrollo

Por seguridad, el proyecto arranca con `DEBUG` apagado. Para trabajar en tu máquina hay que activarlo con la variable de entorno `DJANGO_DEBUG`. **Sin esto no se cargan los estilos del admin de Django ni las fotos subidas.**

Linux / macOS:

```bash
export DJANGO_DEBUG=True
```

Windows (PowerShell):

```powershell
$env:DJANGO_DEBUG = "True"
```

Windows (CMD):

```bat
set DJANGO_DEBUG=True
```

La variable dura mientras la terminal esté abierta: hay que volver a definirla si abrís una terminal nueva.

### 8. Ejecutar la aplicación

```bash
python manage.py runserver
```

Abrí el navegador en <http://127.0.0.1:8000/>. Para detener el servidor, `Ctrl + C`.

## Direcciones principales

| Dirección | Qué es |
|---|---|
| `/` | Página de inicio |
| `/recorridos/`, `/paradas/`, `/atractivos/` | Listados públicos |
| `/admin-panel/login/` | Ingreso al panel de administración |
| `/admin-panel/dashboard/` | Panel principal (requiere usuario staff) |
| `/admin-panel/reportes/viajes/` | Reporte diario de viajes |
| `/admin/` | Administrador estándar de Django |

## Primeros pasos: cargar datos

La base de datos arranca vacía. Para ver el sitio completo, cargá los datos desde el panel (`/admin-panel/login/`) en este orden:

1. **Atractivos** y **Paradas** (la parada admite una foto).
2. **Recorridos** y, después, las paradas de cada recorrido con su orden.
3. Los atractivos cercanos de cada parada.
4. **Autobuses** y **Choferes**.
5. **Viajes**: programar un viaje, iniciarlo y finalizarlo. Al finalizar se abre el ticket.
6. Revisar el **Reporte diario** desde el dashboard.

## Tests

```bash
python manage.py test
```

## Estructura del proyecto

```
├── Config/                  Configuración de Django (settings, urls, wsgi, asgi)
├── recorridos/              Aplicación principal
│   ├── models.py            Modelos (Recorrido, Parada, Atractivo, Autobus, Chofer, Viaje, ...)
│   ├── views.py             Vistas basadas en clases (CBV)
│   ├── forms*.py            Formularios con validaciones
│   ├── urls.py              Rutas de la aplicación
│   ├── admin.py             Configuración del admin de Django
│   ├── tests.py             Tests automáticos
│   └── migrations/          Migraciones de la base de datos
├── templates/
│   ├── base.html            Plantilla base (Bootstrap 5)
│   ├── public/              Sitio público
│   └── admin_panel/         Panel de administración
├── docs/                    Diagramas UML y ER (Mermaid)
├── static/                  Archivos estáticos
├── requirements.txt         Dependencias
└── manage.py
```

## Diagramas

Los diagramas están en la carpeta `docs/`, en formato [Mermaid](https://mermaid.js.org/):

- `docs/umlBusTuristico.mmd`: diagrama UML de clases.
- `docs/derBusTuristico.mmd`: diagrama entidad-relación.

Para verlos, pegá el contenido de cada archivo en <https://mermaid.live>.

## Solución de problemas

| Problema | Solución |
|---|---|
| `python: command not found` | Usá `python3` en lugar de `python` (Linux / macOS). |
| `No module named 'django'` | El entorno virtual no está activo. Activalo (paso 3) e instalá las dependencias (paso 4). |
| En PowerShell: *la ejecución de scripts está deshabilitada* | Ejecutá `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y volvé a activar el entorno. |
| El admin de Django se ve sin estilos o las fotos no aparecen | Falta activar el modo desarrollo (paso 7). |
| `That port is already in use` | Usá otro puerto: `python manage.py runserver 8001`. |
| El panel no me deja entrar | El usuario debe ser *staff*. Los creados con `createsuperuser` ya lo son. |
| Quiero empezar con la base vacía | Borrá el archivo `db.sqlite3` y volvé a ejecutar `python manage.py migrate` y `createsuperuser`. |
| Error de migraciones después de un `git pull` | Ejecutá `python manage.py migrate` para aplicar las migraciones nuevas. |

## Flujo de trabajo en equipo

- Cada tarea se desarrolla en una **rama propia** (`feat/nombre-de-la-tarea`) y se integra a `main` mediante Pull Request.
- Antes de crear una rama: `git switch main` y `git pull origin main`.
- Después de traer cambios del equipo: `pip install -r requirements.txt` y `python manage.py migrate`.
- Antes de generar migraciones nuevas, aplicar siempre las del repositorio, para evitar conflictos entre compañeros.

## Notas

- El proyecto está pensado para ejecutarse en desarrollo. La `SECRET_KEY` incluida es solo para uso local y habría que reemplazarla por una variable de entorno antes de publicarlo.
- Las fotos que se suben desde el panel se guardan en la carpeta `media/`, que no se incluye en el repositorio.

## Integrantes

- Felipe Faule
- Máximo Corallo Margosian
- Ramiro Cardo
Sistema de Gestión - Bus Turístico Buenos Aires (Caso 7)
Aplicación web y API desarrollada en Django para la administración del servicio de Bus Turístico de Buenos Aires, sus recorridos, flota de vehículos, asignación de choferes y control operativo de viajes.

Funcionalidades del Sistema:

Gestión de Recorridos y Paradas: Registro de circuitos por colores (ej. Verde), frecuencias, horarios de inicio/fin y secuencia ordenada de paradas con fotos, descripción geográfica y dirección.

Atractivos Cercanos: Puntos turísticos de interés asociados a cada parada con su respectiva calificación en estrellas (1 a 5).

Control de Flota y Choferes: Registro de unidades (patente, nro. de unidad, fecha de compra y estado de mantenimiento/reparación) y legajo de choferes.

Planificación y Operación: Asignación semanal de duplas bus-chofer a horarios programados.

Registro de Viajes y Tickets: API / módulo para registro de inicio y fin real de viajes desde la app móvil del chofer, emitiendo comprobantes/tickets con el detalle completo.

Reportes Operativos: Generación del reporte diario para la Gerencia de Operaciones con cálculo de demoras respecto a la hora programada, tiempo de recorrido y promedios diarios.

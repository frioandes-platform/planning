**Al equipo de arquitectura cloud de FríoAndes**

Estimado equipo:

Con mucho gusto les entregamos la estrategia de la plataforma cloud que reemplaza el datacenter de Cali. Durante estas semanas trabajamos con un propósito: que la torre de control siga despachando de 04:00 a 22:00 mientras todo cambia por debajo, y que la cadena de frío gane lo que hoy le falta, como la alerta de temperatura en menos de un minuto, ambientes separados y un archivo de cinco años que no dependa de un solo servidor.

Este informe reúne la estrategia completa en un solo documento. Lo escribimos para que se pueda leer sin abrir el repositorio: cada decisión aparece con su porqué, sus cifras y lo que todavía depende de una confirmación de ustedes. El detalle técnico, los diagramas completos y cada supuesto están en los documentos de arquitectura y de costos que acompañan este informe.

Tres puntos merecen su atención antes de la aprobación del 13 de noviembre:

1. **El corte del domingo 14 de febrero de 2027.** Volver atrás es limpio hasta las 02:30. Después, la base de Azure ya tiene escrituras reales, y el informe explica qué se hace en ese caso.
2. **La siembra del archivo de 1,2 PB con discos.** Es la ruta crítica del proyecto, con dos días de holgura antes del ensayo.
3. **Las confirmaciones pendientes.** La sección 17 resume las que cambian el diseño o el costo: entre ellas, que los datos queden en Estados Unidos, las licencias de Microsoft 365 y el costo actual de Cali.

Quedamos atentos a sus comentarios y a resolver cualquier duda en la revisión.

Cordialmente,

**Equipo de arquitectura cloud del proyecto**\
Proyecto de migración de FríoAndes a Azure

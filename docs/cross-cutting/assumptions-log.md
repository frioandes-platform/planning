# Registro de supuestos

Supuestos que no están en el enunciado y que tomó el equipo al diseñar la plataforma. Cada historia agrega sus filas.

| Supuesto | Justificación | Issue que lo originó | Estado |
|---|---|---|---|
| El firewall de Cali es un solo equipo; la contingencia (segundo equipo, VPN de usuario o aceptar el riesgo) la decide FríoAndes | El enunciado describe un único firewall en Cali; dos proveedores no protegen contra su falla | #8 | Por confirmar con el cliente |
| Cali contrata un segundo proveedor de internet por una ruta física distinta, sin compartir última milla, ducto ni nodo, usado como respaldo (activo-pasivo) | El enunciado pide ruta redundante para Cali; es la opción más barata y rápida frente a ExpressRoute | #8 | Decidido en el diseño; el cliente confirma proveedor y ruta |
| Los equipos de red de los centros soportan IKEv2, dos túneles simultáneos y BGP | Permite conectar cada centro directo a Azure con conmutación automática; si no, se usa túnel activo y de respaldo con rutas fijas | #8 | Por confirmar con el cliente |
| Una VPN de usuario con Entra ID y MFA podría contar como red corporativa para usar la torre de control | Es una de las opciones de contingencia si cae el firewall de Cali | #8 | Por confirmar con el cliente |
| Los camiones envían su telemetría a un endpoint público de IoT Hub, con una credencial por camión | Los camiones no tienen subred corporativa y salen por la red móvil del operador | #8 | Por confirmar con el cliente |
| Pruebas y desarrollo publican su portal solo a orígenes autorizados, sin entrada pública abierta | No manejan datos reales ni usuarios externos | #8 | Por confirmar con el cliente |
| Se acepta sembrar el archivo de 1,2 PB con Azure Import/Export (discos propios enviados a Microsoft) | Data Box Heavy está retirado y Data Box no se envía a Colombia; por la red tomaría unos 278 días | #8 | Por confirmar con el cliente y con Microsoft |
| El video y las fotos de evidencias después de la migración se generan en sitios que no saturan la VPN de ninguna sede | Define por dónde llegan los unos 12 TB al mes | #8 | Por confirmar con el cliente |
| Es aceptable que los datos y el procesamiento queden en Estados Unidos (East US 2 y Central US) | La medición de latencia confirmó East US 2; FríoAndes maneja datos personales sujetos a la Ley 1581 | #8 | Por confirmar con el cliente |
| El segundo proveedor cuesta unos COP 3.000.000 al mes por 200 Mbps | No hay cotización; es un valor de referencia del mercado para ese tamaño de enlace | #8 | Asumido en el diseño |
| Cada usuario genera unos 300 Kbps de tráfico hacia la plataforma | Se usa para comparar la carga del enlace de Cali con y sin los centros pasando por la sede | #8 | Asumido en el diseño |
| Los cambios por centro se hacen en la ventana de 22:00 a 04:00, uno o dos centros por noche, con un piloto primero | El despacho diurno no puede detenerse | #8 | Asumido en el diseño |
| Plan de ASN: Azure 65515, Cali 65020, centros 65031 a 65038 | Valores privados que no chocan entre sí y se leen fácil | #8 | Asumido en el diseño |
| Máximos de capacidad usados para los tamaños: Application Gateway hasta 10 instancias, base de datos con 2 réplicas y 1 servidor temporal, hasta 10 endpoints por subred, hasta 9 nodos del gateway de Fabric | Una subred no se puede agrandar con recursos dentro; se dimensiona para el máximo con margen | #8 | Asumido en el diseño |
| Unas 60 personas de desarrollo y operación trabajan fuera de la sede | Define el tamaño de la reserva para VPN de usuario | #8 | Asumido en el diseño |
| La plataforma de aplicación es Container Apps con perfiles de carga, con un máximo de 20 nodos dedicados y 200 réplicas por entorno | Se confirma con el diseño de la plataforma logística. Si fuera AKS, aplica la sección 7.3 | #8 | Asumido en el diseño |
| Cada mensaje de telemetría pesa alrededor de 1 KB | Se usa para estimar el volumen de los dos caminos | #8 | Asumido en el diseño |
| La copia continua del archivo mueve unos 12.154 GB al mes (37 Mbps) | Sale del crecimiento de 12 TB al mes que indica el reto | #8 | Asumido en el diseño |
| El portal se publica con Application Gateway v2 y WAF, el firewall de nube es Azure Firewall Standard y el acceso administrativo es Azure Bastion | El portal y el firewall quedaron confirmados en el diseño del firewall de nube (#9). El acceso administrativo se confirma con el diseño del acceso remoto | #8 | Portal y firewall decididos; acceso remoto por confirmar |
| La migración en línea de la base usa una cuenta de almacenamiento con token SAS temporal | El servicio de migración no admite una cuenta restringida a la red virtual; se confirma con el diseño de la migración | #8 | Asumido en el diseño |
| Una diferencia de latencia menor al 30 % no justifica cambiar de región | La plataforma es una consola web, un portal y alertas con margen de 60 segundos; 10 a 30 ms no cambian la experiencia | #8 | Asumido en el diseño |
| El plazo de vuelta atrás después del corte dura como máximo hasta el día 90 y lo fija el plan de migración | Mantener el camino de vuelta no cuesta más en la red; define cuándo se retiran las reglas temporales, el NAT del portal y la VPN de los centros hacia Cali | #9 | Por confirmar con el cliente |
| FríoAndes exporta la política real del firewall de Cali antes del inicio de la convivencia | Las políticas actuales del diseño son deducidas del inventario de redes y de las cargas descritas | #9 | Por confirmar con el cliente |
| Los centros envían los históricos de temperatura por FTP pasivo al servidor de archivo de Cali | El enunciado dice que se cargan por lote cada hora y que ese servidor ofrece FTP y NFS; define la regla temporal FW-402 | #9 | Por confirmar con el cliente |
| El plan de vuelta atrás puede replicar los datos de Azure hacia la base de Cali después del corte | Si no se usa, la regla temporal FW-505 y su pareja en el NSG no se crean | #9 | Por confirmar con el cliente |
| La integración entre los servidores de Cali y la plataforma nueva usa solo HTTPS (443) | Es la base de las reglas temporales FW-503 y FW-504 | #9 | Por confirmar con el cliente |
| La respuesta media del portal pesa unos 150 KB | Define la capacidad del Application Gateway (20 unidades reservadas en producción); se confirma con la prueba de carga antes del corte | #9 | Asumido en el diseño |
| Cada unidad de cómputo del WAF atiende unas 10 solicitudes por segundo | Referencia de Microsoft para WAF v2; depende del tamaño de las solicitudes y se confirma con la prueba de carga | #9 | Asumido en el diseño |
| El equipo que prueba la torre en pruebas y desarrollo trabaja desde Cali o con el acceso remoto definido | Por eso solo los usuarios de Cali llegan a la torre de esos ambientes | #9 | Asumido en el diseño |
| Pruebas y desarrollo usan datos de sensores simulados | No se llevan datos reales a ambientes con menos controles; los sensores reales solo llegan a producción | #9 | Asumido en el diseño |
| El volumen de registros del firewall, del WAF y de flujos se mide en el primer mes de operación | No hay tráfico real para estimarlo; con ese dato se decide qué tablas pasan al plan Basic | #9 | Asumido en el diseño |

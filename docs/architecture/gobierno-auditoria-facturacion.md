# FríoAndes — Auditoría, retención y facturación interna

## 1. Alcance y relación con la landing zone

FríoAndes necesita responder **quién accedió, a qué, cuándo y con qué resultado** en tres ámbitos: datos de clientes, evidencias de entregas y lecturas de temperatura. También necesita separar el gasto de operación, telemetría y pruebas, y mostrar la capacidad de Microsoft Fabric por separado. Las evidencias y la trazabilidad de temperatura se conservan **cinco años** por contrato. No se tratan datos de tarjetas de pago.

La [landing zone (#5)](gobierno-landing-zone.md) propone cinco suscripciones: `sub-fa-security`, `sub-fa-connectivity`, `sub-fa-prod`, `sub-fa-dev` y `sub-fa-test`. El espacio central de Log Analytics reside en `sub-fa-security`; las etiquetas `ambiente`, `carga`, `costo`, `criticidad` y `responsable`, junto con los presupuestos, son la base de la facturación interna. Este documento concreta la política P-04 de diagnósticos y la distribución del costo compartido. Las identidades y sus permisos específicos se detallan en [#7](https://github.com/frioandes-platform/planning/issues/7).

## 2. Eventos que deben poder reconstruirse

El registro del perímetro identifica IP, ruta y regla aplicada, pero por sí solo no sabe qué cliente o guía consultó un usuario. Cada servicio de negocio debe emitir **un evento estructurado por acceso**, exitoso o denegado, y enviarlo al espacio central; los logs de plataforma aportan evidencia adicional. Un cambio de datos o de permisos también queda registrado.

| Tipo de evento exigido | Origen principal y acciones | Datos mínimos para investigar | Corroboración técnica |
|---|---|---|---|
| **Acceso a datos de clientes** | Consola interna, API y portal: iniciar sesión, consultar guía/cliente, exportar, modificar y denegar una consulta ajena | Identidad o cuenta de servicio, rol, cliente y guía identificados por claves internas, acción, resultado, motivo de denegación y correlación de solicitud | Inicio de sesión en Entra ID, eventos del portal, Application Gateway y WAF; consultar MySQL por la clave interna cuando proceda |
| **Acceso a evidencias** | Servicio de archivo y portal: listar, leer, descargar, agregar, corregir mediante anotación y solicitar borrado de foto, comprobante o video | Actor, cliente/guía, identificador de objeto, operación, resultado y correlación; autorización aprobada | Registros de acceso de Blob (`StorageRead`, `StorageWrite`, `StorageDelete`) y cambios de permisos en Azure Activity Log |
| **Acceso a lecturas de temperatura** | Calidad, torre, API y cliente: consultar, exportar, vincular a reclamo y reconocer alerta | Actor, cliente/guía o cuarto/camión, intervalo consultado, operación, resultado, identificador de alerta y correlación | Accesos a la cuenta de telemetría y evidencia cruda de IoT Hub; la identidad del sensor acredita el origen de la lectura, no el lector humano |

Esquema común propuesto para la tabla de auditoría de negocio: `TimeGenerated` en UTC, `event_id` único, `actor_id` o identidad de servicio, `actor_type`, `role`, `action`, `resource_type`, `resource_id`, `client_id` cuando aplique, `outcome`, `reason_code`, `correlation_id`, `source_app` y `source_ip` cuando exista. En reclamos, la consulta por `client_id`/`resource_id` y período reúne el evento de acceso, la evidencia original y el acuse de alerta. Se registra el identificador del objeto, **sin copiar al log** el documento de identidad, el contenido de la guía, la posición completa, la temperatura en bruto, la firma, el video, credenciales o tokens. Se limita la exposición de IP y se restringe su consulta.

Los servicios producen los eventos en una tabla personalizada de Log Analytics mediante una regla de recopilación de datos y la API de ingesta de Azure Monitor, o mediante una canalización equivalente validada en la implementación. La identidad administrada de cada servicio obtiene permiso solo para escribir en esa regla. `event_id` permite detectar duplicados; se supervisan errores de envío y se reintentan sin bloquear la operación. La prueba de aceptación debe comprobar expresamente que un acceso denegado también queda registrado. Los diagnósticos de Azure no reemplazan estos eventos de aplicación.

## 3. Centralización y acceso a los registros

| Fuente | Configuración propuesta | Destino y propósito |
|---|---|---|
| Servicios de aplicación: despacho, portal, archivo y calidad | Instrumentación del evento de negocio anterior, incluida identidad y resultado | Tabla de auditoría de negocio del Log Analytics central |
| Azure Activity Log de las cinco suscripciones | Diagnóstico de ámbito de suscripción para cambios de recursos, RBAC y configuración | Mismo espacio; investigar quién cambió controles |
| Microsoft Entra ID | Diagnósticos de inicio de sesión y auditoría de identidad, categorías disponibles según licencia | Mismo espacio; corroborar autenticación, MFA y cambios de identidad |
| Azure Firewall, Application Gateway/WAF y flujos de red virtual | Categorías relevantes en modo de tabla específica por recurso cuando estén disponibles; evitar duplicados | Mismo espacio; tráfico, bloqueos y cambios de perímetro definidos en [#9](red-firewall-y-publicacion.md) |
| Cuentas Blob de evidencias y telemetría | Diagnósticos **del servicio Blob**, incluidas categorías de lectura, escritura y borrado; verificar los campos de identidad disponibles | Mismo espacio; contrastar acceso directo a objetos y cambios. Los registros no sustituyen el control de acceso de la aplicación |
| IoT Hub, Stream Analytics y alertas de temperatura | Categorías diagnósticas aplicables y eventos de alerta/acuse del servicio | Mismo espacio para investigación; la evidencia cruda y la tabla Delta siguen en las cuentas de datos de [#13](carga-b-telemetria.md) |
| Defender for Cloud | Alertas de seguridad y notificaciones según los planes definidos por [#10](seguridad-datos-personales-perimetro.md) | Investigación por seguridad; no se presume que activar Defender registre accesos de negocio |

La política P-04 de #5 aplica `DeployIfNotExists` a recursos compatibles y apunta al **mismo Log Analytics en `sub-fa-security`**. Hay que configurar aparte diagnósticos de ámbito de suscripción y de Entra ID, además de la instrumentación de aplicación. Se comprueba la compatibilidad de categorías, permisos y suscripciones cruzadas antes de habilitar la política. El equipo de plataforma valida cada mes que los recursos nuevos tengan diagnóstico y que lleguen eventos de ejemplo desde las cinco suscripciones; una ausencia de eventos es una alerta, no prueba de ausencia de accesos.

Seguridad conserva el control administrativo del espacio. Auditoría tiene lectura de las tablas que necesita y de las evidencias por un procedimiento autorizado; FinOps ve costos sin permisos de lectura de datos o logs sensibles. Las aplicaciones y desarrolladores no reciben lectura global del espacio. Las consultas de investigación y los cambios de retención quedan registrados; la matriz detallada de RBAC y MFA se alinea con #7.

## 4. Retención, integridad y eliminación

| Información | Ubicación | Retención propuesta | Consulta y salida |
|---|---|---|---|
| Evidencias de entrega y trazabilidad cruda de temperatura, alertas y acuses | Contenedores de evidencia de Blob del diseño de cargas | **Cinco años contractuales** con política de inmutabilidad bloqueada, según el servicio que la almacena | Acceso autorizado para reclamos; eliminación al vencer el plazo y si no hay obligación adicional |
| Eventos de acceso a datos de clientes, evidencias y lecturas de temperatura | Tabla de auditoría de negocio en Log Analytics | **Cinco años de retención total**, con **90 días consultables** para operación y el resto a largo plazo | Investigación histórica mediante búsqueda sobre retención a largo plazo; comprobar que el evento existe durante todo el plazo contractual |
| Eventos de acceso directo a Blob y cambios de identidad/permisos relevantes para esos tres tipos de acceso | Tablas de recurso, actividad e identidad seleccionadas | **Cinco años de retención total** para las categorías necesarias para reconstruir un reclamo; 90 días consultables inicialmente | Reducir categorías de alto volumen después de medir, sin perder las que prueban lectura, escritura, borrado y cambios de permisos |
| Diagnósticos de funcionamiento y tráfico sin relación directa con reclamos (por ejemplo, solicitudes permitidas del firewall) | Tablas técnicas del mismo espacio | **90 días** como propuesta inicial; los eventos de seguridad que exijan más tiempo se clasifican por tabla | Análisis operativo; no se les atribuye automáticamente la obligación contractual de cinco años |
| Posiciones de camiones y tabla analítica de temperatura | Tabla Delta de análisis descrita en #13 | Según [#10](seguridad-datos-personales-perimetro.md) y #13, con posibilidad de corregir y borrar datos personales cuando proceda | No se vuelcan masivamente al log ni a un contenedor inmutable de auditoría |

La retención en Log Analytics se fija **por tabla**, separando el período de consulta habitual de la retención total. El plazo de cinco años es una **decisión de diseño para la pista de auditoría relacionada con reclamos**; FríoAndes debe confirmar su alcance contractual y de protección de datos antes de bloquear una política de inmutabilidad. Si se abre un litigio o una investigación, seguridad preserva el conjunto concreto con el procedimiento de conservación aplicable y deja constancia de su entrega. Una política de retención de Log Analytics, por sí misma, no vuelve inmutables los logs: la evidencia contractual inmutable vive en los contenedores de Blob definidos por las cargas.

Se revisan mensualmente volumen, costos, consultas a registros antiguos y fechas de expiración. El borrado al vencimiento se implementa en el almacén correspondiente y se registra; no se crean copias permanentes en Fabric ni en informes descargados. Para los registros que contienen datos personales, #10 define las solicitudes de acceso, corrección y supresión y las excepciones justificadas por obligaciones contractuales.

## 5. Modelo de facturación interna

Azure Cost Management agrupa primero por suscripción y después por `costo`, `ambiente` y `carga` de #5. Cada cargo se cuenta **una sola vez**. Los costos de plataformas comunes y los cargos sin etiqueta se muestran durante la conciliación, para que el total de las líneas internas coincida con el total facturado. No se asignan importes ficticios: los presupuestos y valores monetarios se tomarán de [#25 a #28](https://github.com/frioandes-platform/planning/issues/28).

| Línea visible a finanzas | Regla para costos directos | Ejemplos |
|---|---|---|
| **Operación** | En `sub-fa-prod`, `costo=operacion`; incluir `carga=logistica` y `archivo` que soporta la operación | Consola, portal, base, archivo histórico |
| **Telemetría** | En `sub-fa-prod`, `costo=telemetria`, aunque IoT Hub se ubique en Central US | IoT Hub, Stream Analytics, función de alerta y cuentas de telemetría |
| **Pruebas** | Todo costo de `sub-fa-test` y `sub-fa-dev` se reporta en esta línea por `ambiente=test/dev`, incluso cuando `carga=telemetria` | Sensores simulados, cómputo temporal, WAF de pruebas |
| **Fabric** | Identificar aparte los cargos de la capacidad de Microsoft Fabric por **recurso y medidor de facturación** en Cost Management, en la suscripción que la aloje; excluirlos de Operación/Telemetría | Capacidad F y cargos asociados que identifique #27; no asumir que cada cargo admite etiquetas |
| **Compartido, antes de repartir** | `sub-fa-security` y `sub-fa-connectivity`, más recursos `costo=compartido` de otras suscripciones | Log Analytics central, firewall, VPN Gateway, DNS |

**Regla de reparto propuesta para el informe interno:** cada mes, después de excluir Fabric y Pruebas, calcular los costos directos de Operación (`O`) y Telemetría (`T`). Distribuir los costos compartidos (`S`) proporcionalmente: `Operación final = O + S × O/(O+T)` y `Telemetría final = T + S × T/(O+T)`. Se registra el valor de `O`, `T`, `S`, la regla aplicada y cualquier cargo no clasificado en la conciliación. Si `O+T=0`, se deja `S` como Compartido sin reparto. Es un criterio inicial de **showback**, sujeto a aprobación de FinOps; el porcentaje se sustituye por medidores de consumo más representativos si existen. Las reglas de asignación de Cost Management pueden hacer el reparto en el ámbito de facturación compatible; si no está disponible, se aplica al export mensual sin alterar la factura oficial. No se reparte ni se factura dos veces el mismo cargo.

La cuenta de evidencia de telemetría en Central US sigue siendo **Telemetría**, no un costo de infraestructura común. El historial del archivo de 1,2 PB sigue siendo **Operación**; si Fabric lo consulta mediante accesos directos, no se contabiliza una segunda copia del archivo. Los presupuestos por suscripción de #5 se mantienen (alertas propuestas al 80 %, 100 % y 120 % del gasto real, y 100 % previsto) y la vista de Fabric tiene presupuesto propio. Las alertas financieras no detienen recursos de despacho ni telemetría. La atribución se revisa con #27 y el consolidado de #28.

**Conciliación mensual:** FinOps exporta el costo real o amortizado de un período consistente; clasifica Fabric por recurso/medidor, luego dev/test, después producción por etiquetas, y finalmente reparte Compartido. Compara la suma final con el total del ámbito facturado, identifica cargos sin etiqueta o sin recurso y corrige la clasificación con un propietario. Las etiquetas de RG no se suponen heredadas automáticamente por los recursos: se aplican según #5; cuando un tipo no admite etiquetas se usa suscripción, RG y un registro de excepciones. Se documenta por separado cualquier compra de reserva o crédito que cambie el costo efectivo.

## 6. Verificación y decisiones abiertas

| Prueba para la implementación | Resultado que se debe demostrar |
|---|---|
| Consultar una guía propia y una ajena; leer una evidencia; consultar un intervalo de temperatura; reconocer una alerta | Los eventos permitidos y denegados tienen actor, objeto, hora UTC, resultado y correlación; la evidencia original se localiza sin guardar su contenido en el log |
| Acceder directamente a un blob y cambiar una regla de acceso | Los diagnósticos del servicio Blob y el Activity Log registran las operaciones; seguridad puede relacionarlas con el evento de negocio cuando hay correlación disponible |
| Simular alta de recurso en cada suscripción y pérdida de diagnóstico | P-04 y las configuraciones complementarias envían eventos al espacio de `sub-fa-security`; la falta de recepción genera incidencia |
| Buscar un evento fuera de los 90 días de consulta habitual | Se recupera mediante la retención a largo plazo antes de los cinco años; se prueba el procedimiento y su autorización |
| Comparar Cost Management con las cuatro líneas y el reparto | Operación + Telemetría + Pruebas + Fabric iguala el ámbito conciliado, incluyendo Compartido repartido y excepciones explicadas |

**Confirmaciones de FríoAndes:** responsable de auditoría y personas autorizadas; alcance exacto de los contratos de cinco años para los logs de acceso; procedimiento de conservación por litigio; ubicación definitiva de datos personales; suscripción y modalidad de compra de Fabric; presupuesto mensual y criterio de showback compartido. No se presenta ninguna prueba de consulta, costo o retención como ejecutada: este documento establece qué debe verificarse al implementar.

## 7. Referencias técnicas

- [Microsoft Learn — diagnósticos y destinos de Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/diagnostic-settings)
- [Microsoft Learn — políticas integradas para enviar diagnósticos a Log Analytics](https://learn.microsoft.com/en-us/azure/azure-monitor/platform/diagnostic-settings-policy-built-in)
- [Microsoft Learn — API de ingesta de logs de aplicación](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview)
- [Microsoft Learn — retención por tabla de Log Analytics](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-configure)
- [Microsoft Learn — supervisión de Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/blob-storage-monitoring-scenarios)
- [Microsoft Learn — asignación de costos compartidos](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/cost-allocation-introduction)
- [Microsoft Learn — facturación de la capacidad Fabric](https://learn.microsoft.com/en-us/fabric/enterprise/azure-billing)

# Cronograma general del proyecto

Este documento junta en un solo calendario todo el proyecto de FríoAndes, desde el diseño hasta el cierre: el diseño de la arquitectura, la construcción del código de infraestructura y del pipeline, el despliegue de los ambientes, las adaptaciones de la aplicación, la siembra del archivo, los 90 días de convivencia con el ensayo y el corte, el retiro de Zabbix, el apagado de Cali, el primer release de Fabric y el cierre. No cambia ninguna fecha ya decidida: las toma de los documentos que las fijan y completa con supuestos las fases que nadie había fechado.

## Contenido

1. Contexto y alcance
2. Hitos
3. Fases
4. Ruta crítica y holgura
5. Campañas y ventanas de cambio
6. Responsables
7. Si se mueve una fecha
8. Después del cierre
9. Supuestos

---

## 1. Contexto y alcance

### 1.1 De dónde salen las fechas

| Fecha o fase | Documento que la fija |
|---|---|
| Campañas, día 0, ensayo, corte, plazo de vuelta atrás, apagado de Cali y día 90 | `carga-c-migracion-y-campana.md`, secciones 4.1 a 4.3 |
| Preparación de la siembra, trabajos de discos, T0, T1 y conciliación | `carga-c-siembra-1-2pb.md`, sección 5 |
| Despliegue de pruebas y desarrollo el 1 de diciembre y de hub y producción el 14 de diciembre | `docs/costs/costo-migracion.md`, sección 4 |
| Retiro de Zabbix el día 61 y vigilancia de Azure Monitor desde el despliegue | `observabilidad-slo-zabbix.md`, sección 8 |
| Copia de la base hacia Fabric desde el corte y ajustes de la aplicación para Fabric antes del día 0 | `fabric-workspaces-ingesta-region.md`, secciones 4.4 y 4.6 |
| Primer y segundo release de los usos de IA, y medición de la capacidad después del primer mes | `fabric-acceso-casos-uso-costo.md`, secciones 6 y 8 |

Las fases que no tenían fecha (diseño, código de infraestructura, landing zone, adaptaciones, pruebas de carga, capacitación, preparación de Fabric y cierre) se fechan aquí con los supuestos de la sección 9.

### 1.2 Términos usados

| Término | Significado en este documento |
|---|---|
| Día N | Los días del plan de migración: día 0, inicio de la convivencia (11 de enero de 2027); día 34, corte; día 90, límite de la convivencia |
| Hito | Fecha que cierra una fase y abre la siguiente. Si se mueve, se mueve lo que depende de ella |
| Ruta crítica | Cadena de fases sin holgura: un día de atraso en cualquiera atrasa el corte |
| Holgura | Días que una fase puede atrasarse sin mover la fase siguiente |
| Cambio productivo | Cambio sobre algo que usan despacho, calidad o los clientes. Solo de 22:00 a 04:00 y fuera de campaña, salvo incidente |

---

## 2. Hitos

| Hito | Fecha | Qué cierra | Quién lo aprueba |
|---|---|---|---|
| Arranque del proyecto | Lunes 28 de septiembre de 2026 | — | Gerencia de FríoAndes |
| Arranque de la siembra | Martes 13 de octubre | Compra de discos y estaciones aprobada por separado (sección 4.1) | Gerencia y arquitecto cloud |
| **Diseño y presupuesto aprobados** | Viernes 13 de noviembre | Fase 1 (arquitectura), Fase 3 (costos) y Fase 4 (plantillas de cambio) | Arquitecto cloud del cliente y gerencia |
| Pruebas y desarrollo desplegados | Martes 1 de diciembre | Código de infraestructura y pipeline (Fase 2) | Equipo de plataforma |
| Hub y producción desplegados | Lunes 14 de diciembre | Landing zone y red de producción, sin usuarios | Comité de cambios |
| Listo para el día 0 | Viernes 8 de enero de 2027 | Adaptaciones probadas, prueba de carga, capacitación de operación | Comité de cambios |
| **Día 0** | Lunes 11 de enero | Inicio de la convivencia | Comité de cambios |
| Siembra conciliada | Viernes 29 de enero | Archivo completo en Azure, salvo la copia continua | Base de datos y migración |
| **Ensayo del corte** | Domingo 31 de enero, 01:00 a 03:00 | Criterios del ensayo cumplidos | Líder del corte |
| **Corte** | Domingo 14 de febrero, 01:00 a 03:00 | Azure pasa a ser la plataforma principal | Comité de cambios y líder del corte |
| Cierre del plazo de vuelta atrás | Lunes 8 de marzo (día 56) | Ya no se vuelve a Cali | Comité de cambios |
| Fabric en producción | Viernes 12 de marzo | Primer release de los tres usos de IA | Equipo de datos e IA y calidad |
| **Cali apagada** | Domingo 14 de marzo (día 62) | Zabbix retirado el día 61 y VMware el 62 | Equipo de plataforma |
| Día 90 | Domingo 11 de abril | Límite de la convivencia | — |
| **Cierre del proyecto** | Viernes 30 de abril | Entrega a operación, informe de cierre y lecciones aprendidas | Gerencia de FríoAndes |

---

## 3. Fases

![Cronograma general del proyecto, de septiembre de 2026 a mayo de 2027](diagramas/cronograma-proyecto.drawio.png)

| Fase | Fechas | Responsable | Qué incluye | Depende de |
|---|---|---|---|---|
| Arquitectura | 28 de septiembre al 30 de octubre de 2026 | Arquitecto cloud | Los documentos de la Fase 1 (#5 a #18) y este documento | — |
| Costos y cambio | 31 de octubre al 13 de noviembre | Arquitecto cloud | Costo de la migración, del mes estable y de campaña, de Fabric y del proyecto completo (Fase 3); plantillas de release notes (Fase 4) | Arquitectura |
| Gestión del proyecto | 28 de septiembre al 30 de abril de 2027 | Gerente de proyecto | Seguimiento semanal, riesgos, presupuesto, comité de cambios y comunicación con FríoAndes | — |
| Código de infraestructura y pipeline | 19 de octubre al 27 de noviembre | Equipo de plataforma | Módulos de red, seguridad y cómputo, pipeline con aprobación y bloqueo de la ventana, `plan` limpio (#20 a #24) | Diseño de red y firewall (#8, #9) |
| Landing zone, identidades y políticas | 2 al 27 de noviembre | Equipo de plataforma | Grupos de administración, cinco suscripciones, Azure Policy, etiquetas, presupuestos, grupos de Entra ID, MFA, acceso condicional y PIM (#5 a #7) | Diseño de gobierno y seguridad |
| Despliegue de los ambientes | 1 al 4 de diciembre (pruebas y desarrollo) y 14 al 18 de diciembre (hub y producción) | Equipo de plataforma | Todo desde el pipeline. Producción queda encendida al mínimo y sin usuarios hasta el día 0 | Código de infraestructura y landing zone |
| Observabilidad | 14 de diciembre al 14 de marzo | Equipo de plataforma | Azure Monitor, alertas y tableros desde el despliegue; Zabbix sigue vigilando Cali hasta el día 61 | Despliegue de producción |
| Adaptaciones de la aplicación | 2 de noviembre al 18 de diciembre (desarrollo) y 19 de diciembre al 8 de enero (pruebas) | Equipo de aplicación | Evidencias en Blob sin NFS, compatibilidad con MySQL 8.4, contenedores, columnas y borrado lógico para Fabric | Diseño de la plataforma (#12) y de Fabric (#17) |
| Pruebas de carga, seguridad y continuidad | 28 de diciembre al 8 de enero | QA | 2.000 solicitudes por minuto en el portal, WAF en modo detección y luego prevención, prueba de la réplica en Central US | Adaptaciones en pruebas y producción desplegada |
| Siembra del archivo | 13 de octubre al 29 de enero | Base de datos y migración | Preparación, nueve trabajos de discos, diferencial y conciliación (#15) | Compra de discos aprobada |
| Convivencia: centros y telemetría | 11 al 30 de enero | Equipo de plataforma | Túneles, centros uno por uno, sensores y camiones en IoT Hub, fin de la carga por lote | Día 0 |
| Replicación de la base | 16 de enero al 14 de febrero | Base de datos y migración | Carga inicial con DMS, réplica, alta disponibilidad y réplica en Central US | Día 0 |
| Ensayo y corte | 31 de enero y 14 de febrero | Líder del corte | Corte completo sobre un servidor temporal, y luego el corte real | Siembra conciliada y réplica al día |
| Vuelta atrás y apagado de Cali | 15 de febrero al 14 de marzo | Equipo de plataforma | 21 días con Cali intacta y en espera; apagado en el orden de `carga-c-migracion-y-campana.md`, sección 6.3 | Corte |
| Microsoft Fabric, primer release | 18 de enero al 12 de febrero (no productivo) y 15 de febrero al 12 de marzo (producción) | Equipo de datos e IA | Capacidades, espacios, gateway, Copy Job, accesos directos al archivo, Activator, hora estimada de llegada y fotos ilegibles | Corte (la copia lee la base de Azure) |
| Medición de Fabric | 29 de marzo al 23 de abril | Equipo de datos e IA | Uso real de la capacidad después del primer mes; decisión de pasar a F8 fuera de campaña | Fabric en producción |
| Capacitación y gestión del cambio | 30 de noviembre al 8 de enero (operación y guardia) y 17 al 30 de enero (usuarios clave) | Gestión del cambio | Operación de Azure, runbooks, guardia nocturna; pruebas de los usuarios clave de despacho y facturación con datos replicados; avisos a clientes | Despliegue de pruebas |
| Estabilización | 15 de marzo al 11 de abril | Gerente de proyecto | Semana Santa sin cambios; lo pendiente se cierra del 29 de marzo al 11 de abril | Cali apagada |
| Cierre | 12 al 30 de abril | Gerente de proyecto | Entrega a operación, ajuste de tamaños tras el primer mes (registros del firewall, Fabric), compra de reservas, informe de cierre y lecciones aprendidas | Estabilización |

---

## 4. Ruta crítica y holgura

### 4.1 La siembra es la ruta más larga

La ruta crítica es la del archivo: **preparación de la siembra → nueve trabajos de discos → conciliación → ensayo → corte → plazo de vuelta atrás → apagado de Cali**. Dura del 13 de octubre al 14 de marzo y tiene muy poca holgura:

| Paso | Termina | Lo necesita | Holgura |
|---|---|---|---|
| Conciliación de la siembra | 29 de enero | Ensayo del 31 de enero | 2 días |
| Ensayo | 31 de enero | Corte del 14 de febrero | Una semana de reserva (7 de febrero) |
| Corte | 14 de febrero | Día 90 (11 de abril) | Hasta el 7 de marzo (`carga-c-migracion-y-campana.md`, sección 4.4) |

Por eso la siembra arranca el 13 de octubre, un mes antes de que se apruebe el diseño completo. La compra de discos y estaciones se aprueba por separado: no depende de ninguna otra decisión del diseño y es la única fase que, si espera la aprobación del 13 de noviembre, empuja el corte más allá del 7 de marzo.

### 4.2 La segunda cadena: la plataforma

**Código de infraestructura → despliegue de pruebas y desarrollo → adaptaciones probadas → prueba de carga → día 0.**

| Paso | Termina | Lo necesita | Holgura |
|---|---|---|---|
| Código de infraestructura y pipeline | 27 de noviembre | Despliegue de pruebas, 1 de diciembre | 3 días |
| Despliegue de hub y producción | 18 de diciembre | Prueba de carga, 28 de diciembre | 9 días |
| Adaptaciones en pruebas y prueba de carga | 8 de enero | Día 0, 11 de enero | 2 días; luego, el día 0 puede correrse hasta el 1 de febrero |

Esta cadena se puede atrasar más que la siembra, porque el día 0 se corre sin romper el día 90 mientras el corte no pase del 7 de marzo. Pero durante la convivencia la base no admite cambios de esquema: cualquier adaptación que no esté lista el día 0 espera hasta después del corte.

---

## 5. Campañas y ventanas de cambio

| Campaña | Fechas supuestas | Qué pasa en el proyecto |
|---|---|---|
| Fin de año | 15 de noviembre de 2026 al 10 de enero de 2027 | Se construye y se despliega, pero nada que use la operación: producción queda sin usuarios hasta el día 0. La siembra solo lee el servidor de archivo |
| Semana Santa | 15 al 28 de marzo de 2027 | Ningún cambio. Cali ya está apagada desde el 14 de marzo y la medición de Fabric empieza después, el 29 de marzo |
| Mitad de año | 15 de junio al 15 de julio de 2027 | Después del cierre. Es la primera campaña completa en Azure, y la capacidad de Fabric sube a F16 una semana antes si ya pasó a F8 |

Los cambios productivos van de 22:00 a 04:00, fuera de campaña, y los aprueba el comité de cambios con la plantilla de release notes que corresponde (aplicación o infraestructura). El pipeline bloquea el despliegue automático a producción fuera de esa ventana (#23).

**Desplegar en campaña no es un cambio productivo.** El despliegue de hub y producción del 14 de diciembre cae dentro de la campaña de fin de año, pero producción no tiene usuarios hasta el día 0. Las conexiones hacia Cali, que sí tocan la operación, no se abren hasta el día 0, ya fuera de campaña.

---

## 6. Responsables

Los responsables son roles, no personas: FríoAndes los asigna a su equipo o a un proveedor. El costo de cada rol por fase va en el costo total del proyecto (#28).

| Rol | Responde por | Fases principales |
|---|---|---|
| Gerente de proyecto | Calendario, presupuesto, riesgos, comité de cambios, informe de cierre | Todo el proyecto |
| Arquitecto cloud | Diseño, coherencia entre documentos, decisiones de arquitectura y aprobación técnica de cambios | Arquitectura, costos y cambio; acompaña el ensayo y el corte |
| Equipo de plataforma | Código de infraestructura, pipeline, landing zone, red, firewall, observabilidad y apagado de Cali | Fase 2, despliegue, convivencia y apagado |
| Equipo de aplicación | Adaptaciones de los cinco contenedores y del front; pruebas funcionales | Adaptaciones, ensayo y corte |
| Base de datos y migración | DMS, compatibilidad con MySQL 8.4, siembra y conciliación del archivo | Siembra, replicación, ensayo y corte |
| QA | Pruebas de carga, de seguridad y de continuidad; criterios del ensayo | Pruebas y ensayo |
| Equipo de datos e IA | Capacidades y espacios de Fabric, Copy Job, Activator, hora estimada de llegada y evidencias | Fabric |
| Gestión del cambio | Capacitación de operación y de usuarios, avisos a despacho, calidad y clientes | Capacitación y convivencia |
| Líder del corte | Guion del corte, decisión de seguir o volver atrás | Ensayo y corte |

---

## 7. Si se mueve una fecha

| Si pasa esto | Qué se hace |
|---|---|
| La compra de discos no se aprueba el 13 de octubre | Cada semana de atraso mueve la conciliación una semana. Con más de una semana, el ensayo pasa al 7 de febrero y el corte al 21 (`carga-c-migracion-y-campana.md`, sección 4.4) |
| El diseño no se aprueba el 13 de noviembre | La construcción sigue, porque no toca la operación, pero el despliegue de pruebas se corre. Con más de tres semanas de atraso, el día 0 pasa al 18 o al 25 de enero y el corte sigue dentro del 7 de marzo |
| El código de infraestructura no está el 27 de noviembre | Se despliega primero lo que esté listo (red y seguridad) y el cómputo después; el despliegue de producción del 14 de diciembre tiene 9 días de holgura hasta la prueba de carga |
| El ensayo no cumple los criterios | Se repite el 7 de febrero y el corte pasa al 21 de febrero. Cali se apaga el 29 de marzo, después de Semana Santa, y el cierre del proyecto se mantiene |
| El corte se atrasa más de dos semanas | El primer release de Fabric pasa a después de Semana Santa (29 de marzo al 23 de abril) y la medición de la capacidad a mayo. El cierre del proyecto se corre hasta el 28 de mayo, antes de la campaña de mitad de año |

---

## 8. Después del cierre

Quedan fuera del proyecto y pasan a la operación o a un proyecto nuevo:

| Tema | Cuándo | Documento |
|---|---|---|
| Segundo release de Fabric: pronóstico de temperatura y análisis de clips de video de reclamos | Después de la campaña de mitad de año | `fabric-acceso-casos-uso-costo.md`, sección 3.5 |
| Segunda nube | Horizonte de 24 meses, cuando haya una necesidad aprobada | `red-acceso-remoto-segunda-nube.md` |
| Revisión de reservas y tamaños | Cada trimestre, con los datos de Cost Management | `gobierno-auditoria-facturacion.md` y `docs/costs/` |
| Pruebas de continuidad hacia Central US | Cada semestre | `carga-a-plataforma-logistica.md`, sección 6 |

---

## 9. Supuestos

| Supuesto | Por qué se asume |
|---|---|
| El proyecto arranca el lunes 28 de septiembre de 2026 | Es la semana en que empezó el diseño; el enunciado no da fecha de inicio |
| La Fase 1 dura cinco semanas y los costos y el cambio dos más, con aprobación el viernes 13 de noviembre | Deja la aprobación antes de la campaña de fin de año y un mes completo para construir |
| La compra de discos y estaciones se aprueba por separado el 13 de octubre | La siembra es la ruta crítica y no depende del resto del diseño |
| El código de infraestructura y la landing zone se construyen en seis semanas, del 19 de octubre al 27 de noviembre | Cuatro módulos, un pipeline y un `plan` limpio con el equipo de plataforma; el diseño de red ya fija direcciones y reglas |
| Las adaptaciones de la aplicación toman siete semanas en desarrollo y tres en pruebas | Son cambios acotados: evidencias en Blob, MySQL 8.4, columnas y borrado lógico para Fabric |
| Fabric se prepara en no productivo durante la convivencia y entra a producción después del corte | La copia de la base lee la base de Azure, que solo es la principal desde el corte |
| El proyecto se cierra el 30 de abril de 2027, tres semanas después del día 90 | Tiempo para entregar a operación, ajustar tamaños con el primer mes de datos y documentar |
| Los responsables son roles, no personas | FríoAndes decide si los cubre su equipo o un proveedor; el costo por rol va en #28 |

![FríoAndes](../design/brand/logo/logo-principal.png)

# Nota de versión de infraestructura: ejemplo diligenciado

Ejemplo real de `plantilla-release-notes-infraestructura.md`: el corte de la migración del domingo 14 de febrero de 2027, el cambio de infraestructura más sensible del proyecto. Toma el plan de `carga-c-migracion-y-campana.md` (secciones 4 a 6) sin cambiarlo. El corte se aprueba y se avisa igual que cualquier otro cambio, con una diferencia que la nota dice sin rodeos: **volver atrás solo es limpio hasta las 02:30**. Después, la base de Azure ya recibió escrituras reales que MySQL no puede devolver a la 5.7 de Cali.

---

## Nota de versión RN-INF-2027-007

| Campo | Valor |
|---|---|
| Título | Corte de la migración: la base transaccional y el tráfico de despacho y rastreo pasan de Cali a Azure |
| Tipo de cambio | Corte, con cambios de datos (base), de cómputo (réplicas) y de red (DNS y reglas temporales) |
| Ambientes y suscripciones | `sub-fa-prod` y `sub-fa-connectivity` en Azure; base, aplicación y DNS de Cali |
| Solicitante | Gerencia del proyecto de migración |
| Responsable técnico | Líder del corte |
| Pull request y `plan` | `frioandes-platform/iac` #87, con dos `plan` de producción publicados por el pipeline. **Plan A, réplicas** (01:40): 0 para crear, 8 para cambiar, 0 para destruir. **Plan B, retiro de lo temporal de la migración** (03:10, solo si se sigue): 0 para crear, 0 para cambiar, 4 para destruir |
| Estado | Cerrada |

### 1. Qué cambia

**Para la operación.** Desde las 04:00 del domingo 14 de febrero, la torre de control despacha sobre Azure y los clientes consultan el portal en Azure. Las direcciones y el inicio de sesión no cambian para nadie. Cali queda intacta y sin tráfico durante 21 días, como contingencia.

**Técnicamente.**

| Recurso o módulo | Cambio | ¿Se puede deshacer con un `apply`? |
|---|---|---|
| Base: DMS y MySQL Flexible Server 8.4 | DMS termina la replicación desde Cali y Flexible Server pasa a ser la base principal, con escrituras | **No.** Una actividad de DMS terminada no se reanuda: otro intento exige una actividad nueva desde el principio. Después de las 02:30, las escrituras en Azure no vuelven a Cali |
| Base de Cali | Pasa a `read_only` y `super_read_only` a la 01:00 | Sí, manualmente, durante la ventana |
| `modules/compute`: 6 aplicaciones del entorno de la torre y 2 del portal (Plan A) | Del mínimo sin usuarios a su número normal de réplicas: 13 en la torre y 4 en el portal | Sí: se revierte el commit y se aplica |
| DNS público del portal | De la IP de Cali (NAT y Nginx) a la IP del Application Gateway. El TTL se bajó a 5 minutos el martes 9 de febrero | Sí: el registro vuelve a la IP de Cali, que sigue configurada 21 días |
| DNS interno de la torre, en el DNS de Cali | De los servidores de aplicación de Cali al entorno de la torre en Azure, con TTL de 5 minutos | Sí, ídem |
| `modules/security`: FW-501, FW-502 y su pareja en el NSG de `snet-data`; cuenta de almacenamiento de la migración y su token (Plan B) | Se retiran | **No del todo.** Las reglas se pueden recrear con un `apply`, pero la cuenta de la migración se borra con su contenido, que ya no se necesita |

**Lo que no cambia.**

- **La telemetría.** IoT Hub, Stream Analytics y la función notificadora ya funcionan en Azure desde antes del día 0, y la alerta a la guardia de calidad sigue llegando durante toda la madrugada.
- **El archivo de 1,2 PB.** Ya está sembrado y conciliado desde el 29 de enero. En el corte solo se copian unos 17 GB de la última hora, en paralelo con la validación.
- **Las reglas temporales FW-503 y FW-504 y la VPN de los centros hacia Cali.** Siguen hasta el cierre del plazo de vuelta atrás, el 8 de marzo.
- **Fabric.** Empieza a copiar la base de Azure después del corte.

**Pruebas hechas.**

- **Ensayo del domingo 31 de enero, de 01:00 a 03:00,** sobre el servidor temporal de `snet-data` de producción, con el portal en un nombre de prueba (`carga-c-migracion-y-campana.md`, sección 5.2):
  - el retraso de DMS llegó a cero en 3 minutos;
  - la validación de conteos y sumas tomó 17 minutos, sin diferencias;
  - las pruebas de humo tomaron 26 minutos y pasaron completas;
  - la decisión de seguir se tomó a las 02:19;
  - se cumplieron todos los criterios, así que no hizo falta la reserva del 7 de febrero.
- **El Plan A se aplicó en pruebas** el 2 de febrero. El `plan` de producción coincide con el de pruebas, salvo el número de réplicas.
- **El Plan B pasó `verify_firewall_policy.py`**, sin errores, con FW-501 y FW-502 retiradas de `firewall-policy.csv`.

### 2. Ventana

| Campo | Valor |
|---|---|
| Fecha | Sábado 13 y domingo 14 de febrero de 2027 |
| Hora, Colombia | Congelamiento desde el sábado 22:00. Mantenimiento de 01:00 a 03:00 del domingo. Monitoreo reforzado hasta las 06:00 |
| Hora, UTC | Congelamiento desde las 03:00 del domingo. Mantenimiento de 06:00 a 08:00 |
| Duración prevista | Hasta 2 horas de mantenimiento; la ventana completa va de las 22:00 a las 04:00 |
| Interrupción del servicio | La torre queda en solo lectura y el portal muestra un aviso de mantenimiento de 01:00 a 03:00, como máximo. La alerta de temperatura no se interrumpe |
| ¿Fuera de campaña? | Sí. La campaña de fin de año terminó el 10 de enero y Semana Santa empieza el 15 de marzo |
| ¿Excepción por incidente? | No |
| Fechas de reserva si se suspende | Domingos 21 y 28 de febrero, a la misma hora. El corte no puede pasar del domingo 7 de marzo (`carga-c-migracion-y-campana.md`, sección 4.4) |

La hora de 03:00 a 04:00 queda libre para resolver cualquier problema antes de que empiece el despacho.

### 3. Impacto

| Pregunta | Respuesta |
|---|---|
| ¿Qué servicios se afectan? | La torre de control (despacho, inventario, facturación y evidencias) y el portal de rastreo. Tocan la base, la aplicación, el DNS y reglas temporales del firewall |
| ¿Hay interrupción o degradación durante la ventana? | Sí: la torre en solo lectura y el portal en mantenimiento, de 01:00 a 03:00 como máximo. A esa hora el despacho no trabaja y el portal recibe unas 20 solicitudes por minuto |
| ¿Puede cortar la alerta de temperatura? | No. La telemetría ya corre en Azure y no participa del corte. La guardia de calidad tiene un contacto directo con el equipo del corte |
| ¿Toca datos personales, cifrado o accesos? | Sí: la base con datos personales cambia de lugar. Llega cifrada, con DMS por la VPN, a un servidor con cifrado en reposo y endpoint privado. El inicio de sesión con Entra ID y MFA no cambia |
| ¿Cambia el costo mensual? | Sí: desde el corte, Azure deja de ser costo de la migración y pasa a costo recurrente, unos USD 17.240 al mes (`costo-mes-estable-y-campana.md`) |
| Riesgo | Alto, por ser el único cambio con un punto de no retorno. Lo mitigan el ensayo completo, los criterios cerrados para seguir y la vuelta atrás limpia hasta las 02:30 |

### 4. Aprobación

| Rol | Decisión | Fecha |
|---|---|---|
| Gerencia de operaciones (comité de cambios) | Aprobado, con el reporte del ensayo y los criterios para seguir | Lunes 8 de febrero de 2027 |
| Líder técnico (comité de cambios) | Aprobado | Lunes 8 de febrero de 2027 |
| Responsable de calidad (comité de cambios) | Aprobado, con el contacto de la guardia de calidad confirmado | Lunes 8 de febrero de 2027 |
| Equipo de redes, por el DNS y las reglas del hub | Aprobado | Lunes 8 de febrero de 2027 |
| Aprobación adicional, por lo que no se puede deshacer con un `apply` (base y cuenta de la migración) | Aprobado por la gerencia de FríoAndes | Martes 9 de febrero de 2027 |
| Seguridad | No aplica: no es una excepción por incidente. Revisó el Plan B | Lunes 8 de febrero de 2027 |

Los dos `plan` quedaron aprobados en el Environment de producción de GitHub. En la ventana, el líder del corte decide si se sigue o se vuelve atrás en los dos puntos de decisión del guion, sin volver al comité.

### 5. Pasos y verificación durante la ventana

| Hora | Paso | Responsable | Cómo se comprueba |
|---|---|---|---|
| Martes 9 de febrero | TTL del DNS público del portal y del DNS interno de la torre a 5 minutos | Red | Consulta del TTL desde Cali y desde internet |
| Sábado 22:00 | Congelamiento de cambios en Cali y en Azure | Líder del corte | Pipeline sin despliegues pendientes; ningún cambio en curso en Cali |
| Sábado 22:00 | Revisión del retraso de DMS y de la réplica de Central US | Base de datos | Retraso de DMS cercano a cero; réplica de Central US al día |
| 00:30 | Volcado completo de la base de Cali, el respaldo de vuelta atrás | Base de datos | Volcado terminado y con su suma de verificación |
| 00:55 | **Primera decisión:** seguir o suspender | Líder del corte | Están las 8 personas, el volcado terminó y DMS va al día. Si no, se suspende y se pasa al 21 de febrero |
| 01:00 | La aplicación de Cali entra en modo de mantenimiento y la base de Cali queda en `read_only` y `super_read_only` | Aplicación, base de datos | Aviso visible en el portal. Una escritura de prueba en Cali es rechazada |
| 01:05 | Se espera a que DMS marque cero segundos de retraso y se anota la posición final del binlog | Base de datos | Métrica de DMS |
| 01:10 | Corte en DMS | Base de datos | La actividad termina sin errores |
| 01:20 | Validación de datos y, en paralelo, última sincronización del archivo | Base de datos, archivo | Conteo de filas de todas las tablas y suma de verificación de guías, inventario y facturas, iguales en Cali y en Azure. Archivo: la última pasada termina sin errores |
| 01:40 | **Plan A** por el pipeline: las 8 aplicaciones pasan a su número normal de réplicas y abren escrituras contra Flexible Server | Aplicación | Chequeos de salud en verde |
| 01:50 | Cambio de DNS: el portal pasa al Application Gateway y la torre al entorno de Azure | Red | Resolución correcta desde Cali, desde un centro y desde internet |
| 01:55 | Pruebas de humo con el cliente de prueba | Usuarios clave de despacho y facturación, pruebas | Inicio de sesión en la torre con Entra ID y MFA desde Cali y desde un centro; creación de una guía de prueba; consulta de esa guía en el portal; carga y consulta de una evidencia; consulta de una factura. Lista firmada |
| 02:25 | **Segunda decisión:** seguir o volver atrás | Líder del corte, con despacho y calidad | Criterios de la sección 8.4 |
| 02:30 | Si se sigue: se borran los datos del cliente de prueba y se abre el servicio. **Punto de no retorno.** Si se vuelve atrás: sección 7 | Aplicación | Torre y portal aceptan escrituras reales |
| 03:00 | Fin del mantenimiento. Monitoreo reforzado hasta las 06:00 | Todos | Azure Monitor: sin errores 5xx en el Application Gateway, réplicas estables, retraso de la réplica de Central US bajo 15 minutos |
| 03:10 | **Plan B** por el pipeline: se retiran FW-501, FW-502 y su pareja en el NSG, y la cuenta de almacenamiento de la migración con su token | Red | `apply` sin errores; la tabla de políticas sin esas reglas |
| 04:00 | Empieza el despacho sobre Azure | Despacho | La torre de control confirma la operación a las 04:30 |
| Lunes 15 de febrero, 22:00 | Se elimina el servicio DMS, con la validación firmada. Cierre de la copia continua del archivo y retiro de la regla temporal del NSG de `snet-archive` | Base de datos, red | Fuera de esta nota: van en RN-INF-2027-008 |

### 6. Aviso a despacho, a calidad y a clientes

| A quién | Qué se le dice | Cuándo | Por dónde |
|---|---|---|---|
| Comité de cambios: gerencia de operaciones, responsable de calidad y líder técnico | Pedido de aprobación con el guion, el reporte del ensayo y los criterios para seguir | Lunes 8 de febrero | Reunión del comité y esta nota |
| Torre de control (despacho) | La torre queda en solo lectura de 01:00 a 03:00 del domingo 14. A las 04:00 abre en Azure, con la misma dirección y el mismo inicio de sesión de Entra ID. Ante cualquier problema, se llama al canal del corte | Domingo 7 de febrero y sábado 13 de febrero | Correo, canal de la torre en Teams y cartelera de la torre |
| Guardia de calidad | La alerta de temperatura no cambia y sigue llegando por los mismos canales. Durante el corte tiene un contacto directo con el equipo | Domingo 7 de febrero y a las 00:55 del domingo 14 | Canal de guardia en Teams y llamada del líder del corte |
| Centros | La torre queda en solo lectura de 01:00 a 03:00. La conexión de los centros no cambia | Domingo 7 de febrero | Correo a los jefes de centro |
| Clientes corporativos | El portal queda en mantenimiento el domingo 14 de febrero de 01:00 a 03:00 | Domingo 7 de febrero | Correo a los contactos de cada cliente y aviso en el portal |
| Equipo del corte | Guion, turnos y canal del corte | Después del ensayo, el lunes 1 de febrero | Reunión y canal del corte |

**Equipo del corte, ocho personas:** el líder del corte, base de datos, red, dos de aplicación, pruebas y dos usuarios clave (despacho y facturación). Lo acompaña el partner de Microsoft (`costo-total-proyecto.md`, sección 3.3).

### 7. Cómo se vuelve atrás

La vuelta atrás depende de la hora. La nota lo dice así porque no es lo mismo antes y después del punto de no retorno:

| Momento | Qué se hace | ¿Se pierden datos? (RPO de 15 minutos) | ¿Cuánto tarda en volver el servicio? (RTO de 4 horas) |
|---|---|---|---|
| **Antes de la 01:00** (primera decisión) | Se suspende. Nada cambió todavía | No | No hubo interrupción |
| **De 01:00 a 02:30** | **Vuelta atrás limpia**, en cuatro pasos (`carga-c-migracion-y-campana.md`, sección 5.5): los dos registros de DNS vuelven a Cali; la base de Cali sale de `read_only`; la aplicación de Cali sale del modo de mantenimiento; en Azure, las aplicaciones vuelven a su mínimo y la base de Azure se descarta | **No.** Cali no recibió escrituras desde la 01:00 y Azure solo recibió los datos del cliente de prueba | Menos de 30 minutos. El servicio vuelve antes de las 03:00, dentro de la ventana de mantenimiento |
| **Después de las 02:30** | **No hay vuelta atrás limpia.** Las salidas, en este orden (sección 6.2): 1) corregir en Azure; 2) pasar a Central US con el runbook de continuidad, si lo que falla es la región; 3) volver a Cali, solo si lo decide el comité de cambios ante una falla que impida despachar | 1) No. 2) Hasta 15 minutos: la réplica de Central US tiene alerta si su retraso pasa de ese umbral. 3) Lo creado en Azure se recarga en Cali con la exportación de la aplicación; lo que la exportación no cubra se vuelve a digitar | 1) Según la falla. 2) Hasta 4 horas: es el tiempo del runbook. 3) Horas; no tiene un tiempo comprometido y por eso es la última salida |

| Campo | Valor |
|---|---|
| Método | Hasta las 02:30, la vuelta atrás limpia de la tabla. Después, las tres salidas en ese orden |
| Cuánto tarda | Menos de 30 minutos hasta las 02:30 |
| Criterios para volver atrás | Que falle cualquiera de los criterios de la sección 8.4. No se discute: si uno falla, se vuelve atrás |
| Quién decide | El líder del corte, con despacho y calidad, a las 02:25. Después de las 02:30, el comité de cambios decide si se vuelve a Cali |
| Hasta cuándo es limpio | Hasta las **02:30**. Si a las 02:30 no hay decisión, se vuelve atrás |
| ¿Se pierde algún dato? | Hasta las 02:30, no. Después, depende de la salida (tabla anterior) |
| ¿Cuánto tarda en volver el servicio? | Hasta las 02:30, antes de las 03:00. Después, hasta 4 horas con Central US |
| Lo que no se deshace con un `apply` | El corte de DMS: otro intento exige una actividad nueva y una carga inicial completa, lo que lleva el corte a una fecha de reserva. La cuenta de la migración, que solo se borra si se siguió (Plan B, 03:10) |

**Por qué no hay replicación de vuelta.** MySQL no replica de 8.4 hacia 5.7, así que Cali no puede seguir recibiendo lo que pasa en Azure (`carga-c-migracion-y-campana.md`, sección 3.5). Por eso Cali queda congelada en el estado de las 01:00, con el volcado de las 00:30 como respaldo, y por eso la vuelta a Cali después del corte no es limpia.

### 8. Sección por tipo de cambio

#### 8.4 Corte

| Pregunta | Respuesta |
|---|---|
| Qué cubre y qué no | Cubre la base transaccional y el tráfico de despacho y rastreo. No cubre la copia del archivo de 1,2 PB, sembrada y conciliada antes, ni la telemetría, que ya corre en Azure |
| Ensayo | Domingo 31 de enero de 2027, de 01:00 a 03:00, sobre el servidor temporal. Cumplió todos los criterios; la decisión de seguir se tomó a las 02:19 (sección 1) |
| Guion | Sección 5 de esta nota, igual a `carga-c-migracion-y-campana.md`, sección 5.3 |
| Criterios para seguir | 1) DMS terminó el corte sin errores. 2) Conteos y sumas de verificación iguales en Cali y en Azure. 3) Pruebas de humo completas y firmadas. 4) Las aplicaciones responden su chequeo de salud y no hay errores 5xx en el Application Gateway. 5) La réplica de Central US está al día. 6) Son las 02:30 o antes |
| Punto de no retorno | 02:30, cuando se abre el servicio con escrituras reales. Antes, la vuelta atrás es limpia; después, no (sección 7) |
| Equipo y canal | Ocho personas (sección 6), con el partner de Microsoft; canal del corte en Teams y puente telefónico |
| Fechas de reserva | Domingos 21 y 28 de febrero. Como máximo, el 7 de marzo |

**Datos (sección 8.3), lo que aplica al corte:**

- **Respaldo previo:** el volcado completo de las 00:30, guardado en Cali, y la base de Cali congelada en solo lectura.
- **Esquema:** congelado en Cali desde el arranque de DMS, el 16 de enero; no cambia en el corte.
- **Réplica de Central US:** al día antes de empezar y como criterio para seguir.
- **Inmutabilidad:** no se toca ningún contenedor del archivo.

**Red y firewall (sección 8.1), lo que aplica al corte:**

- **Reglas que se retiran:** FW-501, FW-502 y su pareja en el NSG de `snet-data`, todas temporales de la migración. FW-503, FW-504 y los grupos 400 y 500 siguen hasta el 8 de marzo.
- **DNS:** los dos registros, con TTL de 5 minutos desde el martes 9.
- **Verificador:** `verify_firewall_policy.py` sin errores en el pull request del Plan B.
- **Telemetría de los cuartos fríos:** no se afecta, porque entra por la VPN de cada centro hacia Azure, que no cambia.

### 9. Cierre

| Campo | Valor |
|---|---|
| Resultado | Ejecutada, sin volver atrás |
| Hora real de inicio y fin | Mantenimiento de 01:00 a 02:41 del domingo 14 de febrero de 2027. Segunda decisión a las 02:22 |
| Incidentes o desviaciones | La validación tomó 19 minutos, 2 más que en el ensayo, dentro de los 20 previstos. Ningún criterio falló |
| Pendientes | RN-INF-2027-008: eliminar DMS, cerrar la copia continua y retirar la regla temporal de `snet-archive` (lunes 15 de febrero). Cierre del plazo de vuelta atrás y retiro de FW-503, FW-504 y los grupos 400 y 500 (lunes 8 de marzo) |
| Cerrada por | Líder del corte, el lunes 15 de febrero de 2027, con la validación firmada |

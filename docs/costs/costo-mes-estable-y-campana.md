# Costo mensual en estado estable y escenario de campaña

Este documento estima lo que cuesta cada mes la plataforma cuando ya opera en Azure, y aparte lo que agrega una campaña. Son dos cifras distintas: el mes estable incluye el archivo con sus cinco años de retención, y el sobrecosto de campaña aplica las tres reglas del enunciado solo durante las horas en que cada una actúa. Cada cifra lleva el supuesto que la sostiene. El costo del proyecto de migración está en #25 (`costo-migracion.md`) y el de Fabric, en línea aparte, en #27 (`costo-fabric.md`).

## Contenido

1. Alcance y convención
2. Resumen
3. El mes estable
4. El archivo con cinco años de retención
5. Escenario de campaña
6. Presupuesto de cinco años
7. Continuidad en Central US
8. Fabric, en línea aparte
9. Lo que no incluye
10. Decisiones que bajan o evitan gasto
11. Cómo se recalcula
12. Supuestos y confirmaciones pendientes de FríoAndes
13. Validación y cierre

---

## 1. Alcance y convención

**Regla:** el costo recurrente empieza el día del corte, el domingo 14 de febrero de 2027. Todo lo anterior, y lo que existe solo por la migración, está en #25. El **mes 0** es febrero de 2027, y el **mes estable** empieza en el mes 1 (marzo de 2027), cuando ya no hay DMS, ni copia continua, ni tránsito de los centros hacia Cali, y Cali se apaga entre el 8 y el 14 de marzo.

- **Precios:** de lista, sin descuentos ni reservas ni impuestos, en dólares. Salen de la API pública de precios de Azure, consultada el 19 de octubre de 2026, para East US 2 (Central US donde se indica). Un mes son 730 horas.
- **Pesos colombianos:** a 3.311 pesos por dólar, la misma tasa de #25 y #27.
- **Tamaños:** los mismos de los diseños: la plataforma logística (#12), la telemetría (#13), la migración y la campaña (#14), la siembra (#15), la observabilidad (#16), la red (#8 y #9) y la seguridad (#10). Los componentes que esos diseños ya costearon se toman tal cual, con la sección de origen.
- **Campañas:** fin de año (15 de noviembre a 10 de enero, 57 días), Semana Santa (15 a 28 de marzo, 14 días) y mitad de año (15 de junio a 15 de julio, 31 días): 102 días al año (`carga-c-migracion-y-campana.md`, sección 4.1).

---

## 2. Resumen

**Mes estable**

| Bloque | Qué incluye | USD, mes 1 | Parte | USD, mes 60 |
|---|---|---|---|---|
| Archivo histórico y evidencias | 1,2 PB en dos cuentas, etiquetas, escrituras, lecturas y endpoint privado | 7.768,11 | 45 % | 6.922,93 |
| Hub y tráfico | Firewall, VPN Gateway, Bastion, DNS y la salida de datos hacia los usuarios y el portal | 3.415,86 | 20 % | 3.415,86 |
| Producción: aplicación y datos | MySQL con alta disponibilidad y réplica, Redis, Container Apps, Application Gateway, endpoints, administración y registro de contenedores | 3.255,46 | 19 % | 3.255,46 |
| Pruebas y desarrollo | Los dos ambientes y sus ejecutores del pipeline | 1.169,51 | 7 % | 1.169,51 |
| Fuera de Azure | Segundo proveedor de internet en Cali | 906,07 | 5 % | 906,07 |
| Monitoreo, auditoría y seguridad | Observabilidad, auditoría con cinco años de retención y Defender for Cloud | 560,36 | 3 % | 580,88 |
| Telemetría | IoT Hub, Stream Analytics, función, Event Hub e historial | 164,40 | 1 % | 198,38 |
| **Total** | | **17.239,76** | | **16.449,08** |
| | | Unos COP 57 millones | | |

**Campaña**

| | USD |
|---|---|
| Sobrecosto por día de campaña, solo en las horas del pico | 7,39 |
| Sobrecosto de un mes completo de campaña (30 días) | 221,79 |
| Mes de campaña, total (mes 1 más 30 días de campaña) | 17.461,55 |
| Sobrecosto de las campañas de un año (102 días) | 754,10 |
| Lo que se factura con la regla de calendario de la torre de 04:00 a 22:00 (sección 5.4) | 16,02 al día; 480,48 el mes; 1.633,62 el año |

**Año y cinco años**

| | USD | COP |
|---|---|---|
| Primer año de operación, con campañas y pruebas de carga | 207.672,35 | Unos 688 millones |
| Cinco años | 1.019.077,28 | Unos 3.374 millones |
| Fabric, aparte (F16 todo el año, `costo-fabric.md`) | 34.857,76 al año | Unos 115 millones |

Tres conclusiones:

- **El archivo es casi la mitad del mes** y no crece: el borrado a los cinco años saca cada mes lo mismo que entra (sección 4). Sin ese borrado, la capacidad pasaría de USD 6.780 a 10.454 al mes en cinco años.
- **La campaña cuesta poco más de USD 7 por día**, porque los tamaños fijos ya cubren el pico: el Application Gateway reserva sus 20 unidades, IoT Hub recibe 800.000 mensajes al día y la base no es capa de aplicación. Un 40 % plano sobre el mes de Azure sumaría unos USD 6.533 al mes, casi 30 veces lo calculado (sección 5.5).
- **Tres propuestas sobre el archivo pueden bajar el mes en unos USD 4.400** (sección 10). La mayor, unos USD 3.000, depende solo de que FríoAndes responda si se pueden borrar los archivos de más de cinco años.

---

## 3. El mes estable

### 3.1 Qué cambia frente a los meses antes del corte

| Cambio | Antes del corte (#25) | Mes estable |
|---|---|---|
| Torre | 2 nodos D4, sin usuarios | 4 nodos D4: 13 réplicas de 1 vCPU y 2 GiB, con dos zonas (`carga-c-migracion-y-campana.md`, sección 7.2) |
| Portal | 2 réplicas en espera | 4 réplicas de consumo (2 de rastreo y 2 del front) que atienden de verdad 18 horas al día |
| Usuarios | Siguen en Cali | Los 450 llegan a la torre por la VPN y el Azure Firewall, y la respuesta sale de Azure |
| Escaneo de malware | Apagado durante la siembra | Encendido para las fotos y comprobantes nuevos |
| Archivo | Se carga por trabajos | Completo: 1,2 PB, con lo nuevo entrando y lo vencido saliendo |
| Auditoría | Sin tráfico real | Unos 18 GB al mes, con cinco años de retención |
| Migración | DMS, copia continua, tránsito de los centros por Azure | Nada: se retiran con el apagado de Cali |

### 3.2 Hub y tráfico

| Concepto | Cálculo | USD al mes |
|---|---|---|
| Azure Firewall Standard | 1,25 × 730 | 912,50 |
| Procesamiento del firewall: usuarios de Cali y los centros hacia la torre | 16.630 GB × 1,1 × 0,016 | 292,69 |
| VPN Gateway VpnGw1AZ, con 10 túneles incluidos (Cali 2 y los 8 centros) | 0,21 × 730 | 153,30 |
| Azure Bastion Standard (2 instancias incluidas) | 0,29 × 730 | 211,70 |
| DNS Private Resolver: entrada, salida y conjunto de reglas | 180 + 180 + 2,50 | 362,50 |
| IP públicas del hub: VPN Gateway activo-activo, firewall y Bastion | 4 × 0,005 × 730 | 14,60 |
| Salida de Azure: respuestas a los usuarios por la VPN y del portal a internet | 17.300 GB por tramos: 100 sin costo, hasta 10.335 a 0,087 y el resto a 0,083 | 1.468,57 |
| **Subtotal** | | **3.415,86** |

**De dónde salen los 16.630 GB.** 450 usuarios, la mitad conectados a la vez durante las 18 horas del despacho, a 300 Kbps cada uno: el valor que usó la red para dimensionar la VPN y #25 para el tránsito de los centros. Es una cifra alta para una aplicación web, así que la salida y el procesamiento del firewall son un techo que se mide el primer mes (sección 12). El factor 1,1 suma las solicitudes a las respuestas. El portal suma 670 GB: 6,7 millones de solicitudes al mes (`observabilidad-slo-zabbix.md`, sección 9.1) a unos 100 KB cada una. El portal no pasa por el firewall, porque el Application Gateway está en paralelo (`red-firewall-y-publicacion.md`).

### 3.3 Producción: aplicación y datos

| Concepto | Cálculo | USD al mes |
|---|---|---|
| MySQL Flexible, servidor principal: 4 vCores General Purpose y 512 GB | 4 × 0,0855 × 730 + 512 × 0,115 | 308,54 |
| MySQL: servidor en espera de la alta disponibilidad zonal | Ídem | 308,54 |
| MySQL: réplica de lectura en Central US | 4 × 0,096615 × 730 + 512 × 0,13 | 348,68 |
| Replicación hacia Central US | Unos 100 GB × 0,02 | 2,00 |
| Azure Managed Redis Balanced B1 | 0,032 × 730 | 23,36 |
| Container Apps, torre: plan dedicado y 4 nodos D4 | 0,10 × 730 + 4 × (4 × 0,057077 + 16 × 0,004978) × 730 | 972,23 |
| Container Apps, portal: 4 réplicas de consumo de 1 vCPU y 2 GiB, activas 18 horas al día | 4 × (547,5 h × 0,108 + 182,5 h × 0,0324) | 260,17 |
| Container Apps, solicitudes del portal | 6,7 millones × 0,40 por millón | 2,68 |
| Application Gateway WAF v2 y DDoS de la IP del portal | 473,04 + 199 (`red-firewall-y-publicacion.md`, 7.1) | 672,04 |
| Endpoints privados: 14 | 14 × 0,01 × 730 | 102,20 |
| Máquinas de administración: 2 D2s v5 con disco E10 | 2 × (0,096 × 730 + 9,60) | 159,36 |
| Ejecutor del pipeline de producción: una B2s en `snet-admin`, con disco E10 | 0,0416 × 730 + 9,60 | 39,97 |
| Registro de contenedores Premium, con endpoint privado y 50 GB | 1,6666 × 30,42 días + 50 × 0,10 | 55,69 |
| **Subtotal** | | **3.255,46** |

- **Una réplica activa** de consumo cuesta 1 × 0,000024 + 2 × 0,000003 por segundo, es decir USD 0,108 por hora; en espera, 3 × 0,000003 por segundo, USD 0,0324 por hora.
- **La base** sigue con 4 vCores y 512 GB, el mismo tamaño de #25 y de #14 (sección 3.4). La prueba de carga lo confirma; si no alcanza en campaña, la sección 5.6 dice cuánto cuesta subirla.
- **Los respaldos de MySQL** no suman: Azure no cobra el almacenamiento de respaldo hasta el 100 % del almacenamiento aprovisionado.
- **El ejecutor del pipeline y el registro de contenedores** salen del diseño de automatización (`automatizacion-devops.md`, sección 3): ejecutores autoalojados en `snet-admin` de cada ambiente, separados de las máquinas de administración, y un registro privado del que Container Apps descarga las imágenes por endpoint privado, lo que exige el nivel Premium.

### 3.4 Archivo histórico y evidencias, mes 1

| Concepto | Cálculo | USD al mes |
|---|---|---|
| Documentos: fotos, comprobantes e históricos de temperatura, Cool GRS | 149.600 GB × 0,02 | 2.992,00 |
| Video de muelles y de entregas, Cold LRS | 1.050.400 GB × 0,0036 | 3.781,44 |
| Etiquetas de índice con la fecha original de lo sembrado | 113,8 millones × 0,067 + 2,0 millones × 0,03, por 10.000 | 768,74 |
| Escritura de lo nuevo | 1,1 millones de archivos × 0,20 + 2,6 millones de bloques de 4 MiB × 0,18, por 10.000 | 68,78 |
| Copia geográfica de los documentos nuevos (GRS) | 1.100 GB × 0,02 | 22,00 |
| Endpoint privado: lo que entra y sale del archivo | (12.000 + 400) GB × 0,01 | 124,00 |
| Lecturas: reclamos y comprobantes del portal | 300 GB de video × 0,03 + 100 GB de documentos × 0,01, con sus operaciones | 10,82 |
| Inventario mensual para el borrado a los cinco años | 117 millones de objetos | 0,34 |
| **Subtotal** | | **7.768,11** |

- **Las etiquetas** son las que pone la siembra: después de cada importación, la fecha original de cada archivo se guarda como etiqueta y el borrado mensual la lee (`carga-c-siembra-1-2pb.md`, sección 4.3). Azure cobra cada etiqueta de índice cada mes. Bajan a medida que vence lo sembrado. La sección 10 propone guardarla como metadato, que no se cobra.
- **Las lecturas** suponen unos 300 GB de video al mes por reclamos y unos 100 GB de comprobantes y fotos que consultan los clientes en el portal.
- **El escaneo de malware** de los documentos nuevos está en Defender for Cloud (sección 3.5).
- La sección 4 muestra cómo cambian estas cifras en los cinco años.

### 3.5 Monitoreo, auditoría y seguridad, mes 1

| Concepto | Cálculo | USD al mes |
|---|---|---|
| Observabilidad de la plataforma: 44,4 GB de ingesta, retención de 90 días, alertas y pruebas de disponibilidad | `observabilidad-slo-zabbix.md`, 9.2 | 159,04 |
| Ingesta de la auditoría: eventos de negocio (8 GB), accesos directos a Blob (8 GB) e identidad (2 GB) | 18 GB × 2,76 | 49,68 |
| Retención consultable de 90 días de la auditoría | 18 × 59/30 × 0,12 | 4,25 |
| Retención a largo plazo de la auditoría, hasta cinco años | Crece 18 GB cada mes desde el mes 4 (sección 4.4) | 0,00 |
| Defender for Cloud, con el escaneo de malware de 1.138 GB al mes | `seguridad-datos-personales-perimetro.md`, 6.1 | 347,39 |
| **Subtotal** | | **560,36** |

La observabilidad no incluye la auditoría de negocio, Entra ID ni los accesos directos a Blob, que dimensiona el diseño de auditoría (`gobierno-auditoria-facturacion.md`) con cinco años de retención y 90 días consultables. Ese diseño no da un volumen: los 18 GB son un supuesto que se mide el primer mes. Los 5 GB gratuitos ya se usan en la observabilidad, así que la auditoría paga toda su ingesta.

### 3.6 Telemetría, pruebas y desarrollo, y lo que está fuera de Azure

| Concepto | Cálculo | USD al mes |
|---|---|---|
| IoT Hub, aprovisionamiento, Stream Analytics, función, Event Hub y transferencia | `carga-b-telemetria.md`, 6.4, sin el historial | 163,52 |
| Historial de telemetría: las dos copias | 15 GB × (0,02 + 0,0184) + copia geográfica (sección 4.4) | 0,88 |
| **Telemetría** | | **164,40** |
| Pruebas y desarrollo: Application Gateway, MySQL Burstable, Redis, Container Apps, endpoints e IoT Hub | `costo-migracion.md`, 4.2 | 1.089,57 |
| Ejecutores del pipeline de pruebas y desarrollo: 2 B2s con disco E10 | 2 × (0,0416 × 730 + 9,60) | 79,94 |
| **Pruebas y desarrollo** | | **1.169,51** |
| Segundo proveedor de internet en Cali | COP 3.000.000 al mes (`red-topologia-subnetting.md`, 2.2) | 906,07 |
| **Fuera de Azure** | | **906,07** |

El segundo proveedor se queda después del apagado de Cali: la sede sigue llegando a la torre por la VPN, y es la ruta redundante que pide el enunciado. El proveedor principal no se suma, porque FríoAndes ya lo paga hoy.

---

## 4. El archivo con cinco años de retención

### 4.1 Qué hay el día del corte

El enunciado da 1,2 PB que crecen unos 12 TB al mes. A ese ritmo, el archivo junta unos **100 meses, poco más de 8 años**. Supuesto: cada tipo de contenido se acumuló parejo en esos 100 meses. La cifra cuadra con el enunciado: 110 TB de fotos y comprobantes en 100 meses son exactamente los 1,1 TB al mes que crecen hoy.

| | Documentos (Cool GRS) | Video (Cold LRS) | Total |
|---|---|---|---|
| Sembrado | 150 TB: 110 de fotos y comprobantes, 40 de históricos de temperatura | 1.050 TB | 1.200 TB |
| Con menos de cinco años (60 de los 100 meses) | 90 TB | 630 TB | 720 TB |
| Con más de cinco años | 60 TB | 420 TB | 480 TB |
| Crecimiento mensual desde el corte | 1,1 TB de fotos y comprobantes; los históricos de temperatura ya no crecen, porque los centros pasan a IoT Hub | 10,9 TB | 12 TB |

### 4.2 Cómo evoluciona

Tres movimientos a la vez, mes a mes:

- **Entra lo nuevo:** 12 TB al mes, con cinco años de retención desde su creación.
- **Sale lo sembrado que vence:** el proceso mensual de borrado lee la fecha original de cada archivo y borra lo que cumple cinco años (`carga-c-siembra-1-2pb.md`, sección 4.3). Con el supuesto de 4.1, salen 12 TB al mes durante 60 meses: el mismo volumen que entra.
- **Lo de más de cinco años se queda** hasta que FríoAndes confirme si se puede borrar (pregunta 1 de la sesión de aclaraciones). Para presupuestar se supone que se queda los cinco años: es el escenario más caro.

Por eso el volumen total queda en 1.200 TB: lo que entra reemplaza lo que vence. Cambia la mezcla: los documentos bajan, porque los 24 TB de históricos de temperatura con menos de cinco años vencen y ya no se reponen, y el video sube un poco, porque crece 10,9 TB al mes mientras vence a 10,5.

### 4.3 Capacidad mes a mes, en tres escenarios

| Mes | Documentos | Video | Total | USD al mes | Sin el borrado a los cinco años | USD al mes | Si se borra lo de más de cinco años | USD al mes |
|---|---|---|---|---|---|---|---|---|
| 0, corte | 150,0 TB | 1.050,0 TB | 1.200 TB | 6.780,00 | 1.200 TB | 6.780,00 | 720 TB | 4.068,00 |
| 12 | 145,2 | 1.054,8 | 1.200 | 6.701,28 | 1.344 | 7.514,88 | 720 | 3.989,28 |
| 24 | 140,4 | 1.059,6 | 1.200 | 6.622,56 | 1.488 | 8.249,76 | 720 | 3.910,56 |
| 36 | 135,6 | 1.064,4 | 1.200 | 6.543,84 | 1.632 | 8.984,64 | 720 | 3.831,84 |
| 48 | 130,8 | 1.069,2 | 1.200 | 6.465,12 | 1.776 | 9.719,52 | 720 | 3.753,12 |
| 60 | 126,0 | 1.074,0 | 1.200 | 6.386,40 | 1.920 | 10.454,40 | 720 | 3.674,40 |

Solo capacidad, a 0,02 por GB en documentos y 0,0036 en video. Las etiquetas, las escrituras y las lecturas van aparte (sección 3.4).

- **El escenario base** es la columna "Total": se borra lo que vence y se guarda lo de más de cinco años. Es el que usa el resto del documento.
- **Sin el borrado**, el archivo llega a 1,92 PB y la capacidad a USD 10.454 al mes en el año 5: es lo que pasaría si el proceso de borrado no se construye, y es lo que costaría una política que contara cinco años desde la importación.
- **Si FríoAndes autoriza borrar lo de más de cinco años**, el archivo queda en 720 TB desde el primer mes, el tamaño de equilibrio: cinco años de crecimiento.
- **Desde el mes 61** el archivo queda estable: los 720 TB de cinco años de crecimiento, más lo de más de cinco años si no se borró.

Lo que realmente baja en el escenario base son las etiquetas de lo sembrado: de USD 769 al mes en el mes 1 a unos 311 en el mes 60, cuando solo quedan las de lo que tiene más de cinco años. Por eso el bloque del archivo pasa de USD 7.768 a 6.923.

### 4.4 Lo demás que acumula retención

| Qué | Retención | Mes 1 | Mes 60 | Por qué crece |
|---|---|---|---|---|
| Historial de telemetría, dos copias | Cinco años (`carga-b-telemetria.md`, 4.4) | USD 0,88 | USD 34,86 | 15 GB al mes por copia, hasta 900 GB cada una en el mes 60 |
| Auditoría a largo plazo en Log Analytics | Cinco años, 90 días consultables | USD 0 | USD 20,52 | 18 GB al mes desde el mes 4, hasta 1.026 GB en el mes 60 |
| Archivo histórico | Cinco años | Sección 4.3 | Sección 4.3 | Se compensa con el borrado |

Las dos primeras crecen, pero pesan poco: juntas suman unos USD 55 al mes al final del quinto año.

---

## 5. Escenario de campaña

### 5.1 Las tres reglas y sus horas

El sobrecosto de campaña es lo que se paga **de más** frente a un día normal. Cada regla del enunciado se aplica a su parte y se cobra solo durante las horas en que actúa:

| Regla | Parte | Cuánto crece | Horas que se cobra |
|---|---|---|---|
| +40 % de cómputo | Capa de aplicación: el entorno de la torre | De 13 a 20 vCPU: de 4 a 6 nodos D4 (`carga-c-migracion-y-campana.md`, 7.2) | Las 4 horas del pico |
| 2.000 solicitudes por minuto | Portal | Rastreo de 2 a 4 réplicas y front de 2 a 3 (sección 7.3) | Las 4 horas del pico |
| 180 camiones | Telemetría | 10,1 mensajes por segundo en vez de 7,1, sin cambiar ningún tamaño (sección 7.4) | Las 18 horas de ruta, porque se cobra por mensaje |

La base, la caché, el firewall y la red no son capa de aplicación: el 40 % no se les aplica. La sección 5.6 dice qué pasa si la prueba de carga pide subir la base.

### 5.2 Sobrecosto de un día de campaña

| Regla | Qué cambia | Cálculo | USD por día |
|---|---|---|---|
| Capa de aplicación: +40 % | Torre de 4 a 6 nodos D4 | 2 nodos × 4 h × 0,308 | 2,46 |
| Portal: 2.000 solicitudes por minuto | 3 réplicas más | 3 réplicas × 4 h × 0,108 | 1,30 |
| | Solicitudes de más: 1.200 por minuto sobre el pico normal de 800, durante 4 horas | 288.000 × 0,40 por millón | 0,12 |
| | Salida a internet de esas respuestas | 28,8 GB × 0,083 | 2,39 |
| | Registros del gateway y trazas (1 KB y 4 × 1 KB al 10 %, por solicitud) | 0,40 GB × 2,76 | 1,11 |
| | Application Gateway | Las 20 unidades reservadas cubren las 18 del pico | 0,00 |
| Telemetría: 180 camiones | IoT Hub y Stream Analytics | El mismo tamaño: 2 unidades S1 reciben 800.000 mensajes al día y la campaña llega a unos 682.000 | 0,00 |
| | Event Hub e historial | 194.400 eventos × 0,028 por millón + 5 GB más al mes por copia | 0,02 |
| **Total** | | | **7,39** |

### 5.3 Por regla, por mes y por año

| Regla | Por día | Mes completo de campaña (30 días) | Año (102 días) |
|---|---|---|---|
| Capa de aplicación: +40 % | 2,46 | 73,91 | 251,29 |
| Portal: 2.000 solicitudes por minuto | 4,91 | 147,43 | 501,27 |
| Telemetría: 180 camiones | 0,02 | 0,45 | 1,53 |
| **Total** | **7,39** | **221,79** | **754,10** |

**Un mes de campaña** cuesta USD 17.461,55: el mes estable más 30 días de campaña. Fabric suma 2.938,13 en ese mes, aparte (sección 8).

### 5.4 La regla de calendario de la torre

#14 aplica el 40 % con una regla de escalado por calendario de **04:00 a 22:00** en los días de campaña (`carga-c-migracion-y-campana.md`, sección 7.6), porque en campaña no se hacen cambios y la capacidad tiene que estar lista sin intervención. Con esa regla, los 2 nodos extra se cobran 18 horas y no 4:

| | Por día | Mes de 30 días | Año |
|---|---|---|---|
| Torre, solo en el pico | 2,46 | 73,91 | 251,29 |
| Torre, de 04:00 a 22:00 | 11,09 | 332,60 | 1.130,81 |
| **Sobrecosto total con la regla de 04:00 a 22:00** | **16,02** | **480,48** | **1.633,62** |

La diferencia son unos USD 880 al año. Para no tener sorpresas, el presupuesto de la sección 6 usa la regla tal como está configurada. La sección 10 propone acotar la franja cuando la primera campaña mida a qué horas llega el pico de la torre.

### 5.5 Por qué no un porcentaje plano

Un 40 % sobre todo el mes de Azure sumaría **unos USD 6.533 al mes** de campaña (40 % de 16.333,69). Lo calculado es USD 222, o 480 con la regla de 04:00 a 22:00. El porcentaje plano se equivoca por tres razones:

- Le aplica el 40 % a partes que no crecen: el archivo (45 % del mes), el hub, la base y la telemetría.
- No distingue las horas: el pico dura unas 4 horas, no el mes entero.
- Ignora la capacidad que ya está reservada: el Application Gateway tiene 20 unidades y el pico pide 18.

### 5.6 Lo que podría costar más

| Riesgo | Cuándo se sabe | Costo si pasa |
|---|---|---|
| La base supera el 70 % de CPU con la carga de campaña | En la prueba de carga antes de cada campaña | Subir de 4 a 8 vCores el servidor principal y el de espera, en una ventana antes de la campaña: 2 × 4 × 0,0855 × 730 = USD 499,32 al mes mientras dure. La réplica de Central US puede quedarse en 4 vCores si no recibe lecturas |
| Una réplica del portal atiende menos de 15 solicitudes por segundo | En la prueba de carga | Cada réplica de más durante el pico: USD 0,43 por día de campaña |
| El pico del portal dura más de 4 horas | En la primera campaña | El sobrecosto del portal crece en proporción: USD 1,23 por cada hora más por día |

### 5.7 La prueba de carga antes de cada campaña

#14 pide una prueba en el ambiente de pruebas antes de cada campaña, con 2.000 solicitudes por minuto durante 4 horas, la torre con el 40 % y 180 camiones simulados (sección 7.6). Se cobra en pruebas, por unas 6 horas:

| Concepto | Cálculo | USD por prueba |
|---|---|---|
| Torre de pruebas, de 1 a 6 nodos D4 | 5 × 6 h × 0,308 | 9,24 |
| Portal de pruebas: 7 réplicas activas | 7 × 6 h × 0,108 | 4,54 |
| Application Gateway de pruebas: unas 18 unidades | 18 × 6 h × 0,0144 | 1,56 |
| Generador de carga: 2 máquinas D4s v5 | 2 × 6 h × 0,192 | 2,30 |
| **Total** | | **17,63** |

Son tres pruebas al año, unos USD 53. La prueba antes del día 0 ya está en #25.

---

## 6. Presupuesto de cinco años

| Año | Meses | Plataforma | Campañas (regla de 04:00 a 22:00) y pruebas de carga | Total | Fabric, aparte |
|---|---|---|---|---|---|
| 1 | Marzo de 2027 a febrero de 2028 | 205.985,83 | 1.686,52 | 207.672,35 | 34.857,76 |
| 2 | 13 a 24 | 204.056,73 | 1.686,52 | 205.743,26 | 34.857,76 |
| 3 | 25 a 36 | 202.128,72 | 1.686,52 | 203.815,24 | 34.857,76 |
| 4 | 37 a 48 | 200.200,70 | 1.686,52 | 201.887,22 | 34.857,76 |
| 5 | 49 a 60 | 198.272,69 | 1.686,52 | 199.959,21 | 34.857,76 |
| **Cinco años** | | | | **1.019.077,28** | **174.288,80** |

El año baja unos USD 1.900 cada año porque vencen las etiquetas de lo sembrado y los documentos de temperatura. Lo demás no cambia de tamaño con las cifras del caso. Es la base para el costo total del proyecto y el TCO de #28, que suma la migración (#25), el equipo que opera la plataforma y las decisiones de ahorro.

---

## 7. Continuidad en Central US

| Pieza | Estado en un mes normal | Costo |
|---|---|---|
| Réplica de lectura de MySQL | Encendida, con replicación continua (RPO de 15 minutos) | En producción (sección 3.3): 348,68 al mes |
| IoT Hub y copia de evidencia de la telemetría | Encendidos: IoT Hub vive en Central US | En telemetría (sección 3.6) |
| Copia geográfica de los documentos | Encendida (GRS) | En el archivo (sección 3.4) |
| Entornos de Container Apps | Apagados: se crean con el mismo módulo de Terraform como parte del runbook (`carga-a-plataforma-logistica.md`, sección 6) | 0 al mes. Si se activan, unos USD 1,76 por hora con precios de East US 2 (torre con 4 nodos y portal con 4 réplicas activas) |

El hub de Central US y la forma de redirigir el portal en una conmutación no están decididos (`carga-a-plataforma-logistica.md`, sección 8): no se costean aquí.

---

## 8. Fabric, en línea aparte

Fabric no entra en las tablas de este documento: el enunciado pide su costo aparte, y está en `costo-fabric.md` (#27).

| | USD |
|---|---|
| Mes normal, F16 | 2.891,89 |
| Mes de campaña, F16 | 2.938,13 |
| Año con F16 todo el año | 34.857,76 |

Las lecturas que Fabric hace al archivo por atajo se cobran en las cuentas del archivo, pero #27 las atribuye a Fabric: no están en la sección 3.4.

---

## 9. Lo que no incluye

| Qué | Por qué | Dónde va |
|---|---|---|
| Fabric y las licencias de Power BI | Línea aparte, por el enunciado | `costo-fabric.md` (#27) |
| El equipo que opera la plataforma, soporte y capacitación | No es costo de Azure | Costo total del proyecto (#28) |
| Descuentos, reservas y planes de ahorro | Los precios son de lista | Decisiones de ahorro (#28) |
| Impuestos | Dependen de cómo factura FríoAndes | Confirmación pendiente (sección 12) |
| Proveedor de SMS de las alertas | Depende de la cotización | Telemetría y observabilidad, sin cifra |
| Cuenta de almacenamiento de la función notificadora | Se mide en pruebas (`carga-b-telemetria.md`, 6.4) | Pocos dólares al mes |
| Hub de Central US y redirección del portal en una conmutación | No están diseñados | Pendiente de `carga-a-plataforma-logistica.md`, sección 8 |
| Operaciones de Key Vault y de Event Grid | Centavos al mes con este volumen | — |
| Lo que hoy paga Cali: proveedor principal, sede y equipos de red de los centros | FríoAndes ya lo paga | — |

---

## 10. Decisiones que bajan o evitan gasto

| Decisión | Alternativa descartada | Ahorro al mes | Estado |
|---|---|---|---|
| Borrado mensual a los cinco años, con la fecha original de cada archivo | Contar cinco años desde la importación, o no borrar | Hasta USD 4.068 de capacidad en el año 5 (10.454,40 − 6.386,40) | Decidido en #15 |
| Video en Cold LRS | Cold GRS | USD 4.653 | Decidido en #15; si FríoAndes exige copia geográfica del video, es lo que cuesta |
| Portal en consumo, que escala solo con la concurrencia | Réplicas fijas para el pico de campaña | Las 3 réplicas del pico existen solo 4 horas por día de campaña | Decidido en #14 |
| Application Gateway con 20 unidades reservadas | Escalar el gateway en campaña | Ningún cambio en campaña; el pico cabe en lo reservado | Decidido en #9 |
| **Propuesta:** borrar lo de más de cinco años al momento de la siembra | Guardarlo hasta que FríoAndes decida | USD 2.712 de capacidad, más unos 311 de etiquetas | Depende de la pregunta 1 de la sesión de aclaraciones |
| **Propuesta:** guardar la fecha original como metadato y que el borrado lea el inventario mensual, que ya incluye los metadatos | Etiqueta de índice por archivo | USD 768,74 en el mes 1, bajando hasta unos 311 en el mes 60 | Para #15: cambia el proceso de la sección 4.3 de la siembra, no la inmutabilidad |
| **Propuesta:** documentos de más de un año a Cold GRS por ciclo de vida | Todo en Cool GRS | Unos USD 1.633 | Para #15. Cold cobra USD 0,03 por GB leído y 90 días mínimos; los reclamos sobre fotos viejas son pocos. La inmutabilidad permite cambiar de nivel |
| **Propuesta:** acotar la regla de calendario de la torre a la franja del pico, medida en la primera campaña | 04:00 a 22:00 | Unos USD 880 al año | Para #14, después de la primera campaña |

Las tres propuestas del archivo suman unos USD 4.400 al mes en el mes 1, sin contar dos veces lo que se solapa: si se borra lo de más de cinco años, el ciclo de vida a Cold ya no mueve esos 60 TB de documentos. #28 toma esta tabla para el documento de costos consolidado.

---

## 11. Cómo se recalcula

Todas las cifras salen de `tools/calc_costo_mes_estable.py`. Los precios, los tamaños y los supuestos están al comienzo del script, junto a la cifra que afectan.

```bash
cd docs/costs/tools
python3 calc_costo_mes_estable.py
```

Si cambia un precio, un tamaño o un supuesto (por ejemplo, la respuesta de FríoAndes sobre los archivos de más de cinco años, o el tráfico real del primer mes), se cambia en el script, se corre de nuevo y se copian las tablas.

---

## 12. Supuestos y confirmaciones pendientes de FríoAndes

### 12.1 Confirmaciones que necesita el estimado

| Tema | Pregunta | Qué pasa si la respuesta cambia |
|---|---|---|
| Archivos de más de cinco años | ¿El 1,2 PB incluye archivos de más de cinco años? ¿Se pueden borrar? (pregunta 1) | Si se pueden borrar, el mes baja unos USD 3.000 (sección 10) |
| Edad del archivo | ¿Cómo se reparte el 1,2 PB por año de creación? | Cambia cuánto vence cada mes y cuánto queda de más de cinco años (sección 4.1) |
| Copia geográfica del video | ¿Los contratos exigen copia en otra región para el video? | USD 4.653 más al mes |
| Ruta del video de los muelles | ¿Las cámaras de los centros suben el video por la VPN? | Si pasa por el Azure Firewall, suma unos USD 175 al mes (10.900 GB × 0,016) |
| Tráfico real de los usuarios | Se mide el primer mes con los registros del firewall | Los 300 Kbps por usuario son un techo: la salida y el firewall suman USD 1.761 al mes con esa cifra |
| Moneda e impuestos | ¿En qué moneda se presentan los costos y con qué impuestos? (pregunta 12) | Cambia la presentación |

### 12.2 Supuestos del estimado

| Supuesto | Por qué se asume |
|---|---|
| El costo recurrente empieza el día del corte, y el mes estable en marzo de 2027 | Sigue la regla de #25, sin contar dos veces |
| El 1,2 PB se acumuló parejo en unos 100 meses al ritmo actual: el 60 % tiene menos de cinco años y el 40 % más | 1,2 PB a 12 TB al mes; cuadra con los 110 TB de fotos que crecen 1,1 TB al mes |
| Lo de más de cinco años se guarda los cinco años del presupuesto | Es el escenario más caro mientras FríoAndes no responda la pregunta 1 |
| El archivo crece 12 TB al mes los cinco años (1,1 de documentos y 10,9 de video), y los históricos de temperatura dejan de crecer | Es el crecimiento del enunciado; la temperatura pasa a IoT Hub |
| La fecha original de lo sembrado es una etiqueta de índice por archivo: 115 millones de documentos y 2 millones de videos | Es lo que diseña la siembra; los archivos nuevos no la necesitan |
| 450 usuarios, la mitad conectados a la vez durante 18 horas, a 300 Kbps | El mismo valor de la red y de #25; se mide el primer mes |
| El portal recibe 6,7 millones de solicitudes al mes de unos 100 KB, con réplicas de 1 vCPU y 2 GiB | Las solicitudes vienen de la observabilidad; el tamaño de la respuesta y de la réplica se confirman en la prueba de carga |
| La auditoría ingiere unos 18 GB al mes, con 90 días consultables y cinco años de retención | El diseño de auditoría fija la retención pero no el volumen |
| Cada ambiente tiene un ejecutor del pipeline B2s en `snet-admin`, y hay un registro de contenedores Premium | Lo piden el diseño de automatización y el acceso privado a las imágenes |
| El pico de campaña dura 4 horas por día de campaña, y hay 102 días de campaña al año | El enunciado da unas 4 horas; las fechas son las de #14 |
| El segundo proveedor de Cali se queda después del apagado | Es la ruta redundante de la sede hacia la torre |
| Los entornos de Container Apps de Central US están apagados hasta una conmutación | Lo decide la plataforma logística (#12) |

---

## 13. Validación y cierre

| Criterio de aceptación | Evidencia en este documento |
|---|---|
| El costo de almacenamiento incluye el efecto acumulado de 5 años de retención, no solo el año 1 | Sección 4: el archivo mes a mes hasta el mes 60, con lo que entra, lo que vence y lo que se guarda de más de cinco años, en tres escenarios. La sección 4.4 suma el historial de telemetría y la auditoría, que crecen hasta el año 5, y la sección 6 lleva todo al presupuesto de cada año |
| El sobrecosto de campaña distingue las 3 reglas de dimensionamiento y se calcula solo por las horas del pico | Sección 5: cada regla en su parte (torre, portal y telemetría) y con sus horas (sección 5.1); el cálculo por día y por regla (secciones 5.2 y 5.3). La sección 5.4 muestra aparte lo que agrega la regla de calendario de #14, y la 5.5 por qué no se usa un porcentaje plano |

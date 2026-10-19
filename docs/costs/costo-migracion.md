# Costo de la migración del núcleo

Este documento estima el costo único del proyecto de migración: la siembra del archivo de 1,2 PB, los servicios temporales de la migración, lo que Azure cuesta antes de que la plataforma opere y las horas del equipo en la convivencia, el ensayo y el corte. Cada cifra lleva el supuesto que la sostiene. El costo de cada mes en estable y en campaña está en #26, y el de Fabric en #27.

## Contenido

1. Alcance y regla de corte
2. Resumen
3. Siembra del archivo
4. Azure y red antes del corte
5. Servicios temporales de la migración
6. Horas del equipo
7. Contingencia
8. Lo que no incluye
9. Decisiones que bajan o evitan gasto
10. Cómo se recalcula
11. Supuestos y confirmaciones pendientes de FríoAndes
12. Validación y cierre

## 1. Alcance y regla de corte

**Regla:** es costo de la migración todo lo que se paga **antes del corte del domingo 14 de febrero de 2027**, más los costos únicos que existen solo por la migración. Desde el corte, Azure opera el negocio y su costo es recurrente (#26).

Por eso la plataforma de Azure entra aquí desde que se despliega hasta el corte: en ese tiempo FríoAndes la paga, pero la operación sigue corriendo en Cali. Es el costo de mantener dos plataformas a la vez. El lado de Cali no se suma, porque FríoAndes ya lo paga hoy (sección 8).

- **Precios:** de lista, sin descuentos ni reservas, en dólares. Salen de la API pública de precios de Azure, consultada el 13 de octubre de 2026, para East US 2 (Central US donde se indica). Un mes son 730 horas.
- **Pesos colombianos:** se convierten a 3.311 pesos por dólar, la misma tasa que usó el diseño de red (COP 3.000.000 = USD 906).
- **Fechas y tamaños:** salen del plan de migración (`carga-c-migracion-y-campana.md`) y del plan de siembra (`carga-c-siembra-1-2pb.md`).

## 2. Resumen

| Bloque | Qué incluye | USD | Parte |
|---|---|---|---|
| Siembra del archivo | Discos, Import/Export, envíos, escrituras en Azure y estaciones de copia | 64.920,00 | 49 % |
| Horas del equipo | Siembra, ventanas nocturnas, ensayo, corte y apagado | 38.352,16 | 29 % |
| Azure y red antes del corte | La plataforma y el archivo en Azure mientras la operación sigue en Cali, y el segundo proveedor de Cali | 27.667,86 | 21 % |
| Servicios temporales de la migración | DMS, servidor del ensayo, copia continua y conciliación | 892,31 | 1 % |
| Tránsito de los centros por Azure | Usuarios de los centros que llegan a la torre de Cali a través de Azure hasta el corte | 667,96 | 0,5 % |
| Otros costos únicos | Instalación del segundo proveedor de Cali | 906,07 | 0,7 % |
| **Subtotal** | | **133.406,36** | |
| Contingencia (15 %) | Sección 7 | 20.010,95 | |
| **Total del proyecto de migración** | | **153.417,32** | Unos COP 508 millones |

La siembra pesa casi la mitad del proyecto, y dentro de ella los discos y el envío son casi el 70 %. El costo de tener las dos plataformas a la vez queda en unos USD 27.500 porque Azure corre al mínimo hasta el corte y Cali se apaga el día 62, no el 90.

## 3. Siembra del archivo

Línea propia, como pide la historia. Viene del plan de siembra (`carga-c-siembra-1-2pb.md`, secciones 5 y 9). El medio es Azure Import/Export con discos propios: Data Box Heavy está retirado y Data Box no se envía a Colombia.

| Concepto | Cálculo | USD | Supuesto |
|---|---|---|---|
| Discos: 74 HDD de 20 TB | 74 × 450 | 33.300,00 | 71 discos para 9 trabajos más 3 de repuesto. HDD de 3,5" SATA III, 512e, a USD 450 puesto en Cali, por cotizar |
| Cargo de Import/Export: 71 discos | 71 × 80 | 5.680,00 | Precio de lista por disco procesado |
| Envío internacional de ida y vuelta, con aduana | 9 envíos × 2 × 600 | 10.800,00 | Una caja de hasta 10 discos por envío, por cotizar con el transportador |
| Escritura de los documentos al importar | 115 millones × 0,20 / 10.000 | 2.300,00 | Unos 115 millones de archivos en Cool GRS, una escritura por archivo |
| Escritura del video al importar | 250 millones de bloques × 0,18 / 10.000 | 4.500,00 | Peor caso: un bloque de 4 MiB por escritura, en Cold LRS |
| Fecha original e inmutabilidad por archivo | 117 millones × 2 × 0,10 / 10.000 | 2.340,00 | Dos escrituras por archivo después de importarlo |
| Estaciones de copia | 2 × 3.000 | 6.000,00 | Si FríoAndes no tiene equipos Windows con bahías SATA que sirvan |
| **Subtotal** | | **64.920,00** | |

El almacenamiento del archivo mientras se carga no está en esta tabla: se cuenta en la sección 4, junto con el resto de Azure antes del corte.

## 4. Azure y red antes del corte

### 4.1 Desde cuándo se paga cada parte

| Parte | Desde | Hasta | Días | Por qué esa fecha |
|---|---|---|---|---|
| Pruebas y desarrollo | 1 de diciembre de 2026 | 14 de febrero de 2027 | 75 | Las adaptaciones de la aplicación y la prueba de carga de campaña se prueban antes del día 0 |
| Hub y producción | 14 de diciembre de 2026 | 14 de febrero de 2027 | 62 | Cuatro semanas para desplegar y probar antes del día 0, sin tocar Cali |
| Alta disponibilidad y réplica de la base | 24 de enero de 2027 (día 13) | 14 de febrero | 21 | Se activan cuando termina la carga inicial (#14, sección 3.6) |
| Archivo | Cada trabajo desde que queda cargado | 14 de febrero | — | Cronograma de la siembra (`carga-c-siembra-1-2pb.md`, sección 5.3) |
| Segundo proveedor de Cali | 1 de enero de 2027 | 14 de febrero | 44 | Los túneles por los dos proveedores existen desde el día 0 |

### 4.2 Costo mensual de cada parte, al mínimo

Hasta el corte la plataforma corre al mínimo, sin usuarios: la torre con 2 nodos en vez de 4 y el portal con sus réplicas en espera. Los componentes que ya costearon otros diseños se toman tal cual.

**Hub**

| Concepto | Cálculo | USD al mes |
|---|---|---|
| Azure Firewall Standard | 1,25 × 730 | 912,50 |
| VPN Gateway VpnGw1AZ, con 10 túneles incluidos (Cali 2 y los 8 centros) | 0,21 × 730 | 153,30 |
| Azure Bastion Standard (2 instancias incluidas) | 0,29 × 730 | 211,70 |
| DNS Private Resolver: entrada, salida y conjunto de reglas | 180 + 180 + 2,50 | 362,50 |
| IP públicas del hub: VPN Gateway activo-activo, firewall y Bastion | 4 × 0,005 × 730 | 14,60 |
| **Subtotal** | | **1.654,60** |

**Producción**

| Concepto | Cálculo | USD al mes |
|---|---|---|
| MySQL Flexible, servidor principal: 4 vCores General Purpose y 512 GB | 4 × 0,0855 × 730 + 512 × 0,115 | 308,54 |
| Azure Managed Redis Balanced B1 | 0,032 × 730 | 23,36 |
| Container Apps, torre: plan dedicado y 2 nodos D4 | 0,10 × 730 + 2 × (4 × 0,057077 + 16 × 0,004978) × 730 | 522,62 |
| Container Apps, portal: 2 réplicas en espera, en consumo | 2 × (1 vCPU + 2 GiB) × 0,000003 × 2.628.000 s | 47,30 |
| Application Gateway WAF v2 y DDoS de la IP del portal | 473,04 + 199 (`red-firewall-y-publicacion.md`, 7.1) | 672,04 |
| Endpoints privados: 14 | 14 × 0,01 × 730 | 102,20 |
| Máquinas de administración: 2 D2s v5 | 2 × 0,096 × 730 | 140,16 |
| Log Analytics: unos 60 GB al mes | 60 × 2,76 | 165,60 |
| Defender for Cloud, sin el escaneo de malware, que queda apagado durante la migración | `seguridad-datos-personales-perimetro.md`, 6.1 | 170,00 |
| Telemetría de producción | `carga-b-telemetria.md`, 6.4 | 167,00 |
| **Subtotal** | | **2.318,82** |

**Pruebas y desarrollo**

| Concepto | Cálculo | USD al mes |
|---|---|---|
| Application Gateway de pruebas y de desarrollo, con sus IP | 273,31 + 151,84 + 10,95 (`red-firewall-y-publicacion.md`, 7.1) | 436,10 |
| MySQL Burstable B2s con 64 GB, en cada ambiente | 2 × (0,068 × 730 + 64 × 0,115) | 114,00 |
| Managed Redis B0, en cada ambiente | 2 × 0,016 × 730 | 23,36 |
| Container Apps: pruebas con plan dedicado y 1 nodo D4; desarrollo solo en consumo | 73 + 224,77 + 2 réplicas en espera | 345,11 |
| Endpoints privados: 10 por ambiente | 20 × 0,01 × 730 | 146,00 |
| IoT Hub S1 de pruebas | `carga-b-telemetria.md`, 6.4 | 25,00 |
| **Subtotal** | | **1.089,57** |

**Alta disponibilidad y réplica de la base**, desde el día 13

| Concepto | Cálculo | USD al mes |
|---|---|---|
| Servidor en espera de la alta disponibilidad zonal | 4 × 0,0855 × 730 + 512 × 0,115 | 308,54 |
| Réplica de lectura en Central US | 4 × 0,096615 × 730 + 512 × 0,13 | 348,68 |
| **Subtotal** | | **657,22** |

El tamaño de la base sale de los supuestos de la plataforma: 4 vCores para 450 usuarios internos y un portal de 33 solicitudes por segundo en campaña, y 512 GB para una base de menos de 400 GB (#14, sección 3.4). #26 usa el mismo tamaño y lo confirma la prueba de carga.

### 4.3 Total antes del corte

| Concepto | Cálculo | USD |
|---|---|---|
| Hub | 1.654,60 al mes × 62 días | 3.372,66 |
| Producción | 2.318,82 al mes × 62 días | 4.726,58 |
| Pruebas y desarrollo | 1.089,57 al mes × 75 días | 2.686,62 |
| Alta disponibilidad y réplica de la base | 657,22 al mes × 21 días | 453,75 |
| Archivo: cuenta de documentos, Cool GRS a 0,02 por GB al mes | 150 TB desde el 26 de noviembre, el diferencial desde el 23 de enero y lo nuevo desde el día 0 | 7.939,06 |
| Archivo: cuenta de video, Cold LRS a 0,0036 por GB al mes | Cada trabajo desde que queda cargado (3 de diciembre a 3 de enero), el diferencial y lo nuevo | 7.178,49 |
| Segundo proveedor de internet en Cali | COP 3.000.000 al mes × 44 días | 1.310,70 |
| **Subtotal** | | **27.667,86** |

**Tránsito de los centros por Azure.** Entre el paso de cada centro a la conexión directa (en promedio el 19 de enero) y el corte, los usuarios de los centros llegan a la torre, que sigue en Cali, a través del hub de Azure (FW-401). Ese tráfico sale de Azure por la VPN y paga transferencia de salida:

| Concepto | Cálculo | USD |
|---|---|---|
| Salida de Azure por la VPN | (218,70 GB al día × 26 días − 100 GB gratis) × 0,087 | 486,00 |
| Procesamiento del Azure Firewall, ida y vuelta | 2 × 5.686,20 GB × 0,016 | 181,96 |
| **Subtotal** | | **667,96** |

Los 218,70 GB al día salen de 180 usuarios en los centros, la mitad conectados a la vez durante 18 horas, a 300 Kbps cada uno, el valor que usó la red (`red-topologia-subnetting.md`). La sección 9 propone cómo evitarlo.

## 5. Servicios temporales de la migración

| Concepto | Cálculo | USD | Supuesto |
|---|---|---|---|
| DMS Premium de 4 vCores | 0,308 × 730 = 224,84 al mes | 0,00 | Microsoft no cobra los primeros 183 días, y DMS se usa del 16 de enero al 15 de febrero |
| MySQL a 16 vCores durante la carga inicial | 12 vCores extra × 0,0855 × 48 h | 49,25 | Microsoft recomienda subir el destino de tamaño mientras dura la carga; dos días |
| Servidor temporal del ensayo | 4 × 0,0855 × 336 h + 512 × 0,115 × 14 / 30,4 | 142,01 | El mismo tamaño que producción, 14 días alrededor del 31 de enero |
| Copia continua: procesamiento del endpoint privado | 16.800 GB × 0,01 | 168,00 | 400 GB al día del 11 de enero al 15 de febrero, más 2.800 GB para ponerse al día |
| Copia continua: escrituras | Unos 1,2 meses de documentos y video nuevos | 83,05 | Archivos de 1 MB en documentos y bloques de 4 MiB en video |
| Conciliación: lectura de la muestra del 1 % | 10.500 GB × 0,03 + 1.100 GB × 0,01 + 11.600 GB × 0,01 | 442,00 | Lectura de Cold y de Cool más el endpoint privado, desde una máquina de `snet-admin` |
| Firewall por la carga inicial y la replicación de la base | Unos 500 GB × 0,016 | 8,00 | Base de menos de 400 GB más la replicación hasta el corte |
| **Subtotal** | | **892,31** | |

La entrada de datos a Azure no se cobra: ni la carga inicial de la base, ni la copia continua, ni la importación de los discos pagan transferencia.

## 6. Horas del equipo

**Tarifa:** COP 120.000 por hora, costo para la empresa, es decir **USD 36,24**. Es una tarifa promedio del equipo interno.

**Recargos** de la Ley 2466 de 2025: la hora nocturna (de 19:00 a 06:00) lleva un 35 % adicional, y la de domingo un 90 % desde julio de 2026. Se suman: una hora nocturna de domingo vale 2,25 veces la hora normal.

| Concepto | Horas | Cálculo | USD |
|---|---|---|---|
| Siembra: preparación, copia de discos, envíos, conciliación e inmutabilidad | 336 diurnas | 336 × 36,24 | 12.177,59 |
| Compatibilidad de la base con MySQL 8.4 y parámetros del servidor | 40 diurnas | 40 × 36,24 | 1.449,71 |
| Guion del corte, scripts de validación y aprobación | 60 diurnas | 60 × 36,24 | 2.174,57 |
| Ventanas nocturnas de la convivencia: unas 15 noches | 15 × 2 personas × 6 h | 180 × 1,35 × 36,24 | 8.807,01 |
| **Ensayo**, sábado 22:00 a domingo 06:00 | 8 personas × 8 h | 8 × (2 × 1,35 + 6 × 2,25) × 36,24 | 4.697,07 |
| **Corte**, sábado 22:00 a domingo 06:00 | 8 personas × 8 h | Ídem | 4.697,07 |
| Acompañamiento el domingo del corte, 06:00 a 10:00 | 3 personas × 4 h | 12 × 1,90 × 36,24 | 826,34 |
| Apagado de Cali: 6 noches | 6 × 2 personas × 6 h | 72 × 1,35 × 36,24 | 3.522,80 |
| **Subtotal** | | | **38.352,16** |

Las 8 personas del ensayo y del corte son las del guion (#14, sección 5.3): el líder del corte, base de datos, red, dos de aplicación, pruebas y dos usuarios clave de despacho y facturación. Solo el ensayo y el corte suman unos USD 10.220 con el acompañamiento.

## 7. Contingencia

Se agrega un 15 % sobre el subtotal, **USD 20.010,95**, por las cifras que todavía no tienen cotización ni medición:

- el precio de los discos y del envío con aduana, que suman USD 44.100;
- la velocidad de lectura del servidor de archivo, que alarga o acorta la siembra y sus horas;
- un segundo ensayo, si el primero no pasa (#14, sección 4.4): unos USD 4.700 más;
- un disco rechazado, que va en el envío siguiente.

## 8. Lo que no incluye

| Qué | Por qué no está |
|---|---|
| Lo que cuesta Cali durante la convivencia (energía, soporte de VMware, soporte extendido de Ubuntu) | FríoAndes ya lo paga hoy y el enunciado no da esas cifras. Apagar Cali el día 62 en vez del 90 ahorra 28 días de ese costo |
| Las adaptaciones de la aplicación (#14, sección 2.4) | El enunciado dice que se piden y se justifican, no que se implementen. Su esfuerzo depende del código, que no es parte del caso. Lo estima el equipo de desarrollo |
| Licencias de Microsoft 365, Entra ID P1 o P2 y PIM | Dependen de lo que FríoAndes ya tenga (pregunta 10 de la sesión de aclaraciones) |
| Capacidad de Fabric | Va en línea aparte (#27) |
| Formación del equipo | No hay datos del equipo actual |
| El costo de Azure desde el corte | Es costo de operación (#26) |

## 9. Decisiones que bajan o evitan gasto

| Decisión | Alternativa descartada | Qué se evita | Viene de |
|---|---|---|---|
| Siembra con discos propios | Copiar 1,2 PB por la red | No es posible: 278 días con todo el enlace | #15 |
| El video se importa directo a Cold | Importar a Hot y moverlo después | Unos USD 15.500 al mes durante la siembra (Hot LRS 19.320 frente a Cold LRS 3.780 al mes por 1.050 TB) | #15 |
| Escaneo de malware apagado durante la siembra | Escanear el 1,2 PB al importar | Unos USD 180.000 | #10 |
| DMS dentro de los 183 días sin costo | Crear DMS antes o mantenerlo después | USD 224,84 por cada mes fuera de ese plazo | #14 |
| Plataforma al mínimo hasta el corte | La torre con sus 4 nodos desde el despliegue | 2 nodos D4: unos USD 450 al mes, unos USD 920 hasta el corte | #14 |
| Bases de pruebas y desarrollo en Burstable y sin migrar datos | Bases General Purpose o una copia de producción | Unos USD 500 al mes frente a dos servidores de 4 vCores, y sin datos personales en esos ambientes | #14 y #10 |
| Ensayo en el servidor temporal, que se borra | Un ambiente de preproducción permanente | Unos USD 310 al mes | #14 |
| Apagar Cali el día 62 | Esperar al día 90 | 28 días del costo de Cali, que FríoAndes debe cuantificar | #14 |
| **Propuesta:** hasta el corte, los centros siguen llegando a la torre de Cali por su VPN hacia Cali y no por Azure | El tránsito por Azure de FW-401 | Unos USD 670 (sección 4.3). Se propone al diseño de red: basta con que la ruta hacia `10.20.1.0/24` prefiera el túnel a Cali mientras exista | Este documento, para #8 y #9 |

#28 toma esta tabla para el documento de costos consolidado.

## 10. Cómo se recalcula

Todas las cifras salen de `tools/calc_costo_migracion.py`. Los precios, las fechas y los supuestos están al comienzo del script, junto a la cifra que afectan.

```bash
cd docs/costs/tools
python3 calc_costo_migracion.py
```

Si cambia un precio, una fecha del plan o un supuesto, se cambia en el script, se corre de nuevo y se copian las tablas.

## 11. Supuestos y confirmaciones pendientes de FríoAndes

### 11.1 Confirmaciones que necesita el estimado

| Tema | Pregunta | Qué pasa si la respuesta cambia |
|---|---|---|
| Moneda y tope | ¿En qué moneda se presentan los costos? ¿Hay un tope de presupuesto para el proyecto? (pregunta 12 de la sesión de aclaraciones) | Cambia la presentación y, si hay tope, qué decisiones de la sección 9 son obligatorias |
| Tarifa del equipo | ¿Cuál es el costo por hora del equipo interno, y si participan proveedores externos? | Las horas son el 29 % del proyecto |
| Cotizaciones | Precio de los discos de 20 TB puestos en Cali y del envío internacional con aduana | Son USD 44.100 del subtotal |
| Equipos existentes | ¿FríoAndes tiene equipos Windows con bahías SATA para las estaciones de copia? | Si sí, se ahorran USD 6.000 |
| Usuarios en los centros | ¿Cuántos de los 450 usuarios internos trabajan en los centros? | Cambia el tránsito por Azure de la sección 4.3 |
| Costo de Cali | ¿Cuánto cuesta al mes mantener el datacenter de Cali? | Permite cuantificar el ahorro de apagar el día 62 |

### 11.2 Supuestos del estimado

| Supuesto | Por qué se asume |
|---|---|
| Es costo de la migración todo lo que se paga antes del corte, más los costos únicos de la migración | Separa con una fecha lo que cuenta #25 y lo que cuenta #26, sin contar dos veces |
| Pruebas y desarrollo se despliegan el 1 de diciembre de 2026, y el hub y producción el 14 de diciembre | Dejan tiempo para probar las adaptaciones y la carga de campaña antes del día 0 |
| La base de producción es MySQL Flexible General Purpose de 4 vCores con 512 GB | Alcanza para 450 usuarios y 33 solicitudes por segundo; se confirma con la prueba de carga |
| Bastion es Standard | Lo decide el diseño del acceso remoto (#11), por el escalado y el cliente nativo |
| Log Analytics recibe unos 60 GB al mes antes del corte | No hay tráfico real; el diseño del firewall mide el volumen el primer mes |
| 180 de los 450 usuarios internos están en los centros | El enunciado no reparte los usuarios entre Cali y los centros |
| El equipo cuesta COP 120.000 por hora, con los recargos de la Ley 2466 de 2025 | Tarifa promedio de referencia, sin cotización |
| Contingencia del 15 % | Cubre las cifras sin cotización ni medición de la sección 7 |

## 12. Validación y cierre

| Criterio de aceptación | Evidencia en este documento |
|---|---|
| Cada cifra de costo indica su supuesto sustentador | Cada tabla tiene su cálculo y su supuesto: región y fecha de los precios (sección 1), tamaños (secciones 3 y 4.2), horas y días (secciones 4.1 y 6), retención y niveles del archivo (sección 4.3) y medio de transferencia (sección 3). Los supuestos generales están en la sección 11.2 |
| El costo de la siembra física aparece como línea propia | Sección 3: USD 64.920 con Azure Import/Export, el medio dimensionado en #15, que reemplaza a Data Box Heavy porque está retirado. También aparece como primera línea del resumen |

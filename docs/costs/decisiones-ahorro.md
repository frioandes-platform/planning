# Decisiones de diseño que bajan el costo

Este documento junta en una sola lista las decisiones de diseño que cuestan menos que la alternativa obvia, cada una con su costo evitado y el issue de arquitectura que la originó. Las tres que pide el enunciado van primero y con detalle: la siembra física del archivo, los accesos directos de Fabric y la capacidad de Fabric fuera de campaña. Las demás vienen de las secciones "Decisiones que bajan o evitan gasto" de cada diseño y de los documentos de costos. Al final quedan las propuestas que todavía esperan una decisión.

## Contenido

1. Cómo leer el costo evitado
2. Resumen
3. Las tres decisiones del enunciado
4. Decisiones tomadas
5. Propuestas pendientes
6. Validación y cierre

---

## 1. Cómo leer el costo evitado

- **Costo evitado** es la diferencia con la **alternativa obvia**: lo que se habría hecho sin pensar en el costo. No es un ahorro sobre un presupuesto que FríoAndes ya tenga.
- **En cinco años** pone en la misma escala lo mensual y lo único: lo mensual por 60 meses, o mes a mes con el modelo del archivo de #26 cuando el volumen cambia, más lo único una sola vez. Los precios son los de lista de cada documento de origen.
- **No todo se suma.** Algunas alternativas se excluyen entre sí (por ejemplo, F64 frente a licencias Pro, y F8 frente a F16). Los totales de la sección 2 sirven para dar el orden de magnitud, no como cifra de presupuesto.
- **Origen** es el issue de arquitectura que tomó la decisión. **Fuente** es el documento y la sección donde está el cálculo. Todas las cifras de cinco años salen de `tools/calc_costo_total_proyecto.py`.

---

## 2. Resumen

| | Cuántas | Costo evitado en cinco años |
|---|---|---|
| Decisiones tomadas | 25 | Unos USD 1,85 millones |
| Propuestas pendientes | 7 | Hasta unos USD 376.000, un 14 % del costo total de propiedad a cinco años |

**Las siete que más evitan, en cinco años:**

| Decisión | USD | Origen |
|---|---|---|
| Licencias Power BI Pro en vez de una capacidad F64 | 344.832,00 | #18 (F1-14) |
| Accesos directos de Fabric en vez de copiar el archivo a OneLake | 325.497,94 | #17 (F1-13) |
| Video en Cold LRS en vez de Cold GRS | 282.332,76 | #15 |
| Escaneo de malware apagado durante la siembra | 180.000,00 | #10 |
| DDoS IP Protection solo para la IP del portal | 164.673,00 | #9 |
| Borrado mensual a los cinco años con la fecha original | 124.074,00 | #15 |
| Escanear solo fotos y comprobantes, no el video | 108.000,00 | #10 |

Casi todo lo que más evita tiene que ver con el archivo de 1,2 PB: no copiarlo, no escanearlo, no replicarlo a otra región y borrar lo que vence a tiempo. Es el 88 % del volumen y lo que más pesa en el mes.

---

## 3. Las tres decisiones del enunciado

### 3.1 Siembra física del archivo en vez de copiarlo por la red (F1-11, #15)

**Decisión.** El 1,2 PB viaja en 71 discos propios por Azure Import/Export, en nueve trabajos, y la red solo lleva el crecimiento diario (`carga-c-siembra-1-2pb.md`, secciones 3 y 5).

**La alternativa por la red no es viable.** Copiar 1,2 PB por el enlace de 400 Mbps de Cali toma **278 días usando el enlace completo**, sin dejar nada para la operación, y 556 días usando la mitad. La convivencia dura como máximo 90 días (`carga-c-siembra-1-2pb.md`, sección 2).

**Qué cuesta cada camino.** Para comparar, se supone que los 90 días no existieran y la copia por red se pudiera esperar:

| Concepto | Cálculo | USD |
|---|---|---|
| Dos plataformas a la vez 216 días más: 278 de copia frente a 62 hasta el apagado de Cali | 6.626,28 al mes (Azure antes del corte y segundo proveedor, #25) × 216 días | 47.055,67 |
| Procesamiento del endpoint privado de 1,2 PB | 1.200.000 GB × 0,01 | 12.000,00 |
| VPN Gateway VpnGw2AZ durante la copia, para no ahogar la operación | 241 más al mes × 9 meses | 2.169,00 |
| **Copia por la red, solo lo de Azure** | | **61.224,67** |
| **Siembra con discos** (#25, sección 3) | | **64.920,00** |

**Costo evitado.** Sin contar Cali, los dos caminos cuestan parecido. La diferencia la pone el datacenter de Cali, que tendría que seguir encendido unos 7 meses más: **basta con que Cali cueste más de USD 520 al mes para que la siembra salga más barata**, y Cali cuesta mucho más que eso (energía, VMware, espacio y personal). Además, la copia por la red ocuparía el enlace que la operación necesita. La decisión es ante todo de factibilidad, y también es la más barata.

**Lo que la siembra evita dentro de sí misma:**

| Decisión | Alternativa obvia | Costo evitado | Origen |
|---|---|---|---|
| El video se importa directo a Cold | Importar a Hot y moverlo después | Unos USD 15.540: un mes de Hot (19.320) frente a Cold (3.780) para 1.050 TB | #15 |
| Escaneo de malware apagado durante la siembra | Escanear el 1,2 PB al importarlo | Unos USD 180.000, una vez | #10 |
| Copia continua por fuera del firewall | Pasarla por el Azure Firewall | Unos USD 194 al mes durante la convivencia | #8 |

### 3.2 Accesos directos de Fabric en vez de duplicar el archivo (F1-13, #17)

**Decisión.** Fabric lee el archivo donde está, en las cuentas de Azure Storage, con accesos directos de OneLake. No copia el 1,2 PB (`fabric-workspaces-ingesta-region.md`; `costo-fabric.md`, sección 6).

| Escenario | Costo único | Al mes | Primer año |
|---|---|---|---|
| Copiar el archivo completo a OneLake Hot | 38.223,94 | 27.600,00 | 387.639,94 |
| Copiar el archivo completo a OneLake Cold | 38.223,94 | 4.800,00 | 98.991,94 |
| **Accesos directos (elegido)** | 0,00 | 12,10 en lecturas | 145,20 |

**Costo evitado:** al menos **USD 4.787,90 al mes y 38.223,94 de costo único**, frente a la copia más barata (OneLake Cold). En cinco años, **USD 325.497,94**. Frente a una copia en Hot, el nivel que Direct Lake y Spark leen sin cargo de recuperación, son USD 27.587,90 al mes.

**Lo que no tiene precio en la tabla:** la copia no sería inmutable, el borrado a los cinco años habría que hacerlo dos veces, y la copia inicial obligaría a subir la capacidad de Fabric durante semanas (#27, sección 6).

### 3.3 Capacidad de Fabric fuera de campaña y fuera del horario (F1-14, #18)

**Decisión.** La capacidad de producción arranca en F16 y, si la medición del primer mes muestra un uso por debajo del 40 %, pasa a F8 fuera de campaña y vuelve a F16 una semana antes de cada campaña. La capacidad de pruebas se pausa fuera del horario laboral. Los reportes internos se ven con licencias Pro, no con una capacidad que regale la lectura (`fabric-acceso-casos-uso-costo.md`, sección 8; `costo-fabric.md`, sección 7).

| Decisión | Alternativa obvia | Costo evitado | En cinco años | Estado |
|---|---|---|---|---|
| Capacidad de pruebas pausada fuera del horario | F4 encendida todo el mes | USD 337,89 al mes | 20.273,40 | Tomada |
| Licencias Pro para quien ve reportes internos | F64 para que todos vean sin licencia | USD 5.747,20 al mes | 344.832,00 | Tomada |
| F8 fuera de campaña | F16 todo el año | USD 8.363,52 al año | 41.817,60 | Se decide con la medición del primer mes |
| Reserva de 8 CU por un año, renovada | Todo en pago por uso | USD 5.110,40 al año | 25.552,00 | Se compra en el cierre del proyecto |

**Por qué no se baja de noche.** Casi toda la carga de Fabric es de segundo plano y Fabric la suaviza en 24 horas: bajar la capacidad de noche no ahorra (`fabric-acceso-casos-uso-costo.md`, sección 8). El ahorro está en el tamaño fuera de campaña, no en la hora del día.

---

## 4. Decisiones tomadas

| Decisión | Alternativa obvia | Costo evitado | En cinco años (USD) | Origen | Fuente |
|---|---|---|---|---|---|
| Siembra del archivo con discos propios | Copiar 1,2 PB por la red | No viable por la red; más barata si Cali cuesta más de USD 520 al mes (sección 3.1) | — | #15 (F1-11) | Siembra, 2 y 9.2 |
| Accesos directos de Fabric sobre el archivo | Copiar el archivo a OneLake | 4.787,90 al mes y 38.223,94 únicos | 325.497,94 | #17 (F1-13) | Fabric, 6 |
| Capacidad de pruebas de Fabric pausada fuera del horario | F4 encendida todo el mes | 337,89 al mes | 20.273,40 | #18 (F1-14) | Fabric, 7 |
| Licencias Pro para quien ve reportes internos | F64 para que todos vean sin licencia | 5.747,20 al mes | 344.832,00 | #18 (F1-14) | Fabric, 7 |
| Escaneo de malware apagado durante la siembra | Escanear el 1,2 PB al importarlo | Unos 180.000, una vez | 180.000,00 | #10 | Seguridad, 6.3 |
| Escanear solo fotos y comprobantes | Escanear también el video | Unos 1.800 al mes | 108.000,00 | #10 | Seguridad, 6.3 |
| Video importado directo a Cold | Importar a Hot y mover después | Unos 15.540: un mes de Hot frente a Cold | 15.540,00 | #15 | Siembra, 9.2 |
| Video en Cold LRS | Cold GRS | 4.653,27 al mes en el mes 1 | 282.332,76 | #15 | Mes estable, 10 |
| Borrado mensual a los cinco años, con la fecha original | Contar desde la importación, o no borrar | Hasta 4.068 al mes en el año 5 | 124.074,00 | #15 | Mes estable, 4.3 |
| DDoS IP Protection solo para la IP del portal | DDoS Network Protection | 2.744,55 al mes | 164.673,00 | #9 | Firewall, 7.2 |
| Azure Firewall Standard, con subida a Premium sin corte | Premium desde el inicio | 365 al mes | 21.900,00 | #9 | Firewall, 7.2 |
| Application Gateway como única entrada del portal | Front Door Premium delante | Al menos 330 al mes | 19.800,00 | #9 | Firewall, 7.2 |
| Gateways de pruebas y desarrollo desde 0 instancias, y desarrollo sin WAF | Una instancia reservada y WAF en cada uno | 210,24 + 116,80 al mes | 19.622,40 | #9 | Firewall, 7.2 |
| VPN Gateway con hub propio | Virtual WAN Standard | Al menos 562 al mes | 33.720,00 | #8 | Red, 2.1 |
| VPN con segundo proveedor en Cali | ExpressRoute | Unos 1.272 al mes | 76.320,00 | #8 | Red, 2.2 |
| Historial de telemetría en el lago, leído por Fabric | Clúster de Azure Data Explorer | Más de 321 al mes | 19.260,00 | #13 | Telemetría, 6.5 |
| Stream Analytics de 1/3 de unidad, validado con la prueba de carga | Una unidad completa | 160,60 al mes | 9.636,00 | #13 | Telemetría, 6.5 |
| Muestreo del 10 % en las trazas | Muestreo por defecto | Unos 259 al mes | 15.540,00 | #16 | Observabilidad, 9.3 |
| Workbooks y vistas de Cost Management | Managed Grafana | Unos 115 al mes | 6.900,00 | #16 | Observabilidad, 9.3 |
| Portal en consumo, que escala solo con la concurrencia | 3 réplicas fijas para el pico de campaña | 236,52 al mes, menos las horas de pico | 13.530,24 | #14 | Mes estable, 3.3 y 5.2 |
| Bases de pruebas y desarrollo en Burstable y sin datos de producción | Dos servidores de 4 vCores | Unos 500 al mes | 30.000,00 | #14 | Migración, 9 |
| Ensayo en un servidor temporal que se borra | Preproducción permanente | Unos 310 al mes | 18.600,00 | #14 | Migración, 9 |
| Plataforma al mínimo hasta el corte | La torre con 4 nodos desde el despliegue | Unos 920, una vez | 920,00 | #14 | Migración, 9 |
| DMS dentro de los 183 días sin costo | Crearlo antes o mantenerlo después | 224,84 por mes fuera del plazo | 224,84 | #14 | Migración, 9 |
| Copia del archivo fuera del firewall durante la convivencia | Pasarla por el firewall | Unos 194 al mes, dos meses | 388,00 | #8 | Red, 6.3 |

Fuentes: Siembra es `carga-c-siembra-1-2pb.md`; Fabric, `costo-fabric.md`; Seguridad, `seguridad-datos-personales-perimetro.md`; Mes estable, `costo-mes-estable-y-campana.md`; Firewall, `red-firewall-y-publicacion.md`; Red, `red-topologia-subnetting.md`; Telemetría, `carga-b-telemetria.md`; Observabilidad, `observabilidad-slo-zabbix.md`; Migración, `costo-migracion.md`.

**Lo que también evita gasto, sin cifra propia:**

- **Apagar Cali el día 62 y no el 90** evita 28 días del costo de Cali, que FríoAndes debe cuantificar (#14).
- **Defender for Cloud y alertas de Log Analytics** en vez de Microsoft Sentinel desde el primer día evitan USD 4,76 por cada GB de registros analizado (#10).
- **Cali sin agentes de Azure** durante la convivencia evita Azure Arc y la ingesta de 14 servidores que se apagan (#16).
- **Sobreconsumo de Fabric con umbral del 10 %** limita el riesgo a USD 630,72 al mes en vez de 1.576,80 (#27).

---

## 5. Propuestas pendientes

| Propuesta | Alternativa actual | Costo evitado | En cinco años (USD) | Origen | Qué falta |
|---|---|---|---|---|---|
| Borrar lo que tenía más de cinco años al momento de la siembra | Guardarlo hasta que FríoAndes decida | Unos 3.000 al mes: capacidad y etiquetas | 181.356,00 | #15 y #26 | Que FríoAndes autorice el borrado (pregunta 1 de la sesión de aclaraciones) |
| Documentos de más de un año a Cold GRS, por ciclo de vida | Todo en Cool GRS | Unos 1.633 al mes | 89.487,72 | #15 y #26 | Que #15 lo acepte; Cold cobra 0,03 por GB leído |
| F8 fuera de campaña | F16 todo el año | 8.363,52 al año | 41.817,60 | #18 y #27 | La medición del primer mes |
| Fecha original como metadato, leída del inventario mensual | Etiqueta de índice por archivo | 768,74 al mes en el mes 1, bajando a unos 311 | 32.380,05 | #15 y #26 | Que #15 cambie el proceso de borrado |
| Reserva de 8 CU de Fabric por un año, renovada | Todo en pago por uso | 5.110,40 al año | 25.552,00 | #27 | Compra en el cierre del proyecto |
| Regla de la torre acotada a la franja del pico | 04:00 a 22:00 | Unos 880 al año | 4.397,61 | #14 y #26 | Medir el pico de la torre en la primera campaña |
| Centros hacia la torre de Cali por su VPN hasta el corte | Tránsito por Azure (FW-401) | Unos 670, una vez | 670,00 | #8, #9 y #25 | Que la red prefiera el túnel a Cali mientras exista |

Juntas suman hasta USD 375.660,98 en cinco años, pero se solapan: si se borra lo de más de cinco años, sus etiquetas ya no existen y el ahorro de pasarlas a metadato baja. La mayor depende solo de una respuesta de FríoAndes.

---

## 6. Validación y cierre

| Criterio de aceptación | Evidencia |
|---|---|
| Al menos 3 decisiones documentadas, cada una con el costo evitado estimado y el issue de arquitectura que la originó | 25 decisiones tomadas en la sección 4 y 7 propuestas en la sección 5, cada una con su alternativa obvia, su costo evitado, su cifra a cinco años, su issue de origen y su fuente. Las tres del enunciado tienen detalle en la sección 3: la siembra física (F1-11, #15), los accesos directos de Fabric (F1-13, #17) y la capacidad de Fabric fuera de campaña (F1-14, #18) |

# Costo total del proyecto y costo total de propiedad

Este documento suma todo lo que cuesta el proyecto, no solo la nube: el equipo que lo hace, por rol y por fase; la capacitación del equipo de FríoAndes; la consultoría externa; la migración; y, una vez en Azure, la nube, Fabric, las licencias, el soporte y el equipo que opera la plataforma con su guardia. Con eso arma el costo total de propiedad a 1, 3 y 5 años. Toma las cifras de los otros tres documentos de costos sin calcularlas de nuevo: la migración (#25, `costo-migracion.md`), el mes estable y la campaña (#26, `costo-mes-estable-y-campana.md`) y Fabric (#27, `costo-fabric.md`). Las decisiones que bajan el costo están en `decisiones-ahorro.md`.

## Contenido

1. Alcance y convención
2. Resumen
3. Costos únicos del proyecto
4. Costos recurrentes del primer año
5. Costo total de propiedad a 1, 3 y 5 años
6. Comparación con seguir en Cali
7. Cómo se evita contar dos veces
8. Cómo se recalcula
9. Supuestos y confirmaciones pendientes de FríoAndes
10. Validación y cierre

---

## 1. Alcance y convención

- **Únicos** son los costos que existen porque existe el proyecto, del arranque (28 de septiembre de 2026) al cierre (30 de abril de 2027). **Recurrentes** son los que se pagan cada año desde el mes 1 de operación, marzo de 2027.
- **Tarifa del equipo:** COP 120.000 por hora, costo para la empresa, es decir **USD 36,24**, la misma de #25. Es la tarifa promedio del equipo interno, igual para todos los roles hasta que FríoAndes dé las tarifas por rol (sección 9.1). Un año de una persona de tiempo completo son 1.920 horas: 48 semanas de 40 horas.
- **Pesos colombianos:** a 3.311 pesos por dólar, la misma tasa de #25, #26 y #27.
- **Precios:** los de Azure son de lista, de la API pública de precios. Las licencias de Microsoft y de GitHub son precios de lista publicados, con compromiso anual. Lo que no tiene precio publicado (cursos, partner, mensajes de texto) es un supuesto marcado como tal. Sin impuestos.
- **Fechas y fases:** las del cronograma general (`docs/architecture/cronograma-proyecto.md`).

---

## 2. Resumen

| | Únicos | Recurrentes | Total | COP | Por mes |
|---|---|---|---|---|---|
| **1 año** | 419.354,89 | 445.004,97 | **864.359,86** | Unos 2.862 millones | 72.029,99 |
| **3 años** | 419.354,89 | 1.329.228,69 | **1.748.583,59** | Unos 5.790 millones | 48.571,77 |
| **5 años** | 419.354,89 | 2.205.740,36 | **2.625.095,25** | Unos 8.692 millones | 43.751,59 |

**Costos únicos: USD 419.354,89** (unos COP 1.388 millones)

| Bloque | USD | Parte |
|---|---|---|
| Equipo del proyecto: 4.550 horas por rol y fase | 164.904,86 | 39 % |
| Migración (#25), con su propia contingencia | 153.417,32 | 37 % |
| Capacitación del equipo de FríoAndes | 42.680,50 | 10 % |
| Costos entre documentos: del corte al mes 1, Fabric antes del corte y licencias antes del mes 1 | 14.064,70 | 3 % |
| Consultoría externa | 9.600,00 | 2 % |
| Contingencia del 15 % sobre lo nuevo | 34.687,51 | 8 % |

**Costos recurrentes del primer año: USD 445.004,97** (unos COP 1.473 millones)

| Bloque | USD | Parte |
|---|---|---|
| Nube en estado estable, con campañas y pruebas de carga (#26) | 207.672,35 | 47 % |
| Equipo de operación, con guardia | 167.470,85 | 38 % |
| Licencias, herramientas y soporte | 35.004,00 | 8 % |
| Fabric, en línea aparte (#27) | 34.857,76 | 8 % |

Tres conclusiones:

- **La nube es menos de la mitad.** En cinco años la nube y Fabric son el 45 % del costo total. La operación es el 32 % y el proyecto con la migración el 16 %.
- **El equipo del proyecto cuesta más que la migración.** Las 4.550 horas de diseño, construcción, adaptaciones, Fabric y cambio son USD 164.905, frente a los 153.417 de la migración completa. Con las 828 horas que ya cuenta #25, el proyecto suma unas 5.380 horas de trabajo.
- **Las licencias de Entra ID son casi toda la línea de licencias.** Son USD 32.940 al año, porque el acceso condicional exige P1 para los 450 usuarios internos. Si FríoAndes ya tiene Microsoft 365 E3 o E5, que incluyen P1, la línea baja a unos USD 3.700 al año (sección 9.1).

---

## 3. Costos únicos del proyecto

### 3.1 Equipo del proyecto, por rol y fase

**Fases.** Agrupan las del cronograma general. Se solapan en el calendario (el diseño sigue mientras empieza la construcción), así que cada rol cuenta cada semana una sola vez.

| Fase | Fechas | Qué incluye |
|---|---|---|
| Diseño | 28 de septiembre al 13 de noviembre de 2026 | Arquitectura (Fase 1), costos y plantillas de cambio (Fases 3 y 4), aprobación |
| Construcción | 19 de octubre al 18 de diciembre | Código de infraestructura y pipeline, landing zone e identidades, despliegue de los ambientes, adaptaciones en desarrollo |
| Preparación del día 0 | 19 de diciembre al 8 de enero de 2027 | Adaptaciones en pruebas, pruebas de carga, seguridad y continuidad, capacitación de operación |
| Convivencia y corte | 11 de enero al 14 de marzo | Centros y telemetría, replicación de la base, Fabric en no productivo y en producción, ensayo, corte, apagado de Cali |
| Estabilización y cierre | 15 de marzo al 30 de abril | Semana Santa sin cambios, medición de Fabric, entrega a operación, informe de cierre |

**Horas por rol y fase**

| Rol | Diseño | Construcción | Preparación del día 0 | Convivencia y corte | Estabilización y cierre | Horas | USD |
|---|---|---|---|---|---|---|---|
| Gestión del proyecto | 140 | 100 | 60 | 180 | 140 | 620 | 22.470,55 |
| Arquitectura | 280 | 50 | 30 | 90 | 70 | 520 | 18.846,27 |
| Redes y seguridad | — | 280 | 60 | 180 | — | 520 | 18.846,27 |
| Ingeniería de IaC y pipeline | — | 720 | 60 | 90 | — | 870 | 31.531,26 |
| Desarrollo de las adaptaciones | — | 560 | 120 | 90 | — | 770 | 27.906,98 |
| Base de datos y migración | — | — | — | 80 | — | 80 | 2.899,43 |
| Datos y Fabric | — | — | — | 480 | 40 | 520 | 18.846,27 |
| QA y pruebas de carga | — | 80 | 160 | 80 | — | 320 | 11.597,70 |
| Gestión del cambio | — | 60 | 60 | 180 | 30 | 330 | 11.960,13 |
| **Total** | **420** | **1.850** | **550** | **1.450** | **280** | **4.550** | **164.904,86** |

**De dónde salen las horas** (personas × semanas × 40 horas × dedicación):

| Rol | Supuesto |
|---|---|
| Gestión del proyecto | Media dedicación las 31 semanas del proyecto: seguimiento semanal, riesgos, presupuesto, comité de cambios e informe de cierre |
| Arquitectura | Tiempo completo las 7 semanas del diseño; después, un cuarto de tiempo para aprobar cambios y acompañar la construcción, el ensayo, el corte y el cierre |
| Redes y seguridad | Tiempo completo 7 semanas (landing zone, identidades, MFA, acceso condicional, PIM, firewall y túneles); media dedicación en la preparación y en la convivencia, cuando se conectan los centros uno por uno y se retiran las reglas temporales |
| Ingeniería de IaC y pipeline | Dos personas las 9 semanas de construcción: cuatro módulos, tres ambientes y el pipeline con aprobación y bloqueo de la ventana (#20 a #24) |
| Desarrollo de las adaptaciones | Dos personas 7 semanas en desarrollo y media dedicación 3 semanas en pruebas: evidencias en Blob, MySQL 8.4, contenedores, columnas y borrado lógico para Fabric |
| Base de datos y migración | Media dedicación las 4 semanas de la replicación con DMS. La siembra, la compatibilidad con MySQL 8.4 y las noches ya están en #25 |
| Datos y Fabric | Dos personas a tres cuartos de tiempo las 8 semanas del primer release; un cuarto de tiempo en la medición del primer mes |
| QA y pruebas de carga | Preparar los guiones 2 semanas; dos personas en las pruebas de carga, seguridad y continuidad; media dedicación en la convivencia para los criterios del ensayo |
| Gestión del cambio | Media dedicación desde la capacitación de operación hasta el apagado: material, sesiones, avisos a despacho, calidad y clientes |

**Lo que no está en esta tabla porque ya está en #25:** las 336 horas de la siembra, las 40 de compatibilidad con MySQL 8.4, las 60 del guion del corte, las ventanas nocturnas de la convivencia, el ensayo, el corte, el acompañamiento del domingo y las noches del apagado de Cali. Son 828 horas de persona, con sus recargos nocturnos y dominicales (`costo-migracion.md`, sección 6).

### 3.2 Capacitación del equipo de FríoAndes

| Concepto | Cálculo | USD |
|---|---|---|
| Cursos con instructor: administración de Azure, seguridad, Fabric, Terraform y GitHub Actions | 10 cupos × USD 1.200 | 12.000,00 |
| Exámenes de certificación | 10 × USD 165 | 1.650,00 |
| Horas de quienes toman los cursos | 10 personas × 32 h × 36,24 | 11.597,70 |
| Operación y guardia: runbooks y simulacro de alertas | 6 personas × 16 h × 36,24 | 3.479,31 |
| Usuarios clave de despacho y facturación: pruebas con datos replicados | 20 personas × 8 h × 36,24 | 5.798,85 |
| Sesión de cambios para los usuarios internos | 450 personas × 0,5 h × 36,24 | 8.154,64 |
| **Subtotal** | | **42.680,50** |

Los 10 cupos son para quienes operan la plataforma después del cierre: plataforma, seguridad, base de datos, datos y FinOps (sección 4.4). La torre sigue siendo la misma aplicación, así que los 450 usuarios internos solo necesitan una sesión corta sobre lo que cambia: el acceso con MFA, la dirección y a quién llamar. Quien prepara y dicta las sesiones está en el rol de gestión del cambio (sección 3.1).

### 3.3 Consultoría externa

| Concepto | Cálculo | USD |
|---|---|---|
| Partner de Microsoft: revisión Well-Architected del diseño | 40 h × USD 100 | 4.000,00 |
| Partner de Microsoft: acompañamiento del ensayo y del corte | 2 noches × 2 personas × 8 h × USD 100 | 3.200,00 |
| Partner de Microsoft: soporte del primer mes en Azure | 24 h × USD 100 | 2.400,00 |
| **Subtotal** | | **9.600,00** |

Es una segunda mirada externa en los dos momentos de más riesgo: antes de aprobar el diseño y durante el ensayo y el corte. No reemplaza al equipo. Si FríoAndes no la contrata, el total baja USD 11.040, con su contingencia.

### 3.4 Costos que caen entre documentos

Cada documento de costos corta en una fecha. Estas cuatro partidas caen entre esos cortes y ninguno las cuenta:

| Concepto | Cálculo | USD |
|---|---|---|
| Plataforma del corte al mes 1: 14 al 28 de febrero de 2027 | 17.239,76 × 14 / 30,42 | 7.935,01 |
| Fabric de producción del 15 al 28 de febrero | 2.891,89 × 14 / 30,42 | 1.331,06 |
| Fabric no productivo antes del corte: 18 de enero al 14 de febrero | 187,71 × 27 / 30,42 | 166,62 |
| Licencias antes del mes 1: Entra ID desde el día 0 y GitHub desde octubre | (435 × 6 + 15 × 9) × 1,6 meses + 12 × 4 × 5 meses | 4.632,00 |
| **Subtotal** | | **14.064,70** |

- #25 cuenta Azure hasta el corte del 14 de febrero, y #26 empieza el mes estable el 1 de marzo: las dos semanas del medio van aquí, al costo del mes 1.
- #27 da el costo mensual de Fabric, y el cronograma lo prepara en no productivo desde el 18 de enero y lo pasa a producción el 15 de febrero.

### 3.5 Migración

**USD 153.417,32**, tal como lo calcula #25 (`costo-migracion.md`, sección 2): la siembra del archivo, Azure y la red antes del corte, los servicios temporales de la migración, el tránsito de los centros, las horas del equipo en la migración y su propia contingencia del 15 %. No se le suma otra contingencia.

### 3.6 Total de los costos únicos

| Bloque | USD |
|---|---|
| Equipo del proyecto (3.1) | 164.904,86 |
| Capacitación (3.2) | 42.680,50 |
| Consultoría externa (3.3) | 9.600,00 |
| Costos entre documentos (3.4) | 14.064,70 |
| **Subtotal de lo nuevo** | **231.250,06** |
| Contingencia del 15 % sobre lo nuevo | 34.687,51 |
| Migración, con su contingencia (3.5) | 153.417,32 |
| **Total de los costos únicos** | **419.354,89** |

La contingencia es la misma de #25 y cubre que las horas por rol son una estimación sin el plan detallado de cada equipo, y que los cursos y el partner no están cotizados.

---

## 4. Costos recurrentes del primer año

### 4.1 Nube

**USD 207.672,35** en el primer año, de marzo de 2027 a febrero de 2028 (#26, sección 6). Incluye la plataforma en estado estable, el archivo con sus cinco años de retención, las campañas con la regla de la torre de 04:00 a 22:00, las tres pruebas de carga y el segundo proveedor de internet de Cali. Los años 2 a 5 bajan un poco porque vencen las etiquetas de lo sembrado (sección 5).

### 4.2 Fabric

**USD 34.857,76** al año, con F16 todo el año y 40 licencias Pro (#27, sección 2). Si la medición del primer mes permite F8 fuera de campaña, baja a 26.494,24 (`decisiones-ahorro.md`).

### 4.3 Licencias, herramientas y soporte

| Concepto | Cálculo | USD al año |
|---|---|---|
| Entra ID P1: MFA y acceso condicional para los usuarios internos | 435 × 6 × 12 | 31.320,00 |
| Entra ID P2: PIM para administradores y aprobadores | 15 × 9 × 12 | 1.620,00 |
| Entra External ID para los clientes del portal | Sin costo hasta 50.000 usuarios activos al mes | 0,00 |
| Power BI Pro | En la línea de Fabric (#27): 40 × 14 × 12 | 0,00 |
| GitHub Team: repositorios, Actions y Environments | 12 × 4 × 12 | 576,00 |
| Terraform | Versión abierta; el estado vive en Azure Storage (#26) | 0,00 |
| Mensajes de texto de las alertas nocturnas | 300 × 0,08 × 12 | 288,00 |
| Plan de soporte de Azure Standard | 100 × 12 | 1.200,00 |
| **Subtotal** | | **35.004,00** |

- **Entra ID.** El acceso condicional y la MFA del diseño de gobierno (`gobierno-landing-zone.md`) exigen P1 para cada usuario al que se aplican: los 450 internos. PIM exige P2 para quien tiene roles elegibles o los aprueba: unas 15 personas de plataforma, seguridad, base de datos y aprobadores del comité de cambios. P2 incluye P1, así que esas 15 no pagan las dos.
- **Clientes del portal.** Los unos 2.000 clientes corporativos entran con Entra External ID, que no cobra los primeros 50.000 usuarios activos al mes.
- **Monitoreo.** Azure Monitor, Log Analytics y Defender ya están en la nube (#26). Lo que queda fuera de Azure son los mensajes de texto de las alertas de guardia: unos 300 al mes, por cotizar con el proveedor.
- **Soporte.** El plan Standard responde en menos de una hora a un caso crítico, las 24 horas. Professional Direct (USD 1.000 al mes) suma un gestor de cuenta y revisiones de arquitectura, y queda como opción si FríoAndes quiere ese acompañamiento después del primer año.

### 4.4 Equipo de operación de la plataforma

| Concepto | Cálculo | USD al año |
|---|---|---|
| Ingeniería de plataforma: operación diaria, cambios en ventana, costos y respuesta a incidentes | 1 × 1.920 h × 36,24 | 69.586,23 |
| Seguridad e identidades: Defender, accesos, PIM y revisión de registros | 0,25 × 1.920 h × 36,24 | 17.396,56 |
| Base de datos: rendimiento, réplica, respaldos y pruebas de continuidad | 0,25 × 1.920 h × 36,24 | 17.396,56 |
| Datos y Fabric: modelos, Activator, capacidad y licencias | 0,25 × 1.920 h × 36,24 | 17.396,56 |
| FinOps y gobierno: presupuestos, conciliación mensual y reservas | 0,25 × 1.920 h × 36,24 | 17.396,56 |
| Guardia: disponibilidad de noche y fines de semana | 128 h × 52 semanas = 6.656 h × 10 % × 36,24 | 24.123,23 |
| Guardia: incidentes atendidos | 24 al año × 3 h × 1,6 × 36,24 | 4.175,17 |
| **Subtotal** | | **167.470,85** |

- **Dos personas de tiempo completo en total**, repartidas en cinco roles. La plataforma corre en servicios administrados (Container Apps, MySQL Flexible, Managed Redis, IoT Hub), así que no hay servidores que parchar. El trabajo es de cambios, accesos, costos y respuesta.
- **Guardia de la plataforma.** Una persona disponible cada noche y fin de semana, en rotación entre las cinco funciones. Se paga la disponibilidad al 10 % de la hora y cada incidente con el recargo nocturno o dominical de la Ley 2466 de 2025, en promedio 1,6 veces la hora. Es distinta de la guardia de calidad, que ya existe y recibe de noche las alertas de temperatura (`carga-b-telemetria.md`, sección 3.4).
- **Desde cuándo.** El equipo de operación empieza en el mes 1. Entre el corte y el mes 1, la operación la hace el equipo del proyecto con las horas de la sección 3.1.
- **No es todo costo nuevo.** Este equipo reemplaza a quienes hoy operan VMware, los servidores y Zabbix en Cali. El costo de ese equipo no está en el enunciado (sección 6).

---

## 5. Costo total de propiedad a 1, 3 y 5 años

### 5.1 Recurrentes por año

| Año | Nube (#26) | Fabric (#27) | Licencias y soporte | Operación | Total |
|---|---|---|---|---|---|
| 1 | 207.672,35 | 34.857,76 | 35.004,00 | 167.470,85 | 445.004,97 |
| 2 | 205.743,26 | 34.857,76 | 35.004,00 | 167.470,85 | 443.075,87 |
| 3 | 203.815,24 | 34.857,76 | 35.004,00 | 167.470,85 | 441.147,86 |
| 4 | 201.887,22 | 34.857,76 | 35.004,00 | 167.470,85 | 439.219,84 |
| 5 | 199.959,21 | 34.857,76 | 35.004,00 | 167.470,85 | 437.291,82 |

Precios de lista constantes: no se proyecta inflación, cambio de precios de Azure ni aumento salarial. El archivo crece con las cifras del caso y lo absorbe el borrado a los cinco años (#26, sección 4).

### 5.2 Costo total de propiedad

| Horizonte | Únicos | Recurrentes acumulados | Total | COP | Por mes |
|---|---|---|---|---|---|
| 1 año | 419.354,89 | 445.004,97 | 864.359,86 | Unos 2.862 millones | 72.029,99 |
| 3 años | 419.354,89 | 1.329.228,69 | 1.748.583,59 | Unos 5.790 millones | 48.571,77 |
| 5 años | 419.354,89 | 2.205.740,36 | 2.625.095,25 | Unos 8.692 millones | 43.751,59 |

**Qué pesa en cinco años**

| Bloque | USD en 5 años | Parte |
|---|---|---|
| Nube (#26) | 1.019.077,28 | 39 % |
| Operación | 837.354,27 | 32 % |
| Proyecto nuevo, con contingencia | 265.937,57 | 10 % |
| Licencias, herramientas y soporte | 175.020,00 | 7 % |
| Fabric (#27) | 174.288,80 | 7 % |
| Migración (#25) | 153.417,32 | 6 % |

Los costos únicos se diluyen: son el 49 % del primer año y el 16 % de cinco años. Por eso el costo por mes baja de USD 72.030 en un horizonte de un año a 43.752 en uno de cinco.

**Con las propuestas de ahorro aprobadas.** Las siete propuestas pendientes de `decisiones-ahorro.md` restarían hasta USD 375.661 en cinco años, un 14 % del total. La mayor depende solo de que FríoAndes autorice borrar los archivos de más de cinco años.

---

## 6. Comparación con seguir en Cali

El enunciado no da lo que cuesta hoy el datacenter de Cali, y #25 ya lo pidió como confirmación pendiente. Sin ese dato, la comparación queda como supuesto, con el umbral que la decide.

**Umbral.** Azure cuesta menos en cinco años si seguir en Cali cuesta más de **USD 29.795,68 al mes**, sin contar el equipo de operación: (2.625.095,25 − 837.354,27) / 60. La operación se deja fuera de los dos lados porque Cali también necesita su equipo. Si FríoAndes demuestra que Cali se opera sin personal, el umbral sube a USD 43.751,59 al mes.

**Qué tendría que sumar Cali para cumplir lo mismo que el diseño:**

| Necesidad del enunciado | Qué exige seguir en Cali | Dato que falta |
|---|---|---|
| El archivo no tiene holgura ni respaldo, y crece 12 TB al mes | Almacenamiento nuevo para 1,2 PB más 720 TB en cinco años, y una segunda copia fuera de Cali | Cotización de almacenamiento y de un sitio alterno |
| El despacho se pone lento en campaña | Capacidad fija para el pico de campaña todo el año | Cotización de servidores |
| RPO de 15 minutos y RTO de 4 horas | Un segundo sitio con réplica de la base | Cotización del sitio y del enlace |
| MySQL 5.7 y CentOS 7 sin soporte | Migrar versiones dentro de Cali, o pagar soporte extendido | Plan de actualización |
| VMware | Renovar licencias con el modelo de suscripción actual | Contrato vigente |
| Energía, espacio, refrigeración y enlaces | Lo que se paga hoy, más lo que se agregue | Costo mensual de hoy |

El umbral es el dato que FríoAndes necesita para cerrar la comparación: si la suma de esas filas, llevada al mes, pasa de unos USD 30.000, Azure cuesta menos en cinco años, además de resolver lo que Cali no resuelve.

---

## 7. Cómo se evita contar dos veces

| Partida | Dónde se cuenta | Dónde no se repite |
|---|---|---|
| Azure y red hasta el corte | #25 | No está en la nube del primer año, que empieza en marzo |
| Del corte al 28 de febrero | Sección 3.4 | Ni #25 ni #26 lo cuentan |
| Horas de la siembra, la compatibilidad de la base, el guion, las noches, el ensayo, el corte y el apagado | #25, sección 6 | Fuera de las horas por rol (sección 3.1) |
| Contingencia de la migración | Dentro de #25 | La contingencia de este documento solo se aplica a lo nuevo |
| Licencias Power BI Pro | #27 | En licencias aparecen en cero, con la referencia |
| Lecturas del archivo que hace Fabric | #27 | No están en el archivo de #26 |
| Segundo proveedor de internet de Cali | #25 hasta el corte; #26 después | Una sola vez por periodo |
| Defender, Log Analytics y Azure Monitor | #26 | No están en licencias ni en herramientas |
| Prueba de carga antes del día 0 | #25 | #26 cuenta solo las tres de cada año |
| Operación entre el corte y el mes 1 | Equipo del proyecto (sección 3.1) | El equipo de operación empieza en el mes 1 |

---

## 8. Cómo se recalcula

Todas las cifras salen de `tools/calc_costo_total_proyecto.py`. El script importa el modelo del mes estable (`calc_costo_mes_estable.py`) para los años de nube y los ahorros a cinco años, y toma las cifras de #25 y #27 de sus documentos, con la sección de origen anotada.

```bash
cd docs/costs/tools
python3 calc_costo_total_proyecto.py
```

Si cambia la tarifa del equipo, una dedicación, una licencia o el mes estable, se cambia en su script, se corre de nuevo y se copian las tablas. El PDF de costos se compila después con `tools/build_costs_pdf.py`.

---

## 9. Supuestos y confirmaciones pendientes de FríoAndes

### 9.1 Confirmaciones que necesita el estimado

| Tema | Pregunta | Qué pasa si la respuesta cambia |
|---|---|---|
| Tarifa por rol | ¿Cuánto cuesta por hora cada rol, y qué roles cubre un proveedor? | Hoy todos usan la tarifa promedio de #25. Las horas del equipo son el 39 % de los costos únicos |
| Microsoft 365 | ¿Qué plan tiene FríoAndes? E3 y E5 incluyen Entra ID P1, y E5 incluye P2 y Power BI Pro | Con E3, licencias baja de 35.004 a unos 3.684 al año; con E5, también salen las Pro de #27 |
| Costo de Cali | ¿Cuánto cuesta al mes mantener el datacenter de Cali y quién lo opera? | Cierra la comparación de la sección 6 |
| Equipo de operación | ¿Las personas que hoy operan Cali pasan a operar Azure? | Si es así, la operación no es costo nuevo para FríoAndes |
| Guardia | ¿Cómo compensa FríoAndes la disponibilidad? | Cada 10 puntos de la hora son unos USD 24.000 al año |
| Partner y cursos | ¿Se contrata un partner? ¿Hay cursos con Microsoft o con un centro autorizado? | Partner, cursos y exámenes son USD 26.737,50 con contingencia |
| Plan de soporte | ¿Standard o Professional Direct? | Professional Direct suma USD 10.800 al año |

### 9.2 Supuestos del estimado

| Supuesto | Por qué se asume |
|---|---|
| Todos los roles usan la tarifa promedio de COP 120.000 por hora | Es la tarifa de #25; el issue pide la misma |
| Un año de tiempo completo son 1.920 horas | 48 semanas de 40 horas, sin festivos ni vacaciones |
| Las horas por rol salen de personas × semanas × dedicación, con las fases del cronograma | No hay todavía un plan detallado por equipo |
| La contingencia del 15 % se aplica solo a lo nuevo | La migración ya trae la suya |
| El equipo de operación son 2 personas de tiempo completo repartidas en cinco roles, desde el mes 1 | La plataforma usa servicios administrados; el trabajo es de cambios, accesos, costos y respuesta |
| La guardia de la plataforma paga la disponibilidad al 10 % de la hora, con unos 24 incidentes al año | Referencia sin política de FríoAndes |
| 450 usuarios con Entra ID P1, de ellos 15 con P2 | El acceso condicional se aplica a todos los internos; PIM, a administradores y aprobadores |
| 10 cupos de curso a USD 1.200 y exámenes a USD 165 | Referencia sin cotización |
| Partner a USD 100 la hora, 96 horas | Referencia sin cotización |
| Plan de soporte Standard | Respuesta en menos de una hora para casos críticos, las 24 horas |
| Precios constantes en los cinco años | Sin inflación ni cambios de precio; se revisa cada año con Cost Management |

---

## 10. Validación y cierre

| Criterio de aceptación | Evidencia |
|---|---|
| El costo total incluye recursos humanos por rol y fase, capacitación, gestión del proyecto y del cambio, licencias, soporte y operación, además de nube, Fabric y migración, sin contar ninguna cifra dos veces | Sección 3.1 (nueve roles por cinco fases, gestión del proyecto y del cambio incluidas), 3.2 (capacitación), 3.3 (consultoría), 3.5 (migración), 4.1 y 4.2 (nube y Fabric), 4.3 (licencias y soporte) y 4.4 (operación con guardia). La sección 7 dice dónde se cuenta cada partida que podría repetirse |
| Presenta el costo total de propiedad a 1, 3 y 5 años, separando únicos y recurrentes | Sección 5.2, con los recurrentes de cada año en la 5.1 y la comparación con Cali como supuesto, con su umbral, en la 6 |
| Al menos 3 decisiones documentadas, cada una con su costo evitado y el issue que la originó | `decisiones-ahorro.md`: 25 decisiones tomadas y 7 propuestas |
| Existe un PDF único con F3-01, F3-02, F3-03 y el costo total en su cuerpo, y cada cifra es trazable a su supuesto | `docs/costs/costs-frioandes.pdf`, compilado con `tools/build_costs_pdf.py`, con los supuestos de costos como anexo |

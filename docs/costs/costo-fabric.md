# Costo de Microsoft Fabric, en línea aparte

Este documento estima el costo mensual de Microsoft Fabric separado del resto de la plataforma, en mes normal y en mes de campaña, y lo compara con la alternativa descartada de copiar el archivo histórico completo a OneLake. Cada cifra lleva el supuesto que la sostiene. Las cantidades (tamaños de capacidad, horas, licencias, lecturas) vienen del diseño de Fabric: `fabric-workspaces-ingesta-region.md` y `fabric-acceso-casos-uso-costo.md`.

## Contenido

1. Alcance y convención
2. Resumen
3. Mes normal
4. Mes de campaña
5. Después de la medición del primer mes
6. Copiar el archivo completo frente a atajos
7. Decisiones que bajan o evitan gasto
8. Sensibilidad
9. Cómo se recalcula
10. Supuestos y confirmaciones pendientes de FríoAndes

---

## 1. Alcance y convención

### 1.1 Convención

- **Precios:** de lista, en dólares, sin descuentos ni reservas, de la API pública de precios de Azure para East US 2. El precio de Power BI Pro sale de la página de precios de Microsoft. Un mes son 730 horas.
- **Pesos colombianos:** a 3.311 pesos por dólar, la misma tasa del costo de la migración.
- **Reserva:** no entra en las tablas de costo; se presenta como decisión en la sección 7.
- **Sin contingencia porcentual:** la capacidad es un precio fijo por hora. Lo que puede mover el costo se muestra en la sección 8.

### 1.2 Qué entra en la línea de Fabric

Todo lo que existe solo porque existe Fabric, separado por quién lo cobra. La conciliación mensual identifica cada cargo como indica `gobierno-auditoria-facturacion.md`: Fabric por recurso y medidor, antes que pruebas.

| Partida | Quién la cobra | Cómo se separa en la conciliación |
|---|---|---|
| `fcfaprod` y `fcfanoprod` | Azure, recurso de capacidad de Fabric en `rg-fa-analitica-prod` y `rg-fa-analitica-dev` | Por recurso y etiqueta `costo=fabric` |
| Almacenamiento de OneLake | Azure, medidor de OneLake; se cobra aunque la capacidad esté pausada | Por medidor |
| Licencias Pro | Microsoft 365, fuera de Azure | Factura de licencias |
| Lecturas del archivo por atajo | Las cuentas del archivo, en `sub-fa-prod` | Estimación atribuida a Fabric: no se pueden separar por recurso |
| Registros de los modelos | El espacio central de Log Analytics | Por tabla (`PowerBIDatasetsWorkspace`) |

Dentro de `fcfaprod` corren, sin cargo aparte, el gateway de red virtual, Eventstream, Activator, Copy Job, los cuadernos de Python y de Spark, las funciones de IA y las transacciones de OneLake. Con las tasas publicadas suman unos 8,2 CU en mes normal y 10,7 en campaña, de los 16 de F16 (`fabric-acceso-casos-uso-costo.md`, sección 8.1).

No entran la base, el Event Hub, Stream Analytics ni las cuentas del archivo y de la telemetría: existen aunque Fabric no exista y van en el costo de la plataforma.

---

## 2. Resumen

| Escenario | USD al mes | COP al mes |
|---|---|---|
| Mes normal, al arranque (F16) | 2.891,89 | Unos 9,6 millones |
| Mes de campaña (F16) | 2.938,13 | Unos 9,7 millones |
| Mes normal con F8, si el primer mes de operación lo permite | 1.840,69 | Unos 6,1 millones |

| Escenario | USD al año |
|---|---|
| F16 todo el año | 34.857,76 |
| F8 fuera de campaña | 26.494,24 |
| Reserva de 8 CU (sección 7) | Resta 5.110,40 a cualquiera de los dos |

**Lo que se ahorra al no copiar el archivo:** al menos USD 4.787,90 al mes y 38.223,94 de costo único (sección 6).

---

## 3. Mes normal

| Partida | Cálculo | USD al mes | Quién lo cobra |
|---|---|---|---|
| `fcfaprod` | F16: 16 × 0,18 × 730 | 2.102,40 | Fabric |
| `fcfanoprod` | F4: 4 × 0,18 × 261 horas (lunes a viernes, de 07:00 a 19:00) | 187,71 | Fabric |
| Almacenamiento de OneLake | 90 GB × 0,023 | 2,08 | Fabric |
| Licencias Pro | 40 × 14 | 560,00 | Microsoft 365 |
| Lecturas del archivo por atajo | 1.100 GB × 0,01 + 1,1 millones de lecturas × 0,01 por 10.000 | 12,10 | Cuenta de documentos |
| Registros de los modelos | 10 GB × 2,76 | 27,60 | Log Analytics |
| **Total** | | **2.891,89** | Unos COP 9,6 millones |

- Lo que factura Fabric en Azure: USD 2.292,19.
- Si FríoAndes tiene Microsoft 365 E5, que incluye Pro, no se compran licencias y el total queda en USD 2.331,89.

**De dónde salen las cantidades:**

- `fcfanoprod` encendida 12 horas al día, 5 días a la semana: 12 × 30,4 × 5/7 = 261 horas.
- OneLake: vistas del libro operativo hasta 80 GB (como máximo el 20 % de una base de menos de 400 GB), eventos de Activator de 30 días (unos 487.000 al día de 0,5 KB, 7,3 GB) y tablas curadas y resultados (unos 3 GB).
- Lecturas: las fotos y comprobantes nuevos, unos 1,1 TB al mes en archivos de 1 MB, que se leen una vez al día desde Cool para revisarlos.
- Registros: unos 10 GB al mes, sobre todo consultas del reporte del cliente; se confirma con la tabla de uso de Log Analytics el primer mes.

---

## 4. Mes de campaña

| Partida | Cálculo | USD al mes | Cambio frente al mes normal |
|---|---|---|---|
| `fcfaprod` | F16: 16 × 0,18 × 730 | 2.102,40 | Ninguno: F16 cubre los 10,7 CU estimados (67 %) |
| `fcfanoprod` | F4 en 261 horas | 187,71 | Ninguno: el desarrollo sigue, aunque no se despliega a producción |
| Almacenamiento de OneLake | 90 GB × 0,023 | 2,08 | Ninguno |
| Licencias Pro | 40 × 14 | 560,00 | Ninguno |
| Lecturas del archivo por atajo | 1.540 GB × 0,01 + 1,54 millones de lecturas | 16,94 | 40 % más fotos con 180 camiones |
| Registros de los modelos | 25 GB × 2,76 | 69,00 | Vistas del cliente × 2,5 (2.000 frente a 800 solicitudes por minuto en el pico) |
| **Total** | | **2.938,13** | **+46,24 (2 %)** |

La campaña casi no mueve el costo: la capacidad es un cargo fijo por hora y F16 tiene margen.

**Red de seguridad.** El sobreconsumo de la capacidad paga el uso por encima de F16 a tres veces la tarifa (USD 0,54 por CU hora), solo si ocurre. Microsoft lo activa por defecto con un umbral del 25 %; aquí se deja activo con un umbral del 10 % (38,4 CU hora en 24 horas móviles) y avisos por correo al equipo de datos al 50 % del umbral. El máximo posible es de unos USD 20,74 al día o 630,72 al mes; no se espera usarlo.

---

## 5. Después de la medición del primer mes

Si el uso suavizado de `fcfaprod` queda por debajo del 40 % de F16, la capacidad pasa a F8 fuera de campaña y vuelve a F16 una semana antes de cada campaña, con el runbook de `fabric-acceso-casos-uso-costo.md` (sección 8.4).

| Partida | Mes normal con F8 |
|---|---|
| `fcfaprod` | F8: 8 × 0,18 × 730 = 1.051,20 |
| Resto, igual al mes normal | 789,49 |
| **Total** | **1.840,69** |

El mes de campaña sigue en USD 2.938,13. En el año, con unos 102 días de campaña y una semana previa en F16 por cada una, quedan unos 8 meses en F8.

---

## 6. Copiar el archivo completo frente a atajos

| Escenario | Costo único (leer el origen y escribir en OneLake) | OneLake Hot al mes | OneLake Cold al mes | Primer año en Hot | Primer año en Cold |
|---|---|---|---|---|---|
| Copiar el archivo completo (1,2 PB) | 38.223,94 | 27.600,00 | 4.800,00 | 387.639,94 | 98.991,94 |
| Copiar solo el video (1,05 PB) | 36.373,34 | 24.150,00 | 4.200,00 | 342.719,54 | 89.650,94 |
| **Atajos (elegido)** | 0,00 | 12,10 en lecturas | | 145,20 | |

**Cómo se calcula la copia:**

- **Leer el origen.** 1.050.000 GB de video desde Cold a 0,03 por GB y 150.000 GB de documentos desde Cool a 0,01, más las operaciones de lectura por bloque de 4 MB (0,10 y 0,01 por 10.000).
- **Escribir en OneLake.** 1.626 CU segundos por cada 10.000 bloques de 4 MB: unos 13.875 CU hora, a 0,18. Es más que un mes completo de F16 (11.680 CU hora): la copia inicial obligaría a subir la capacidad o a pagar sobreconsumo durante semanas.
- **Guardar.** 0,023 por GB al mes en Hot o 0,004 en Cold, más el crecimiento de unos 12 TB al mes.
- **El archivo de Azure se queda igual en los dos escenarios.** La evidencia inmutable que pide el contrato y que lee la aplicación de evidencias sigue en sus cuentas: la copia en OneLake se paga además.

**Lo que no tiene precio en la tabla:** la copia no sería inmutable; el borrado a los cinco años y las supresiones habría que hacerlos en los dos lugares; leer desde OneLake Cold también cobra recuperación en CU.

**El ahorro de los atajos:** al menos USD 4.787,90 al mes y 38.223,94 de costo único, comparando con una copia en OneLake Cold. Frente a una copia en Hot, que es el nivel en que Direct Lake y Spark leen sin cargo de recuperación, el ahorro es de USD 27.587,90 al mes. En el primer año, entre USD 98.846,74 y 387.494,74.

---

## 7. Decisiones que bajan o evitan gasto

| Decisión | Alternativa descartada | Efecto |
|---|---|---|
| Atajos en vez de copiar el archivo | Copia de 1,2 PB en OneLake | Al menos USD 4.787,90 al mes y 38.223,94 de costo único (sección 6) |
| Licencias Pro para quien ve reportes internos | F64 para que todos vean con licencia gratuita | USD 5.747,20 al mes (8.409,60 frente a 2.102,40 + 560) |
| `fcfanoprod` pausada fuera del horario | F4 encendida todo el mes | USD 337,89 al mes |
| F8 fuera de campaña, si la medición lo permite | F16 todo el año | USD 1.051,20 por mes normal; unos 8.363,52 al año |
| Reserva de 8 CU por un año | Todo en pago por uso | USD 425,87 al mes; 5.110,40 al año |
| Sobreconsumo con umbral del 10 % | Umbral por defecto del 25 % | Tope de riesgo de USD 630,72 al mes en vez de 1.576,80 |
| Trabajos nocturnos de Spark dentro de la capacidad | Spark a demanda | USD 32,85 al mes; suman unos 0,25 CU promedio dentro de F16 |

**La reserva.** Se compra por CU, a uno o tres años, y el descuento se aplica hora por hora: la CU reservada que no se usa en una hora se pierde, y la reserva no cubre almacenamiento ni red. Con USD 938 por CU por un año (78,17 al mes) frente a 131,40 en pago por uso, se reservan 8 CU, el piso que `fcfaprod` no baja nunca (F8 o F16). Uno y tres años cuestan lo mismo por mes (USD 2.814 por CU por tres años), así que un año compromete menos. Si la medición confirma F16 todo el año, se compran 8 CU más. Reservar los 16 CU desde el arranque ahorraría USD 851,73 al mes, pero con F8 fuera de campaña la mitad de la reserva se perdería.

---

## 8. Sensibilidad

| Variable | Si cambia a | Efecto al mes |
|---|---|---|
| Licencias | FríoAndes tiene Microsoft 365 E5 | −560,00 |
| Licencias | 100 personas ven reportes internos | +840,00 |
| Licencias | Más de unas 525 personas ven reportes | Conviene F64 en vez de Pro |
| Capacidad en campaña | La medición pide F32 | +2.102,40 por mes de campaña |
| Funciones de IA, reportes y Spark | Consumen más de lo estimado | Sin cambio mientras quepan en F16; luego, sobreconsumo hasta 630,72 |
| Registros de los modelos | El doble de volumen | +27,60 en mes normal |
| OneLake | El doble de volumen | +2,08 |

---

## 9. Cómo se recalcula

Todas las cifras salen de `docs/costs/tools/calc_costo_fabric.py`, con los precios y las cantidades al principio del archivo y cada supuesto junto al número que mueve.

```bash
cd docs/costs/tools
python3 calc_costo_fabric.py
```

Después del primer mes de operación se reemplazan los supuestos por lo medido: uso de la capacidad (app de métricas), volumen de registros (tabla de uso de Log Analytics), tamaño de OneLake (reporte de almacenamiento) y licencias asignadas.

---

## 10. Supuestos y confirmaciones pendientes de FríoAndes

### 10.1 Confirmaciones que necesita el estimado

| Tema | Pregunta para FríoAndes | Qué cambia |
|---|---|---|
| Licencias | ¿Tiene Microsoft 365 E5? ¿Cuántas personas verán reportes internos? | Las licencias Pro: de 0 a varios cientos de dólares al mes |
| Compra | ¿Paga Azure por uso, con Enterprise Agreement o con Microsoft Customer Agreement? | Cómo y desde qué suscripción se compra la reserva |
| Campañas | ¿Son reales las fechas que supone el plan de migración para las tres campañas? | Los meses en F16 y en F8 del año |

### 10.2 Supuestos del estimado

| Supuesto | Por qué se asume |
|---|---|
| Precios de lista de East US 2, 730 horas al mes, COP 3.311 por dólar | La misma convención del costo de la migración |
| `fcfaprod` en F16 al arranque y `fcfanoprod` en F4 por 261 horas | Diseño de Fabric, con la carga estimada por componente |
| 40 personas con licencia Pro | Calidad, guardia, líderes y equipo de datos; los despachadores y los clientes no la necesitan |
| 90 GB en OneLake | Vistas del libro operativo, eventos de Activator de 30 días y tablas curadas |
| 1,1 TB al mes de fotos y comprobantes nuevos, en archivos de 1 MB | Mismo supuesto de la siembra del archivo |
| 10 GB al mes de registros de los modelos (25 en campaña) | Sin dato de uso; se mide el primer mes |
| Unos 102 días de campaña al año, con una semana previa en F16 | Calendario supuesto del plan de migración |
| 40 % más fotos y 2,5 veces más vistas del cliente en campaña | Flota de 180 camiones y pico del portal de 2.000 solicitudes por minuto |
| Reserva de 8 CU por un año | Es el piso de `fcfaprod` en cualquier escenario |

# Revisión final de consistencia y verificación de subnetting

Revisión cruzada entre los cuatro grupos de entregables: arquitectura (Fase 1), infraestructura como código (Fase 2), costos (Fase 3) y gestión del cambio (Fase 4). Busca lo que es común en un diseño que evolucionó durante semanas: un documento que cambió y otro que no se actualizó. Al final repite la verificación de no solapamiento de direcciones sobre el código de Terraform.

> **Estado de esta versión, 20 de octubre de 2026.** Están revisadas tres de las cuatro parejas: arquitectura y costos, arquitectura y cambio, y costos y cambio. La pareja arquitectura e IaC tiene una revisión preliminar sobre el módulo de red, que está en revisión (`frioandes-platform/iac`, pull request #2). La verificación final de subnetting sobre el `plan` de Terraform espera a #24. Las dos se completan cuando cierre la Fase 2.

## Contenido

1. Método
2. Arquitectura y costos
3. Arquitectura y cambio
4. Costos y cambio
5. Arquitectura e infraestructura como código
6. Verificación de subnetting sobre el código
7. Inconsistencias corregidas y riesgos abiertos
8. Supuestos
9. Validación y cierre

---

## 1. Método

Para cada pareja se listaron las cifras, fechas y nombres que aparecen en los dos lados, y se compararon una por una contra su fuente: el script de costos, la tabla de políticas del firewall, el guion del corte o el plan de direcciones. Una diferencia se corrige cuando una de las dos fuentes está claramente desactualizada. Cuando depende de algo que no está terminado, queda como riesgo abierto (sección 7).

## 2. Arquitectura y costos

Cada cifra de costo que citan los documentos de arquitectura se comparó con lo que calcula `docs/costs/tools/calc_costo_mes_estable.py` para el mes 1.

| Qué | Arquitectura | Costos (#26) | Resultado |
|---|---|---|---|
| Red completa, con el segundo proveedor de Cali | Unos USD 4.300 al mes (`red-topologia-subnetting.md`, sección 2.1) | Hub y tráfico 3.415,86 + segundo proveedor 906,07 = 4.321,93 | Coincide |
| Azure Firewall Standard | USD 912,50 al mes (`red-firewall-y-publicacion.md`, sección 2) | 1,25 × 730 = 912,50 | Coincide |
| Observabilidad | Unos USD 159 al mes (`observabilidad-slo-zabbix.md`, sección 9) | 159,04 | Coincide |
| Defender for Cloud, con el escaneo de malware | Unos USD 350 al mes (`seguridad-datos-personales-perimetro.md`, sección 6.1) | 347,39 | Coincide |
| Telemetría | De unos USD 167 a 199 al mes, con el historial (`carga-b-telemetria.md`, sección 6.4) | 163,52 sin historial; 164,40 el mes 1 y 198,38 el mes 60 con él | Coincide |
| Capacidad del archivo | USD 6.780 al mes con todo cargado (`carga-c-siembra-1-2pb.md`, sección 9.3) | 2.992,00 + 3.781,44 = 6.773,44 el mes 1 (6.780 en el mes 0) | Coincide |
| Siembra | Unos USD 65.000 sin almacenamiento (`carga-c-siembra-1-2pb.md`, sección 9.1) | 64.920,00 en #25: 74 discos (71 de los nueve trabajos y 3 de repuesto) | Coincide |
| Torre en operación normal y en campaña | 13 vCPU en 4 nodos D4; 20 vCPU en 6 nodos de 04:00 a 22:00 (`carga-c-migracion-y-campana.md`, sección 7.2) | 4 nodos D4 en el mes y 2 nodos más en las horas de campaña | Coincide |
| Portal | 2 réplicas de rastreo y 2 de front; 4 y 3 en campaña (sección 7.3) | 4 réplicas de consumo en el mes; 3 réplicas más en las horas del pico | Coincide |
| Application Gateway | 20 unidades reservadas que cubren las 18 del pico (`red-firewall-y-publicacion.md`, sección 3.3) | Sin costo adicional en campaña | Coincide |
| Fabric | F16 a USD 2.102,40 y pruebas en F4 a 187,71; 40 licencias Pro a USD 560 (`fabric-acceso-casos-uso-costo.md`, sección 8) | 2.891,89 en un mes normal (#27) | Coincide |
| Base de datos | Menos de unos 400 GB (`carga-c-migracion-y-campana.md`, supuestos) | Servidores de 512 GB | Coincide, con margen |
| Costo del proyecto en la visión general | La sección 6 de `vista-general.md` tenía cifras anteriores a #26 y #28 | 419.354,89 de costos únicos y el costo total de propiedad | **Corregido** en #36 |

**Conclusión:** sin inconsistencias pendientes. La única diferencia, el costo de la visión general, ya se corrigió.

## 3. Arquitectura y cambio

El ejemplo de infraestructura (`docs/change/ejemplo-release-notes-infraestructura.md`) es el corte del plan de migración, así que se comparó paso por paso con `carga-c-migracion-y-campana.md`, secciones 4 a 6, y con la tabla de políticas del firewall. El ejemplo de aplicación se comparó con la plataforma de `carga-a-plataforma-logistica.md` y con la estrategia de cambio de `automatizacion-devops.md`, sección 5.

| Qué | Resultado |
|---|---|
| Fechas: día 0, ensayo, corte, plazo de vuelta atrás, apagado de Cali y fechas de reserva | Coinciden |
| Guion del corte, de las 22:00 del sábado a las 04:00 del domingo, con sus dos decisiones (00:55 y 02:25) y el punto de no retorno (02:30) | Coincide paso por paso |
| Criterios para seguir y vuelta atrás en tres momentos | Coinciden |
| Equipo del corte: ocho personas | Coincide |
| Aprobación del comité el lunes 8 de febrero | Coincide; la regla de anticipación se ajustó en #31 |
| Aplicaciones que suben de réplicas a la 01:40 | **Corregido.** El plan decía "los cinco contenedores" y el ejemplo "las ocho aplicaciones". Las dos cosas son ciertas: los cinco contenedores de hoy son ocho aplicaciones en Azure, seis en la torre y dos en el portal (sección 7 del plan). El guion, el criterio de salud y la cita en `observabilidad-slo-zabbix.md` ahora dicen "las ocho aplicaciones" |
| Reglas temporales del firewall que siguen hasta el 8 de marzo | **Corregido.** El ejemplo decía que los grupos 400 y 500 seguían completos hasta el 8 de marzo, pero FW-402 se retira en enero, centro por centro (orden 3 del apagado), y faltaba NSG-prod-14. El ejemplo ahora nombra FW-401, FW-503, FW-504 y NSG-prod-14 |
| Reglas que se retiran en el corte: FW-501, FW-502, NSG-prod-12 y la cuenta de la migración | Coinciden con `firewall-policy.csv` ("En el corte") |
| Regla temporal de `snet-archive` el 15 de febrero | Coincide con `firewall-policy.csv` (NSG-prod-11, al terminar la copia continua) |
| Ejemplo de aplicación: revisiones de Container Apps, réplicas del portal, límites del WAF y filtro por cliente | Coinciden |
| Ventana, campañas y excepción por incidente | Verificadas en `docs/change/verificacion-ventana-cambio.md` (#31) |

## 4. Costos y cambio

| Qué | Cambio | Costos | Resultado |
|---|---|---|---|
| Equipo del ensayo y del corte | Ocho personas, de las 22:00 del sábado a las 06:00 del domingo | 8 personas × 8 horas con recargo nocturno y dominical (#25, sección 6) | Coincide |
| Segundo ensayo si el primero falla | Reserva del 7 de febrero | Cubierto por la contingencia de #25, unos USD 4.700 | Coincide |
| Ventanas de cambio durante la convivencia | De 22:00 a 04:00 | 15 noches × 2 personas × 6 horas, con recargo nocturno | Coincide |
| Partner de Microsoft en el ensayo y el corte | Acompaña al equipo del corte | 2 noches × 2 personas × 8 horas (#28, sección 3.3) | Coincide |
| Comité de cambios y gestión del cambio | Aprueba y avisa cada cambio | Gestión del proyecto (comité) y gestión del cambio (avisos), por rol y fase (#28, sección 3.1) | Coincide |
| Guardia que atiende una vuelta atrás de noche | Ingeniero de plataforma de turno | Equipo de operación con guardia (#28, sección 4) | Coincide |
| Costo después del corte | El ejemplo cita unos USD 17.240 al mes | 17.239,76 el mes 1 (#26) | Coincide |

**Conclusión:** sin inconsistencias.

## 5. Arquitectura e infraestructura como código

Revisión preliminar del módulo de red del pull request #2 de `frioandes-platform/iac` contra la arquitectura. Se hizo en la revisión del 20 de octubre (comentario en #20).

| Qué | Resultado |
|---|---|
| Estructura `modules/` y `environments/dev`, `test` y `prod` | Coincide con `automatizacion-devops.md`, sección 2 |
| Las 11 subredes de cada ambiente, con nombres y CIDR | Idénticos a `ip-plan.csv`: el módulo los lee del CSV y comprueba sus hashes antes de planear |
| Delegaciones: MySQL en `snet-data`, Container Apps en la torre, el portal y la función, y Power Platform en `snet-fabric-egress` | Coinciden con la red y la plataforma |
| Región East US 2 | Coincide |
| Etiquetas `ambiente`, `carga`, `costo`, `criticidad` y `responsable`, con `costo=compartido` en la red de producción y `pruebas` en desarrollo y pruebas | Coinciden con `gobierno-landing-zone.md`, sección 5 |
| Salida a internet por defecto deshabilitada en las subredes | Coincide: la única salida es el Azure Firewall |
| NSG y tablas de rutas | **Riesgo abierto R-1.** `automatizacion-devops.md` dice que `modules/network` crea también los NSG y las tablas de rutas, pero el módulo los deja explícitamente para el módulo de seguridad (#21) |
| Módulos de seguridad y de cómputo, pipeline y `plan` limpio | Pendientes de #21 a #24 |

## 6. Verificación de subnetting sobre el código

**Pendiente de #24.** La verificación final compara el `plan` de Terraform de los tres ambientes con `ip-plan.csv` usando `docs/architecture/red/tools/compare_tfplan.py`, y repite `verify_ip_plan.py` contra las 23 subredes on-premises. El `plan` necesita una suscripción de Azure y es la evidencia de #24.

Lo que ya está verificado:

- **Sobre el diseño:** `ip-plan.csv` pasa las 12 comprobaciones de `verify_ip_plan.py`, sin solapamiento. Se volvió a correr el 20 de octubre, después de corregir las comillas de las notas (pull request #64). Hash: `a520eba842e6d7781705613d539fcfd018bfd00481f3842814d07d97036b91a0`.
- **Sobre el código:** el módulo de red no escribe ningún CIDR a mano. Lee `ip-plan.csv` y una precondición rechaza el `plan` si el hash del archivo no coincide con el registrado. Sus pruebas con proveedor simulado comprueban que las subredes planeadas son las del CSV en los tres ambientes, y pasan.

Esta sección concluirá "sin solapamiento" o listará las diferencias cuando exista el `plan` de #24.

## 7. Inconsistencias corregidas y riesgos abiertos

**Corregidas en esta revisión**

| # | Dónde | Qué decía | Corrección |
|---|---|---|---|
| C-1 | `carga-c-migracion-y-campana.md`, guion y criterios; `observabilidad-slo-zabbix.md` | "Los cinco contenedores" suben de réplicas y responden su chequeo de salud | "Las ocho aplicaciones", con la equivalencia: cinco contenedores de hoy, seis aplicaciones en la torre y dos en el portal |
| C-2 | `ejemplo-release-notes-infraestructura.md`, secciones 1, 8.1 y 9 | Los grupos 400 y 500 seguían completos hasta el 8 de marzo, y faltaba NSG-prod-14 | Nombra FW-401, FW-503, FW-504 y NSG-prod-14, y dice que FW-402 salió en enero |
| C-3 | Guía de lectura (#15), cronograma e informe | La siembra eran "nueve trabajos más un envío del diferencial", como si fueran diez | Los nueve trabajos son una prueba, siete principales y el diferencial, como dicen la tabla de la siembra y los nueve envíos de #25 |
| C-4 | `vista-general.md`, sección 6 | Cifras de costo anteriores a #26 y #28 | Corregido en #36 con las cifras vigentes |

**Riesgos abiertos**

| # | Riesgo | Qué lo cierra |
|---|---|---|
| R-1 | `automatizacion-devops.md` pone los NSG y las tablas de rutas en `modules/network`, y el módulo los deja para `modules/security` | Cuando cierre #21: se alinea el documento con el código. Tiene sentido que vayan en seguridad, porque las reglas de NSG están en `firewall-policy.csv` junto con las del firewall |
| R-2 | La verificación de subnetting sobre el `plan` no está hecha | El `plan` limpio de #24 |
| R-3 | Los módulos de seguridad y de cómputo y el pipeline todavía no existen | #21, #22 y #23 |

## 8. Supuestos

| Supuesto | Por qué se asume |
|---|---|
| Una diferencia de redondeo dentro del mismo orden ("unos USD 4.300" frente a 4.321,93) no es una inconsistencia | Los documentos de arquitectura redondean a propósito y remiten al documento de costos para la cifra exacta |
| La revisión preliminar del módulo de red vale para la pareja arquitectura e IaC hasta que cierren #21 a #24 | Es el único código que existe al 20 de octubre |

## 9. Validación y cierre

| Criterio de aceptación | Evidencia |
|---|---|
| Se revisan explícitamente las cuatro parejas, y cualquier inconsistencia queda corregida o registrada como riesgo abierto | Secciones 2 a 4 completas; sección 5 preliminar. Cuatro inconsistencias corregidas y tres riesgos abiertos (sección 7). **Pendiente:** completar la sección 5 con #21 a #24 |
| El chequeo final de subnetting se hace contra el código de Terraform y concluye "sin solapamiento" | **Pendiente de #24** (sección 6) |

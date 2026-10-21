# Revisión final de consistencia y verificación de subnetting

Revisión cruzada entre los cuatro grupos de entregables: arquitectura (Fase 1), infraestructura como código (Fase 2), costos (Fase 3) y gestión del cambio (Fase 4). Busca lo que es común en un diseño que evolucionó durante semanas: un documento que cambió y otro que no se actualizó. Al final repite la verificación de no solapamiento de direcciones sobre el código de Terraform.

> **Estado, 21 de octubre de 2026.** Las cuatro parejas están revisadas y la verificación de subnetting está hecha sobre el código de Terraform que está en `main` de `frioandes-platform/iac` (commit `c0944a3`, con los módulos de red, seguridad e ingesta de #20 a #22). Lo que todavía no existe en el código, como el pipeline (#23), el `plan` contra una suscripción real (#24) o las tablas de rutas, queda como riesgo abierto en la sección 7.

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

Revisión de los tres módulos que están en `main` de `frioandes-platform/iac` (commit `c0944a3`) contra la arquitectura. Se corrieron sus verificaciones completas: red, seguridad e ingesta, con 17 pruebas de Python, `validate` y pruebas con proveedor simulado en conectividad, desarrollo, pruebas y producción. Todas pasan.

| Qué | Arquitectura | Código | Resultado |
|---|---|---|---|
| Estructura | `modules/` y `environments/dev`, `test` y `prod` (`automatizacion-devops.md`, sección 2) | Igual, más `environments/connectivity` para el hub | Coincide |
| Subredes de los ambientes | Las 11 de `ip-plan.csv` en cada ambiente | Las lee de `ip-plan.csv` y comprueba sus hashes antes de planear | Coincide (sección 6) |
| Delegaciones y salida a internet | MySQL, Container Apps, función y gateway de Fabric; sin salida por defecto | Las mismas delegaciones; `default_outbound_access_enabled = false` | Coincide |
| Etiquetas | Las cinco obligatorias, con `costo=compartido` en red y `pruebas` en desarrollo y pruebas (`gobierno-landing-zone.md`, sección 5) | Las mismas, y `ambiente=shared` en conectividad | Coincide |
| Azure Firewall | Standard, inteligencia de amenazas en bloqueo, sin proxy DNS, una IP de salida, tarjeta de gestión desde el inicio (`red-firewall-y-publicacion.md`, sección 2.2) | Lo mismo, leído de `firewall-settings.csv` | Coincide |
| Reglas del firewall y de los NSG | `firewall-policy.csv`, con las temporales marcadas | Un solo firewall compartido y un NSG por subred. Las temporales quedan apagadas por defecto y se activan por identificador, con referencia de cambio | Coincide: siete comparaciones "sin discrepancias" (`docs/iac/verificacion-iac-vs-firewall.md`, #21) |
| Componente de cómputo o ingesta | El Event Hub de alertas de la telemetría, en `snet-data-pe` (`carga-b-telemetria.md`, sección 3.2) | Event Hubs Standard con endpoint privado en `snet-data-pe`, sin acceso público ni claves locales | Coincide |
| NSG y tablas de rutas | `automatizacion-devops.md` ponía los NSG y las rutas en `modules/network` | Los NSG están en `modules/security`; las rutas no están en ningún módulo | **Corregido** el documento para los NSG (C-5). Las rutas, **riesgo abierto R-3** |
| Componentes del hub | VPN Gateway, Bastion y DNS Private Resolver, con sus subredes (`red-topologia-subnetting.md`, sección 2.1) | El hub solo tiene las dos subredes del firewall | **Riesgo abierto R-5**: fuera del alcance de #20 a #24 |
| WAF del portal y reglas de IoT Hub | En `firewall-policy.csv`, puntos de control `waf` e `iot-hub` | No están en el módulo de seguridad, que lo dice explícitamente | **Riesgo abierto R-5** |
| Pipeline | GitHub Actions con OIDC, aprobación y bloqueo de la ventana (`automatizacion-devops.md`, sección 3) | No existe todavía | **Riesgo abierto R-2** (#23) |

## 6. Verificación de subnetting sobre el código

La verificación se hizo sobre lo que el código de Terraform va a crear, no sobre el plan en papel:

1. **El `plan` del código.** Las pruebas de cada ambiente (`terraform test -json -verbose` en `environments/dev`, `test` y `prod` de `iac`, commit `c0944a3`) generan el `plan` con un proveedor simulado, sin suscripción de Azure. De ese `plan` salen las redes virtuales y las subredes que Terraform crearía.
2. **Comparación con el plan de direcciones.** `docs/architecture/red/tools/compare_tfplan.py`, ampliado para leer los planes de `terraform test`, compara el código con `ip-plan.csv`:

```
Terraform: 3 redes virtuales, 33 subredes · ip-plan.csv: 3 redes virtuales, 33 subredes
Terraform y ip-plan.csv coinciden: mismas redes virtuales, mismas subredes, mismos CIDR.
```

3. **No solapamiento sobre el código.** El mismo script escribe las direcciones del código en el formato del plan (`docs/architecture/red/verification/tf-ip-plan.csv`, SHA-256 `1b1caf566058ad882bc18298648052fc8c94223d8c8055ba94a48fe21b3b9b14`). Ahí, los tres ambientes salen del código, y el hub y las reservas, de `ip-plan.csv`. `verify_ip_plan.py` lo compara contra las 23 subredes on-premises y pasa las 12 comprobaciones (`docs/architecture/red/verification/reporte-ip-plan-terraform.md`).

**Conclusión: sin solapamiento.** Las 33 subredes que crea el código en los tres ambientes son idénticas a las del diseño, y ninguna se solapa con Cali, con los centros, con el hub, con las otras subredes ni con las reservas.

**El hub.** El código del hub crea solo las dos subredes del firewall, con los CIDR del plan. Las otras cuatro (VPN Gateway, Bastion y las dos del DNS Private Resolver) todavía no están en el código (riesgo R-5), así que se verificaron sobre el diseño.

**Cómo repetirlo** desde la raíz de `iac` y de `planning`:

```bash
terraform -chdir=environments/dev test -json -verbose > dev.jsonl    # ídem test y prod
python3 docs/architecture/red/tools/compare_tfplan.py --tfplan dev.jsonl test.jsonl prod.jsonl \
  --vnets vnet-dev vnet-test vnet-prod --out-csv tf-ip-plan.csv
python3 docs/architecture/red/tools/verify_ip_plan.py --plan tf-ip-plan.csv
```

Con el `plan` contra una suscripción real de #24 se repite el paso 2 con `terraform show -json`.

## 7. Inconsistencias corregidas y riesgos abiertos

**Corregidas en esta revisión**

| # | Dónde | Qué decía | Corrección |
|---|---|---|---|
| C-1 | `carga-c-migracion-y-campana.md`, guion y criterios; `observabilidad-slo-zabbix.md` | "Los cinco contenedores" suben de réplicas y responden su chequeo de salud | "Las ocho aplicaciones", con la equivalencia: cinco contenedores de hoy, seis aplicaciones en la torre y dos en el portal |
| C-2 | `ejemplo-release-notes-infraestructura.md`, secciones 1, 8.1 y 9 | Los grupos 400 y 500 seguían completos hasta el 8 de marzo, y faltaba NSG-prod-14 | Nombra FW-401, FW-503, FW-504 y NSG-prod-14, y dice que FW-402 salió en enero |
| C-3 | Guía de lectura (#15), cronograma e informe | La siembra eran "nueve trabajos más un envío del diferencial", como si fueran diez | Los nueve trabajos son una prueba, siete principales y el diferencial, como dicen la tabla de la siembra y los nueve envíos de #25 |
| C-4 | `vista-general.md`, sección 6 | Cifras de costo anteriores a #26 y #28 | Corregido en #36 con las cifras vigentes |
| C-5 | `automatizacion-devops.md`, sección 2 | `modules/network` creaba también los NSG y las tablas de rutas | Los NSG están en `modules/security`, junto con el firewall, porque salen de la misma tabla. Se agregó `modules/ingest`, y las rutas quedan marcadas como pendientes |

**Riesgos abiertos**

| # | Riesgo | Qué lo cierra |
|---|---|---|
| R-1 | La verificación de subnetting está hecha sobre el `plan` simulado, no contra una suscripción real | El `plan` de #24, repitiendo la sección 6 con `terraform show -json` |
| R-2 | El pipeline todavía no existe: no hay bloqueo automático de la ventana ni promoción entre ambientes | #23 |
| R-3 | Ningún módulo crea las tablas de rutas. Sin ellas, el tráfico de las subredes no pasa por el Azure Firewall, y como las subredes no tienen salida por defecto a internet, los servicios se quedarían sin salida | Un módulo de rutas o una ampliación del de red, antes de desplegar. El `plan` de #24 sale limpio igual, así que no lo detecta |
| R-4 | El cierre `NSG-*-99` de la tabla deniega todo lo que entra con prioridad 4000, antes que las reglas por defecto de Azure. El Application Gateway v2 exige aceptar las sondas de `AzureLoadBalancer` en su subred, y la tabla no tiene esa regla. Hay que revisar lo mismo para la alta disponibilidad de MySQL y para Container Apps | Corregir `firewall-policy.csv` (#9) y volver a correr `verify_firewall_policy.py` y la verificación de #21. El módulo toma el cambio solo, porque lee la tabla |
| R-5 | El hub del código solo tiene el firewall: faltan el VPN Gateway, Bastion, el DNS Private Resolver y el peering con los ambientes. El WAF del portal y las reglas de IoT Hub tampoco están en el código | Fuera del alcance de #20 a #24, que pide red, seguridad y un componente. Se construyen en la fase de despliegue (cronograma, sección 3) |

## 8. Supuestos

| Supuesto | Por qué se asume |
|---|---|
| Una diferencia de redondeo dentro del mismo orden ("unos USD 4.300" frente a 4.321,93) no es una inconsistencia | Los documentos de arquitectura redondean a propósito y remiten al documento de costos para la cifra exacta |
| El `plan` simulado de `terraform test` vale como verificación sobre el código | Las direcciones salen de la configuración, no de Azure: el proveedor simulado no cambia ningún CIDR. El `plan` real de #24 lo confirma |
| Lo que no está en el código al 21 de octubre (pipeline, rutas, componentes del hub) se registra como riesgo abierto y no bloquea la revisión | El criterio de la issue permite corregir o registrar como riesgo abierto |

## 9. Validación y cierre

| Criterio de aceptación | Evidencia |
|---|---|
| Se revisan explícitamente las cuatro parejas, y cualquier inconsistencia queda corregida o registrada como riesgo abierto | Secciones 2 a 5: arquitectura y costos, arquitectura y cambio, costos y cambio, y arquitectura e IaC. Cinco inconsistencias corregidas y cinco riesgos abiertos (sección 7) |
| El chequeo final de subnetting se hace contra el código de Terraform y concluye "sin solapamiento" | Sección 6: el `plan` del código de los tres ambientes coincide con `ip-plan.csv` y pasa las 12 comprobaciones contra las 23 subredes on-premises. **Sin solapamiento** |

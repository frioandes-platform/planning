# Lista de verificación de la entrega final

Compara uno por uno los seis entregables finales del enunciado con lo producido, y comprueba que los supuestos de todos los entregables estén en el registro (`assumptions-log.md`) y que el informe de la estrategia los referencie.

> **Estado, 27 de octubre de 2026.** Cinco entregables están completos. Falta la presentación de 20 minutos y su ensayo (#37 y #38), fuera del tablero. Las 35 tarjetas del tablero están cerradas y el registro de supuestos cubre todo lo producido.

## Contenido

1. Los seis entregables
2. Supuestos: registro completo y referenciado desde el informe
3. Lo que falta y quién lo hace
4. Supuestos
5. Validación y cierre

---

## 1. Los seis entregables

| # | Entregable del enunciado | Artefacto | Estado | Lo que falta |
|---|---|---|---|---|
| 1 | Diagramas | `docs/architecture/architecture-frioandes.pdf`: los ocho puntos del reto con sus diagramas, la tabla de subnetting y la tabla de políticas del firewall. Las 26 fuentes editables de draw.io están en `docs/architecture/diagramas/` y las generan scripts | ✅ Completo | — (recompilado el 27 de octubre, con el sistema de diseño completo en el capítulo 8) |
| 2 | Repositorio Git de infraestructura como código | [`frioandes-platform/iac`](https://github.com/frioandes-platform/iac): módulos de red (#20), seguridad (#21) e ingesta (#22), ambientes de desarrollo, pruebas, producción y conectividad, pipeline de promoción (#23), evidencia del `plan` con proveedor simulado (#24, `docs/iac/evidencia-plan-limpio.md`), TFLint, Checkov y costo de cada cambio con Infracost. El no solapamiento está verificado sobre el código (`revision-final-consistencia-y-subnetting.md`, sección 6) | ✅ Completo | Al activar el pipeline sobre Azure: el primer `plan` autenticado. Antes de desplegar: tablas de rutas y corrección del cierre de los NSG (riesgos R-3 y R-4 de #39) |
| 3 | Dos plantillas de release notes con su ejemplo | `docs/change/`: plantilla y ejemplo de aplicación, plantilla y ejemplo de infraestructura, y la verificación de la ventana de cambio | ✅ Completo | — |
| 4 | Documento de costos | `docs/costs/costs-frioandes.pdf`: migración con la siembra, mes estable y campaña, Fabric aparte, costo total del proyecto y decisiones de ahorro, con los supuestos como anexo | ✅ Completo | — |
| 5 | Presentación de sustentación | Informe de la estrategia `docs/presentation/report.pdf` (#36), versión 1.1, completo | ⏳ Pendiente | #37 presentación de 20 minutos y #38 ensayo, abiertas y fuera del tablero |
| 6 | Sistema de diseño | `docs/design/`: logo y paleta (#32), tipografía y espaciado (#33), componentes y reglas de uso (#34), la lámina que los aplica en tres pantallas (#35, `docs/design/sistema-de-diseno-frioandes.md`) y las reglas de los documentos de entrega | ✅ Completo | — |

## 2. Supuestos: registro completo y referenciado desde el informe

**Cobertura del registro.** Se comprobó que cada documento y cada módulo que declara supuestos o confirmaciones pendientes tenga sus filas en el registro. Faltaban las de once issues, y se agregaron:

| Issue | Fuente | Filas agregadas |
|---|---|---|
| #5 | `gobierno-landing-zone.md` | 4: suscripciones, regiones, presupuestos y etiqueta de pruebas |
| #6 | `gobierno-auditoria-facturacion.md` | 3: retención de la auditoría, reparto de lo compartido y responsables |
| #7 | `seguridad-iam-cifrado.md` | 3: clientes como invitados B2B, claves y revisión de accesos |
| #11 | `red-acceso-remoto-segunda-nube.md` | 3: Bastion, segunda nube y tamaño del acceso administrativo |
| #12 | `carga-a-plataforma-logistica.md` | 4: MySQL 8.4, Central US apagado, redirección del portal y asignación de muelle |
| #20 | Módulo de red de `iac` | 2: cada ambiente se aplica desde su carpeta y los proveedores quedan fijados |
| #21 | Módulo de seguridad de `iac` | 4: un solo firewall, temporales apagadas, marcadores como variables y la denegación implícita |
| #22 | Módulo de ingesta de `iac` | 2: el componente representativo y el acceso de Stream Analytics |
| #32 | `docs/design/logo-y-paleta.md` | 3: colores de marca, nombre con tilde y contraste en pantallas reales |
| #33 | `docs/design/tipografia-espaciado.md` | 3: distancia de lectura, coma decimal y reloj de 24 horas, y fuentes propias |
| #34 | `docs/design/componentes-y-reglas-de-uso.md` | 3: estados de los componentes, vista del cliente y contraste nocturno |

Con esto, todos los issues que produjeron un documento o un módulo tienen sus supuestos en el registro, de #5 a #36, #39 y #40.

**Referencia desde el informe.** El informe (#36) referencia el registro de tres formas:

- la sección 17 da el total de entradas y cuántas esperan una confirmación de FríoAndes. El script del informe calcula esas cifras desde el registro cada vez que se genera, para que nunca queden desactualizadas;
- el anexo B lista los supuestos que más pesan y la sección del informe donde pesa cada uno;
- el anexo C remite al documento de arquitectura, que trae el registro completo como anexo.

**Revisión de las cifras del informe.** Cada cifra del informe sale de un documento con su supuesto, o es un dato del enunciado:

| Sección del informe | De dónde salen sus cifras | Supuestos en el registro |
|---|---|---|
| 1 y 14. Resumen ejecutivo y costos | Scripts de `docs/costs/tools/` | #25 a #28 |
| 2. Punto de partida | Enunciado, más 180 usuarios en los centros | #25 |
| 3, 5 y 6. Solución, seguridad y red | Diseños de red, firewall, seguridad e identidades | #5 a #11 |
| 7. Plataforma y telemetría | Diseños de las cargas A y B | #12 y #13 |
| 8. Migración y campaña | Plan de migración y de siembra | #14 y #15 |
| 9. Observabilidad | Diseño de observabilidad | #16 |
| 10. Fabric | Diseños de Fabric | #17, #18 y #27 |
| 11. IaC y DevOps | Diseño de automatización, cronograma, módulos y pipeline de `iac` | #19 a #24 |
| 12. Gestión del cambio | Plantillas, ejemplos y verificación | #29 a #31 |
| 13. Sistema de diseño | Logo, paleta, tipografía, componentes y lámina | #32 a #35 |
| 15 y 16. Cronograma y riesgos | Cronograma y plan de migración | #14, #15 y #19 |
| 17. Confirmaciones | El propio registro | Todas |

## 3. Lo que falta y quién lo hace

| Qué | Quién | Qué cambia aquí cuando se cierre |
|---|---|---|
| #37 presentación y #38 ensayo | Fuera del tablero | El entregable 5 pasa a completo |
| Primer `plan` autenticado, al activar el pipeline sobre las suscripciones | Equipo de plataforma | Se repite la verificación de subnetting con el `plan` real (riesgo R-1 de #39). Condición para desplegar, no para entregar |
| Tablas de rutas y cierre de los NSG (riesgos R-3 y R-4 de #39) | Por asignar | Condición para desplegar, no para entregar |

## 4. Supuestos

| Supuesto | Por qué se asume |
|---|---|
| El informe de la estrategia cuenta dentro del entregable 5 junto con la presentación | La guía de lectura señala que el informe está en la Tarea 5 pero no en la lista de entrega, y que lo más seguro es entregar todo |
| Un supuesto "referenciado desde el informe" puede estar en el anexo B o en el registro completo que acompaña al documento de arquitectura | El informe es breve: no puede listar los casi 190 supuestos uno por uno |

## 5. Validación y cierre

| Criterio de aceptación | Evidencia |
|---|---|
| No hay una cifra o decisión relevante del informe sin su supuesto en el registro, y el informe lo referencia explícitamente | Sección 2: el registro cubre todos los documentos y módulos producidos, y el informe lo referencia en la sección 17 y en los anexos B y C |
| Los seis entregables están marcados como completos con su enlace, o señalados con la tarea que los resuelve | Sección 1: cinco completos y uno con su tarea pendiente nombrada (#37 y #38) |

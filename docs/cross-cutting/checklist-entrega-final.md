# Lista de verificación de la entrega final

Compara uno por uno los seis entregables finales del enunciado con lo producido, y comprueba que los supuestos de todos los entregables estén en el registro (`assumptions-log.md`) y que el informe de la estrategia los referencie.

> **Estado de esta versión, 20 de octubre de 2026.** Tres entregables están completos y tres tienen tareas pendientes, cada una nombrada abajo. La revisión de supuestos está hecha sobre todo lo producido hasta hoy y se repite al cerrar las tareas pendientes.

## Contenido

1. Los seis entregables
2. Supuestos: registro completo y referenciado desde el informe
3. Lo que falta para cerrar
4. Supuestos
5. Validación y cierre

---

## 1. Los seis entregables

| # | Entregable del enunciado | Artefacto | Estado | Lo que falta |
|---|---|---|---|---|
| 1 | Diagramas | `docs/architecture/architecture-frioandes.pdf`: los ocho puntos del reto con sus diagramas, la tabla de subnetting y la tabla de políticas del firewall. Las 26 fuentes editables de draw.io están en `docs/architecture/diagramas/` y las generan scripts | ✅ Completo | Recompilar el PDF al final, con la lámina del sistema de diseño (#35) |
| 2 | Repositorio Git de infraestructura como código | `frioandes-platform/iac`: módulo de red, ambientes y pruebas en revisión (pull request #2) | ⏳ Pendiente | #20 (correcciones pedidas en la revisión), #21 seguridad, #22 cómputo o ingesta, #23 pipeline y #24 `plan` limpio |
| 3 | Dos plantillas de release notes con su ejemplo | `docs/change/`: plantilla y ejemplo de aplicación, plantilla y ejemplo de infraestructura, y la verificación de la ventana de cambio | ✅ Completo | — |
| 4 | Documento de costos | `docs/costs/costs-frioandes.pdf`: migración con la siembra, mes estable y campaña, Fabric aparte, costo total del proyecto y decisiones de ahorro, con los supuestos como anexo | ✅ Completo | — |
| 5 | Presentación de sustentación | Informe de la estrategia `docs/presentation/report.pdf` (#36), primera versión. La presentación de 20 minutos y su ensayo son #37 y #38 | ⏳ Pendiente | #36: secciones de IaC y de diseño cuando cierren #24 y #35. #37 y #38: abiertas y fuera del tablero |
| 6 | Sistema de diseño | `docs/design/`: logo y paleta, con tokens, íconos e insignias (#32) | ⏳ Pendiente | #33 tipografía y grilla, #34 componentes y #35 lámina consolidada |

## 2. Supuestos: registro completo y referenciado desde el informe

**Cobertura del registro.** Se comprobó que cada documento que declara supuestos o confirmaciones pendientes tenga sus filas en el registro. Cinco documentos de arquitectura y el de logo y paleta no tenían ninguna, aunque sí declaraban supuestos, y se agregaron en esta revisión:

| Issue | Documento | Filas agregadas |
|---|---|---|
| #5 | `gobierno-landing-zone.md` | 4: suscripciones, regiones, presupuestos y etiqueta de pruebas |
| #6 | `gobierno-auditoria-facturacion.md` | 3: retención de la auditoría, reparto de lo compartido y responsables |
| #7 | `seguridad-iam-cifrado.md` | 3: clientes como invitados B2B, claves y revisión de accesos |
| #11 | `red-acceso-remoto-segunda-nube.md` | 3: Bastion, segunda nube y tamaño del acceso administrativo |
| #12 | `carga-a-plataforma-logistica.md` | 4: MySQL 8.4, Central US apagado, redirección del portal y asignación de muelle |
| #32 | `docs/design/logo-y-paleta.md` | 3: colores de marca, nombre con tilde y contraste en pantallas reales |

Con esto, todos los issues que produjeron un documento de diseño tienen sus supuestos en el registro: de #5 a #19, de #25 a #32 y #36. Faltan los de la Fase 2 (#20 a #24) y los de #33 a #35, que se agregan al cerrar esas tareas.

**Referencia desde el informe.** El informe (#36) referencia el registro de tres formas:

- la sección 17 da el total de entradas y cuántas esperan una confirmación de FríoAndes. El script del informe calcula esas cifras desde el registro, para que nunca queden desactualizadas;
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
| 11. IaC y DevOps | Diseño de automatización y cronograma | #19 |
| 12. Gestión del cambio | Plantillas, ejemplos y verificación | #29 a #31 |
| 13. Sistema de diseño | Logo y paleta | #32 |
| 15 y 16. Cronograma y riesgos | Cronograma y plan de migración | #14, #15 y #19 |
| 17. Confirmaciones | El propio registro | Todas |

## 3. Lo que falta para cerrar

1. **Fase 2:** que #20 a #24 cierren. Con el `plan` de #24 se completan la sección 5 y la verificación de subnetting de `revision-final-consistencia-y-subnetting.md` (#39), y la sección 11 del informe.
2. **Sistema de diseño:** que #33 a #35 cierren. Con la lámina se completa la sección 13 del informe, se pone la tipografía de la marca en la plantilla común y se recompilan los tres PDF.
3. **Supuestos de las Fases 2 y 5:** agregar al registro los de #20 a #24 y #33 a #35.
4. **Presentación:** #37 y #38, fuera del tablero.
5. **Cierre:** repetir esta lista y marcar los seis entregables como completos.

## 4. Supuestos

| Supuesto | Por qué se asume |
|---|---|
| El informe de la estrategia cuenta dentro del entregable 5 junto con la presentación | La guía de lectura señala que el informe está en la Tarea 5 pero no en la lista de entrega, y que lo más seguro es entregar todo |
| Un supuesto "referenciado desde el informe" puede estar en el anexo B o en el registro completo que acompaña al documento de arquitectura | El informe es breve: no puede listar los más de 170 supuestos uno por uno |

## 5. Validación y cierre

| Criterio de aceptación | Evidencia |
|---|---|
| No hay una cifra o decisión relevante del informe sin su supuesto en el registro, y el informe lo referencia explícitamente | Sección 2: el registro cubre todos los documentos de diseño producidos, y el informe lo referencia en la sección 17 y en los anexos B y C. **Pendiente:** los supuestos de #20 a #24 y #33 a #35 |
| Los seis entregables están marcados como completos con su enlace, o señalados con la tarea que los resuelve | Sección 1: tres completos y tres con sus tareas pendientes nombradas |

# Briefing inicial — Decisiones base del proyecto FríoAndes

Este documento reúne las decisiones que los Senior deben tomar y comunicar **antes** de asignar
las primeras tareas a los Junior. No es un issue del tablero: es información de contexto que
condiciona cómo se ejecutan varias tareas de la Fase 1 (en particular #5 y #8, que son las
primeras que se abren).

Estado: 🟡 en construcción — los campos marcados `[ PENDIENTE ]` los completan los Senior antes
de la reunión de kickoff con los Junior.

---

## 1. Idioma de los entregables

| Tipo de entregable | Idioma |
|---|---|
| Documentos académicos (arquitectura, costos, informe, presentación, sistema de diseño) | **Español** |
| Diagramas (rótulos, leyendas) | **Español** |
| Plantillas y ejemplos de release notes | **Español** |
| Código de infraestructura (IaC), nombres de recursos y variables | **Inglés** |
| Comentarios de código | **Inglés** |
| README técnico del repositorio `iac` | **Inglés** |
| Mensajes de commit y nombres de rama | **Inglés** |
| Etiquetas (labels) y milestones del tablero de GitHub | **Español, sin tildes ni espacios** |

Justificación: el enunciado no define el idioma de entrega en ningún punto — es un supuesto del
equipo. Se documenta aquí en vez de en el tablero porque es una decisión de gobierno, no una
tarea ejecutable.

---

## 2. Nube principal y alcance multicloud

El enunciado permite elegir **una sola nube principal** (Azure, AWS o GCP) y exige justificar la
elección. Cita textual:

> "Puede elegir una nube principal (Azure, AWS o GCP) y justificar la elección. El diseño debe
> dejar preparada una interconexión futura con una segunda nube, sin duplicar toda la plataforma
> desde el día uno."

Esto significa:
- **No es un diseño multicloud.** Hoy se construye sobre una única nube.
- La preparación para una segunda nube (horizonte 24 meses) se limita a dejar reutilizables un
  punto de interconexión, una estrategia de DNS híbrido y un modelo de identidad federada — eso
  ya está cubierto por la tarea #11 (F1-07). No implica construir infraestructura en la segunda
  nube ahora.

**Nube principal elegida:** `[ PENDIENTE ]`
**Justificación breve:** `[ PENDIENTE ]`
**Región primaria:** `[ PENDIENTE ]`
**Justificación de la región** (latencia hacia Cali / residencia de datos personales): `[ PENDIENTE ]`

> Por qué importa para la semana 1: la tarea #5 (F1-01, landing zone) y la #8 (F1-05, topología
> y subnetting) no pueden ejecutarse de forma concreta sin esto — la jerarquía de cuentas se
> llama distinto según el proveedor (Management Groups/Subscriptions en Azure, Organizations/OUs
> en AWS, Folders/Projects en GCP) y el diseño de red depende de la región.

---

## 3. Herramientas de infraestructura como código y CI/CD

**Herramienta de IaC:** `[ PENDIENTE ]` (Terraform / Bicep / Pulumi / CloudFormation)
**Plataforma de CI/CD:** `[ PENDIENTE ]` (GitHub Actions / Azure DevOps / GitLab CI)
**Repositorio de IaC:** `frioandes-platform/iac` (crear cuando se confirme la herramienta)

No bloquea la semana 1, pero conviene decidirlo pronto: si Junior A ya sabe qué herramienta se
va a usar, puede nombrar recursos en #5 y #7 de forma que se traduzcan directo a módulos de esa
herramienta en la Fase 2, en vez de tener que traducir el vocabulario después.

---

## 4. Estructura de `docs/` en este repositorio

Los nombres de carpeta van en **inglés** (son rutas/slugs, igual que el código); el contenido
dentro de cada archivo sigue en español según la sección 1.

| Carpeta | Contenido | Quién escribe ahí |
|---|---|---|
| `docs/governance-and-decisions/` | Este documento + ADR de nube, región y herramientas cuando se definan | Senior |
| `docs/architecture/` (+ `diagrams/`) | Los 8 puntos del reto: gobierno, seguridad, red, cargas, migración, observabilidad, Fabric | Fase 1 |
| `docs/iac/` | Evidencia y verificación del código (el código en sí vive en el repo `iac`) | Fase 2 |
| `docs/costs/` | Estimaciones de migración, mes estable, campaña, Fabric | Fase 3 |
| `docs/change/` | Plantillas y ejemplos de release notes | Fase 4 |
| `docs/design/` | Sistema de diseño de marca | Fase 5 |
| `docs/presentation/` | Informe, presentación, banco de preguntas, ensayo | Fase 6 |
| `docs/cross-cutting/` | Registro de supuestos, preguntas de la sesión de aclaraciones, revisión final, checklist de entrega | Fase 7 (y continuo) |

---

## 5. Registro de supuestos

Cualquier decisión que un Junior tome sin que esté escrita en el enunciado ni en este documento
debe quedar anotada en `docs/cross-cutting/assumptions-log.md` con esta estructura:

| Supuesto | Justificación | Issue que lo originó | Estado |
|---|---|---|---|
| _(ejemplo)_ El SLO de disponibilidad del portal se fija en 99.5% | No está definido en el enunciado; se usa como valor de referencia de la industria para portales B2B | #16 | Por confirmar |

---

## 6. Sesión de aclaraciones (30 minutos, el docente representa al cliente)

Antes de esa sesión, revisar `docs/cross-cutting/sesion-aclaraciones-preguntas.md` y priorizar
las preguntas sobre los puntos que sigan en `[ PENDIENTE ]` en este documento y que no se hayan
podido resolver solo con criterio del equipo.

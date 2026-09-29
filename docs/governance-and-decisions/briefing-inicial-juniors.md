# Decisiones base del proyecto FríoAndes

Este documento presenta las decisiones base tomadas por el equipo senior para el proyecto
FríoAndes. Es información de contexto para el equipo junior, necesaria para ejecutar las tareas
de la Fase 1 en adelante, en particular la landing zone (#5) y la topología de red (#8), que son
las primeras que se abren.

## 1. Idioma de los entregables

| Tipo de entregable | Idioma |
|---|---|
| Documentos académicos (arquitectura, costos, informe, presentación, sistema de diseño) | Español |
| Diagramas (rótulos, leyendas) | Español |
| Plantillas y ejemplos de release notes | Español |
| Código de infraestructura (IaC), nombres de recursos y variables | Inglés |
| Comentarios de código | Inglés |
| README técnico del repositorio `iac` | Inglés |
| Mensajes de commit y nombres de rama | Inglés |
| Etiquetas (labels) y milestones del tablero de GitHub | Español, sin tildes ni espacios |

El enunciado no define el idioma de entrega en ningún punto, así que esta convención queda
registrada aquí como decisión de gobierno del proyecto.

## 2. Nube principal

La nube principal del proyecto es **Microsoft Azure**.

La elección se sostiene en cuatro razones concretas del caso:

Primero, la torre de control necesita inteligencia artificial provista por Microsoft Fabric sin
importar cuál sea la nube principal. Si Azure es la nube principal, Fabric queda en el mismo
tenant de identidad (Microsoft Entra ID), con un solo esquema de autenticación y auditoría entre
la plataforma y la capa analítica. Con cualquier otra nube principal, Fabric exige una
organización de identidad separada, lo que añade una integración adicional sin necesidad real
para el caso.

Segundo, la red híbrida actual de FríoAndes ya opera con un firewall de próxima generación y VPN
site to site hacia ocho centros. Azure Virtual WAN y Azure VPN Gateway están pensados justamente
para consolidar ese tipo de topología hub and spoke con múltiples sitios remotos, y ofrecen una
ruta directa hacia ExpressRoute cuando el negocio decida contratar un enlace dedicado en vez de
depender solo del internet compartido de 400 Mbps.

Tercero, la siembra física del archivo de 1,2 PB se resuelve con Azure Data Box Heavy, un
dispositivo pensado para volúmenes de ese orden en un solo envío, lo que simplifica la logística
frente a mover varios dispositivos más pequeños.

Cuarto, Azure Policy y Management Groups dan un modelo de gobierno maduro para separar cuentas de
seguridad, red, producción y ambientes no productivos desde un punto común, que es exactamente lo
que pide la tarea de landing zone (#5).

### Región principal

La región principal es **East US 2**.

Se descarta Brazil South como primera opción a pesar de estar geográficamente más cerca de Cali,
porque el tráfico de internet colombiano hacia la nube se apoya mayoritariamente en la
infraestructura de cables submarinos que conecta con Miami, y los enlaces desde Colombia hacia el
este de Estados Unidos suelen medir menor latencia real que hacia Brasil, donde el enrutamiento es
menos directo. East US 2 también tiene paridad completa de servicios (incluye Azure Data Box,
Azure Virtual WAN y las capacidades de IA que consumen Fabric y la plataforma) y una logística de
envío y devolución del dispositivo de siembra más madura desde Colombia que la que ofrece Brasil.

Como región de respaldo para el esquema de alta disponibilidad de la Parte A, se usa **Central
US**, que es la región emparejada de East US 2 dentro del esquema de regiones emparejadas de
Azure, lo que simplifica la replicación geográfica de la base de datos y del almacenamiento.

Esta elección de región es una decisión de partida razonada con la información disponible. El
equipo de red debe validarla con una prueba de latencia real desde Cali como parte de la tarea
#8, y ajustar la decisión si los datos de campo dicen lo contrario.

### Alcance de nube única

El proyecto se construye sobre una sola nube principal. La segunda nube queda prevista para un
horizonte de 24 meses, con un punto de interconexión, una estrategia de DNS híbrido y un modelo
de identidad federada reutilizables, sin construir hoy infraestructura en esa segunda nube. Esa
preparación está cubierta por la tarea #11 (F1-07).

## 3. Herramientas de infraestructura como código y CI/CD

La herramienta de infraestructura como código es **Terraform**.

Se prefiere sobre Bicep, que es nativo de Azure y más simple de aprender, porque Terraform es
agnóstico de proveedor. Eso conserva el conocimiento del equipo si la segunda nube del punto 2 no
termina siendo Azure, y porque el verbo central de Terraform, `terraform plan`, coincide de forma
literal con el requisito de la Tarea 2 de que el código se pueda planear antes de aplicarse.

La plataforma de integración y despliegue continuo es **GitHub Actions**, porque toda la
organización `frioandes-platform` ya vive en GitHub (issues, Project y los dos repositorios), lo
que evita licenciar o configurar una plataforma adicional. GitHub Actions tiene soporte directo
para ejecutar Terraform, gestionar secretos por ambiente mediante Environments, y aprobar
despliegues manualmente antes de un `apply` a producción, que es exactamente lo que pide la tarea
#23 (F2-Pipeline).

El repositorio de infraestructura como código es `frioandes-platform/iac`.

## 4. Estructura de `docs/` en este repositorio

Los nombres de carpeta van en inglés, porque son rutas del repositorio y siguen la misma
convención que el código. El contenido dentro de cada archivo sigue en español, según la sección
1.

| Carpeta | Contenido | Se llena en |
|---|---|---|
| `docs/governance-and-decisions/` | Este documento y cualquier decisión base adicional | Fase 0 (senior) |
| `docs/architecture/` (con `diagrams/`) | Los 8 puntos del reto: gobierno, seguridad, red, cargas, migración, observabilidad, Fabric | Fase 1 |
| `docs/iac/` | Evidencia y verificación del código de infraestructura (el código en sí vive en el repositorio `iac`) | Fase 2 |
| `docs/costs/` | Estimaciones de migración, mes estable, campaña y Fabric | Fase 3 |
| `docs/change/` | Plantillas y ejemplos de release notes | Fase 4 |
| `docs/design/` | Sistema de diseño de marca | Fase 5 |
| `docs/presentation/` | Informe, presentación, banco de preguntas y ensayo | Fase 6 |
| `docs/cross-cutting/` | Registro de supuestos, preguntas de la sesión de aclaraciones, revisión final y checklist de entrega | Fase 7 (y de forma continua) |

## 5. Registro de supuestos

Cualquier decisión que un junior tome sin que esté escrita en el enunciado ni en este documento
queda anotada en `docs/cross-cutting/assumptions-log.md`, con esta estructura:

| Supuesto | Justificación | Issue que lo originó | Estado |
|---|---|---|---|
| Ejemplo: el SLO de disponibilidad del portal se fija en 99.5% | No está definido en el enunciado; se usa como valor de referencia de la industria para portales B2B | #16 | Por confirmar |

## 6. Sesión de aclaraciones

La sesión de aclaraciones dura 30 minutos y el docente representa al cliente. Antes de esa
sesión, el equipo revisa `docs/cross-cutting/sesion-aclaraciones-preguntas.md` y prioriza las
preguntas sobre los puntos de este documento que convenga confirmar con el cliente, en particular
la elección de nube y región si surge alguna restricción de negocio que no conocíamos.

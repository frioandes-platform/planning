# FríoAndes — Gobierno y landing zone de Azure

Estado: propuesta de arquitectura para revisión del equipo. Fecha: 4 de octubre de 2026.
Issue cubierto: #5.

## 1. Objetivo y alcance

Establecer una estructura común para gobernar recursos, accesos y costos en Azure, separando seguridad, red compartida, producción y ambientes no productivos. El diagrama de jerarquía se entrega como PNG por separado; este documento describe y justifica su contenido. La jerarquía no representa la topología de red ni un despliegue realizado.

El diagnóstico actual muestra que desarrollo, pruebas y producción comparten actualmente el clúster de aplicación del datacenter. Esto dificulta delimitar permisos, cambios y consumo por ambiente. La propuesta crea ámbitos distintos y conserva una administración corporativa común.

Azure es la nube principal del proyecto, según el briefing inicial (`docs/governance-and-decisions/briefing-inicial-juniors.md`). Los nombres, cinco suscripciones y umbrales siguientes son decisiones propuestas, no cifras obligatorias del caso. El issue #8 fija East US 2 como región principal y Central US como región emparejada, y registra una medición de latencia desde Cali que confirma East US 2. Los valores de esa prueba y los montos de presupuesto se consultan en los documentos respectivos.

## 2. Cómo leer el diseño

- **Tenant de Microsoft Entra ID:** directorio corporativo que autentica identidades. No es una suscripción de recursos ni una cuenta de facturación.
- **Management Group (MG):** agrupa suscripciones para aplicar reglas comunes.
- **Subscription (SUB):** ámbito para administrar recursos, permisos, cuotas y seguimiento de costos.
- **Resource Group (RG):** conjunto de recursos con un ciclo de vida relacionado dentro de una suscripción.

En el PNG, las líneas indican pertenencia e herencia de gobierno. No indican conexiones de red ni flujos de datos. Las políticas asignadas a un grupo se aplican a sus descendientes; el acceso de una persona se concede mediante RBAC en el ámbito que necesita.

## 3. Jerarquía de gobierno

Se propone una jerarquía poco profunda dentro del tenant corporativo: `mg-frioandes` contiene `mg-fa-platform` (plataforma compartida) y `mg-fa-workloads` (cargas de negocio). El primero agrupa las suscripciones de seguridad y conectividad; el segundo agrupa producción, desarrollo y pruebas. Los ambientes se separan con suscripciones bajo el mismo MG de cargas; no se crean MG únicamente para representar dev/test/prod. El PNG entregado junto a este documento debe mostrar estas mismas relaciones.

Las suscripciones propuestas se vinculan al mismo directorio Entra ID. La separación dev/test/prod se realiza mediante suscripciones, permisos, identidades de despliegue y controles de red independientes.

| Suscripción | Dominio y recursos previstos | Administración propuesta |
|---|---|---|
| `sub-fa-security` | Seguridad y observabilidad central: Log Analytics y herramientas de investigación; archivo de auditoría a definir en #6 | Equipo de seguridad/plataforma; lectura limitada para auditoría |
| `sub-fa-connectivity` | Red compartida: hub, Azure Firewall, conectividad con Cali y DNS híbrido; los controles del portal y de los flujos que no pasan por el firewall se precisan en #9 | Equipo de redes |
| `sub-fa-prod` | Cargas productivas: logística, portal, datos, archivo e ingesta de telemetría | Operadores autorizados e identidad de despliegue de producción |
| `sub-fa-dev` | Desarrollo con datos sintéticos o anonimizados | Desarrolladores dentro de RG autorizados |
| `sub-fa-test` | Pruebas de integración y validación previa a producción | QA y automatización dentro de RG autorizados |

Ejemplos de RG: `rg-fa-logistica-prod`, `rg-fa-telemetria-prod`, `rg-fa-archivo-prod`, `rg-fa-logistica-dev` y `rg-fa-logistica-test`. Las llaves y secretos de cada carga permanecen en su ambiente; centralizar la política no implica compartir secretos.

Se agrupan inicialmente seguridad y observabilidad en una suscripción de plataforma para reducir complejidad. Esto adapta el patrón de landing zones de Microsoft; no reproduce toda su jerarquía de referencia. Una suscripción adicional de administración podrá incorporarse si la separación de responsabilidades lo exige. No se crea una suscripción de identidad únicamente para alojar Entra ID.

## 4. Identidades y responsabilidades

Un tenant corporativo evita crear directorios independientes para cada ambiente. Los grupos de Entra ID se asignan a roles Azure RBAC por suscripción o RG. Una identidad única no significa permisos iguales en todos los ámbitos.

| Grupo propuesto | Ámbito y permiso previsto | Restricción |
|---|---|---|
| `grp-fa-governance` | Gestión de políticas y jerarquía mediante roles adecuados | Sin acceso de lectura de datos por defecto |
| `grp-fa-security` | Visibilidad de seguridad e investigación autorizada | Sin modificación de cargas de negocio por defecto |
| `grp-fa-network` | Network Contributor en conectividad | Sin administración de bases o aplicaciones |
| `grp-fa-dev` | Contributor en RG de desarrollo necesarios | Sin permisos productivos; Contributor no permite asignar roles |
| `grp-fa-qa` | Lectura y permisos específicos de ejecución en test | Sin administración de producción |
| `grp-fa-ops-prod` | Roles de operación específicos en producción | Elevación temporal para acciones privilegiadas |
| `grp-fa-finops` | Cost Management Reader en las suscripciones pertinentes | Sin modificación de infraestructura |

No se concede Owner global a desarrolladores o QA. Se proponen MFA, acceso condicional y elevación temporal mediante PIM para administradores, sujetos al licenciamiento correspondiente. La matriz completa de usuarios y cifrado pertenece a #7.

Los pipelines usarán identidades distintas por ambiente con federación de identidad cuando sea compatible. Los permisos de acceso a datos deben configurarse por servicio: un rol de gobierno o de lectura de recursos no sustituye la autorización de la aplicación. El acceso a la consola de despacho se diseñará por separado.

## 5. Etiquetado obligatorio

Se aplican claves y valores normalizados en minúsculas a los RG y recursos compatibles. No se incluyen nombres de clientes, documentos, secretos ni otros datos personales.

| Dimensión | Clave | Valores permitidos propuestos | Ejemplo |
|---|---|---|---|
| Ambiente | `ambiente` | `prod`, `dev`, `test`, `shared` | `prod` |
| Carga | `carga` | `logistica`, `telemetria`, `archivo`, `red`, `seguridad`, `analitica` | `telemetria` |
| Línea de costo | `costo` | `operacion`, `telemetria`, `pruebas`, `compartido`, `fabric` | `telemetria` |
| Criticidad | `criticidad` | `alta`, `media`, `baja` | `alta` |
| Responsable | `responsable` | Identificador del equipo propietario | `equipo-plataforma` |

Ejemplo para la ingesta productiva: `ambiente=prod`, `carga=telemetria`, `costo=telemetria`, `criticidad=alta`, `responsable=equipo-plataforma`.

Dev/test se clasifican como `costo=pruebas`, incluso si allí se prueba telemetría. Esto evita contar el mismo recurso simultáneamente como telemetría productiva y pruebas. Red y seguridad comunes usan `costo=compartido`; su reparto interno se definirá en #6. La capacidad de Fabric tendrá una línea separada, mediante su ámbito de facturación y filtros disponibles, sin asumir que todos sus cargos admiten las mismas etiquetas.

Los recursos no heredan automáticamente etiquetas del RG o la suscripción. Terraform las aplicará explícitamente y Azure Policy verificará su cumplimiento. Para recursos existentes compatibles podrá usarse `Modify` con identidad administrada y remediación. Los recursos sin soporte de etiquetas se clasifican por suscripción/RG y un inventario de excepciones.

## 6. Políticas concretas de Azure Policy

Las políticas se agrupan en iniciativas versionadas. Los efectos siguientes son objetivos de implementación: se seleccionarán definiciones integradas o personalizadas y se comprobarán sus tipos de recurso y aliases al construir IaC.

| Política | Ámbito | Efecto previsto | Resultado y ejemplo |
|---|---|---|---|
| P-01. Etiquetas y valores obligatorios | `mg-frioandes`, para tipos compatibles | `Deny` | Rechazar un RG sin `ambiente` o un recurso etiquetable sin `costo`; validar valores según suscripción |
| P-02. Regiones autorizadas | `mg-frioandes` | `Deny` | Impedir despliegues regionales fuera de la lista aprobada; tratar recursos globales según la definición |
| P-03. Datos sin acceso público | `sub-fa-prod`, sobre servicios de datos seleccionados | `Deny` donde exista soporte | Rechazar almacenamiento/base de datos con acceso público incompatible con el diseño; el ingreso público autorizado del portal se trata aparte |
| P-04. Diagnósticos centralizados | Suscripciones de cargas y conectividad | `DeployIfNotExists` en servicios compatibles | Crear configuración de diagnóstico hacia el destino autorizado; usar identidad administrada y remediación para recursos existentes |
| P-05. Transporte seguro en almacenamiento | Suscripciones de cargas | `Deny` para propiedades compatibles | Exigir HTTPS y TLS mínimo 1.2 en cuentas de almacenamiento; otros servicios tendrán controles específicos |

P-02 toma East US 2 y Central US como regiones iniciales para recursos regionales, sujeto a excepciones justificadas para servicios globales y a las definiciones compatibles con cada tipo de recurso. Antes de activar su efecto de bloqueo se comprueba el alcance exacto de la política. P-04 no garantiza por sí sola registrar accesos de negocio: la aplicación debe emitir los eventos definidos en #6. También se debe coordinar con #9 el envío central de registros de Azure Firewall, WAF y flujos de red virtual, incluidos los recorridos que no atraviesan el firewall.

Se verifica primero la compatibilidad de cada política en dev/test. Las excepciones deberán registrar recurso/ámbito, justificación, responsable, control compensatorio y vencimiento. No se excluirá toda producción para resolver un error puntual.

## 7. Presupuestos y seguimiento de costos

Se propone un presupuesto mensual por suscripción, filtros para las líneas de negocio y una vista consolidada para finanzas con permisos sobre todos los ámbitos necesarios. Los MG organizan gobierno; no sustituyen el contrato ni la cuenta de facturación.

| Presupuesto | Alcance | Responsable |
|---|---|---|
| Seguridad | `sub-fa-security` | Seguridad y FinOps |
| Conectividad | `sub-fa-connectivity` | Redes y FinOps |
| Producción | `sub-fa-prod`, con vistas separadas por `costo` | Operaciones y FinOps |
| Desarrollo | `sub-fa-dev` | Desarrollo |
| Pruebas | `sub-fa-test` | QA |
| Fabric | Capacidad y cargos asociados identificados por facturación | Analítica y FinOps |

Como decisión inicial, se proponen alertas al 80 %, 100 % y 120 % del gasto real, y al 100 % del gasto previsto. Los montos se obtendrán del documento de costos; no se presentan valores inventados como cotización. Los periodos de campaña tendrán límites aprobados antes de su inicio.

Los presupuestos notifican; no son topes que apaguen automáticamente recursos. Ante una alerta se investiga el consumo y se aprueban acciones. No se detendrá despacho ni telemetría por una alerta financiera. El seguimiento tiene retraso y no sustituye monitoreo operativo en tiempo real.

## 8. Cómo resuelve la situación actual

| Problema actual | Cambio propuesto | Condición para que funcione |
|---|---|---|
| Dev/test/prod comparten clúster de aplicación | Suscripciones y recursos propios por ambiente | No reutilizar el mismo cómputo, base o identidad de despliegue entre ambientes |
| Permisos sin delimitación común | Tenant corporativo y grupos RBAC con ámbitos separados | Validar permisos efectivos y evitar herencia excesiva |
| Red y cargas administradas juntas | Conectividad compartida bajo responsabilidad de redes | Definir segmentación, rutas y firewall en #8 |
| Costos mezclados | Etiquetas, presupuestos por suscripción y vistas por línea | Controlar cargos sin etiquetas y distribuir costos comunes |
| Auditoría dispersa | Destino central y políticas de diagnóstico | Definir eventos, acceso y retención en #6 |

Una suscripción no es un firewall. El aislamiento requiere redes y reglas explícitas; tampoco prohíbe por sí sola que alguien configure conexiones entre ambientes. Los controles de red y los datos de prueba deberán respetar la separación propuesta.

## 9. Validación y cierre

Este documento permite revisar el diseño sin contratar ni desplegar servicios. La implementación posterior verificará que un desarrollador de dev no pueda modificar producción, que una creación sin etiquetas sea rechazada, que un recurso regional no autorizado sea bloqueado y que el consumo pueda agruparse por las líneas acordadas.

| Criterio de aceptación | Evidencia en este documento |
|---|---|
| Jerarquía con seguridad, red, prod y no-prod | PNG entregado por separado y descripción y tabla de cinco suscripciones en la sección 3 |
| Cuatro dimensiones de etiquetas y tres políticas concretas | Cinco dimensiones en sección 5 y cinco políticas en sección 6 |
| Explicar cómo se resuelve la mezcla de clústeres e identidades | Modelo de accesos en sección 4 y comparación en sección 8 |

Antes de marcar Done: revisión del equipo, confirmación de nombres y responsables, incorporación a `docs/architecture/gobierno-landing-zone.md` en el repositorio y verificación de que el PNG adjunto coincide con la sección 3. Los importes siguen abiertos para los issues de costos (#25 a #28); no cambian la jerarquía propuesta. El plan de direcciones, las rutas y las reglas detalladas son responsabilidad de #8 y #9.

## 10. Fuentes técnicas

Las decisiones de FríoAndes son propuestas del equipo. Las fuentes explican el comportamiento de los servicios y no certifican que este diseño esté desplegado.

- [Microsoft Learn — Management groups y diseño de landing zones](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org-management-groups)
- [Microsoft Learn — Azure Policy](https://learn.microsoft.com/en-us/azure/governance/policy/overview)
- [Microsoft Learn — Etiquetas de recursos](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/tag-resources)
- [Microsoft Learn — Crear y administrar presupuestos](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets)

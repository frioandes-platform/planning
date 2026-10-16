# Acceso remoto administrativo y preparación para una segunda nube

## 1. Decisión y alcance

Se adopta **Azure Bastion Standard en el hub de conectividad**, con autenticación corporativa de Microsoft Entra ID, MFA, acceso condicional y permisos sobre máquinas de administración específicas. Las personas remotas administran la infraestructura que les corresponde sin incorporar sus equipos domésticos a la red de despacho.

La torre de control conserva su acceso desde las redes corporativas autorizadas de Cali y los centros, con los roles funcionales definidos para la aplicación. Tener un rol de administrador de infraestructura, acceso a Bastion o una sesión en una máquina de operación no autoriza a utilizar la consola de despacho.

Para la segunda nube se reutilizarán el hub, la estrategia de Azure DNS Private Resolver y el tenant corporativo de Entra ID. Se conserva la reserva de direcciones de #8. El proveedor y las cargas que se llevarán a esa nube se decidirán cuando exista una necesidad aprobada.

### 1.1 Relación con las decisiones existentes

| Referencia | Base que aporta | Decisión de este documento |
|---|---|---|
| [#5 — Landing zone](https://github.com/frioandes-platform/planning/issues/5), [documento](gobierno-landing-zone.md) | Tenant corporativo; suscripciones de conectividad, seguridad, producción, pruebas y desarrollo; grupos y etiquetas | Bastion y DNS pertenecen a `sub-fa-connectivity`; las máquinas administrativas a su ambiente; los registros se centralizan en `sub-fa-security` |
| [#8 — Red híbrida](https://github.com/frioandes-platform/planning/issues/8), [documento](red-topologia-subnetting.md), secciones 4 y 5 | Hub y spokes, Bastion, subredes administrativas, DNS y reservas | Confirma Bastion como mecanismo inicial y conserva los rangos de `red/data/ip-plan.csv` |
| [#7 — IAM](https://github.com/frioandes-platform/planning/issues/7), [documento](seguridad-iam-cifrado.md) | Grupos, mínimo privilegio, MFA, separación de roles de aplicación y Azure RBAC | Aplica esos controles al acceso remoto y a la futura federación |
| [#9 — Firewall](https://github.com/frioandes-platform/planning/issues/9), [documento](red-firewall-y-publicacion.md) | Reglas de Bastion, DNS, torre y salida de administración | Conserva sus puntos de control y concreta los bloqueos de movimiento lateral |
| [#6 — Auditoría](https://github.com/frioandes-platform/planning/issues/6), [documento](gobierno-auditoria-facturacion.md) | Registro central, responsabilidades y retención | Añade las fuentes y evidencias del acceso remoto sin crear otro destino de auditoría |

Las dependencias directas de #11 son #5 y #8; las demás referencias coordinan identidad, controles y auditoría.

## 2. Acceso remoto administrativo

### 2.1 Por qué Bastion

| Alternativa | Evaluación para FríoAndes |
|---|---|
| Azure Bastion | Elegida: ya está prevista en #8 y permite sesiones SSH/RDP a máquinas privadas concretas. El equipo remoto no obtiene una conexión general a las redes de los ambientes |
| VPN punto a sitio con Entra ID | Se conserva como alternativa futura si hacen falta herramientas locales con conectividad IP privada. Exigiría definir grupos, rutas, DNS y reglas adicionales; la VPN por sí sola no separa administración y despacho |

Se propone Standard para disponer de escalado y opciones de cliente nativo cuando sean necesarias. El camino inicial preferente es SSH desde el navegador a una máquina Linux de administración compatible con inicio de sesión Entra. Bastion no es un escritorio ni administra directamente MySQL, Container Apps o Key Vault: proporciona acceso a la máquina desde la que se ejecutan herramientas autorizadas. La gestión por Azure Portal o API de Azure Resource Manager utiliza su propio control de acceso. [T1][T2]

No se activa VPN punto a sitio el día uno. El bloque `10.100.8.0/22` continúa reservado. Una eventual VPN de contingencia para despacho requiere una decisión expresa sobre qué considera FríoAndes red corporativa y una revisión de #7, #8 y #9; no queda autorizada por este documento.

### 2.2 Ubicación y direcciones

Los rangos siguientes proceden de `red/data/ip-plan.csv`; no se asignan bloques nuevos.

| Elemento | Ubicación | Rango |
|---|---|---|
| Hub compartido | `sub-fa-connectivity`, East US 2, `vnet-hub` | `10.100.0.0/23` |
| Bastion | `AzureBastionSubnet` del hub | `10.100.0.192/26` |
| Administración de producción | `sub-fa-prod`, `snet-admin` | `10.101.2.128/27` |
| Administración de pruebas | `sub-fa-test`, `snet-admin` | `10.102.2.128/27` |
| Administración de desarrollo | `sub-fa-dev`, `snet-admin` | `10.103.2.128/27` |
| Torre de producción | `snet-app-torre` | `10.101.1.0/25` |
| Torre de pruebas y desarrollo | `snet-app-torre` de cada ambiente | `10.102.1.0/25` y `10.103.1.0/25` |

Bastion se conecta a las máquinas de los spokes mediante el peering previsto en #8. Las máquinas no reciben IP pública. Las sesiones de usuarios entran a Bastion por HTTPS; SSH/RDP se habilita únicamente entre Bastion y los destinos administrativos autorizados. Se preservan además las comunicaciones de plataforma que requiere el servicio. [T1][T3]

### 2.3 Secuencia de acceso y Zero Trust

1. La persona usa una cuenta corporativa individual desde un equipo gestionado. Entra ID evalúa MFA y la política de acceso condicional: grupo autorizado y dispositivo conforme. Seguridad valida las licencias y la integración de gestión de dispositivos antes de habilitar el acceso.
2. El usuario accede al recurso permitido en Azure. Los roles se asignan por máquina o grupo de recursos administrativo, sin conceder lectura ni administración de toda producción para poder usar Bastion.
3. Para la sesión en el sistema operativo se configura también el inicio de sesión Entra de la VM. Iniciar sesión en Azure Portal no sustituye la autenticación en la máquina.
4. La persona recibe acceso de usuario normal. Si necesita privilegios, solicita elevación temporal con PIM, justificación y aprobación para producción, conforme a #7.
5. Ejecuta únicamente las acciones y conexiones permitidas. La red restringe destinos y puertos; el servicio de destino vuelve a comprobar la identidad y sus permisos.
6. El cierre de sesión, la baja del usuario o un incidente activan la retirada de accesos. Ante un incidente también se terminan las sesiones activas: retirar un grupo no garantiza cortar inmediatamente una sesión ya abierta.

Zero Trust se concreta en comprobar identidad, equipo, privilegio y destino, sin confiar en una conexión solo porque procede de una máquina interna.

Para las VM se asignan los roles `Virtual Machine User Login` o, temporalmente, `Virtual Machine Administrator Login`, más las lecturas de VM, NIC, Bastion y VNet que requiera la conexión. Las extensiones de inicio de sesión y el sistema operativo deben ser compatibles. El acceso RDP con Entra desde el navegador figura en vista previa en la documentación consultada; no es una dependencia de la solución inicial. Si se necesitan máquinas Windows, se valida el camino de cliente nativo compatible con MFA antes de incorporarlas. [T2]

La configuración inicial mantiene deshabilitados los enlaces compartibles, la conexión por IP arbitraria y el soporte de cliente nativo mientras no exista una necesidad aprobada. Las sesiones SSH no permiten reenvío de puertos ni de agente. Una futura habilitación del cliente nativo no amplía destinos ni permisos.

### 2.4 Quién puede entrar

| Perfil de #5 y #7 | Acceso administrativo remoto | Límite |
|---|---|---|
| `grp-fa-dev` | Máquina de administración de desarrollo y recursos de sus RG autorizados | Sin acceso a máquinas o datos de producción |
| `grp-fa-qa` | Máquina de pruebas cuando la función lo requiera | Datos sintéticos o anonimizados; sin acceso a producción |
| `grp-fa-ops-prod` | Máquinas de operación de producción aprobadas | Elevación temporal para acciones privilegiadas; sin uso de la torre por este permiso |
| `grp-fa-network` | Administración de conectividad según sus roles; sesión en VM solo si se asigna expresamente | No adquiere permisos sobre bases, secretos o funciones de despacho |
| Seguridad y auditoría | Lectura de registros según #6 y #7 | Sin sesión administrativa en VM por defecto |
| Despachadores y clientes | Ninguno por su rol funcional | El despacho usa el acceso corporativo existente; el cliente utiliza su portal |

Las máquinas interactivas y los ejecutores de despliegue deben ser recursos distintos, aunque compartan `snet-admin`. No se entrega una sesión humana en un ejecutor que pueda obtener credenciales del pipeline. Una identidad administrada con privilegios en una VM sería utilizable por procesos de esa VM; por eso las máquinas interactivas no llevan una identidad de despliegue privilegiada.

## 3. Cómo se mantiene aislada la torre

### 3.1 Controles por recorrido

| Recorrido | Decisión | Control |
|---|---|---|
| Equipo remoto → Bastion | Permitir la sesión autorizada por HTTPS | Entra, MFA, acceso condicional y Azure RBAC |
| Bastion → VM de `snet-admin` | Permitir SSH 22 o RDP 3389 según la VM | NSG y permisos de inicio de sesión; reglas `NSG-prod-08`, `NSG-test-08` y `NSG-dev-08` de #9 |
| Bastion → torre u otras VM no administrativas | Denegar | Destinos restringidos en red y ausencia de permisos de sesión |
| Máquina administrativa → torre, en cualquier ambiente | Denegar | NSG de origen y destino; firewall cuando el recorrido atraviese el hub |
| Máquina administrativa → otro ambiente o redes de usuarios de Cali y centros | Denegar por defecto | NSG y reglas del firewall; sin proxy ni salto por una máquina corporativa |
| Máquina administrativa → herramientas de gestión, repositorios y actualizaciones | Permitir únicamente destinos aprobados | Salida por Azure Firewall; base en `FW-306`, `FW-312` y `FW-318` |
| Máquina administrativa → datos del mismo ambiente | Solo una operación autorizada y con identidad propia | NSG del servicio y permisos del motor; no equivale a acceso general a datos |
| Usuario corporativo autorizado → torre | Mantener el flujo de #8 y #9 | VPN sitio a sitio, firewall, NSG y autorización de aplicación |

En #9, `NSG-*-03` ya contempla acceso desde administración a MySQL del mismo ambiente. La existencia de ese permiso de red no concede una cuenta de base de datos. Los accesos humanos a datos productivos necesitan una autorización específica y auditoría; los desarrolladores no heredan credenciales de producción.

### 3.2 Reglas que deben comprobarse en la implementación

- Mantener la denegación final de entrada de `NSG-*-99` con prioridad anterior a las reglas predeterminadas permisivas. No se añade `snet-admin` a los orígenes permitidos de la torre.
- Añadir a los NSG administrativos una denegación de salida explícita hacia los tres rangos de la torre y las redes corporativas de usuarios. Enumerar las excepciones administrativas antes del cierre general, con destino y puerto concretos.
- No asumir que el firewall del hub ve todo el tráfico de una VNet. Una ruta entre subredes del mismo ambiente puede ser directa; el NSG y la autorización del destino son necesarios.
- Restringir Bastion a las VM administrativas, preservando las reglas de funcionamiento del servicio. El flujo Bastion–VM se controla con NSG y no se fuerza a atravesar el firewall del hub. [T3]
- Deshabilitar reenvío IP, proxies y túneles en las máquinas interactivas. No otorgar a sus usuarios permisos para modificar NSG, rutas, NIC o la identidad de esas máquinas.
- Separar administración de infraestructura y roles de despacho. También se restringen operaciones como ejecución remota de comandos, acceso a consolas de contenedores o recuperación de credenciales cuando permitan saltarse la separación funcional.

Un administrador con capacidad para cambiar la red puede alterar sus controles. Ese privilegio debe ser excepcional, temporal, aprobado y auditado; no se presenta como una garantía absoluta frente al administrador más privilegiado.

Las denegaciones de salida y el endurecimiento anterior son requisitos de #11 que deben incorporarse a la implementación y conciliarse con `red/data/firewall-policy.csv`. Este documento no afirma que esas filas adicionales ya existan en la tabla de #9.

### 3.3 Registros y continuidad

Se envían los diagnósticos de Bastion y los eventos de administración al espacio Log Analytics central de `sub-fa-security`, el mismo destino lógico de #6 y #9. Se correlacionan con inicios de sesión de Entra, activaciones PIM, eventos del sistema operativo, cambios de red y accesos al servicio de destino. La retención sigue #6; no se crea otra política independiente.

Los registros de conexión no equivalen a una grabación completa de pantalla o de todos los comandos. Si se exige grabación de sesiones, se evaluarán las capacidades, compatibilidades y costos de Bastion Premium antes de comprometer esa evidencia.

Ante la indisponibilidad de Bastion no se abren SSH/RDP públicos ni la torre. Se recupera el servicio; el trabajo de despacho continúa por sus conexiones corporativas existentes mientras estas estén disponibles. Bastion no sustituye el plan de continuidad regional ni resuelve una caída del firewall de Cali.

## 4. Punto de interconexión con la segunda nube

El punto único **lógico** será `vnet-hub` en `sub-fa-connectivity`. La segunda nube se conectará al hub, sin crear túneles individuales a cada ambiente ni usar la sede de Cali como tránsito obligatorio.

Como opción inicial para ese momento se propone VPN sitio a sitio con IPsec/IKEv2 y BGP sobre el VPN Gateway de #8, con enlaces redundantes compatibles en ambos extremos. La redundancia física no contradice un punto lógico común. Un enlace dedicado, una NVA o Virtual WAN se evaluarán si el tráfico, la latencia o las restricciones del proveedor lo justifican.

| Reserva de #8 | Uso futuro |
|---|---|
| `10.110.0.0/15` | Bloque de segunda nube: `10.110.0.0/16` para tránsito y `10.111.0.0/16` para cargas; subdivisión detallada cuando se elija proveedor |
| `10.100.1.128/25` | Espacio disponible del hub para una NVA, si resulta necesaria |
| `10.100.4.0/22` | Reserva para una futura topología Virtual WAN |
| `10.104.0.0/15` | Recuperación en otra región de Azure; es una reserva distinta de la segunda nube |

La interconexión exigirá validar los prefijos reales de ambas nubes, filtrar anuncios BGP, evitar rutas por defecto no aprobadas y verificar el retorno simétrico a través de los controles previstos. El tráfico de las cargas entre nubes deberá pasar por el firewall del hub con permisos específicos; el DNS tendrá su recorrido controlado según la sección siguiente. No se habilita tránsito libre hacia Cali, los centros o todos los ambientes.

La capacidad disponible se revisará contando conexiones, túneles, ancho de banda y fallos simultáneos según el SKU vigente. Que el diseño de #8 contemple una conexión adicional no prueba por sí solo que tenga capacidad para cualquier segunda nube. Antes de incorporarla se medirán latencia y transferencia con sus cargas reales.

## 5. DNS híbrido reutilizable

Se utiliza Azure DNS Private Resolver en el hub, con las subredes exclusivas de #8, delegadas a `Microsoft.Network/dnsResolvers`. Los prefijos identifican subredes; en los reenviadores se configurará la IP privada concreta del endpoint, no el CIDR. [T4]

| Elemento | Rango | Función |
|---|---|---|
| `snet-dns-inbound` | `10.100.1.0/28` | Recibir consultas de redes autorizadas sobre nombres privados de Azure |
| `snet-dns-outbound` | `10.100.1.16/28` | Reenviar consultas de dominios externos a Azure hacia sus servidores DNS |

Las zonas privadas de Azure se vinculan al hub. Para esta propuesta, las VNet de los ambientes usan como DNS personalizado la IP del endpoint inbound. El conjunto de reglas de reenvío se vincula al hub para resolver los dominios de Cali y, en el futuro, los de la segunda nube. La IP asignada al inbound se registra en IaC; su recreación exige comprobar los clientes y reenviadores que la utilizan. [T4][T5]

| Consulta | Recorrido previsto |
|---|---|
| Cali o centros → nombre privado de Azure | DNS corporativo autorizado → VPN → endpoint inbound → zona privada vinculada al hub |
| Ambiente de Azure → nombre privado de Azure | DNS configurado en la VNet → endpoint inbound → zona privada |
| Ambiente de Azure → dominio interno de Cali | Resolver del hub → regla para el dominio de Cali → endpoint outbound → DNS corporativo |
| Segunda nube → nombre privado de Azure, cuando se incorpore | Reenviador DNS de la segunda nube → interconexión privada → endpoint inbound |
| Azure → nombre privado de la segunda nube, cuando se incorpore | Regla específica del dominio de esa nube → endpoint outbound → endpoint DNS remoto |

Se permiten UDP y TCP 53 únicamente para los servidores y orígenes acordados. La base actual son `NSG-hub-01` y `NSG-hub-02`; se completan las IP de los DNS de Cali y se agregan los futuros endpoints remotos cuando existan. Los centros usan el DNS corporativo autorizado; un DNS propio de un centro necesitará una entrada expresa en esa lista.

Cada dominio mantiene una autoridad definida. No se crean reglas que reenvíen una consulta de vuelta al resolver que la originó, ni se vincula al hub una regla para sus propias zonas apuntando a su mismo inbound. Se prueba tanto la resolución correcta como la ausencia de bucles. Resolver un nombre no concede permiso de conexión al servicio. [T5]

## 6. Identidad federada para la segunda nube

El tenant corporativo de Microsoft Entra ID de #5 sigue siendo la fuente de identidad de las personas. Al seleccionar otra nube se configura su integración de federación admitida —por ejemplo, SAML u OIDC según el servicio— y se mapean grupos corporativos a roles locales de esa nube. Entra autentica; el proveedor de destino autoriza las acciones con su propio modelo de IAM. [T6]

No se presume que Azure RBAC o PIM administren automáticamente los permisos de otro proveedor. Se deberá diseñar el equivalente de roles, duración de sesión, elevación, revocación y cuentas de emergencia en la nube elegida. La desactivación de una persona debe retirar el acceso federado y los permisos o sesiones locales que correspondan.

Las identidades de aplicaciones se mantienen separadas por carga y ambiente. Para automatizaciones se evaluará federación de identidad de cargas de trabajo con tokens de corta duración donde exista soporte. No se copiarán secretos de producción ni se supondrá que una identidad administrada de Azure tiene permisos automáticos fuera de Azure.

## 7. Qué existe el día uno y qué se difiere

| Día uno de la solución | Incorporación futura, sujeta a diseño y aprobación |
|---|---|
| Un tenant corporativo y grupos con permisos por ambiente | Federación con el IAM de la nube seleccionada y mapeo de roles |
| Un Bastion compartido y máquinas administrativas necesarias por ambiente | Otro mecanismo remoto solo si lo exige una necesidad validada |
| Hub, VPN de las sedes y firewall definidos en #8 y #9 | Enlaces redundantes hacia la segunda nube y reglas por flujo |
| DNS Private Resolver para las necesidades actuales de Cali y Azure | Endpoints DNS y reglas para los dominios privados de la segunda nube |
| Reservas IP y convenciones comunes | Subredes concretas del proveedor elegido y su verificación de no solapamiento |
| Auditoría y etiquetas integradas con #5 y #6 | Exportación de los eventos de la nueva nube y clasificación de sus costos |

**No se duplican el día uno** las aplicaciones de despacho o rastreo, las bases de datos, Redis, el archivo de 1,2 PB, la ingesta de telemetría ni las capacidades de Fabric en otra nube. Tampoco se contratan enlaces a un proveedor todavía no seleccionado, se crea un segundo directorio corporativo ni se despliegan anticipadamente una NVA o Virtual WAN. Reservar direcciones no crea recursos ni replica datos.

La segunda nube no se presenta como recuperación ante desastres automática. La continuidad entre regiones de Azure tiene su propio alcance; si una carga exige recuperación entre proveedores, deberá definir replicación, RPO, RTO y pruebas adicionales.

### 7.1 Capacidad y costos que deben presupuestarse

La estimación consolidada debe contar Bastion Standard, sus unidades y horas, las VM administrativas y discos, transferencia, DNS Private Resolver, registros y las licencias necesarias para acceso condicional, gestión de dispositivos y PIM. Se reutilizan los componentes ya presupuestados en #8 para evitar cobrarlos dos veces.

No se presenta un precio mensual sin el número de administradores simultáneos, tamaños y horarios de VM, volumen de registros y licencias disponibles. La segunda nube agregará en su momento enlaces, transferencia de salida, DNS y recursos del proveedor. Esos conceptos quedan identificados, pero no como gasto contratado ni como una plataforma duplicada desde el inicio.

## 8. Verificación de aceptación

La revisión documental contrasta los rangos y las reglas citadas con #8 y #9. Los escenarios siguientes son pruebas de implementación pendientes, no resultados obtenidos en Azure.

| Prueba | Resultado esperado | Evidencia |
|---|---|---|
| Desarrollador autorizado desde equipo conforme y con MFA | Sesión en su VM de desarrollo | Inicio de sesión Entra, evento Bastion y evento de VM |
| Usuario sin MFA, fuera del grupo o con equipo no conforme | Acceso rechazado | Resultado de acceso condicional y autorización |
| Desarrollador intenta acceder a VM de producción | Acceso rechazado | Permisos efectivos y registro del intento |
| Usuario tiene lectura del recurso, pero no permiso de inicio de sesión en VM | No obtiene sesión en el sistema operativo | Prueba de autorización de VM |
| Desde la VM administrativa se intenta HTTPS a la torre y un salto por una máquina corporativa | Ambos caminos bloqueados | Pruebas de conectividad y reglas efectivas de NSG; firewall si atraviesa el hub |
| Usuario con rol de despacho intenta usar la torre desde fuera de las redes corporativas | Bloqueado por red aunque su rol funcional sea válido | Prueba externa y control de origen |
| Despachador autorizado desde una sede corporativa | Torre accesible sin alteración de su recorrido | Prueba funcional desde Cali o centro |
| Operador solicita elevación y termina su intervención | Activación aprobada, limitada y registrada | Eventos PIM y de la operación |
| Máquina administrativa intenta usar identidad de despliegue o secretos ajenos | Acceso rechazado | Inventario de identidades y permisos del servicio |
| Consultas DNS entre Cali y Azure, incluida una inexistente | Respuestas privadas correctas o error esperado, sin bucles | Consultas a DNS y configuración de reenvío |
| Retirada de un usuario o incidente | Nuevos accesos denegados y sesiones terminadas según procedimiento | Prueba de baja y cierre de sesión |
| Revisión del alcance de segunda nube | Reservas conservadas y ausencia de duplicación anticipada | Inventario y plan IaC |

Antes de activar la segunda nube se añadirán pruebas de no solapamiento, filtrado BGP, caída de cada túnel, retorno por el firewall, DNS bidireccional, SSO, revocación y aislamiento entre ambientes.

| Criterio de #11 | Evidencia de diseño |
|---|---|
| Mecanismo remoto identificado y justificado, con protección de despacho | Secciones 2 y 3: Bastion, Entra, mínimo privilegio y bloqueos explícitos; pruebas en sección 8 |
| Interconexión, DNS e identidad reutilizables, sin duplicación el día uno | Secciones 4, 5, 6 y 7 |

## 9. Datos que se confirman antes del despliegue

| Dato pendiente | Responsable propuesto | Qué condiciona |
|---|---|---|
| Administradores simultáneos, herramientas y sistemas operativos | Plataforma y operaciones | Tamaño de Bastion y VM; necesidad de cliente nativo o Windows |
| Licencias de Entra/PIM y dispositivos gestionados | Identidad y seguridad | Aplicación efectiva de MFA, acceso condicional y elevación |
| Inventario de máquinas administrativas y ejecutores | Plataforma | Separación de sesiones humanas, identidades y destinos |
| IP y dominios del DNS corporativo, incluida su continuidad tras migrar Cali | Redes | Reenvío DNS y reglas concretas |
| Nombre o ID exacto del Log Analytics central | Seguridad | Configuración de diagnósticos al mismo destino de #6 y #9 |
| Orígenes y acciones permitidas de operación | Seguridad, redes y responsables de cargas | Reglas concretas y permisos en datos, sin abrir despacho |
| Proveedor, región, cargas y residencia de datos de segunda nube | Arquitectura y cliente | Diseño de la futura interconexión y federación |

Estos pendientes no cambian la decisión inicial de acceso mediante Bastion. Hasta resolverlos no se habilitan accesos amplios para compensar datos faltantes.

## 10. Referencias técnicas

Las fuentes describen capacidades de Azure. Los rangos y las restricciones de negocio proceden de los documentos de FríoAndes enlazados en la sección 1.1.

- **[T1]** Microsoft Learn: [Planificación del acceso remoto a VM con Azure Bastion](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/plan-for-virtual-machine-remote-access) y [configuración de Bastion](https://learn.microsoft.com/en-us/azure/bastion/configuration-settings).
- **[T2]** Microsoft Learn: [Autenticación de Entra ID en Bastion](https://learn.microsoft.com/en-us/azure/bastion/bastion-entra-id-authentication) y [conexión SSH a Linux](https://learn.microsoft.com/en-us/azure/bastion/bastion-connect-vm-ssh-linux).
- **[T3]** Microsoft Learn: [Reglas NSG de Bastion](https://learn.microsoft.com/en-us/azure/bastion/bastion-nsg).
- **[T4]** Microsoft Learn: [Azure DNS Private Resolver](https://learn.microsoft.com/en-us/azure/dns/dns-private-resolver-overview).
- **[T5]** Microsoft Learn: [Endpoints y conjuntos de reglas del resolver](https://learn.microsoft.com/en-us/azure/dns/private-resolver-endpoints-rulesets).
- **[T6]** Microsoft Learn: [Autenticación de aplicaciones y usuarios con Entra ID](https://learn.microsoft.com/en-us/entra/architecture/authenticate-applications-and-users).

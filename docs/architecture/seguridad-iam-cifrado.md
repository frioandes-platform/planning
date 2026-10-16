# FríoAndes — IAM de mínimo privilegio, MFA y cifrado

## 1. Objetivo y límites de confianza

Los 450 usuarios internos y los aproximadamente 2.000 usuarios de clientes corporativos no deben compartir los mismos privilegios. La consola de despacho muestra ubicación de cargas y datos de clientes: solo es accesible desde la red corporativa por el camino privado definido en #8 y #9, y exige autenticación multifactor (**MFA**). El portal público pasa por el WAF, pero una sesión válida solo puede consultar las guías de su propio cliente; ni el WAF ni una etiqueta de Azure sustituyen esa autorización de negocio.

Se utiliza el **tenant corporativo de Microsoft Entra ID** de #5, con grupos distintos y permisos explícitos en aplicaciones y Azure. Para los clientes se propone colaboración B2B: usuarios externos invitados como *guest* a la aplicación del portal en el mismo tenant. El alta y baja las aprueba un administrador de cada cliente y FríoAndes; no se conceden roles Azure RBAC a esos invitados. Antes del despliegue se validan licencias, experiencia de acceso y el sistema de identidad real de los clientes. Si se escogiera un servicio de identidad para consumidores en otro tenant, habría que actualizar este diseño, las políticas y la integración con Fabric.

## 2. Matriz de roles y autorizaciones

grp-fa-governance, grp-fa-security, grp-fa-network, grp-fa-dev, grp-fa-qa, grp-fa-ops-prod y grp-fa-finops gobiernan Azure por suscripción o grupo de recursos. Los siguientes roles funcionales se asignan a grupos de Entra ID y se traducen a permisos dentro de cada servicio. La aplicación siempre verifica `cliente_id`, guía y acción en el servidor; nunca confía solo en lo que muestra la interfaz.

| Rol | Consola / portal | Datos y evidencias | Azure y ambientes | MFA y condición de acceso |
|---|---|---|---|---|
| **Administradores de plataforma** (`grp-fa-ops-prod` y grupo de gobernanza según función) | No reciben permisos de despacho por administrar Azure | Sin lectura rutinaria de datos de clientes ni secretos; acceso excepcional aprobado y auditado | Rol Azure específico para cada recurso y suscripción; elevación temporal para cambios productivos | **Obligatorio** con política de acceso condicional; método resistente a phishing para privilegios altos cuando esté disponible; activación con PIM según licencias |
| **Despachadores** (`grp-fa-despacho`) | Consola interna: crear y actualizar guías, asignar ruta/muelle y consultar estado de la flota; sin administración del portal | Datos de las guías necesarias para operar y posición en vivo; no video completo salvo procedimiento de reclamo autorizado | Ningún rol de administración de Azure | **Obligatorio en la consola**, además de origen en red corporativa; acceso remoto a la consola solo si #11 define y autoriza esa contingencia |
| **Calidad y guardia** (`grp-fa-calidad`, turno de guardia controlado por la aplicación) | Tablero de calidad; reconocer alertas según horario de #13; no asignar rutas | Temperatura, alertas, evidencias y video necesarios para un reclamo, con acceso registrado; sin modificación de la evidencia inmutable | Ningún rol de administración de Azure | MFA obligatorio para aplicaciones internas con datos sensibles; el turno de guardia no amplía permisos de Azure |
| **Desarrolladores** (`grp-fa-dev`) | Servicios y datos sintéticos en desarrollo; sin consola productiva | Sin datos personales reales ni acceso al archivo productivo | Contributor solo en RG autorizados de `sub-fa-dev`; despliegue productivo por identidad del pipeline con aprobación | MFA en acceso interactivo a Azure; sin Owner global ni asignación de roles |
| **QA** (`grp-fa-qa`) | Ejecutar pruebas en `sub-fa-test` con usuarios y sensores simulados | Datos sintéticos o anonimizados; sin evidencias de producción | Lectura y permisos de ejecución específicos en test; sin administración de producción | MFA en acceso interactivo a Azure |
| **Clientes corporativos** (invitados B2B y vínculo a un `cliente_id`) | Solo portal: estado, temperatura y ETA de **sus** guías | Comprobante propio únicamente si #10 lo confirma; sin flota completa, posición exacta, datos del conductor, video ni guías ajenas | Ningún rol Azure RBAC, ni acceso a torre, Fabric administrativo o Key Vault | Inicio de sesión en Entra ID; MFA según política para invitados y riesgo del portal; sesiones y revocación definidas por FríoAndes |
| **Seguridad y auditoría** (`grp-fa-security`) | No operan despacho por pertenecer a seguridad | Lectura autorizada de registros y evidencia para investigaciones, con trazabilidad; sin edición de evidencia | Permisos de investigación limitados en `sub-fa-security`; sin modificar cargas de negocio por defecto | **Obligatorio** para administradores de seguridad; elevación temporal para operaciones privilegiadas |

FinOps (`grp-fa-finops`) solo lee Cost Management y no recibe acceso a datos o secretos. Redes (`grp-fa-network`) administra recursos de `sub-fa-connectivity`, sin privilegios de base de datos. Los permisos por grupo no se heredan automáticamente a las otras suscripciones. Las identidades de los servicios no son usuarios humanos: se definen por separado en la sección 4.

### 2.1 Cómo se hace cumplir

1. **Inicio de sesión:** Entra ID autentica usuarios internos y invitados. Acceso condicional exige MFA para administradores y para la aplicación de la consola; prueba primero las políticas en modo de informe antes de habilitarlas. Se preservan cuentas de emergencia controladas, excluidas solo de la política que podría bloquear una recuperación y vigiladas con alertas.
2. **Red:** la consola solo acepta solicitudes desde la red corporativa privada, con las reglas de #8 y #9. MFA no convierte un origen de internet en una red corporativa. El portal público se publica únicamente por el WAF y no ofrece una ruta hacia la torre.
3. **Autorización de negocio:** las API validan el token de Entra ID (emisor, audiencia y vigencia), el rol y la relación del usuario con el `cliente_id`/guía de **cada solicitud**. El cliente corporativo no elige el `cliente_id` confiable mediante un parámetro; la aplicación lo resuelve desde su vínculo administrado. Las consultas de Fabric del portal aplican filtrado por cliente como se describe en #13.
4. **Revisión:** baja inmediata al terminar empleo/contrato, revisión trimestral de accesos productivos e invitados; cambios de rol, lecturas sensibles y accesos denegados se registran según gobierno-auditoria-facturacion. Se prueba con una cuenta por rol y con intentos de consultar una guía ajena.

## 3. Cifrado en tránsito y en reposo

La red privada limita quién puede conectarse; **el cifrado protege los datos que viajan o se almacenan**. Se deshabilitan protocolos y accesos inseguros donde el servicio lo permita. Azure cifra por defecto los servicios de datos indicados; Key Vault custodia los secretos, certificados y las claves administradas por FríoAndes cuando se decida usarlas. Usar Key Vault para un secreto de aplicación no significa que ese servicio use automáticamente una clave administrada por cliente para todo su almacenamiento.

| Datos / servicio | Tránsito | Reposo y llaves | Acceso a la llave o secreto |
|---|---|---|---|
| **Base transaccional: Azure Database for MySQL Flexible Server** | TLS 1.2 como mínimo entre servicios y base, con validación de certificado; solo conexión privada desde servicios autorizados. TLS 1.3 tras comprobar compatibilidad de MySQL y conectores | Cifrado del servicio para datos, logs y copias. Si FríoAndes exige control de llaves propio, CMK en el Key Vault de producción con identidad administrada del servidor y prueba de restauración; la pérdida de acceso a la llave afecta la disponibilidad | Aplicaciones con identidad propia y permisos de base mínimos; credenciales que todavía hagan falta en Key Vault, sin contraseñas en repositorio |
| **Caché: Azure Managed Redis** | TLS 1.2/1.3; deshabilitar conexiones sin TLS y usar endpoint privado | Si se habilita persistencia, cifrado de discos del servicio; CMK solo si el plan y la necesidad contractual lo justifican. El contenido en memoria no se protege por cifrado de disco: TTL corto y evitar guardar más datos personales de los necesarios | Identidades de los servicios autorizados; secretos residuales en Key Vault si el mecanismo de autenticación elegido los requiere |
| **Archivo histórico y evidencias: Azure Blob Storage** | HTTPS obligatorio y TLS mínimo 1.2, incluso para copia y lectura; acceso por endpoints privados según #8 y #9 | Cifrado de Azure Storage en reposo; CMK de Key Vault para cuentas de evidencias si se requiere control de llaves del cliente. La retención inmutable de cinco años, cuando aplique al tipo de evidencia, se define por separado: el cifrado no impide el borrado | Identidades administradas con roles Blob limitados por cuenta/contenedor; no distribuir claves de cuenta ni SAS de larga vida |
| **Telemetría: IoT Hub, procesamiento y cuentas Blob de evidencia/tabla Delta** | Camiones por red móvil y cuartos fríos por VPN, ambos con MQTT/AMQP/HTTPS sobre TLS 1.2 y credencial única por dispositivo según #13. IoT Hub público para camiones y privado para centros | IoT Hub cifra el contenido almacenado con llaves del servicio; las cuentas Blob de evidencia cruda (Central US) y análisis (East US 2) cifran en reposo, con CMK en Key Vault regional si se aprueba. Las posiciones no van al contenedor inmutable, conforme a #13 | DPS e IoT Hub autentican dispositivos; la credencial por camión/cuarto no es la identidad de un usuario humano. IoT Hub y Stream Analytics escriben a sus cuentas con identidades administradas y reglas de instancia definidas en #13 |
| **Portal, consola y administración** | HTTPS extremo a extremo; Application Gateway y portal por HTTPS interno; sesiones administrativas por Bastion sin publicar SSH/RDP | Certificado público del portal en Key Vault del ambiente, leído por identidad administrada de Application Gateway como define #9; secretos operativos y del pipeline en bóvedas separadas por ambiente | Solo las identidades de servicio que lo consumen; renovación y alertas por vencimiento y acceso fallido |

**Decisión de claves:** se propone cifrado administrado por Azure como base para todos los servicios y CMK en producción para los almacenes de evidencia contractual y, sujeto a confirmación de FríoAndes, la base de datos. Se prueba el comportamiento de restauración y conmutación antes de activar CMK en servicios críticos; CMK añade dependencia de disponibilidad y costo de operación de Key Vault. La capacidad de CMK en Redis e IoT Hub se evalúa únicamente si una obligación la exige y el SKU usado la admite. No se asume que Key Vault cifre directamente cada lectura: entrega o protege las llaves que utiliza el servicio compatible.

## 4. Gestión de secretos, certificados y permisos de servicio

- **Bóvedas por ambiente:** `kv-fa-prod`, `kv-fa-test` y `kv-fa-dev` como nombres propuestos, dentro de sus suscripciones; no compartir secretos productivos con dev/test. Las claves para CMK que se necesitan en Central US se ubican y replican según los requisitos del servicio y el plan regional, sin prometer que una sola bóveda regional resuelve por sí misma la continuidad.
- **Protección:** Azure RBAC como modelo de acceso a la bóveda, endpoint privado, eliminación temporal y protección contra purga. Separar el administrador de la bóveda del lector de secretos y del usuario de claves. Registrar lectura/rotación/borrado en el Log Analytics central de #6.
- **Aplicaciones:** identidad administrada por carga y ambiente. Por ejemplo, la identidad del Application Gateway solo lee el certificado del portal, la del servicio de guías solo sus secretos y datos, y la de la función de alertas solo lo necesario para notificar y registrar acuses. No conceder `Key Vault Administrator` a los servicios.
- **Pipeline:** identidad de despliegue distinta para dev, test y prod, preferiblemente con federación OIDC en lugar de un secreto duradero en GitHub. Leer desde Key Vault únicamente los secretos que una herramienta no pueda reemplazar por identidad; aprobación y permisos mínimos para producción. 
- **Rotación:** fechas de vencimiento y alertas para secretos/certificados; rotar de forma controlada y probar consumidores antes de retirar versiones. La rotación de una CMK debe conservar acceso a versiones anteriores mientras existan datos/copia cifrados con ellas. Ninguna llave, cadena de conexión o certificado privado se sube a Git.

## 5. Verificación y decisiones por confirmar

| Prueba de aceptación del diseño | Evidencia esperada al implementar |
|---|---|
| Administrador sin MFA intenta entrar a Azure y despachador sin MFA intenta abrir la consola | Acceso denegado en ambos casos; la consola tampoco responde desde internet aunque se tenga una sesión válida |
| Cliente A consulta una guía de B; despachador intenta abrir el video completo; dev intenta cambiar producción | Denegación en aplicación/RBAC y evento de auditoría; un permiso administrativo no equivale a un permiso de lectura de negocio |
| Aplicación lee MySQL, Redis, Blob y telemetría | Conexión TLS válida; protocolos inseguros rechazados; datos persistidos cifrados; restauración de base y lectura de evidencia verificadas |
| Identidad de Application Gateway, pipeline y servicios solicita secretos ajenos | Acceso denegado por RBAC de Key Vault; acceso autorizado queda auditado; expiración/rotación generan alerta |
| Se retira temporalmente el acceso a una CMK en pruebas | Se documenta el fallo y el procedimiento de recuperación antes de usar CMK en producción |


## 6. Referencias técnicas

- [Microsoft Learn — MFA resistente a phishing para administradores](https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-admin-phish-resistant-mfa)
- [Microsoft Learn — colaboración B2B en un tenant de empleados](https://learn.microsoft.com/en-us/entra/external-id/what-is-b2b)
- [Microsoft Learn — seguridad de MySQL Flexible Server](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/security-overview)
- [Microsoft Learn — seguridad de Azure Managed Redis](https://learn.microsoft.com/en-us/azure/redis/secure-azure-managed-redis)
- [Microsoft Learn — cifrado de Azure Storage](https://learn.microsoft.com/en-us/azure/storage/common/storage-service-encryption)
- [Microsoft Learn — TLS en IoT Hub](https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-tls-support)
- [Microsoft Learn — protección de Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/secure-your-key-vault)
- [Microsoft Learn — federación OIDC para GitHub Actions](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect)

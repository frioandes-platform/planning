![FríoAndes](../design/brand/logo/logo-principal.png)

# Nota de versión de infraestructura: plantilla

Plantilla para cualquier cambio de infraestructura en producción o en el hub: red, firewall, cómputo, datos o un corte. Tiene los mismos seis campos que la nota de aplicación (`plantilla-release-notes-aplicacion.md`): qué cambia, ventana, impacto, aprobación, aviso y vuelta atrás. Agrega lo que la infraestructura necesita y la aplicación no: el `plan` de Terraform, las reglas del firewall que se tocan, lo que un `apply` no puede deshacer y una sección por tipo de cambio.

Un ejemplo diligenciado, el corte de la migración, está en `ejemplo-release-notes-infraestructura.md`.

## Cómo se usa

1. Quien pide el cambio copia este archivo como `RN-INF-AAAA-NNN.md`, marca el tipo de cambio y llena las secciones comunes y la sección de su tipo. Ningún campo queda vacío: si algo no aplica, se escribe "No aplica" con el porqué.
2. La nota va en el pull request del repositorio `frioandes-platform/iac`, junto con el `plan` de producción que publica el pipeline. Sin la nota y sin la aprobación del Environment, el pipeline no aplica en producción (`automatizacion-devops.md`, sección 3).
3. El comité de cambios la aprueba al menos dos días hábiles antes de la ventana. Un corte o un cambio que no se puede deshacer con un `apply` se aprueba con al menos cinco días de anticipación; un corte, además, después de su ensayo.
4. Los avisos de la sección 6 salen con el texto de la nota, en los plazos que ella misma fija.
5. Después de la ventana se completa la sección 9 y la nota queda cerrada en el repositorio.

## Reglas que la nota tiene que cumplir

| Regla | De dónde sale |
|---|---|
| Ningún cambio en producción ni en el hub entre las 04:00 y las 22:00, hora de Colombia. La ventana es de 22:00 a 04:00, que en UTC es de 03:00 a 09:00 | Enunciado; `automatizacion-devops.md`, sección 5 |
| Ningún cambio durante una campaña: fin de año (15 de noviembre al 10 de enero), Semana Santa y mitad de año (15 de junio al 15 de julio) | `carga-c-migracion-y-campana.md`, sección 4.1 |
| La única excepción es un incidente, con etiqueta de incidente en el pull request y aprobación de seguridad | `automatizacion-devops.md`, sección 3 |
| La aprueban dos personas del comité de cambios, distintas de quien escribió el cambio. Un cambio en el hub lo aprueba también el equipo de redes | `automatizacion-devops.md`, secciones 1 y 3 |
| El mismo código pasó por desarrollo y pruebas, y el `plan` de producción está publicado en el pull request | `automatizacion-devops.md`, sección 3 |
| Lo que no se puede deshacer con un `apply` se marca así y lleva una aprobación adicional | `automatizacion-devops.md`, sección 5 |
| Volver atrás fuera de la ventana también es un cambio en producción: entre las 04:00 y las 22:00 solo se hace como excepción por incidente. Si puede esperar, va en la ventana siguiente | `automatizacion-devops.md`, secciones 3 y 5 |
| Se avisa siempre a despacho y a calidad: de noche la guardia de calidad recibe las alertas de temperatura, y un cambio de red puede cortarlas | Guía de lectura, Reto 4 |

---

## Nota de versión RN-INF-AAAA-NNN

| Campo | Valor |
|---|---|
| Título | *Una línea: qué se cambia y para qué* |
| Tipo de cambio | *Red y firewall, cómputo, datos o corte (sección 8). Puede ser más de uno* |
| Ambientes y suscripciones | *`sub-fa-prod`, `sub-fa-connectivity`, …* |
| Solicitante | *Rol y área* |
| Responsable técnico | *Rol de quien ejecuta la ventana* |
| Pull request y `plan` | *Enlaces; resumen del `plan`: N para crear, N para cambiar, N para destruir* |
| Estado | *Borrador, aprobada, ejecutada, vuelta atrás o cerrada* |

### 1. Qué cambia

**Para la operación.** *Qué gana o qué nota FríoAndes, en lenguaje de negocio.*

**Técnicamente.**

| Recurso o módulo | Cambio | ¿Se puede deshacer con un `apply`? |
|---|---|---|
| *`modules/network`, `modules/security`, …* | *Qué se crea, cambia o destruye* | *Sí, o no y por qué* |

**Lo que no cambia.** *Recursos, rutas y reglas que quedan iguales. Sirve para acotar el impacto.*

**Pruebas hechas.** *Qué se aplicó en desarrollo y pruebas, con qué resultado, y qué verificadores pasaron (sección 8).*

### 2. Ventana

| Campo | Valor |
|---|---|
| Fecha | *Día de la semana y fecha* |
| Hora, Colombia | *Inicio y fin, dentro de 22:00 a 04:00* |
| Hora, UTC | *Inicio y fin, dentro de 03:00 a 09:00* |
| Duración prevista | *Minutos, incluida la verificación* |
| Interrupción del servicio | *Ninguna, o cuánto, de qué y para quién* |
| ¿Fuera de campaña? | *Sí, con la campaña más cercana* |
| ¿Excepción por incidente? | *No. Si es sí: número del incidente, aprobación de seguridad y por qué no espera la siguiente ventana* |

### 3. Impacto

| Pregunta | Respuesta |
|---|---|
| ¿Qué servicios se afectan? | *Torre, portal, telemetría, archivo, conexión de Cali o de los centros* |
| ¿Hay interrupción o degradación durante la ventana? | *Qué, cuánto y para quién* |
| ¿Puede cortar la alerta de temperatura? | *Sí o no; si sí, cómo se cubre esa ventana* |
| ¿Toca datos personales, cifrado o accesos? | *Sí o no* |
| ¿Cambia el costo mensual? | *Cuánto, con la fuente* |
| Riesgo | *Bajo, medio o alto, con la razón* |

### 4. Aprobación

| Rol | Decisión | Fecha |
|---|---|---|
| Gerencia de operaciones (comité de cambios) | *Aprobado o rechazado* | *Fecha* |
| Líder técnico (comité de cambios) | *Ídem* | *Fecha* |
| Responsable de calidad (comité de cambios), si puede afectar la telemetría o las evidencias | *Ídem, o "No aplica"* | *Fecha* |
| Equipo de redes, si toca el hub | *Ídem, o "No aplica"* | *Fecha* |
| Aprobación adicional, si algo no se puede deshacer con un `apply` | *Ídem, o "No aplica"* | *Fecha* |
| Seguridad, solo en una excepción por incidente | *Ídem, o "No aplica"* | *Fecha* |

### 5. Pasos y verificación durante la ventana

| Hora | Paso | Responsable | Cómo se comprueba |
|---|---|---|---|
| | | | |

### 6. Aviso a despacho, a calidad y a clientes

| A quién | Qué se le dice | Cuándo | Por dónde |
|---|---|---|---|
| Torre de control (despacho) | | | |
| Guardia de calidad | | | |
| Centros, si se toca su conexión | | | |
| Clientes corporativos, si el portal se interrumpe | | | |

### 7. Cómo se vuelve atrás

| Campo | Valor |
|---|---|
| Método | *Normalmente: revertir el commit y aplicar de nuevo por el pipeline, con la misma aprobación* |
| Cuánto tarda | |
| Criterios para volver atrás | *Señales y umbrales concretos* |
| Quién decide | *Rol* |
| Fuera de la ventana | *Qué pasa si hay que volver atrás o corregir entre las 04:00 y las 22:00: excepción por incidente o espera a la ventana siguiente* |
| Hasta cuándo es limpio | *El momento después del cual volver atrás pierde datos o exige otro procedimiento* |
| ¿Se pierde algún dato? | *Cuánto, comparado con el RPO de 15 minutos* |
| ¿Cuánto tarda en volver el servicio? | *Comparado con el RTO de 4 horas* |
| Lo que no se deshace con un `apply` | *Y qué se hace en ese caso* |

### 8. Sección por tipo de cambio

Se llena la del tipo marcado arriba y se borran las demás.

#### 8.1 Red y firewall

| Pregunta | Respuesta |
|---|---|
| Reglas que se agregan, cambian o retiran | *Identificadores de `firewall-policy.csv` (por ejemplo, FW-402) y de los NSG* |
| ¿Son temporales de la migración? | *Sí o no; si sí, cuándo se retiran* |
| Direcciones y subredes que se tocan | *Filas de `ip-plan.csv`* |
| Verificadores | *`verify_ip_plan.py` y `verify_firewall_policy.py` sin errores en el pull request; `compare_tfplan.py` sobre el `plan`* |
| Túneles, rutas o DNS afectados | *Cali, centros, reenvío de DNS* |
| ¿Puede cortar la telemetría de los cuartos fríos? | *Los sensores entran por la VPN de cada centro* |

#### 8.2 Cómputo

| Pregunta | Respuesta |
|---|---|
| Entornos y perfiles que cambian | *Torre o portal; perfil dedicado o de consumo* |
| Réplicas y nodos, antes y después | |
| ¿Cubre la capacidad de campaña? | *Las cifras de `carga-c-migracion-y-campana.md`, sección 7* |
| Reglas de escalado o de calendario | |
| ¿Cambia el costo mensual? | *Con la fuente* |

#### 8.3 Datos

| Pregunta | Respuesta |
|---|---|
| Base, caché o almacenamiento que cambia | |
| Respaldo previo | *Volcado o punto de restauración, y dónde queda* |
| ¿Cambia el esquema? | *Compatible hacia atrás, en dos pasos. Durante la convivencia no se admiten cambios de esquema* |
| Réplica de Central US | *¿Queda al día? ¿Hay que recrearla?* |
| Inmutabilidad y retención | *¿Toca contenedores con retención de cinco años?* |

#### 8.4 Corte

| Pregunta | Respuesta |
|---|---|
| Qué cubre y qué no | |
| Ensayo | *Fecha, resultado y tiempos medidos* |
| Guion | *Paso a paso con hora y responsable (sección 5)* |
| Criterios para seguir | *Lista cerrada; si uno falla, se vuelve atrás* |
| Punto de no retorno | *Hora y qué pasa antes y después* |
| Equipo y canal | *Roles y canal del corte* |
| Fechas de reserva | *Si se suspende* |

### 9. Cierre

| Campo | Valor |
|---|---|
| Resultado | *Ejecutada, ejecutada con observaciones o vuelta atrás* |
| Hora real de inicio y fin | |
| Incidentes o desviaciones | |
| Pendientes | *Por ejemplo, retirar reglas temporales* |
| Cerrada por | *Rol y fecha* |

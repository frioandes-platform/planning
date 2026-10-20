![FríoAndes](../design/brand/logo/logo-principal.png)

# Nota de versión de aplicación: plantilla

Plantilla para cualquier cambio de la aplicación en producción: la consola de despacho de la torre, sus servicios (guías, inventario, asignación de muelle y ruta, facturación corporativa y evidencias) y el portal de rastreo. Cada salida a producción lleva una nota diligenciada. El comité de cambios aprueba la nota, y la misma nota sirve para avisar a despacho, a calidad y, si toca el portal, a los clientes. Los cambios de red, firewall, cómputo, datos o un corte usan la plantilla de infraestructura (`plantilla-release-notes-infraestructura.md`).

Un ejemplo diligenciado está en `ejemplo-release-notes-aplicacion.md`.

## Cómo se usa

1. Quien pide el cambio copia este archivo como `RN-APP-AAAA-NNN.md` y llena todas las secciones. Ningún campo queda vacío: si algo no aplica, se escribe "No aplica" con el porqué.
2. La nota va en el pull request del cambio. El pipeline no despliega a producción sin la nota y sin la aprobación del Environment de producción (`automatizacion-devops.md`, secciones 3 y 5).
3. El comité de cambios la aprueba al menos dos días hábiles antes de la ventana.
4. Los avisos de la sección 6 salen con el texto de la nota, en los plazos que ella misma fija.
5. Después de la ventana se completa la sección 8 y la nota queda cerrada en el repositorio.

## Reglas que la nota tiene que cumplir

| Regla | De dónde sale |
|---|---|
| Ningún cambio en producción entre las 04:00 y las 22:00, hora de Colombia. La ventana es de 22:00 a 04:00, que en UTC es de 03:00 a 09:00 | Enunciado; `automatizacion-devops.md`, sección 5 |
| Ningún cambio durante una campaña: fin de año (15 de noviembre al 10 de enero), Semana Santa y mitad de año (15 de junio al 15 de julio) | `carga-c-migracion-y-campana.md`, sección 4.1 |
| La única excepción es un incidente, con etiqueta de incidente en el pull request y aprobación de seguridad | `automatizacion-devops.md`, sección 3 |
| La aprueban dos personas del comité de cambios, distintas de quien escribió el cambio | Ídem |
| La misma imagen, por su digest, pasó por desarrollo y pruebas antes de producción | Ídem |
| Los cambios de esquema son compatibles hacia atrás, en dos pasos: primero se agrega lo nuevo y lo viejo se quita en una ventana posterior | `automatizacion-devops.md`, sección 5 |
| Se avisa siempre a despacho y a calidad, aunque el cambio no los toque: de noche la guardia de calidad recibe las alertas de temperatura | Guía de lectura, Reto 4 |

---

## Nota de versión RN-APP-AAAA-NNN

| Campo | Valor |
|---|---|
| Título | *Una línea: qué gana el usuario* |
| Componentes | *Aplicaciones de Container Apps que cambian (por ejemplo, rastreo y front del portal)* |
| Versión | *Versión anterior → versión nueva de cada componente* |
| Tipo | *Mejora, corrección o ajuste técnico* |
| Solicitante | *Rol y área* |
| Responsable técnico | *Rol de quien ejecuta la ventana* |
| Pull request | *Enlace* |
| Estado | *Borrador, aprobada, ejecutada, vuelta atrás o cerrada* |

### 1. Qué cambia

**Para el usuario.** *Qué ve distinto el usuario interno o el cliente, en lenguaje de negocio.*

**Técnicamente.**

| Componente | Imagen (digest) | Cambio de configuración o secretos | Cambio de esquema |
|---|---|---|---|
| *Aplicación* | *sha256:…* | *Variables o secretos de Key Vault nuevos o modificados, o "Ninguno"* | *Ninguno, o el paso 1 o 2 del cambio en dos pasos, con la nota que lo hizo* |

**Lo que no cambia.** *Componentes, integraciones y datos que quedan iguales. Sirve para acotar el impacto.*

**Pruebas hechas.** *Qué se probó en pruebas, con qué datos y con qué resultado. Enlace a la ejecución del pipeline.*

### 2. Ventana

| Campo | Valor |
|---|---|
| Fecha | *Día de la semana y fecha* |
| Hora, Colombia | *Inicio y fin, dentro de 22:00 a 04:00* |
| Hora, UTC | *Inicio y fin, dentro de 03:00 a 09:00* |
| Duración prevista | *Minutos, incluida la verificación* |
| Interrupción del servicio | *Ninguna, o cuánto y de qué* |
| ¿Fuera de campaña? | *Sí, con la campaña más cercana* |
| ¿Excepción por incidente? | *No. Si es sí: número del incidente, aprobación de seguridad y por qué no espera la siguiente ventana* |

### 3. Impacto

| Pregunta | Respuesta |
|---|---|
| ¿Quiénes lo notan? | *Usuarios internos, clientes corporativos, guardia de calidad* |
| ¿Hay interrupción o degradación durante la ventana? | *Qué y cuánto* |
| ¿Toca datos personales o lo que ve cada cliente? | *Sí o no; si sí, cómo se mantiene el filtro por cliente* |
| ¿Toca la alerta de temperatura o la telemetría? | *Sí o no* |
| ¿Cambia la capacidad o el costo? | *Réplicas, solicitudes, registros* |
| Riesgo | *Bajo, medio o alto, con la razón* |

### 4. Aprobación

| Rol | Decisión | Fecha |
|---|---|---|
| Gerencia de operaciones (comité de cambios) | *Aprobado o rechazado* | *Fecha* |
| Líder técnico (comité de cambios) | *Ídem* | *Fecha* |
| Responsable de calidad (comité de cambios), si toca telemetría o evidencias | *Ídem, o "No aplica"* | *Fecha* |
| Seguridad, solo en una excepción por incidente | *Ídem, o "No aplica"* | *Fecha* |

La aprobación queda registrada en el Environment de producción de GitHub, con el nombre de quien aprueba.

### 5. Verificación durante la ventana

| Paso | Hora | Responsable | Cómo se comprueba |
|---|---|---|---|
| *Despliegue de la revisión nueva sin tráfico* | | | |
| *Pruebas de humo sobre la revisión nueva* | | | |
| *Paso del tráfico a la revisión nueva* | | | |
| *Observación* | | | |
| *Decisión: seguir o volver atrás* | | | |

### 6. Aviso a despacho, a calidad y a clientes

| A quién | Qué se le dice | Cuándo | Por dónde |
|---|---|---|---|
| Torre de control (despacho) | | | |
| Guardia de calidad | | | |
| Atención a clientes | | | |
| Clientes corporativos, si cambia lo que ven | | | |

### 7. Cómo se vuelve atrás

| Campo | Valor |
|---|---|
| Método | *Normalmente: mover el tráfico de Container Apps a la revisión anterior, que se mantiene activa* |
| Cuánto tarda | *Minutos* |
| Criterios para volver atrás | *Señales y umbrales concretos* |
| Quién decide | *Rol* |
| Hasta cuándo se puede | *Por ejemplo, mientras la revisión anterior siga activa* |
| ¿Se pierde algún dato? | *Sí o no, y por qué* |
| Lo que no se deshace moviendo el tráfico | *Esquema, datos o configuración que quedan, y por qué son compatibles con la versión anterior* |

### 8. Cierre

| Campo | Valor |
|---|---|
| Resultado | *Ejecutada, ejecutada con observaciones o vuelta atrás* |
| Hora real de inicio y fin | |
| Incidentes o desviaciones | |
| Revisión anterior desactivada | *Fecha* |
| Cerrada por | *Rol y fecha* |

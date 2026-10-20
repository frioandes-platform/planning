![FríoAndes](../design/brand/logo/logo-principal.png)

# Nota de versión de aplicación: ejemplo diligenciado

Ejemplo real de `plantilla-release-notes-aplicacion.md`, ya cerrado: una mejora del portal de rastreo, la primera salida del portal después del cierre del proyecto. Muestra el despliegue sin interrupción con revisiones de Container Apps, el cambio de esquema en dos pasos y los avisos a despacho, a calidad y a los clientes.

---

## Nota de versión RN-APP-2027-015

| Campo | Valor |
|---|---|
| Título | Búsqueda de guías por orden de compra y exportación del listado en el portal de rastreo |
| Componentes | `rastreo` y `front-portal`, en el entorno del portal (`snet-app-portal`) |
| Versión | `rastreo` 3.1.4 → 3.2.0; `front-portal` 3.1.2 → 3.2.0 |
| Tipo | Mejora |
| Solicitante | Gerencia comercial, a pedido de los clientes corporativos |
| Responsable técnico | Equipo de aplicación, con el ingeniero de plataforma de turno |
| Pull request | `frioandes-platform/app` #214 |
| Estado | Cerrada |

### 1. Qué cambia

**Para el usuario.** Los clientes corporativos pueden buscar sus guías por su propio número de orden de compra, además del número de guía y la fecha. Pueden descargar el listado filtrado en CSV, hasta 5.000 guías por descarga. Hoy esas consultas llegan por correo a atención a clientes, que las arma a mano.

**Técnicamente.**

| Componente | Imagen (digest) | Cambio de configuración o secretos | Cambio de esquema |
|---|---|---|---|
| `rastreo` | `sha256:3b8686ce918ca398e52214bb73604cf825137ff5bd2803d9d25ec3e914e467b7` | Variable nueva `EXPORT_MAX_ROWS=5000` y límite de 10 descargas por hora por cuenta. Sin secretos nuevos | Ninguno en esta nota. Usa el índice `ix_guias_cliente_oc` sobre `(cliente_id, orden_compra)`, creado en el paso 1 (RN-APP-2027-014, martes 18 de mayo de 22:30 a 22:50, sin bloqueo de la tabla) |
| `front-portal` | `sha256:4a4464d883d183b86652b4a1fbc350cb12c35c2e3cd6f2804ec9c582bb169987` | Ninguno | Ninguno |

- La búsqueda y la descarga usan el mismo filtro por cliente que ya aplica `rastreo`: un cliente solo ve sus guías (`seguridad-datos-personales-perimetro.md`).
- El CSV lleva los mismos campos que hoy muestra el detalle de la guía, sin datos de conductores ni de otros clientes.
- La ruta nueva `/api/guias/export` queda detrás del Application Gateway con WAF. El límite de 300 solicitudes por minuto por IP no cambia, porque la descarga cuenta como una sola solicitud.

**Lo que no cambia.** La consola de despacho, los servicios de la torre, la base (salvo el índice ya creado en el paso 1), la telemetría, la alerta de temperatura, Fabric y la facturación que ve cada cliente.

**Pruebas hechas.** En pruebas, del 11 al 14 de mayo, con datos sintéticos:

- búsqueda por orden de compra en 2 millones de guías de prueba, con respuesta p95 de 180 ms;
- descarga de 5.000 guías en 2,1 s;
- prueba de que un cliente no ve guías de otro, con 3 cuentas de prueba;
- prueba de carga del portal a 2.000 solicitudes por minuto con la versión nueva, sin errores 5xx y con 4 réplicas de rastreo, como en la campaña (`carga-c-migracion-y-campana.md`, sección 7.3).

El pipeline promovió las dos imágenes, por su digest, de desarrollo a pruebas (ejecución 1.482).

### 2. Ventana

| Campo | Valor |
|---|---|
| Fecha | Martes 25 de mayo de 2027 |
| Hora, Colombia | 22:30 a 23:45 |
| Hora, UTC | 03:30 a 04:45 del miércoles 26 de mayo |
| Duración prevista | 75 minutos, incluida la observación |
| Interrupción del servicio | Ninguna. La revisión nueva se despliega al lado de la actual y el tráfico pasa de una a otra sin cortar sesiones |
| ¿Fuera de campaña? | Sí. Semana Santa terminó el 28 de marzo y la campaña de mitad de año empieza el 15 de junio, 21 días después |
| ¿Excepción por incidente? | No |

La ventana está dentro de la franja de 22:00 a 04:00 y deja más de cuatro horas libres antes de que empiece el despacho.

### 3. Impacto

| Pregunta | Respuesta |
|---|---|
| ¿Quiénes lo notan? | Los clientes corporativos, que ven la búsqueda y la descarga nuevas. Atención a clientes, que deja de armar listados a mano. Los usuarios internos y la guardia de calidad no notan nada |
| ¿Hay interrupción o degradación durante la ventana? | No. A esa hora el portal recibe unas 20 solicitudes por minuto |
| ¿Toca datos personales o lo que ve cada cliente? | Sí: expone las guías del cliente en un formato descargable. Se mantiene el filtro por cliente existente, que se probó con tres cuentas, y el CSV no incluye datos de conductores |
| ¿Toca la alerta de temperatura o la telemetría? | No |
| ¿Cambia la capacidad o el costo? | No de forma apreciable. El escalado del portal sigue igual (mínimo 2 réplicas, máximo 10). Las descargas suman unos MB de salida a internet al mes |
| Riesgo | Bajo. Cambio acotado al portal, sin cambio de esquema en esta ventana, con vuelta atrás en minutos |

### 4. Aprobación

| Rol | Decisión | Fecha |
|---|---|---|
| Gerencia de operaciones (comité de cambios) | Aprobado | Jueves 20 de mayo de 2027 |
| Líder técnico (comité de cambios) | Aprobado | Jueves 20 de mayo de 2027 |
| Responsable de calidad (comité de cambios) | No aplica: no toca telemetría ni evidencias. Queda informado (sección 6) | — |
| Seguridad | No aplica: no es una excepción por incidente. Revisó el filtro por cliente en el pull request | Miércoles 19 de mayo de 2027 |

Las dos aprobaciones quedaron registradas en el Environment de producción de GitHub. Quien escribió el cambio no aprueba.

### 5. Verificación durante la ventana

| Paso | Hora | Responsable | Cómo se comprueba |
|---|---|---|---|
| El pipeline despliega las revisiones `rastreo--v3-2-0` y `front-portal--v3-2-0` con 0 % del tráfico | 22:30 | Pipeline, con la aprobación del Environment | Las dos revisiones quedan en estado "Running" con su chequeo de salud en verde |
| Pruebas de humo sobre las revisiones nuevas, por su etiqueta, sin tráfico de clientes | 22:40 | Equipo de aplicación | Con el cliente de verificación de producción, que solo tiene guías sintéticas: inicio de sesión, búsqueda por orden de compra, descarga de un CSV, y comprobación de que no aparecen guías de otro cliente |
| Paso del 100 % del tráfico a las revisiones nuevas | 22:55 | Pipeline | División de tráfico en Container Apps: 0/100 |
| Observación | 23:00 a 23:40 | Ingeniero de plataforma de turno | En Azure Monitor (`observabilidad-slo-zabbix.md`): errores 5xx del Application Gateway, latencia p95 del portal, reinicios de réplicas y la alerta de consumo del objetivo de disponibilidad |
| Decisión: seguir o volver atrás | 23:45 | Responsable técnico | Criterios de la sección 7 |

### 6. Aviso a despacho, a calidad y a clientes

| A quién | Qué se le dice | Cuándo | Por dónde |
|---|---|---|---|
| Torre de control (despacho) | El portal de rastreo se actualiza el martes 25 de mayo de 22:30 a 23:45, sin interrupción. La consola de despacho no cambia. Si un cliente pregunta por la búsqueda nueva, se remite a atención a clientes | Jueves 20 de mayo, al aprobarse | Canal de la torre en Teams |
| Guardia de calidad | Esa noche hay un cambio en el portal de rastreo. No toca la telemetría ni la alerta de temperatura, que siguen llegando por los mismos canales. Contacto de la ventana: el ingeniero de plataforma de turno | Martes 25 de mayo, 18:00 | Canal de guardia en Teams |
| Atención a clientes | Guía de una página con la búsqueda y la descarga nuevas, y el límite de 5.000 guías y 10 descargas por hora | Lunes 24 de mayo | Correo y sesión de 30 minutos |
| Clientes corporativos | El portal tiene búsqueda por orden de compra y descarga del listado en CSV | Miércoles 26 de mayo, 08:00, solo si la ventana cerró sin volver atrás | Aviso en el portal y correo a los contactos de cada cliente |

Como no hay interrupción, a los clientes no se les avisa antes de la ventana: se les avisa de la novedad cuando ya está en servicio.

### 7. Cómo se vuelve atrás

| Campo | Valor |
|---|---|
| Método | Mover el 100 % del tráfico a las revisiones anteriores (`rastreo--v3-1-4` y `front-portal--v3-1-2`), que siguen activas. No se despliega nada de nuevo |
| Cuánto tarda | Menos de 5 minutos |
| Criterios para volver atrás | Una prueba de humo falla; los errores 5xx del portal pasan del 1 % durante 10 minutos; la latencia p95 pasa de 1,5 s durante 10 minutos; o aparece una guía de otro cliente en cualquier prueba (en ese caso, de inmediato y con aviso a seguridad) |
| Quién decide | El responsable técnico de la ventana. Si es después de las 23:45, el ingeniero de plataforma de turno |
| Fuera de la ventana | Mover el tráfico también es un cambio en producción. Hasta las 04:00 lo decide quien está en la ventana. Entre las 04:00 y las 22:00 solo se hace como excepción por incidente, con etiqueta de incidente y aprobación de seguridad, porque el pipeline lo bloquea sin ellas. Si el problema puede esperar, se vuelve atrás en la ventana siguiente |
| Hasta cuándo se puede | Siete días, hasta el martes 1 de junio, cuando se desactivan las revisiones anteriores (sección 8). Después, se vuelve atrás desplegando la versión 3.1.4 por el pipeline, en otra ventana |
| ¿Se pierde algún dato? | No. La versión nueva solo lee: no escribe datos nuevos en la base |
| Lo que no se deshace moviendo el tráfico | El índice `ix_guias_cliente_oc`, creado en el paso 1. Es compatible con la versión 3.1.4, que no lo usa, así que se deja |

### 8. Cierre

| Campo | Valor |
|---|---|
| Resultado | Ejecutada, sin volver atrás |
| Hora real de inicio y fin | 22:31 a 23:42 del martes 25 de mayo de 2027 |
| Incidentes o desviaciones | Ninguno. En la observación: 0 errores 5xx, latencia p95 del portal de 210 ms y ningún reinicio de réplicas |
| Revisión anterior desactivada | Martes 1 de junio de 2027, a las 22:15, en la ventana de 22:00 a 04:00 |
| Cerrada por | Responsable técnico, el martes 1 de junio de 2027 |

La sección 8 es la única que se llena después de ejecutar el cambio. Todo lo demás estaba completo antes de pedir la aprobación.

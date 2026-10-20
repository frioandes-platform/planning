![FríoAndes](../design/brand/logo/logo-principal.png)

# Verificación de la ventana de cambio en los dos ejemplos

Revisión cruzada de los dos ejemplos diligenciados contra la ventana de cambio y la excepción por incidente:

- `ejemplo-release-notes-aplicacion.md` (F4-01, RN-APP-2027-015);
- `ejemplo-release-notes-infraestructura.md` (F4-02, RN-INF-2027-007).

Un ejemplo es lo que el equipo copia. Si muestra un cambio a las 15:00 o una vuelta atrás en pleno despacho sin decir que es una excepción, la siguiente nota lo repite. Por eso se revisó cada hora de los dos ejemplos, no solo la ventana declarada.

**Resultado: los dos ejemplos respetan la ventana y ninguno usa la excepción por incidente.** Se encontraron siete inconsistencias: cambios sin hora y vueltas atrás que no decían qué pasa fuera de la ventana. Una octava, de anticipación de la aprobación, no es de horario pero también se corrigió. Las ocho quedaron corregidas en los ejemplos y en las plantillas (sección 5).

## Contenido

1. Reglas contra las que se verifica
2. Método
3. Ejemplo de aplicación: RN-APP-2027-015
4. Ejemplo de infraestructura: RN-INF-2027-007
5. Inconsistencias encontradas y corregidas
6. Conclusión
7. Supuestos
8. Validación y cierre

---

## 1. Reglas contra las que se verifica

| Regla | Fuente |
|---|---|
| Ningún cambio en producción ni en el hub entre las 04:00 y las 22:00, hora de Colombia. La ventana va de 22:00 a 04:00, que en UTC es de 03:00 a 09:00. Colombia no tiene horario de verano: la diferencia es de 5 horas todo el año | Enunciado; `automatizacion-devops.md`, sección 5 |
| Ningún cambio durante una campaña: del 15 de noviembre al 10 de enero, del 15 al 28 de marzo de 2027 y del 15 de junio al 15 de julio | `carga-c-migracion-y-campana.md`, sección 4.1 |
| La única excepción es un incidente, con etiqueta de incidente en el pull request y aprobación de seguridad. El pipeline rechaza el `apply` de producción fuera de la ventana si no las tiene | `automatizacion-devops.md`, secciones 3 y 5 |
| Si un ejemplo usa la excepción, la marca en el campo "¿Excepción por incidente?" | Plantillas F4-01 y F4-02, sección 2 |

## 2. Método

1. Se listó cada paso de los dos ejemplos que tiene fecha u hora: la ventana declarada, el guion, las notas relacionadas, la vuelta atrás, los pendientes y el cierre real.
2. Se separaron los pasos que **cambian producción** de los que no la cambian. No cambian producción la observación, las decisiones, los avisos, las aprobaciones y lo que pasa en pruebas (sección 7).
3. Para cada cambio se comprobó que la hora de Colombia está entre las 22:00 y las 04:00, que la hora UTC es esa misma más 5 horas, y que la fecha cae fuera de campaña.
4. Se comprobó el día de la semana de cada fecha contra el calendario de 2027.
5. Se buscaron lecturas peligrosas: pasos sin hora, que alguien podría ejecutar de día, y vueltas atrás sin límite de horario.

## 3. Ejemplo de aplicación: RN-APP-2027-015

**Ventana declarada:** martes 25 de mayo de 2027, de 22:30 a 23:45 (de 03:30 a 04:45 UTC del miércoles 26). "¿Excepción por incidente?": No.

| Paso | Fecha | Hora, Colombia | Hora, UTC | ¿Cambia producción? | ¿En la ventana y fuera de campaña? |
|---|---|---|---|---|---|
| Índice `ix_guias_cliente_oc` (paso 1 del cambio de esquema, RN-APP-2027-014) | Martes 18 de mayo | 22:30 a 22:50 | 03:30 a 03:50 del 19 | Sí | Sí. **Corregido:** no tenía hora (inconsistencia 5) |
| Despliegue de las revisiones nuevas, sin tráfico | Martes 25 de mayo | 22:30 | 03:30 | Sí | Sí |
| Pruebas de humo sobre las revisiones nuevas | Ídem | 22:40 | 03:40 | No, solo lee con el cliente de verificación | — |
| Paso del 100 % del tráfico | Ídem | 22:55 | 03:55 | Sí | Sí |
| Observación | Ídem | 23:00 a 23:40 | 04:00 a 04:40 | No | — |
| Decisión de seguir o volver atrás | Ídem | 23:45 | 04:45 | No | — |
| Ejecución real (cierre) | Ídem | 22:31 a 23:42 | 03:31 a 04:42 | Sí | Sí |
| Desactivación de las revisiones anteriores | Martes 1 de junio | 22:15 | 03:15 del 2 | Sí | Sí |
| Vuelta atrás moviendo el tráfico | Hasta el 1 de junio | No decía | — | Sí | **Corregido:** no decía qué pasa entre las 04:00 y las 22:00 (inconsistencia 4) |

Lo que no se verifica porque no cambia producción:
- las pruebas en el ambiente de pruebas, del 11 al 14 de mayo;
- las aprobaciones, del 19 y el 20 de mayo;
- los avisos, del 20 al 26 de mayo. El aviso a los clientes sale a las 08:00 del 26, después de la ventana, y no cambia nada.

**Campaña.** Semana Santa terminó el 28 de marzo y la campaña de mitad de año empieza el 15 de junio. El 18 de mayo, el 25 de mayo y el 1 de junio caen fuera.

**Anticipación de la aprobación.** El comité aprobó el jueves 20 de mayo, con dos días hábiles completos antes de la ventana (el viernes 21 y el lunes 24). Cumple.

## 4. Ejemplo de infraestructura: RN-INF-2027-007

**Ventana declarada:** congelamiento desde el sábado 13 de febrero de 2027 a las 22:00 y mantenimiento de 01:00 a 03:00 del domingo 14 (de 06:00 a 08:00 UTC). "¿Excepción por incidente?": No.

| Paso | Fecha | Hora, Colombia | Hora, UTC | ¿Cambia producción? | ¿En la ventana y fuera de campaña? |
|---|---|---|---|---|---|
| Ensayo sobre el servidor temporal de `snet-data` de producción | Domingo 31 de enero | 01:00 a 03:00 | 06:00 a 08:00 | Sí, en un servidor temporal | Sí |
| TTL del DNS público del portal y del DNS interno de la torre a 5 minutos | Martes 9 de febrero | 22:00 | 03:00 del 10 | Sí | Sí. **Corregido:** no tenía hora (inconsistencia 1) |
| Congelamiento de cambios y revisión del retraso de DMS | Sábado 13 de febrero | 22:00 | 03:00 del 14 | No | — |
| Volcado completo de la base de Cali | Domingo 14 de febrero | 00:30 | 05:30 | No, solo lee | — |
| Modo de mantenimiento y base de Cali en solo lectura | Ídem | 01:00 | 06:00 | Sí | Sí |
| Corte en DMS | Ídem | 01:10 | 06:10 | Sí | Sí |
| Plan A: réplicas | Ídem | 01:40 | 06:40 | Sí | Sí |
| Cambio de DNS | Ídem | 01:50 | 06:50 | Sí | Sí |
| Apertura con escrituras reales (punto de no retorno) | Ídem | 02:30 | 07:30 | Sí | Sí |
| Vuelta atrás limpia, si se decide | Ídem | De 01:00 a 02:30, con el servicio de vuelta antes de las 03:00 | De 06:00 a 08:00 | Sí | Sí |
| Plan B: retiro de lo temporal de la migración | Ídem | 03:10 | 08:10 | Sí | Sí |
| Monitoreo reforzado | Ídem | 03:00 a 06:00 | 08:00 a 11:00 | No | **Corregido:** no decía que después de las 04:00 solo se observa (inconsistencia 2) |
| Salidas después del punto de no retorno: corregir en Azure, Central US o volver a Cali | Desde el 14 de febrero | No decía | — | Sí | **Corregido:** no decía que fuera de la ventana son excepción por incidente (inconsistencia 3) |
| Ejecución real (cierre) | Domingo 14 de febrero | 01:00 a 02:41 | 06:00 a 07:41 | Sí | Sí |
| RN-INF-2027-008: eliminar DMS, cerrar la copia continua, retirar la regla de `snet-archive` | Lunes 15 de febrero | 22:00 | 03:00 del 16 | Sí | Sí. **Corregido** en el cierre, que no tenía hora (inconsistencia 6) |
| Cierre del plazo de vuelta atrás: retiro de FW-503, FW-504 y los grupos 400 y 500 | Lunes 8 de marzo | 22:00 | 03:00 del 9 | Sí | Sí. **Corregido** en el cierre (inconsistencia 6) |
| Fechas de reserva del corte | Domingos 21 y 28 de febrero y 7 de marzo | 01:00 a 03:00 | 06:00 a 08:00 | Sí, si se usan | Sí |

Lo que no se verifica porque no cambia producción:
- el Plan A aplicado en pruebas, el 2 de febrero;
- las aprobaciones, del 8 y el 9 de febrero;
- los avisos, del 1 al 14 de febrero.

**Campaña.** La campaña de fin de año terminó el 10 de enero y Semana Santa empieza el 15 de marzo. Todas las fechas del ejemplo, del 31 de enero al 8 de marzo, caen fuera.

**Anticipación de la aprobación.** El comité aprobó el lunes 8 de febrero y la gerencia dio la aprobación adicional el martes 9, a seis y cinco días del corte. La plantilla pedía una semana, así que no cumplía (inconsistencia 8).

## 5. Inconsistencias encontradas y corregidas

| # | Dónde | Qué decía | Por qué era un problema | Corrección |
|---|---|---|---|---|
| 1 | Infraestructura, secciones 1 y 5 | El TTL se bajó "el martes 9 de febrero", sin hora | Cambiar el DNS de producción es un cambio. Sin hora, quien copie la nota puede hacerlo de día | "Martes 9 de febrero, 22:00" en los dos lugares |
| 2 | Infraestructura, sección 2 | "Monitoreo reforzado hasta las 06:00" | Se puede leer como que la ventana se extiende hasta las 06:00 | Se aclara que de 04:00 a 06:00 solo se observa, y que una corrección después de las 04:00 es una excepción por incidente |
| 3 | Infraestructura, sección 7 | Las tres salidas después de las 02:30 no tenían límite de horario | Corregir en Azure o volver a Cali puede pasar en pleno despacho, y la nota no decía con qué autorización | Fila "Fuera de la ventana": después de las 04:00, las tres salidas son excepción por incidente, con etiqueta y aprobación de seguridad |
| 4 | Aplicación, sección 7 | La vuelta atrás se podía hacer durante siete días, sin decir a qué hora | Mover el tráfico es un cambio en producción, y el pipeline lo rechaza de día sin etiqueta de incidente | Fila "Fuera de la ventana": de día, solo como excepción por incidente; si puede esperar, en la ventana siguiente |
| 5 | Aplicación, sección 1 | El índice de RN-APP-2027-014 se creó "el martes 18 de mayo", sin hora | Es un cambio de esquema en producción | "Martes 18 de mayo de 22:30 a 22:50" |
| 6 | Infraestructura, sección 9 | Los pendientes del 15 de febrero y del 8 de marzo, sin hora | Son cambios en producción | "22:00" en los dos, como ya decía el guion para el 15 de febrero |
| 7 | Las dos plantillas | No pedían decir qué pasa con una vuelta atrás fuera de la ventana | Las inconsistencias 3 y 4 venían de ahí, y se repetirían en cada nota nueva | Regla nueva en la tabla de reglas y fila "Fuera de la ventana" en la sección 7 de las dos plantillas |
| 8 | Plantilla de infraestructura y registro de supuestos | Un corte se aprueba "con una semana de anticipación" | El comité del corte aprueba el lunes 8 de febrero (`carga-c-migracion-y-campana.md`, sección 5.6), a seis días. No puede ser antes porque la reserva del ensayo es el domingo 7 | La regla pasa a cinco días como mínimo y, para un corte, después de su ensayo. El ejemplo cumple: 8 y 9 de febrero, a seis y cinco días |

La inconsistencia 8 no es de horario. Se corrige aquí porque es la misma clase de error: el ejemplo contradecía una regla de su propia plantilla.

## 6. Conclusión

- **Los dos ejemplos proponen su ventana dentro de la franja de 22:00 a 04:00**, fuera de campaña, con la hora UTC correcta. Ninguno es una excepción por incidente, y los dos lo dicen en su campo.
- **No queda ninguna inconsistencia.** Las ocho encontradas están corregidas en los ejemplos, en las plantillas y en el registro de supuestos.

## 7. Supuestos

| Supuesto | Por qué se asume |
|---|---|
| Solo cuenta como cambio lo que modifica producción o el hub. La observación, las decisiones, los avisos, las aprobaciones y lo que se hace en pruebas no están sujetos a la ventana | La regla del enunciado y el bloqueo del pipeline se refieren a cambios productivos |
| Una vuelta atrás o una corrección fuera de la ventana es un cambio y se trata como excepción por incidente | El pipeline no distingue un `apply` de avance de uno de vuelta atrás. Si no, la vuelta atrás sería una puerta para cambiar de día |
| El ensayo del corte sobre el servidor temporal de producción se trata como un cambio en producción y respeta la ventana | Está en la subred de datos de producción y usa el mismo DMS |

## 8. Validación y cierre

| Criterio de aceptación | Evidencia |
|---|---|
| Ambos ejemplos muestran una ventana propuesta dentro de la franja de 22:00 a 04:00 (fuera de la restricción de 04:00 a 22:00), o están marcados como excepción por incidente | Secciones 3 y 4: cada cambio de los dos ejemplos está entre las 22:00 y las 04:00, con su hora UTC, y los dos dicen "No" en "¿Excepción por incidente?" |
| El documento concluye "sin inconsistencias" o lista las corregidas | Sección 5: ocho inconsistencias corregidas. Sección 6: no queda ninguna |

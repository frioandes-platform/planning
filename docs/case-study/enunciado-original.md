# Reto: Plataforma cloud para la operación de cadena de frío

> **Universidad Icesi** · Ejercicio académico · Junior DevOps · Senior DevOps
>
> Conversión fiel a Markdown de `Ejercicio-Analista-CloudOps-FrioAndes.pdf` (8 páginas, 23-sep-2026).
> El texto no se modificó; solo se le dio formato (títulos, listas y tabla). Los marcadores
> `<!-- p. N -->` indican dónde empieza cada página del PDF.

<!-- p. 1 -->

**Caso de estudio académico.** El escenario, la empresa y las cifras son ficticios y fueron elaborados para el perfil Junior DevOps y para el perfil Senior DevOps.

## Contexto

FríoAndes S.A. opera almacenamiento y transporte refrigerado de alimentos en Colombia. Tiene un centro nacional de operaciones en Cali, donde está el único datacenter, y ocho centros de distribución regionales. La operación depende de una plataforma propia que hoy corre sobre virtualización local.

Las cargas que sostiene ese datacenter son:

- Torre de control de despachos, usada solo por personal interno.
- Inventario de bodegas refrigeradas.
- Facturación a clientes corporativos.
- Portal público de rastreo de guías.
- Repositorio de evidencias de entrega: fotos, comprobantes firmados y documentos.
- Históricos de temperatura que hoy se cargan por lote, una vez por hora, desde archivos que envían los centros regionales.

La organización describió estos problemas:

- La capacidad de cómputo y almacenamiento es fija. En campañas (Semana Santa, mitad de año y fin de año) el despacho se ralentiza y el portal de rastreo se degrada.
- Publicar un cambio toma semanas porque el despliegue es manual y los ambientes comparten el mismo clúster.
- Un reclamo por ruptura de cadena de frío se investiga con datos de horas o días atrás. No hay alerta mientras el camión sigue en ruta.
- El archivo histórico ya suma cerca de 1,2 PB y sigue creciendo unos 12 TB al mes. El servicio de archivos actual no tiene holgura ni un respaldo separado.
- CentOS 7 y MySQL 5.7 ya están fuera de soporte. Ubuntu 20.04 solo sigue con soporte extendido de pago.
- No existe un esquema único de identidades, presupuestos ni auditoría para pensar en más de un proveedor de nube.

## Visión

FríoAndes quiere dejar de ampliar el datacenter y pasar a una plataforma en la nube operada con gobierno, seguridad, conectividad híbrida y entrega automatizada. El plan combina tres movimientos:

1. Construir una plataforma nueva de operación logística, que reemplaza al núcleo actual.
2. Incorporar telemetría de temperatura y ubicación en tiempo cercano al real.
3. Migrar datos y módulos hacia esa plataforma sin detener el despacho diurno.
4. Sumar, encima de ese diseño, una estrategia de Microsoft Fabric para que la torre de control use inteligencia artificial sobre la operación y la telemetría.

<!-- p. 2 -->

La estrategia debe alinearse con los pilares de un marco Well-Architected: excelencia operacional, seguridad, confiabilidad, eficiencia de desempeño y optimización de costos.

## Qué se evalúa

Quien presenta diseña la plataforma, la estrategia de Microsoft Fabric de la torre de control y el sistema de diseño de FríoAndes. No implementa la lógica de negocio ni la aplicación. Sí debe dejar claro cómo se despliegan, aseguran, observan y cuestan las cargas, cómo Fabric consume esos datos sin volver a copiar el archivo histórico completo por defecto, y cómo se ve la marca en la torre de control y en el portal.

Puede elegir una nube principal (Azure, AWS o GCP) y justificar la elección. El diseño debe dejar preparada una interconexión futura con una segunda nube, sin duplicar toda la plataforma desde el día uno.

Todo supuesto que no esté en este enunciado debe quedar escrito en la propuesta.

## Objetivo

Diseñar y sustentar la adopción de nube de FríoAndes cubriendo gobierno, seguridad, red, automatización, cargas nuevas, migración del núcleo actual, observabilidad y costo. Encima de ese diseño, proponer la estrategia de Microsoft Fabric para la inteligencia artificial de la torre de control.

## Reto

### 1. Gobierno de la plataforma

- Organizar cuentas, suscripciones o proyectos para separar seguridad, redes, cargas productivas y ambientes no productivos.
- Definir cómo se aplican políticas, identidades, etiquetas y presupuestos desde un punto común.
- Proponer auditoría y retención de registros suficiente para reconstruir quién accedió a datos de clientes, evidencias de entrega y lecturas de temperatura.
- Indicar el modelo de facturación interna: cómo FríoAndes distingue el costo de operación, el de telemetría y el de ambientes de prueba.

### 2. Seguridad

- Identidad y acceso con mínimo privilegio, MFA para administradores y para la consola interna de despacho.
- Cifrado en tránsito y en reposo, incluyendo llaves y secretos.
- Separación de red entre la torre de control, el portal público, la ingesta de sensores y los datos analíticos.
- Protección del perímetro público (portal de rastreo) y detección de actividad anómala.
- Tratamiento de datos personales de conductores y destinatarios. No hay datos de pago con tarjeta. Las evidencias y la trazabilidad de temperatura se conservan cinco años por contrato con los clientes de alimentos.

### 3. Red híbrida y preparación para una segunda nube

Situación actual que el diseño debe respetar:

- Un firewall en Cali concentra las políticas y el enrutamiento. El internet de esa sede es de 400 Mbps simétricos, compartido con el resto de la operación. No hay enlace dedicado hacia una nube.
- Cada centro regional se conecta por VPN site-to-site. La torre de control solo puede usarse desde la red corporativa, porque muestra ubicación de carga y datos de clientes.

<!-- p. 3 -->

- Los sensores de los cuartos fríos están en la red local de cada centro. Los sensores y el GPS de los camiones salen por la red móvil del operador de flota, no por la VPN del centro.
- El rastreo público se publica por NAT, con Nginx como proxy inverso. Un firewall de aplicaciones cubre la zona pública y la privada.
- Desarrolladores y operadores trabajan parte de la semana fuera de la sede.

Inventario de redes on-premises. Estas direcciones ya están en uso y la nube no puede solaparse con ellas. El firewall de Cali enruta entre todas.

| Sitio | Uso | Red | Dónde termina |
|---|---|---|---|
| Cali | Usuarios de la sede y torre de control | 10.20.0.0/24 | Firewall de Cali |
| Cali | Servidores de aplicación y front | 10.20.1.0/24 | Firewall de Cali |
| Cali | Bases y caché | 10.20.2.0/24 | Firewall de Cali |
| Cali | Archivo de 1,2 PB y Zabbix | 10.20.3.0/24 | Firewall de Cali |
| Cali | Administración de VMware | 10.20.4.0/24 | Firewall de Cali |
| Cali | Publicación del rastreo (Nginx) | 10.20.5.0/24 | Firewall de Cali, con NAT a internet |
| Cali | Enlaces VPN hacia centros y hacia el firewall | 10.20.10.0/24 | Firewall de Cali |
| Buenaventura | Usuarios del centro | 10.31.0.0/24 | VPN site-to-site |
| Buenaventura | Sensores de cuartos fríos | 10.31.1.0/24 | VPN site-to-site |
| Bogotá | Usuarios del centro | 10.32.0.0/24 | VPN site-to-site |
| Bogotá | Sensores de cuartos fríos | 10.32.1.0/24 | VPN site-to-site |
| Medellín | Usuarios del centro | 10.33.0.0/24 | VPN site-to-site |
| Medellín | Sensores de cuartos fríos | 10.33.1.0/24 | VPN site-to-site |
| Barranquilla | Usuarios del centro | 10.34.0.0/24 | VPN site-to-site |
| Barranquilla | Sensores de cuartos fríos | 10.34.1.0/24 | VPN site-to-site |
| Bucaramanga | Usuarios del centro | 10.35.0.0/24 | VPN site-to-site |
| Bucaramanga | Sensores de cuartos fríos | 10.35.1.0/24 | VPN site-to-site |
| Pereira | Usuarios del centro | 10.36.0.0/24 | VPN site-to-site |
| Pereira | Sensores de cuartos fríos | 10.36.1.0/24 | VPN site-to-site |
| Pasto | Usuarios del centro | 10.37.0.0/24 | VPN site-to-site |
| Pasto | Sensores de cuartos fríos | 10.37.1.0/24 | VPN site-to-site |
| Neiva | Usuarios del centro | 10.38.0.0/24 | VPN site-to-site |
| Neiva | Sensores de cuartos fríos | 10.38.1.0/24 | VPN site-to-site |

Los camiones no tienen subred corporativa. Salen por la red móvil del operador de flota.

Firewall actual. Un firewall de próxima generación en Cali hace enrutamiento, VPN site-to-site con los ocho centros, NAT del rastreo y las políticas entre las subredes de la tabla. Delante de Nginx hay un firewall de aplicaciones para la zona publicada y para la zona interna. Durante la convivencia este firewall sigue en pie. El diseño dice qué políticas se conservan, cuáles se trasladan y cuándo se apaga cada función.

Se pide:

- Conectividad entre el datacenter, los ocho centros y la nube, con ruta redundante al menos para la sede de Cali.
- Mantener el despacho fuera de internet público.

<!-- p. 4 -->

- Publicar el rastreo de forma controlada.
- Acceso administrativo para equipos distribuidos, sin abrir la red de despacho.
- Un punto de interconexión, DNS e identidad pensado para sumar otra nube en un horizonte de 24 meses.
- Tabla de subnetting de la nube, sin solapar el inventario on-premises. Como mínimo: ingreso, aplicación, datos, archivo, ingesta de telemetría, administración, integración con Cali y salida a Fabric. Desarrollo, pruebas y producción van en rangos distintos.
- Firewall de nube a implementar, además del firewall de Cali. La entrega incluye una tabla de políticas: origen, destino, puerto, acción y si la regla es temporal de la migración o queda en estado estable. El firewall de aplicaciones del rastreo forma parte de ese diseño.

### 4. Automatización y DevOps

- Infraestructura como código para el patrón de red, seguridad y un ambiente de aplicación. No hace falta materializar las ocho sedes una por una: sí el módulo reutilizable.
- Pipeline de integración y despliegue para la plataforma y para los contenedores de la aplicación.
- Ambientes de desarrollo, pruebas y producción, con promoción controlada.
- Gestión de secretos dentro del pipeline.
- Estrategia de cambio compatible con la ventana operativa descrita más abajo.
- Gestión del cambio con dos plantillas, una de aplicación y otra de infraestructura. Cada una se entrega llena con un ejemplo, no en blanco. La de aplicación corresponde a una salida del portal o de los servicios de despacho. La de infraestructura corresponde a un cambio de infraestructura como código: red, firewall, cómputo, datos o el corte del domingo. En ambas se lee qué cambia, la ventana, el impacto, la aprobación, cómo se avisa a despacho y a calidad, y cómo se vuelve atrás. Las notas de la versión salen de esa plantilla. No hay cambio productivo de aplicación ni de infraestructura entre las 04:00 y las 22:00, ni durante una campaña, salvo incidente.

### 5. Cargas de trabajo

#### Parte A. Plataforma de operación logística (nueva)

Consola interna de despacho y portal de rastreo para clientes corporativos.

- Front: aplicación web para despachadores y otra vista, acotada, para clientes que consultan sus guías.
- Servicios: guías, inventario de bodega, asignación de muelle y ruta, facturación corporativa.
- Datos: base relacional con alta disponibilidad y un caché para consultas de rastreo.
- Seguridad: autenticación fuerte en la consola interna, cifrado y protección del portal público.
- Continuidad: failover y un esquema de recuperación acorde al RPO y al RTO indicados abajo.

Cifras de referencia para dimensionar, no para copiar un tamaño de máquina:

- 450 usuarios internos.
- Unos 2.000 clientes corporativos habilitados en el portal.
- Pico ordinario del portal: cerca de 800 solicitudes por minuto.
- En campaña el pico del portal llega a 2.000 solicitudes por minuto durante unas cuatro horas.

#### Parte B. Telemetría de cadena de frío

Alertar cuando un camión o un cuarto frío sale del rango de temperatura, y conservar el historial para reclamos.

- Ingesta de sensores de temperatura, apertura de puerta y posición de la flota.
- Procesamiento de baja latencia para la alerta operativa.

<!-- p. 5 -->

- Almacenamiento analítico para historial, reclamos y reportes a clientes.
- Tableros para el equipo de calidad y una vista reducida para el cliente corporativo.

Cifras de referencia:

- 120 camiones en ruta, con lectura de temperatura cada 60 segundos y posición cada 30 segundos, en una jornada típica de 18 horas.
- 8 centros, 4 cuartos fríos por centro, lectura cada 30 segundos, las 24 horas.
- En campaña la flota en ruta sube a 180 camiones.
- La alerta de excursión de temperatura debe poder verse en menos de un minuto desde el evento, en condiciones normales de red.
- El despacho trabaja de 04:00 a 22:00. Los cuartos fríos y los camiones en ruta se vigilan las 24 horas. De noche, la alerta la recibe el turno de guardia de calidad, no la torre de control.

#### Parte C. Migración del núcleo que hoy está en el datacenter

La parte A es la plataforma de destino. La parte C es el camino para llegar a ella. Los módulos actuales no se quedan como un segundo sistema permanente.

- Plan de traslado de las aplicaciones y de sus datos. La convivencia entre el datacenter y la plataforma nueva dura como máximo 90 días. Al cierre se apaga esta carga en Cali.
- Qué se mueve tal como está durante la convivencia y qué se rehace en la plataforma nueva para no pagar los dos diseños.
- El corte de hasta 2 horas cubre el cambio de la base transaccional y del tráfico de despacho y rastreo. No cubre la copia de 1,2 PB: esa copia se siembra antes y el corte solo arrastra el diferencial.
- Estimación de costo del proyecto de migración y del costo mensual cuando la carga ya vive en la nube.
- Escenario de campaña. El 40 % más de cómputo es la hipótesis del negocio para la capa de aplicación. El portal se dimensiona con el pico de 2.000 solicitudes por minuto, no con ese porcentaje. La telemetría de campaña usa la flota de 180 camiones.

#### Detalle técnico del datacenter de origen

Sede nacional en Cali. Ocho centros regionales sin cómputo propio: solo red y sensores.

**Red.** Firewall perimetral, VPN site-to-site hacia cada centro, NAT y Nginx para el rastreo público, firewall de aplicaciones para la capa pública y la privada.

**Virtualización.** VMware, tres clústeres, dos hosts ESXi en cada uno.

Clúster de datos. Soporta las bases de la carga que se va a migrar.

- 1 VM de producción: MySQL 5.7 en CentOS 7. No hay réplica. El único respaldo es un volcado nocturno a la 01:00, guardado en el mismo clúster. Con eso, hoy no se cumple el RPO de 15 minutos.
- 1 VM de desarrollo: MySQL 5.7 en CentOS 7.
- 1 VM de pruebas: MySQL 5.7 en CentOS 7.
- 1 VM de caché: Redis 5 en CentOS 7.

Clúster de aplicación. Desarrollo, pruebas y producción comparten el clúster.

- 4 VM Ubuntu 20.04 con Docker. Producción usa dos VM; desarrollo y pruebas usan una cada una. La aplicación está modularizada en contenedores:
  - despacho
  - inventario
  - facturación corporativa

<!-- p. 6 -->

  - rastreo
  - evidencias
- 2 VM Ubuntu 22.04 con Nginx como proxy inverso.
- 2 VM Ubuntu 22.04 que sirven el front.

Clúster transversal.

- 1 VM CentOS 7 con FTP y un volumen NFS. Ahí están los 1,2 PB que hay que migrar, así repartidos:
  - 1,05 PB de video de muelles y de entregas. Objetos grandes.
  - 110 TB de fotos, comprobantes y PDF. La mayoría pesa menos de 2 MB.
  - 40 TB de archivos históricos de temperatura, los que hoy se cargan por lote.
- Crecimiento aproximado: 12 TB al mes, sobre todo video y fotos. Retención contractual de evidencias y de temperatura: 5 años. No hay copia de este volumen fuera de ese servidor.
- 1 VM Ubuntu 20.04 con Zabbix, usada para el monitoreo del núcleo actual.

**Condiciones de negocio que restringen el diseño.**

- El despacho opera de 04:00 a 22:00. El corte admisible para la migración productiva es de hasta 2 horas, en la madrugada de un domingo.
- RPO deseado de producción: 15 minutos. RTO deseado: 4 horas.
- El equipo de desarrollo puede adaptar la aplicación si la plataforma lo exige. Esas adaptaciones se piden y se justifican; no se implementan en este reto.
- Antes de la sustentación hay una sesión de aclaraciones de 30 minutos. El docente representa al cliente.

### 6. Observabilidad

- Salud de cómputo, contenedores, bases, almacenamiento y enlaces hacia Cali y hacia los centros regionales.
- Señales de seguridad y cómo se integran con la operación.
- Métricas, registros y trazas de los servicios de despacho, rastreo e ingesta.
- Dos objetivos de nivel de servicio, con su indicador: disponibilidad del portal de rastreo y oportunidad de la alerta de temperatura.
- Tableros de operación y de costo.
- Transición desde Zabbix: qué sigue cubriendo durante la migración y qué se apaga al final.

### 7. Inteligencia artificial de la torre de control, sobre Microsoft Fabric

Esta estrategia es adicional al diseño de plataforma. No lo reemplaza. La nube principal de cómputo, red y migración la sigue eligiendo quien presenta. La torre de control, el turno de calidad y la vista analítica del cliente corporativo consumen inteligencia artificial a través de Microsoft Fabric.

No se pide entrenar ni desplegar un modelo propio. Se pide la estrategia de Fabric para estos tres usos:

- Aviso temprano de excursión de temperatura o de sensor caído, incluido el turno de noche de calidad.
- Estimación de hora de llegada a partir de posición e historial de ruta, visible en la torre de control.
- Apoyo al archivo de evidencias: marcar fotos ilegibles o con carga visiblemente dañada. El video de 1,05 PB no se analiza completo; la estrategia dice qué muestra entra y cuál se queda en el archivo.

La estrategia debe cubrir:

- Espacios de trabajo, capacidades y quién de FríoAndes las administra, separados de la organización de la nube principal si no es Azure.

<!-- p. 7 -->

- Cómo llegan a Fabric el libro operativo, la telemetría y el archivo histórico. El camino por defecto no es una segunda copia de 1,2 PB. Si se copia una parte, se dice cuál, por qué y qué cuesta.
- Región de Fabric y residencia de los datos personales de conductores y destinatarios.
- Acceso de la torre de control, de calidad y del cliente corporativo, con mínimo privilegio. El cliente no ve la flota completa ni el video.
- Cómo se observa el flujo y cómo se apaga o se reduce la capacidad cuando no hay campaña.
- Costo de la capacidad de Fabric aparte del costo de la plataforma, en mes normal y en mes de campaña.

Si un uso no se recomienda en el primer release, sustentarlo. La decisión de despacho sigue siendo de la torre de control.

### 8. Sistema de diseño

FríoAndes no tiene manual de marca. Hay que crearlo para la torre de control y para el portal de rastreo, de modo que las dos superficies se reconozcan como la misma empresa.

El sistema de diseño incluye, como mínimo:

- Logo principal, isotipo y versiones en una tinta y en negativo. El logo se usa en la torre, en el portal y en las notas de versión.
- Paleta: color primario, secundarios, neutros y los estados de la operación (normal, advertencia, excursión de temperatura, sensor sin señal).
- Tipografía para interfaz y para documentos, con jerarquía de títulos, texto y datos numéricos.
- Espaciado, grilla y radio de las superficies.
- Componentes base: botón, campo, alerta, tarjeta de guía y distintivo de temperatura. Cada uno con estado normal, foco y deshabilitado.
- Reglas de uso: qué se puede cambiar y qué no, contraste suficiente para la torre en turno de noche, y cómo se presenta el cliente corporativo sin mostrar la flota completa.

No se pide construir la aplicación. Se pide el sistema con el que después se construiría. La entrega es una lámina o un documento donde cada decisión se ve aplicada, no solo nombrada.

## Tareas

1. **Arquitectura.** Documento que recorra los ocho puntos del reto, con diagramas de gobierno, red, seguridad, ambientes, cargas nuevas, migración, observabilidad, la estrategia de Fabric y el sistema de diseño. Incluye la tabla de subnetting cloud y la tabla de políticas del firewall de nube.
2. **Infraestructura como código.** Repositorio con el patrón repetible de un ambiente (red, seguridad base y al menos un componente de cómputo o de ingesta). El código debe poder planearse. No es necesario desplegar las ocho sedes, la flota ni la capacidad de Fabric.
3. **Costo.** Estimación del proyecto de migración, incluida la siembra de 1,2 PB, y del mes de operación en estado estable, más el escenario de campaña. La capacidad de Fabric va en línea aparte. Cada cifra lleva el supuesto que la sostiene (región, tamaño, horas, retención, transferencia, medio usado para mover el archivo).
4. **Cambio.** Plantilla de release notes de aplicación y plantilla de release notes de infraestructura, cada una con un ejemplo diligenciado.
5. **Sustentación.** Informe breve y presentación para un arquitecto cloud del cliente. Duración objetivo de la exposición: 20 minutos, más preguntas.

<!-- p. 8 -->

## Criterios

1. Estrategia completa y coherente con las restricciones de despacho, datos personales y retención.
2. Viabilidad técnica: tamaños, continuidad y crecimiento de campaña salen de las cifras del caso, no de un diagrama genérico.
3. Automatización y cambio: lo entregado en código coincide con lo dibujado, y las dos plantillas permiten aprobar, avisar y volver atrás.
4. Seguridad y cumplimiento: identidades, segmentación, firewall de nube alineado al inventario, cifrado, auditoría y datos personales.
5. Costo: supuestos visibles, siembra del archivo, capacidad de Fabric y al menos tres decisiones que bajan o evitan gasto.
6. Estrategia de Fabric usable por la torre de control, sin duplicar por defecto el archivo de 1,2 PB.
7. Sistema de diseño aplicado: logo, paleta, tipografía, componentes y reglas de uso de la torre y del portal.
8. Claridad de la sustentación frente a un arquitecto cloud.

## Entrega

- Diagramas (PDF o fuente editable).
- Repositorio Git con la infraestructura como código.
- Plantilla de release notes de aplicación y plantilla de release notes de infraestructura, cada una con un ejemplo diligenciado.
- Documento de costos con supuestos.
- Presentación de sustentación.
- Sistema de diseño de FríoAndes: logos, paleta, tipografía, componentes y reglas de uso.

## Alcance y reglas

- La nube principal la elige quien presenta. La segunda nube se diseña como preparación, no como una copia completa. Microsoft Fabric es obligatorio para la inteligencia artificial de la torre de control, aunque la nube principal no sea Azure.
- Se puede asumir lo que falte, siempre que el supuesto quede escrito.
- El trabajo cubre la plataforma y el sistema de diseño. Queda fuera escribir el código de negocio de despacho, inventario o facturación, y queda fuera construir la aplicación.
- La audiencia de la sustentación es un arquitecto cloud, no un comité comercial.
- El mismo enunciado aplica al perfil Junior DevOps y al perfil Senior DevOps.

---

*Universidad Icesi · Material de clase · Junior DevOps y Senior DevOps · Caso FríoAndes*

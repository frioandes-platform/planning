# Visión general de la arquitectura

FríoAndes opera la cadena de frío de alimentos desde un datacenter en Cali, con ocho centros regionales, 120 camiones y una torre de control que despacha de 04:00 a 22:00. Este documento propone la plataforma que la reemplaza en Azure: una plataforma logística nueva, la telemetría de temperatura y ubicación en tiempo cercano al real, la migración del núcleo y del archivo de 1,2 PB sin detener el despacho, y una estrategia de Microsoft Fabric para que la torre de control use inteligencia artificial. Este capítulo muestra la solución en una sola vista y dice dónde se desarrolla cada parte.

## Contenido

1. Punto de partida
2. La solución en una vista
3. Decisiones principales
4. Cifras que dimensionan el diseño
5. Alineación con Well-Architected
6. Costo
7. Cómo leer este documento

---

## 1. Punto de partida

| Hoy | Qué exige el reto |
|---|---|
| Un datacenter en Cali con VMware, tres clústeres y desarrollo, pruebas y producción en el mismo clúster de aplicación | Ambientes separados, con promoción controlada y código de infraestructura |
| Un firewall en Cali concentra políticas, VPN con los centros y NAT del rastreo; internet de 400 Mbps simétricos, sin enlace dedicado a una nube | Ruta redundante para Cali, despacho fuera de internet y un firewall de nube con tabla de políticas |
| Temperatura cargada por lote; sin alerta en tiempo real | Alerta de excursión visible en un minuto, de día en la torre y de noche en la guardia de calidad |
| Archivo de 1,2 PB en FTP y NFS (1,05 PB de video), que crece 12 TB al mes | Llevarlo a la nube sin copiarlo por un enlace de 400 Mbps y sin duplicarlo en Fabric |
| Zabbix vigila la plataforma | Observabilidad de nube con dos objetivos de servicio y transición desde Zabbix |
| Campañas de fin de año, Semana Santa y mitad de año en las que el despacho se degrada | Crecer en campaña y no hacer cambios productivos durante ella ni de 04:00 a 22:00 |
| Sin manual de marca | Un sistema de diseño común a la torre y al portal |

La convivencia entre Cali y la nube dura como máximo 90 días y termina con Cali apagada. Las evidencias de entrega y la trazabilidad de temperatura se conservan cinco años por contrato.

---

## 2. La solución en una vista

![FríoAndes en Azure: la solución completa, con los ocho puntos del reto numerados](diagramas/solucion-vista-general.drawio.png)

El número de cada recuadro es el punto del reto y el capítulo de este documento que lo desarrolla:

1. **Gobierno.** Un tenant de Entra ID y un grupo de administración `mg-frioandes` con cinco suscripciones: seguridad, conectividad, producción, pruebas y desarrollo. Azure Policy, etiquetas y presupuestos se aplican desde ahí, y cada costo se asigna a operación, telemetría, pruebas o Fabric. La auditoría guarda cinco años de accesos a datos de clientes, evidencias y temperatura.
2. **Seguridad.** Mínimo privilegio por grupo, MFA para administradores y para la consola de despacho, PIM para los cambios productivos, un Key Vault por ambiente y cifrado en tránsito y en reposo. Los datos personales de conductores y destinatarios tienen dueño, plazo y lugar; el portal tiene límites de solicitudes para el pico de campaña y Defender for Cloud detecta la actividad anómala.
3. **Red híbrida.** Hub y spoke en East US 2: el hub tiene el VPN Gateway, el Azure Firewall, el DNS Private Resolver y Bastion. Cali se conecta por dos proveedores y cada centro directo a Azure. La torre solo se alcanza desde la red corporativa y el portal solo por el WAF. Las direcciones no se solapan con Cali, y el hub, el DNS y la identidad quedan listos para una segunda nube.
4. **Automatización.** Terraform y GitHub Actions despliegan los tres ambientes desde el mismo código, con OIDC, aprobación para producción y un bloqueo que impide desplegar de 04:00 a 22:00 o en campaña. Dos plantillas de release notes, una de aplicación y otra de infraestructura, gobiernan cada cambio.
5. **Cargas.** La torre y el portal corren en Container Apps sobre MySQL Flexible Server 8.4 con alta disponibilidad zonal y réplica en Central US. La telemetría entra por IoT Hub en Central US y Stream Analytics genera la alerta. El núcleo se migra con DMS en línea y un corte de 2 horas un domingo; el archivo llega en 71 discos con Import/Export y una copia continua cubre lo nuevo.
6. **Observabilidad.** Azure Monitor y Log Analytics recogen la salud de la plataforma y de los enlaces, las trazas de despacho, rastreo e ingesta, y las señales de seguridad. Dos objetivos de servicio: el portal y la alerta de temperatura. Zabbix sigue vigilando Cali hasta el día 61.
7. **Fabric.** Una capacidad F16 en East US 2. Fabric lee la base con un Copy Job incremental y el archivo con accesos directos, sin una segunda copia de 1,2 PB. Tres usos en el primer release: aviso temprano de excursión o sensor caído, hora estimada de llegada y fotos ilegibles o dañadas.
8. **Sistema de diseño.** Logo, paleta con los estados de la operación, tipografía, componentes y reglas de uso para la torre de noche, el portal de día y las notas de versión.

---

## 3. Decisiones principales

| Decisión | Por qué | Capítulo |
|---|---|---|
| Azure, con East US 2 como región principal y Central US como pareja | Fabric es obligatorio y vive en Azure; East US 2 dio la mejor latencia medida desde Cali | 3 |
| Cinco suscripciones bajo un solo grupo de administración | Separa seguridad, red, producción y no productivo sin multiplicar directorios | 1 |
| Hub y spoke con Azure Firewall Standard y el WAF en paralelo | Un solo punto de control para todo lo que no es el portal, y el WAF delante del único servicio público | 3 |
| Centros directo a Azure por su propia VPN, con la VPN hacia Cali de respaldo hasta el día 56 | Los centros no dependen de Cali cuando Cali se apaga | 3 |
| Container Apps para la torre y el portal, con Kubernetes como variante documentada | Menos operación para el mismo patrón de red; la red reserva el espacio de la variante | 5 |
| IoT Hub en Central US | Es la región pareja con zonas de disponibilidad para IoT Hub; la alerta es crítica | 5 |
| Siembra del archivo con discos (Import/Export) y no por la red | Copiar 1,2 PB por 400 Mbps tardaría más de nueve meses y competiría con la operación | 5 |
| Un solo corte, el domingo 14 de febrero de 2027, con 21 días para volver atrás | Torre, portal y servicios comparten la base; cambiar por partes obligaría a sincronizar dos bases | 5 |
| Fabric sin copiar el archivo: accesos directos y solo lo que piden los usos | El camino por defecto no puede ser una segunda copia de 1,2 PB | 7 |
| Capacidad de Fabric con reducción fuera de campaña | Se mide el primer mes y se baja a F8 si el uso lo permite | 7 |

---

## 4. Cifras que dimensionan el diseño

| Cifra | Valor | Dónde pesa |
|---|---|---|
| Usuarios internos | 450, unos 180 en los centros (supuesto) | Torre, VPN, licencias |
| Clientes corporativos | Unos 2.000 | Portal e identidades externas |
| Portal | 800 solicitudes por minuto en pico normal, 2.000 en campaña durante unas 4 horas | WAF, Application Gateway, réplicas |
| Camiones | 120, 180 en campaña | Telemetría |
| Cuartos fríos | 32 en 8 centros | Telemetría y alertas |
| Mensajes de telemetría | Unos 486.000 al día, 682.000 en campaña | IoT Hub y Stream Analytics |
| Archivo | 1,2 PB (150 TB de documentos y 1.050 TB de video), más 12 TB al mes | Siembra, almacenamiento y Fabric |
| Retención | Cinco años para evidencias, temperatura y auditoría de accesos | Inmutabilidad y registros |
| Continuidad | RPO de 15 minutos y RTO de 4 horas | Réplica en Central US |
| Objetivos de servicio | Portal: 99,9 % de minutos buenos en 28 días. Alerta: 99 % visible en 60 segundos o menos | Observabilidad y guardia |
| Convivencia | Máximo 90 días; día 0 el 11 de enero de 2027 y Cali apagada el 14 de marzo | Migración |

---

## 5. Alineación con Well-Architected

El enunciado pide alinear la estrategia con los cinco pilares de un marco Well-Architected. Esta tabla dice qué decisiones del diseño cumplen cada pilar y dónde se desarrollan.

| Pilar | Qué lo cumple en este diseño | Capítulos |
|---|---|---|
| **Excelencia operacional** | Todo se despliega desde Terraform y GitHub Actions, con los mismos módulos en los tres ambientes; cambios solo de 22:00 a 04:00 y fuera de campaña, con release note, aprobación y vuelta atrás; observabilidad con alertas por guardia, tableros de operación y la transición desde Zabbix probada; un ensayo completo del corte antes del corte real | 4, 5 (Parte C), 6 |
| **Seguridad** | Identidades de Entra ID con mínimo privilegio, MFA y PIM; segmentación por subred y NSG, Azure Firewall para todo lo que no es el portal y WAF delante del portal; cifrado en tránsito y en reposo con un Key Vault por ambiente; auditoría de accesos de cinco años; datos personales con dueño, plazo y lugar; Defender for Cloud | 1, 2, 3 |
| **Confiabilidad** | MySQL con alta disponibilidad zonal y réplica en Central US para un RPO de 15 minutos y un RTO de 4 horas; IoT Hub en la región con zonas; dos proveedores de internet en Cali y VPN directa de cada centro; un corte reversible con 21 días de Cali en espera; objetivos de servicio medidos en 28 días | 3, 5, 6 |
| **Eficiencia del rendimiento** | Tamaños calculados con las cifras del caso (800 y 2.000 solicitudes por minuto, 486.000 mensajes al día, 1,2 PB); escalado por calendario solo en la capa que crece en campaña; caché administrada; región elegida por latencia medida desde Cali; Fabric dimensionado por unidades de capacidad medidas | 3, 5, 7 |
| **Optimización de costos** | Siembra con discos en vez de copiar 1,2 PB por la red; Fabric sin una segunda copia del archivo; niveles Cool y Cold y LRS para el video; capacidad de Fabric reducida fuera de campaña; facturación interna por etiqueta y presupuestos por suscripción; cada cifra con su supuesto | 1, 5, 7 y el documento de costos |

---

## 6. Costo

El costo va en su propio documento (`docs/costs/costs-frioandes.pdf`), con cada cifra trazable a su supuesto:

| Concepto | USD | Fuente |
|---|---|---|
| Costos únicos del proyecto: equipo por rol y fase, capacitación, consultoría, migración y 15 % de contingencia | 419.354,89 | `docs/costs/costo-total-proyecto.md` |
| De ellos, la migración con la siembra del archivo | 153.417,32 | `docs/costs/costo-migracion.md` |
| Mes estable de la nube, con el archivo (mes 1) | 17.239,76 | `docs/costs/costo-mes-estable-y-campana.md` |
| Fabric, mes normal y mes de campaña | 2.891,89 y 2.938,13 | `docs/costs/costo-fabric.md` |
| Costo total de propiedad a 1, 3 y 5 años | 864.359,86, 1.748.583,59 y 2.625.095,25 | `docs/costs/costo-total-proyecto.md` |

Las 25 decisiones de diseño que bajan el costo, con su costo evitado, están en `docs/costs/decisiones-ahorro.md`.

---

## 7. Cómo leer este documento

Los capítulos siguen los ocho puntos del reto. Cada uno reúne los documentos de diseño de su tema tal como están en el repositorio, con sus diagramas, tablas y supuestos.

| Capítulo | Punto del reto | Documentos |
|---|---|---|
| 1 | Gobierno de la plataforma | Landing zone; auditoría, retención y facturación interna |
| 2 | Seguridad | IAM, MFA y cifrado; datos personales, perímetro y detección |
| 3 | Red híbrida y segunda nube | Topología y subnetting (con la tabla de subnetting); firewall de nube y publicación del rastreo (con la tabla de políticas); acceso remoto y segunda nube |
| 4 | Automatización y DevOps | Ambientes, pipeline, secretos y estrategia de cambio |
| 5 | Cargas de trabajo | Plataforma logística (Parte A); telemetría (Parte B); migración del núcleo y siembra del archivo (Parte C) |
| 6 | Observabilidad | Observabilidad, objetivos de servicio y transición desde Zabbix |
| 7 | Inteligencia artificial sobre Microsoft Fabric | Espacios, ingesta y región; acceso, usos de IA y capacidad |
| 8 | Sistema de diseño | Logo y paleta |
| 9 | Cronograma | Cronograma general del proyecto |
| Anexo | Supuestos | Registro de supuestos de todo el diseño |

Cuando un documento cita otro archivo del repositorio (un CSV, un script o un documento de costos), el nombre aparece en `letra de código`. Lo necesario para leer el diseño está dentro de este documento; esos archivos son la fuente que verifica las tablas.

# Verificación de la tabla de políticas del firewall de nube

Resultado: **aprobada** (12 de 12 comprobaciones).

- Archivo: `firewall-policy.csv`, 72 reglas.
- SHA-256: `fdbfa737323e5d4789a439dae5e22e5ab7799cc009c0eecc82016320b5163bad`
- Por punto de control: azure-firewall 30, iot-hub 1, nsg 39, waf 2.
- Por vigencia: estable 61, temporal 11.

| Comprobación | Resultado |
|---|---|
| Cada regla tiene sus campos, una vigencia válida y, si es temporal, cuándo se retira | Cumple |
| Identificadores únicos | Cumple |
| Todos los rangos existen en `ip-plan.csv` o en el inventario on-premises | Cumple |
| La torre solo recibe tráfico de las redes corporativas | Cumple |
| Ninguna regla conecta producción, pruebas y desarrollo entre sí | Cumple |
| Los sensores reales solo llegan a producción (pruebas y desarrollo usan datos simulados) | Cumple |
| El gateway de Fabric no tiene salida a internet | Cumple |
| Están todos los flujos del diseño | Cumple |
| El firewall y los NSG terminan en denegar | Cumple |
| Las reglas temporales del firewall están en grupos que se borran completos | Cumple |
| El firewall traduce el origen hacia los endpoints privados (la respuesta vuelve por el mismo camino) | Cumple |
| Las reglas de red no usan nombres de dominio sin proxy DNS | Cumple |

## Reglas temporales y cuándo se retiran

| Regla | Punto de control | Origen | Destino | Se retira |
|---|---|---|---|---|
| FW-401 | azure-firewall | Usuarios de los centros | Torre y portal actuales en Cali | Al cerrar el plazo de vuelta atrás del corte (como máximo el día 90) |
| FW-402 | azure-firewall | Equipos de los centros que envían los históricos de temperatura | Servidor de archivo de Cali (FTP) | Cuando la telemetría en línea reemplaza la carga por lote del centro (como máximo el día 90) |
| FW-501 | azure-firewall | Servicio de migración de la base | Base de datos de Cali | En el corte, cuando termina la replicación hacia Azure |
| FW-502 | azure-firewall | Servicio de migración de la base | Cuenta de almacenamiento de la migración | En el corte, junto con la cuenta y su token |
| FW-503 | azure-firewall | Servidores de aplicación de Cali | Integración con Cali | Al cerrar el plazo de vuelta atrás (como máximo el día 90) |
| FW-504 | azure-firewall | Integración con Cali | Servidores de aplicación de Cali | Al cerrar el plazo de vuelta atrás (como máximo el día 90) |
| FW-505 | azure-firewall | Base de datos de Cali | Base de datos en Azure | Al cerrar el plazo de vuelta atrás (como máximo el día 90) |
| NSG-prod-11 | nsg | Servidor de archivo de Cali | Archivo y evidencias | Al terminar la copia continua del archivo (como máximo el día 90) |
| NSG-prod-12 | nsg | Servicio de migración de la base | Base de datos | En el corte, cuando termina la replicación hacia Azure |
| NSG-prod-13 | nsg | Base de datos de Cali | Base de datos | Al cerrar el plazo de vuelta atrás (como máximo el día 90) |
| NSG-prod-14 | nsg | Servidores de aplicación de Cali | Integración con Cali | Al cerrar el plazo de vuelta atrás (como máximo el día 90) |

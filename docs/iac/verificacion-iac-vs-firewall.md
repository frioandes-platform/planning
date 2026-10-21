# Verificación de IaC frente a la tabla del firewall

## 1. Alcance y versión revisada

Historia: [#21](https://github.com/frioandes-platform/planning/issues/21). Ambiente de referencia: **dev**.

- Código IaC revisado: commit `ba083b0e5d802527b13b09e679ab8f4c5037952d` de `frioandes-platform/iac`.
- Base de red corregida: commit `80bce9aecfe653a6c81b8eda41d1473421325373`, PR [iac#2](https://github.com/frioandes-platform/iac/pull/2), correspondiente a #20.
- Tabla y ajustes: commit `bcb98b538ac7df7f8733c7ed949cef9290d650bc` de `frioandes-platform/planning`.
- El commit IaC identificado debe publicarse sin modificar su contenido para que la referencia pueda consultarse en GitHub. Si se cambia o se recrea el commit, regenerar este informe.

Se revisa un firewall compartido en conectividad y los NSG de aplicación. Para dev hay 11 filas explícitas estables de Azure Firewall, FW-999 como denegación implícita y 14 filas estables de NSG. El cierre de NSG se materializa en 11 subredes: 24 recursos de regla en dev.

La tabla contiene 100 filas: 41 de Azure Firewall, 47 de NSG, 10 de WAF y 2 de IoT Hub/DPS. La sección 6 clasifica todas; no afirma que WAF, DNS e IoT estén desplegados por este módulo.

## 2. Fuentes y trazabilidad

Los CSV originales se conservan en `modules/security/data`, con SHA-256 y Git blob en `source.json`. La revisión verifica ambos. La copia de `ip-plan.csv` de #20 es idéntica en bytes a la de seguridad: ambas usan la corrección de comillas de planning #64. Se conservan las entradas, salidas, nombres, CIDR y delegaciones del módulo de red.

| Archivo | SHA-256 |
|---|---|
| `firewall-policy.csv` | `3f3e8359f220968fa873ee3fc050c44ac860f7cdb079db5858f9a3a489f7684a` |
| `firewall-settings.csv` | `c41ed2e0a2259101486961cfbc535c5bbfd9cc027bae5d7de8b08a8bdb45001d` |
| `ip-plan.csv` | `a520eba842e6d7781705613d539fcfd018bfd00481f3842814d07d97036b91a0` |

## 3. Resultado y límites de la evidencia

**Resultado: sin discrepancias** entre los recursos de los planes simulados revisados y las filas aplicables de la tabla, para los escenarios declarados.

El comparador examinó respectivamente [11, 34, 40, 14, 14, 14, 17] identificadores explícitos de origen en los siete escenarios de firewall/NSG. FW-999 se representa mediante la denegación implícita.

Comprobaciones realizadas:

- Integridad y estructura de los tres CSV: correctas.
- Copias de `ip-plan.csv` de red y seguridad idénticas en bytes y SHA-256; la divergencia entre módulos se rechaza.
- Verificador de diseño de #9: 12 de 12 comprobaciones aprobadas sobre las 100 filas.
- Python: 17 pruebas aprobadas (7 de red y 10 del comparador/procedencia de seguridad). Los planes utilizados en las pruebas unitarias del comparador son fixtures sintéticos.
- `terraform fmt -check -recursive`: aprobado.

La ejecución completa de #20, registrada en `VALIDATION.md` y confirmada en Ubuntu sobre el commit base, corresponde al módulo de red. No se reutiliza como prueba de `validate` o `test` del código añadido en #21.


No se ejecutó un plan autenticado ni un apply. Las credenciales, cuotas, disponibilidad regional, tráfico de plataforma de cada servicio, rutas, DNS, peering, diagnósticos y conectividad efectiva requieren su propia implementación y prueba. No se infiere aislamiento operativo de un plan simulado.

## 4. Traducciones y discrepancias evitadas o corregidas

1. **FW-999 no es una regla de red `Deny *`.** Las reglas de red se procesan antes que las de aplicación; un cierre explícito global bloquearía los permisos de aplicación. Se conserva la denegación implícita del diseño y se documentan las reglas de infraestructura y el retorno con estado propios de Azure.
2. **HTTP y HTTPS se emparejan con su puerto.** En FW-306/312/318 se crean HTTP/80 y HTTPS/443, sin abrir HTTPS/80 por producto cartesiano.
3. **Cada punto de control conserva su lugar.** NSG se implementa como NSG; WAF e IoT no se trasladan al firewall de red. El cierre NSG-*-99 se expande a cada subred y queda antes de los permisos predeterminados de Azure.
4. **SNAT conserva exactamente la lista aprobada.** No se sustituye por `10.0.0.0/8` ni por todos los rangos privados, porque eso cambiaría el retorno desde los endpoints privados.
5. **Los marcadores se resuelven expresamente.** Los FQDN, IP públicas y puertos todavía no confirmados se reciben como entradas. El código rechaza marcadores seleccionados sin resolver y sustituciones de tokens fijos o comodines globales. Las fixtures usan dominios e IP ficticios y no configuran producción.
6. **No se triplica el firewall.** El root de conectividad crea uno; los NSG se gestionan desde la suscripción y estado de cada ambiente.
7. **Temporales desactivadas por defecto.** Se seleccionan por ID y exigen referencia de cambio. Los nombres de las colecciones/grupos y las descripciones distinguen `temporary` de `stable`. El registro conserva el retiro de cada regla.

Estas decisiones son traducciones explícitas de la tabla y correcciones del riesgo de implementación; no se modifica la política de negocio ni se añaden permisos silenciosamente.

## 5. Revisión detallada de las filas estables de dev

| ID | Punto | Origen | Destino | Protocolo | Puerto | Acción | Contraparte |
|---|---|---|---|---|---|---|---|
| `FW-203` | `azure-firewall` | `10.20.0.0/24` | `10.103.1.0/25` | `TCP` | `443` | `Permitir` | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-203` |
| `FW-313` | `azure-firewall` | `10.103.1.0/25 10.103.1.128/25` | `fqdn:mcr.microsoft.com fqdn:*.data.mcr.microsoft.com fqdn:packages.aks.azure.com fqdn:acs-mirror.azureedge.net` | `HTTPS` | `443` | `Permitir` | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-313` |
| `FW-314` | `azure-firewall` | `10.103.1.0/25 10.103.1.128/25 10.103.3.0/27` | `fqdn:*.identity.azure.net fqdn:login.microsoftonline.com fqdn:*.login.microsoftonline.com fqdn:*.login.microsoft.com fqdn:login.microsoft.com` | `HTTPS` | `443` | `Permitir` | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-314` |
| `FW-315` | `azure-firewall` | `10.103.1.0/25 10.103.1.128/25 10.103.2.128/27` | `fqdn:<registro>.azurecr.io fqdn:*.blob.core.windows.net` | `HTTPS` | `443` | `Permitir` | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-315` |
| `FW-316` | `azure-firewall` | `10.103.1.0/25 10.103.1.128/25 10.103.3.0/27` | `tag:AzureMonitor` | `TCP` | `443` | `Permitir` | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-316` |
| `FW-317` | `azure-firewall` | `10.103.1.0/25 10.103.1.128/25` | `fqdn:<dominios-del-proveedor>` | `HTTPS` | `443` | `Permitir` | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-317` |
| `FW-318` | `azure-firewall` | `10.103.2.128/27` | `fqdn:management.azure.com fqdn:login.microsoftonline.com fqdn:packages.microsoft.com fqdn:azure.archive.ubuntu.com fqdn:security.ubuntu.com fqdn:<dominios-github-ejecutores>` | `HTTPS HTTP` | `443 80` | `Permitir` | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-318` |
| `FW-321` | `azure-firewall` | `10.103.3.0/27` | `fqdn:*.api.powerplatform.com fqdn:*.logic.azure.com fqdn:<recurso>.communication.azure.com fqdn:<dominios-del-proveedor-sms>` | `HTTPS` | `443` | `Permitir` | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-321` |
| `FW-324` | `azure-firewall` | `10.103.1.0/25 10.103.1.128/25 10.103.3.0/27` | `fqdn:*.ingest.monitor.azure.com` | `HTTPS` | `443` | `Permitir` | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-324` |
| `FW-327` | `azure-firewall` | `10.103.1.0/25` | `tag:PowerBI tag:Sql` | `TCP` | `1433` | `Permitir` | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-327` |
| `FW-330` | `azure-firewall` | `10.103.1.128/25` | `fqdn:api.powerbi.com` | `HTTPS` | `443` | `Permitir` | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-330` |
| `FW-999` | `azure-firewall` | `any` | `any` | `Cualquiera` | `any` | `Denegar` | Denegación implícita; salida `implicit_deny`. No se crea una regla de red global. |
| `NSG-dev-01` | `nsg` | `10.20.0.0/24` | `10.103.1.0/25` | `TCP` | `443` | `Permitir` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-01` |
| `NSG-dev-02` | `nsg` | `10.103.0.0/24` | `10.103.1.128/25` | `TCP` | `443` | `Permitir` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-02` |
| `NSG-dev-03` | `nsg` | `10.103.1.0/25 10.103.1.128/25 10.103.2.192/27 10.103.2.128/27` | `10.103.2.0/27` | `TCP` | `3306` | `Permitir` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-03` |
| `NSG-dev-04` | `nsg` | `10.103.1.0/25 10.103.1.128/25 10.103.2.128/27` | `10.103.2.32/27` | `TCP` | `10000` | `Permitir` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-04` |
| `NSG-dev-05` | `nsg` | `10.103.1.0/25 10.103.1.128/25 10.103.0.0/24 10.103.2.128/27` | `10.103.2.32/27` | `TCP` | `443` | `Permitir` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-05` |
| `NSG-dev-06` | `nsg` | `10.103.1.0/25 10.103.1.128/25 10.103.2.128/27 10.103.3.0/27` | `10.103.2.64/27` | `TCP` | `443` | `Permitir` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-06` |
| `NSG-dev-07` | `nsg` | `10.100.0.64/26` | `10.103.2.96/27` | `TCP` | `8883 5671 443` | `Permitir` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-07` |
| `NSG-dev-08` | `nsg` | `10.100.0.192/26` | `10.103.2.128/27` | `TCP` | `22 3389` | `Permitir` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-08` |
| `NSG-dev-11` | `nsg` | `10.103.3.0/27` | `10.103.1.0/25` | `TCP` | `443` | `Permitir` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-11` |
| `NSG-dev-12` | `nsg` | `10.103.1.0/25` | `10.103.2.32/27` | `TCP` | `5671 443` | `Permitir` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-12` |
| `NSG-dev-13` | `nsg` | `10.103.3.0/27` | `10.103.2.32/27` | `TCP` | `5671 443` | `Permitir` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-13` |
| `NSG-dev-99` | `nsg` | `any` | `any` | `Cualquiera` | `any` | `Denegar` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-99`; cierre expandido por subred |
| `NSG-dev-09` | `nsg` | `<ip-publicas-cali> <ip-salida-firewall>` | `10.103.0.0/24` | `TCP` | `443 80` | `Permitir` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-09` |
| `NSG-dev-10` | `nsg` | `tag:GatewayManager` | `10.103.0.0/24` | `TCP` | `65200-65535` | `Permitir` | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-10` |

## 6. Cobertura y clasificación de todas las filas

Las reglas de otros ambientes tienen soporte de código donde se indica, pero no se incluyen silenciosamente en la política de referencia dev. Las temporales requieren selección expresa; las de producción no se aplican a dev. Las dos filas de DNS del hub, las diez de WAF y las dos de IoT/DPS quedan identificadas fuera del módulo y deben conciliarse en sus propias implementaciones.

| ID | Punto | Ambiente | Vigencia | Código o razón de exclusión |
|---|---|---|---|---|
| `FW-201` | azure-firewall | prod | estable | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-201` |
| `FW-202` | azure-firewall | test | estable | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-202` |
| `FW-203` | azure-firewall | dev | estable | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-203` |
| `FW-204` | azure-firewall | prod | estable | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-204` |
| `FW-301` | azure-firewall | prod | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-301` |
| `FW-302` | azure-firewall | prod | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-302` |
| `FW-303` | azure-firewall | prod | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-303` |
| `FW-304` | azure-firewall | prod | estable | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-304` |
| `FW-305` | azure-firewall | prod | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-305` |
| `FW-306` | azure-firewall | prod | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-306` |
| `FW-307` | azure-firewall | test | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-307` |
| `FW-308` | azure-firewall | test | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-308` |
| `FW-309` | azure-firewall | test | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-309` |
| `FW-310` | azure-firewall | test | estable | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-310` |
| `FW-311` | azure-firewall | test | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-311` |
| `FW-312` | azure-firewall | test | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-312` |
| `FW-313` | azure-firewall | dev | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-313` |
| `FW-314` | azure-firewall | dev | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-314` |
| `FW-315` | azure-firewall | dev | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-315` |
| `FW-316` | azure-firewall | dev | estable | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-316` |
| `FW-317` | azure-firewall | dev | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-317` |
| `FW-318` | azure-firewall | dev | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-318` |
| `FW-319` | azure-firewall | prod | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-319` |
| `FW-320` | azure-firewall | test | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-320` |
| `FW-321` | azure-firewall | dev | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-321` |
| `FW-322` | azure-firewall | prod | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-322` |
| `FW-323` | azure-firewall | test | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-323` |
| `FW-324` | azure-firewall | dev | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-324` |
| `FW-325` | azure-firewall | prod | estable | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-325` |
| `FW-326` | azure-firewall | test | estable | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-326` |
| `FW-327` | azure-firewall | dev | estable | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-327` |
| `FW-328` | azure-firewall | prod | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-328` |
| `FW-329` | azure-firewall | test | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-329` |
| `FW-330` | azure-firewall | dev | estable | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-330` |
| `FW-401` | azure-firewall | hub | temporal | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-401` |
| `FW-402` | azure-firewall | hub | temporal | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-402` |
| `FW-501` | azure-firewall | prod | temporal | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-501` |
| `FW-502` | azure-firewall | prod | temporal | `modules/security/main.tf`: `application_rule_collection` con nombre de regla `FW-502` |
| `FW-503` | azure-firewall | prod | temporal | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-503` |
| `FW-504` | azure-firewall | prod | temporal | `modules/security/main.tf`: `network_rule_collection` con nombre de regla `FW-504` |
| `FW-999` | azure-firewall | todos | estable | Denegación implícita; salida `implicit_deny`. No se crea una regla de red global. |
| `NSG-prod-01` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-01` |
| `NSG-prod-02` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-02` |
| `NSG-prod-03` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-03` |
| `NSG-prod-04` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-04` |
| `NSG-prod-05` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-05` |
| `NSG-prod-06` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-06` |
| `NSG-prod-07` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-07` |
| `NSG-prod-08` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-08` |
| `NSG-prod-15` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-15` |
| `NSG-prod-16` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-16` |
| `NSG-prod-17` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-17` |
| `NSG-prod-99` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-99`; cierre expandido por subred |
| `NSG-test-01` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-01` |
| `NSG-test-02` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-02` |
| `NSG-test-03` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-03` |
| `NSG-test-04` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-04` |
| `NSG-test-05` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-05` |
| `NSG-test-06` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-06` |
| `NSG-test-07` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-07` |
| `NSG-test-08` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-08` |
| `NSG-test-11` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-11` |
| `NSG-test-12` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-12` |
| `NSG-test-13` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-13` |
| `NSG-test-99` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-99`; cierre expandido por subred |
| `NSG-dev-01` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-01` |
| `NSG-dev-02` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-02` |
| `NSG-dev-03` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-03` |
| `NSG-dev-04` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-04` |
| `NSG-dev-05` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-05` |
| `NSG-dev-06` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-06` |
| `NSG-dev-07` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-07` |
| `NSG-dev-08` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-08` |
| `NSG-dev-11` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-11` |
| `NSG-dev-12` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-12` |
| `NSG-dev-13` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-13` |
| `NSG-dev-99` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-99`; cierre expandido por subred |
| `NSG-prod-11` | nsg | prod | temporal | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-11` |
| `NSG-prod-12` | nsg | prod | temporal | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-12` |
| `NSG-prod-14` | nsg | prod | temporal | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-14` |
| `NSG-hub-01` | nsg | hub | estable | Fuera del módulo de aplicación: NSG del DNS del hub; se integra con el resolver. |
| `NSG-hub-02` | nsg | hub | estable | Fuera del módulo de aplicación: NSG del DNS del hub; se integra con el resolver. |
| `NSG-prod-09` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-09` |
| `NSG-prod-10` | nsg | prod | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-prod-10` |
| `NSG-test-09` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-09` |
| `NSG-test-10` | nsg | test | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-test-10` |
| `NSG-dev-09` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-09` |
| `NSG-dev-10` | nsg | dev | estable | `modules/security/subnet-controls`: `azurerm_network_security_rule`, `NSG-dev-10` |
| `WAF-prod-01` | waf | prod | estable | Fuera del alcance dev: política WAF del portal de prod/test; no convertir a Azure Firewall. |
| `WAF-prod-02` | waf | prod | estable | Fuera del alcance dev: política WAF del portal de prod/test; no convertir a Azure Firewall. |
| `WAF-prod-03` | waf | prod | estable | Fuera del alcance dev: política WAF del portal de prod/test; no convertir a Azure Firewall. |
| `WAF-prod-04` | waf | prod | estable | Fuera del alcance dev: política WAF del portal de prod/test; no convertir a Azure Firewall. |
| `WAF-prod-05` | waf | prod | estable | Fuera del alcance dev: política WAF del portal de prod/test; no convertir a Azure Firewall. |
| `WAF-test-01` | waf | test | estable | Fuera del alcance dev: política WAF del portal de prod/test; no convertir a Azure Firewall. |
| `WAF-test-02` | waf | test | estable | Fuera del alcance dev: política WAF del portal de prod/test; no convertir a Azure Firewall. |
| `WAF-test-03` | waf | test | estable | Fuera del alcance dev: política WAF del portal de prod/test; no convertir a Azure Firewall. |
| `WAF-test-04` | waf | test | estable | Fuera del alcance dev: política WAF del portal de prod/test; no convertir a Azure Firewall. |
| `WAF-test-05` | waf | test | estable | Fuera del alcance dev: política WAF del portal de prod/test; no convertir a Azure Firewall. |
| `IOT-prod-01` | iot-hub | prod | estable | Fuera del alcance dev: TLS y credenciales de IoT Hub/DPS en producción, diseño #13. |
| `IOT-prod-02` | iot-hub | prod | estable | Fuera del alcance dev: TLS y credenciales de IoT Hub/DPS en producción, diseño #13. |

## 7. Reglas temporales y retiro

| ID | Grupo | Condición de retiro copiada de la fuente |
|---|---|---|
| `FW-401` | 400 transito-convivencia | Al cerrar el plazo de vuelta atrás del corte (como máximo el día 90) |
| `FW-402` | 400 transito-convivencia | Cuando la telemetría en línea reemplaza la carga por lote del centro (como máximo el día 90) |
| `FW-501` | 500 migracion | En el corte, cuando termina la replicación hacia Azure |
| `FW-502` | 500 migracion | En el corte, junto con la cuenta y su token |
| `FW-503` | 500 migracion | Al cerrar el plazo de vuelta atrás (como máximo el día 90) |
| `FW-504` | 500 migracion | Al cerrar el plazo de vuelta atrás (como máximo el día 90) |
| `NSG-prod-11` | nsg snet-archive | Al terminar la copia continua del archivo (como máximo el día 90) |
| `NSG-prod-12` | nsg snet-data | En el corte, cuando termina la replicación hacia Azure |
| `NSG-prod-14` | nsg snet-cali-integration | Al cerrar el plazo de vuelta atrás (como máximo el día 90) |

Terraform no programa la retirada por el paso del tiempo. El responsable debe quitar cada ID al alcanzar su hito, revisar el plan y aplicar la retirada por el proceso aprobado. La revisión no asume que todas las temporales se retiren simultáneamente.

## 8. Reproducir y completar la validación

Desde el commit IaC indicado, en la raíz de `iac`:

```bash
terraform fmt -recursive
bash scripts/check-security.sh
```

El script produce planes simulados JSON en `.security-verification/` y los compara contra las filas de referencia. No necesita autenticación de Azure. Para actualizar este documento con el resultado de esos planes:

```bash
python3 scripts/render_security_review.py \
  --plans-directory .security-verification \
  --out ../planning/docs/iac/verificacion-iac-vs-firewall.md
```

El generador rechaza planes con diferencias y requiere que el árbol de trabajo del código esté limpio. Si se modifica o reformatea el código, hacer commit y volver a ejecutar las comprobaciones antes de generar el informe. No registrar como verificado el SHA de un código anterior al cambio.

Los valores de pruebas no sustituyen las confirmaciones del cliente. Antes de desplegar, se completan las entradas reales y se comprueba que las reglas de plataforma necesarias para los servicios no queden bloqueadas por los cierres de NSG. La misma revisión se repite sobre el plan autenticado del despliegue aprobado.

## 9. Referencias

- [Tabla y diseño de firewall #9](../architecture/red-firewall-y-publicacion.md).
- [Plan de red #8](../architecture/red-topologia-subnetting.md).
- [Azure Firewall: orden de procesamiento](https://learn.microsoft.com/en-us/azure/firewall/rule-processing).
- [AzureRM 4.62.0: colecciones de reglas](https://registry.terraform.io/providers/hashicorp/azurerm/4.62.0/docs/resources/firewall_policy_rule_collection_group).

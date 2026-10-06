# Archivos de apoyo de la red híbrida

Datos, herramientas y reportes que respaldan [`../red-topologia-subnetting.md`](../red-topologia-subnetting.md) y [`../red-firewall-y-publicacion.md`](../red-firewall-y-publicacion.md). Todos los comandos se corren desde esta carpeta y solo necesitan Python 3.

## Contenido

| Carpeta | Archivo | Qué es |
|---|---|---|
| `data/` | `ip-plan.csv` | Plan de direcciones de la solución con Container Apps. Es la única fuente de los rangos: el código de Terraform debe leerlo directamente |
| `data/` | `ip-plan-aks.csv` | Plan de direcciones de la variante con Kubernetes (AKS) |
| `data/` | `onprem-inventory.csv` | Las 23 subredes on-premises actuales de Cali y los centros |
| `data/` | `azure-subnet-constraints.csv` | Nombres obligatorios y tamaños mínimos de subred que exige Azure, con su fuente |
| `data/` | `latency-targets.csv` | Un servidor de almacenamiento de Azure por región, para medir latencia |
| `data/` | `firewall-policy.csv` | Tabla de políticas del firewall de nube, los NSG, el WAF e IoT Hub, regla por regla y ambiente por ambiente. Es la única fuente para el módulo de seguridad de Terraform |
| `data/` | `firewall-settings.csv` | Configuración general del Azure Firewall: versión, inteligencia de amenazas, rangos sin traducción de origen, proxy DNS, IP públicas y grupos |
| `tools/` | `verify_ip_plan.py` | Verifica un plan contra el inventario on-premises y las reglas de Azure (12 comprobaciones) |
| `tools/` | `compare_tfplan.py` | Compara la salida de `terraform show -json` con el plan y la convierte al formato del plan |
| `tools/` | `measure_latency.py` | Mide la latencia TCP hacia cada región |
| `tools/` | `verify_firewall_policy.py` | Verifica la tabla de políticas contra el plan de direcciones y las reglas del diseño (12 comprobaciones) |
| `tools/` | `build_drawio_diagrams.py` | Genera los diagramas de draw.io de la red híbrida, las subredes, el firewall, la publicación del portal, la telemetría y los datos personales |
| `verification/` | `reporte-ip-plan.md` | Resultado de la verificación de `ip-plan.csv` |
| `verification/` | `reporte-ip-plan-aks.md` | Resultado de la verificación de `ip-plan-aks.csv` |
| `verification/` | `latencia-medida.md` | Resultados de la medición de latencia desde Cali |
| `verification/` | `reporte-firewall-policy.md` | Resultado de la verificación de `firewall-policy.csv` |

## Verificar el plan

```bash
python3 tools/verify_ip_plan.py --plan data/ip-plan.csv --out verification/reporte-ip-plan.md
sha256sum data/ip-plan.csv
# 2af88d980e4de7b6c83f0e5bf0f123c544d235a80017dc8e42fc109b5608be42
```

Si el hash cambia, el plan cambió: hay que volver a correr la verificación y actualizar el hash en el documento.

## Verificar el código de Terraform

```bash
terraform show -json plan.tfplan > plan.json
python3 tools/compare_tfplan.py --tfplan plan.json --plan data/ip-plan.csv --out-csv tf-ip-plan.csv
python3 tools/verify_ip_plan.py --plan tf-ip-plan.csv --out verification/reporte-terraform.md
```

`compare_tfplan.py` termina con código 0 solo si Terraform crea exactamente las redes y subredes del plan.

## Verificar la tabla de políticas del firewall

```bash
python3 tools/verify_firewall_policy.py --out verification/reporte-firewall-policy.md
sha256sum data/firewall-policy.csv
# a511cdd373e6012fe8dc85f9d51564e07a7aa775924ef60466187d7ec14e7891
```

El script lee `firewall-policy.csv`, `firewall-settings.csv`, `ip-plan.csv` y `onprem-inventory.csv`, y termina con código 0 solo si pasan las 12 comprobaciones. Si el hash cambia, la tabla cambió: hay que volver a correr la verificación y actualizar el hash en el documento del firewall.

## Medir la latencia

```bash
python3 tools/measure_latency.py --targets data/latency-targets.csv --place "Universidad en Cali, red cableada" --samples 30
```

## Regenerar los diagramas

Todos los diagramas se generan como archivos de draw.io (los de la red y las subredes leen `ip-plan.csv` e `ip-plan-aks.csv`) y se exportan a PNG con el diagrama incrustado, con draw.io de escritorio:

```bash
python3 tools/build_drawio_diagrams.py --out ../diagramas
drawio --disable-gpu -x -f png -e -b 20 -s 1 -o ../diagramas/NOMBRE.drawio.png ../diagramas/NOMBRE.drawio
```

Los diagramas de la red y las subredes se exportan con `-s 1` y los demás con `-s 1.5`, porque los primeros son más grandes.

# Archivos de apoyo de la red híbrida

Datos, herramientas y reportes que respaldan [`../red-topologia-subnetting.md`](../red-topologia-subnetting.md) y [`../red-firewall-y-publicacion.md`](../red-firewall-y-publicacion.md). Todos los comandos se corren desde esta carpeta y solo necesitan Python 3.

## Contenido

| Carpeta | Archivo | Qué es |
|---|---|---|
| `data/` | `ip-plan.csv` | Plan de direcciones de la solución con Container Apps. Es la única fuente de los rangos: el código de Terraform debe leerlo directamente |
| `data/` | `ip-plan-aks.csv` | Plan de direcciones de la variante con Kubernetes (AKS) |
| `data/` | `onprem-inventory.csv` | Las 23 subredes on-premises del enunciado |
| `data/` | `azure-subnet-constraints.csv` | Nombres obligatorios y tamaños mínimos de subred que exige Azure, con su fuente |
| `data/` | `latency-targets.csv` | Un servidor de almacenamiento de Azure por región, para medir latencia |
| `data/` | `firewall-policy.csv` | Tabla de políticas del firewall de nube, los NSG, el WAF e IoT Hub, regla por regla y ambiente por ambiente. Es la única fuente para el módulo de seguridad de Terraform |
| `data/` | `firewall-settings.csv` | Configuración general del Azure Firewall: versión, inteligencia de amenazas, rangos sin traducción de origen, proxy DNS, IP públicas y grupos |
| `tools/` | `verify_ip_plan.py` | Verifica un plan contra el inventario on-premises y las reglas de Azure (12 comprobaciones) |
| `tools/` | `compare_tfplan.py` | Compara la salida de `terraform show -json` con el plan y la convierte al formato del plan |
| `tools/` | `measure_latency.py` | Mide la latencia TCP hacia cada región |
| `tools/` | `build_lucid_diagrams.py` | Genera el JSON de importación de Lucidchart de los diagramas de la red |
| `tools/` | `verify_firewall_policy.py` | Verifica la tabla de políticas contra el plan de direcciones y las reglas del diseño (12 comprobaciones) |
| `tools/` | `build_drawio_diagrams.py` | Genera los diagramas de draw.io del firewall, la publicación del portal y la telemetría |
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
# 72fca57a76fbad427163f2890a2f060caf1cfa24e46005b2f3c2d7f7f0b32dad
```

El script lee `firewall-policy.csv`, `firewall-settings.csv`, `ip-plan.csv` y `onprem-inventory.csv`, y termina con código 0 solo si pasan las 12 comprobaciones. Si el hash cambia, la tabla cambió: hay que volver a correr la verificación y actualizar el hash en el documento del firewall.

## Medir la latencia

```bash
python3 tools/measure_latency.py --targets data/latency-targets.csv --place "Sede Cali" --samples 30
```

## Regenerar los diagramas

```bash
python3 tools/build_lucid_diagrams.py --variant container-apps --out red-8-lucid.json
python3 tools/build_lucid_diagrams.py --variant aks --out red-8-lucid-aks.json
```

El JSON se importa en Lucidchart con la importación estándar. Los documentos editables están enlazados al inicio del documento de red.

Los diagramas del firewall y de la telemetría se generan como archivos de draw.io y se exportan a PNG con el diagrama incrustado, con draw.io de escritorio:

```bash
python3 tools/build_drawio_diagrams.py --out ../diagramas
drawio --disable-gpu -x -f png -e -b 20 -s 1.5 -o ../diagramas/NOMBRE.drawio.png ../diagramas/NOMBRE.drawio
```

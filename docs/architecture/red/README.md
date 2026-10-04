# Archivos de apoyo de la red híbrida

Datos, herramientas y reportes que respaldan [`../red-topologia-subnetting.md`](../red-topologia-subnetting.md). Todos los comandos se corren desde esta carpeta y solo necesitan Python 3.

## Contenido

| Carpeta | Archivo | Qué es |
|---|---|---|
| `data/` | `ip-plan.csv` | Plan de direcciones de la solución con Container Apps. Es la única fuente de los rangos: el código de Terraform debe leerlo directamente |
| `data/` | `ip-plan-aks.csv` | Plan de direcciones de la variante con Kubernetes (AKS) |
| `data/` | `onprem-inventory.csv` | Las 23 subredes on-premises del enunciado |
| `data/` | `azure-subnet-constraints.csv` | Nombres obligatorios y tamaños mínimos de subred que exige Azure, con su fuente |
| `data/` | `latency-targets.csv` | Un servidor de almacenamiento de Azure por región, para medir latencia |
| `tools/` | `verify_ip_plan.py` | Verifica un plan contra el inventario on-premises y las reglas de Azure (12 comprobaciones) |
| `tools/` | `compare_tfplan.py` | Compara la salida de `terraform show -json` con el plan y la convierte al formato del plan |
| `tools/` | `measure_latency.py` | Mide la latencia TCP hacia cada región |
| `tools/` | `build_lucid_diagrams.py` | Genera el JSON de importación de Lucidchart de los diagramas |
| `verification/` | `reporte-ip-plan.md` | Resultado de la verificación de `ip-plan.csv` |
| `verification/` | `reporte-ip-plan-aks.md` | Resultado de la verificación de `ip-plan-aks.csv` |
| `verification/` | `latencia-medida.md` | Resultados de la medición de latencia desde Cali |

## Verificar el plan

```bash
python3 tools/verify_ip_plan.py --plan data/ip-plan.csv --out verification/reporte-ip-plan.md
sha256sum data/ip-plan.csv
# 652ed7ebbb7d9a67dbd010634f2bc96304fd63630228cb2ccde0d178b90075fd
```

Si el hash cambia, el plan cambió: hay que volver a correr la verificación y actualizar el hash en el documento.

## Verificar el código de Terraform

```bash
terraform show -json plan.tfplan > plan.json
python3 tools/compare_tfplan.py --tfplan plan.json --plan data/ip-plan.csv --out-csv tf-ip-plan.csv
python3 tools/verify_ip_plan.py --plan tf-ip-plan.csv --out verification/reporte-terraform.md
```

`compare_tfplan.py` termina con código 0 solo si Terraform crea exactamente las redes y subredes del plan.

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

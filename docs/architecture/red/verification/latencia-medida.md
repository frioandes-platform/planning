# Latencia medida desde Cali hacia las regiones candidatas

- **Origen:** la red cableada de una universidad en Cali. Es una aproximación de la latencia desde la ciudad: la sede de FríoAndes del caso es ficticia, así que la medición no usa su enlace de 400 Mbps. La decisión se mantiene mientras el resultado no cruce la regla del 30 %.
- **Método:** `tools/measure_latency.py`, con 30 conexiones TCP al puerto 443 por región y por ronda. El tiempo de conexión TCP equivale aproximadamente a un viaje de ida y vuelta.
- **Servidores:** los de `data/latency-targets.csv`, cuentas de almacenamiento de Azure ubicadas en cada región. Antes de medir se comprobó que los 7 resolvían por DNS y que sus direcciones pertenecen a los rangos oficiales de almacenamiento de cada región.
- **Cómo repetir la medición** (desde la carpeta `red/`):

```bash
python3 tools/measure_latency.py --targets data/latency-targets.csv --place "Universidad en Cali, red cableada" --samples 30
```

## Ronda 1

| Región | Host (IP) | Mínimo ms | Mediana ms | p90 ms | Fallos |
|---|---|---|---|---|---|
| eastus2 | s3eastus2.blob.core.windows.net (20.209.69.193) | 79.6 | 96.5 | 115.0 | 0 |
| centralus | s3centralus.blob.core.windows.net (20.60.240.168) | 94.6 | 110.8 | 162.2 | 0 |
| southcentralus | s3southcentralus.blob.core.windows.net (20.60.161.1) | 84.9 | 97.2 | 115.1 | 0 |
| eastus | s3eastus.blob.core.windows.net (135.130.108.129) | 80.2 | 89.0 | 125.1 | 0 |
| brazilsouth | s3brazilsouth.blob.core.windows.net (20.60.36.65) | 141.0 | 157.9 | 220.4 | 0 |
| mexicocentral | s3mexicocentral.blob.core.windows.net (20.60.97.1) | 104.6 | 114.7 | 128.5 | 0 |
| chilecentral | s3chilecentral.blob.core.windows.net (57.150.101.33) | 132.0 | 159.1 | 224.4 | 0 |

## Ronda 2

| Región | Host (IP) | Mínimo ms | Mediana ms | p90 ms | Fallos |
|---|---|---|---|---|---|
| eastus2 | s3eastus2.blob.core.windows.net (20.209.69.193) | 78.2 | 85.5 | 129.3 | 0 |
| centralus | s3centralus.blob.core.windows.net (20.60.240.168) | 94.1 | 105.2 | 125.9 | 0 |
| southcentralus | s3southcentralus.blob.core.windows.net (20.60.161.1) | 82.9 | 92.0 | 115.3 | 0 |
| eastus | s3eastus.blob.core.windows.net (135.130.108.129) | 80.5 | 95.5 | 180.3 | 0 |
| brazilsouth | s3brazilsouth.blob.core.windows.net (20.60.36.65) | 142.2 | 148.7 | 262.9 | 0 |
| mexicocentral | s3mexicocentral.blob.core.windows.net (20.60.97.1) | 103.9 | 120.3 | 132.5 | 0 |
| chilecentral | s3chilecentral.blob.core.windows.net (57.150.101.33) | 132.9 | 139.6 | 162.4 | 0 |

## Decisión

La regla, fijada antes de medir, mantiene East US 2 salvo que otra región tenga una mediana al menos 30 % menor, todos los servicios y un costo comparable. Ninguna región cumple el umbral: East US y South Central US se alternan con East US 2 entre rondas, y las regiones de Sudamérica miden entre 60 % y 75 % más. **Se mantiene East US 2, con Central US como región pareja.**

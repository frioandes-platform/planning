# Verificación del plan de direcciones de nube

- Fecha: 2026-10-04
- Plan verificado: `ip-plan.csv` (sha256 `652ed7ebbb7d`)
- Inventario on-premises: `onprem-inventory.csv` (23 subredes del enunciado)

## Resumen

| Comprobación | Resultado |
|---|---|
| El inventario on-premises tiene las 23 subredes del enunciado | Cumple |
| Todos los CIDR son válidos | Cumple |
| Ningún rango de nube se solapa con las 23 subredes on-premises | Cumple |
| La nube respeta la reserva de crecimiento on-premises (los /16 completos de Cali y los centros) | Cumple |
| Las redes virtuales de la nube no se solapan entre sí (dev, test y prod en rangos distintos) | Cumple |
| Cada subred está dentro de su red virtual | Cumple |
| Las subredes de la nube no se solapan entre sí | Cumple |
| Cada ambiente (prod, test, dev) tiene las 8 categorías mínimas | Cumple |
| Hay un bloque reservado para la segunda nube, libre de solapes | Cumple |
| Torre, portal, ingesta y analítica tienen subredes propias en cada ambiente | Cumple |
| Despacho fuera de internet: la única entrada pública de aplicación es el ingreso del portal | Cumple |
| Las subredes respetan los nombres y tamaños que exige Azure | Cumple |

## Detalle de problemas y avisos

Ninguno.

## Rango por rango contra las 23 subredes on-premises

| Rango de nube | Red virtual / subred | Resultado |
|---|---|---|
| `10.100.0.0/23` | `vnet-hub` | sin solapamiento |
| `10.100.0.0/26` | `vnet-hub/GatewaySubnet` | sin solapamiento |
| `10.100.0.64/26` | `vnet-hub/AzureFirewallSubnet` | sin solapamiento |
| `10.100.0.128/26` | `vnet-hub/AzureFirewallManagementSubnet` | sin solapamiento |
| `10.100.0.192/26` | `vnet-hub/AzureBastionSubnet` | sin solapamiento |
| `10.100.1.0/28` | `vnet-hub/snet-dns-inbound` | sin solapamiento |
| `10.100.1.16/28` | `vnet-hub/snet-dns-outbound` | sin solapamiento |
| `10.101.0.0/21` | `vnet-prod` | sin solapamiento |
| `10.101.0.0/24` | `vnet-prod/snet-ingress` | sin solapamiento |
| `10.101.1.0/25` | `vnet-prod/snet-app-torre` | sin solapamiento |
| `10.101.1.128/25` | `vnet-prod/snet-app-portal` | sin solapamiento |
| `10.101.2.0/27` | `vnet-prod/snet-data` | sin solapamiento |
| `10.101.2.32/27` | `vnet-prod/snet-data-pe` | sin solapamiento |
| `10.101.2.64/27` | `vnet-prod/snet-archive` | sin solapamiento |
| `10.101.2.96/27` | `vnet-prod/snet-ingest` | sin solapamiento |
| `10.101.2.128/27` | `vnet-prod/snet-admin` | sin solapamiento |
| `10.101.2.160/27` | `vnet-prod/snet-cali-integration` | sin solapamiento |
| `10.101.2.192/27` | `vnet-prod/snet-fabric-egress` | sin solapamiento |
| `10.102.0.0/21` | `vnet-test` | sin solapamiento |
| `10.102.0.0/24` | `vnet-test/snet-ingress` | sin solapamiento |
| `10.102.1.0/25` | `vnet-test/snet-app-torre` | sin solapamiento |
| `10.102.1.128/25` | `vnet-test/snet-app-portal` | sin solapamiento |
| `10.102.2.0/27` | `vnet-test/snet-data` | sin solapamiento |
| `10.102.2.32/27` | `vnet-test/snet-data-pe` | sin solapamiento |
| `10.102.2.64/27` | `vnet-test/snet-archive` | sin solapamiento |
| `10.102.2.96/27` | `vnet-test/snet-ingest` | sin solapamiento |
| `10.102.2.128/27` | `vnet-test/snet-admin` | sin solapamiento |
| `10.102.2.160/27` | `vnet-test/snet-cali-integration` | sin solapamiento |
| `10.102.2.192/27` | `vnet-test/snet-fabric-egress` | sin solapamiento |
| `10.103.0.0/21` | `vnet-dev` | sin solapamiento |
| `10.103.0.0/24` | `vnet-dev/snet-ingress` | sin solapamiento |
| `10.103.1.0/25` | `vnet-dev/snet-app-torre` | sin solapamiento |
| `10.103.1.128/25` | `vnet-dev/snet-app-portal` | sin solapamiento |
| `10.103.2.0/27` | `vnet-dev/snet-data` | sin solapamiento |
| `10.103.2.32/27` | `vnet-dev/snet-data-pe` | sin solapamiento |
| `10.103.2.64/27` | `vnet-dev/snet-archive` | sin solapamiento |
| `10.103.2.96/27` | `vnet-dev/snet-ingest` | sin solapamiento |
| `10.103.2.128/27` | `vnet-dev/snet-admin` | sin solapamiento |
| `10.103.2.160/27` | `vnet-dev/snet-cali-integration` | sin solapamiento |
| `10.103.2.192/27` | `vnet-dev/snet-fabric-egress` | sin solapamiento |
| `10.110.0.0/15` | `segunda-nube/reserva-segunda-nube` | sin solapamiento |
| `10.104.0.0/15` | `region-pareja/reserva-region-pareja` | sin solapamiento |
| `10.100.4.0/22` | `hub-vwan/reserva-hub-vwan` | sin solapamiento |
| `10.100.8.0/22` | `vpn-usuarios/reserva-vpn-usuarios` | sin solapamiento |
| `10.39.0.0/16` | `centros-nuevos/reserva-centros-nuevos` | sin solapamiento |

## Conclusión

**Sin solapamiento y todas las comprobaciones cumplidas.**

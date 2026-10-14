#!/usr/bin/env python3
"""One-off cost of the core migration (issue #25).

Every figure in docs/costs/costo-migracion.md comes from this script. Unit prices are Azure
list prices for East US 2 (Central US where noted), taken from the public Azure Retail Prices
API (https://prices.azure.com/api/retail/prices) on 2026-10-13. Assumptions live next to the
number they drive, so changing one assumption and re-running updates every table.

Usage:
    python3 calc_costo_migracion.py            # prints the tables in Markdown
"""
from datetime import date

H = 730                 # hours per month, same convention as the architecture docs
DAY = H / 24            # days per month
COP_PER_USD = 3311      # rate implied by the network design (COP 3,000,000 = USD 906)

# --- Unit prices (USD), Azure Retail Prices API, 2026-10-13 -------------------------------
P = {
    "mysql_gp_vcore_h": 0.0855,          # General Purpose Dadsv5, per vCore-hour
    "mysql_gp_vcore_h_cus": 0.096615,    # same, Central US
    "mysql_storage_gb": 0.115,           # per GB-month
    "mysql_storage_gb_cus": 0.13,
    "mysql_b2s_h": 0.068,                # Burstable B2s
    "redis_b1_h": 0.032,                 # Azure Managed Redis Balanced B1
    "redis_b0_h": 0.016,
    "aca_plan_h": 0.10,                  # Dedicated plan management, per environment
    "aca_vcpu_h": 0.057077,              # Dedicated vCPU
    "aca_gib_h": 0.004978,               # Dedicated memory
    "aca_idle_s": 0.000003,              # Consumption idle, per vCPU-second and per GiB-second
    "vpngw1az_h": 0.21,                  # 10 site-to-site tunnels included
    "fw_std_h": 1.25,
    "fw_gb": 0.016,
    "bastion_basic_h": 0.19,
    "pip_h": 0.005,
    "dns_resolver_endpoint_m": 180.0,    # inbound or outbound endpoint, per month
    "dns_ruleset_m": 2.5,
    "pe_h": 0.01,
    "pe_gb": 0.01,
    "vm_d2s_v5_h": 0.096,
    "egress_gb": 0.087,                  # internet / VPN egress after the first 100 GB
    "dms_premium_4_h": 0.308,            # free for the first 183 days
    "cold_retrieval_gb": 0.03,
    "cool_retrieval_gb": 0.01,
    "cold_lrs_gb": 0.0036,
    "cool_grs_gb": 0.02,
    "cool_grs_write_10k": 0.20,
    "cold_lrs_write_10k": 0.18,
    "log_ingest_gb": 2.76,               # Log Analytics, as used by the security design
}

# Monthly figures already computed by other designs (USD per month), reused as they are.
FROM_DOCS = {
    "appgw_prod": 473.04,     # red-firewall-y-publicacion.md, 7.1
    "appgw_test": 273.31,
    "appgw_dev": 151.84,
    "appgw_pips": 10.95,
    "ddos_ip": 199.00,
    "telemetry_prod": 167.0,  # carga-b-telemetria.md, 6.4 (low end, before history grows)
    "iot_hub_test": 25.0,
    "defender_no_malware": 170.0,  # seguridad-datos-personales-perimetro.md, 6.1, without malware scanning
}

# --- Dates (carga-c-migracion-y-campana.md and carga-c-siembra-1-2pb.md) ------------------
DEV_TEST_FROM = date(2026, 12, 1)
HUB_PROD_FROM = date(2026, 12, 14)
DAY0 = date(2027, 1, 11)
HA_FROM = date(2027, 1, 24)
ISP2_FROM = date(2027, 1, 1)
CUTOVER = date(2027, 2, 14)


def days(a, b=CUTOVER):
    return (b - a).days


def per_month(m, d):
    return m * d / DAY


def node_d4():
    return (4 * P["aca_vcpu_h"] + 16 * P["aca_gib_h"]) * H


def idle_replica():
    # 1 vCPU and 2 GiB idle for a whole month
    return (1 + 2) * P["aca_idle_s"] * H * 3600


def mysql(vcores, gb, cus=False):
    v = P["mysql_gp_vcore_h_cus" if cus else "mysql_gp_vcore_h"]
    s = P["mysql_storage_gb_cus" if cus else "mysql_storage_gb"]
    return vcores * v * H + gb * s


def monthly_platform():
    """Azure components that run before the cutover, per month, at their pre-cutover minimum."""
    hub = [
        ("Azure Firewall Standard", "1,25 × 730", P["fw_std_h"] * H),
        ("VPN Gateway VpnGw1AZ (10 túneles incluidos)", "0,21 × 730", P["vpngw1az_h"] * H),
        ("Azure Bastion Basic", "0,19 × 730", P["bastion_basic_h"] * H),
        ("DNS Private Resolver: entrada, salida y reglas", "180 + 180 + 2,50", 2 * P["dns_resolver_endpoint_m"] + P["dns_ruleset_m"]),
        ("IP públicas del hub (VPN Gateway activo-activo, firewall, Bastion)", "4 × 0,005 × 730", 4 * P["pip_h"] * H),
    ]
    prod = [
        ("MySQL Flexible, principal: 4 vCores y 512 GB", "4 × 0,0855 × 730 + 512 × 0,115", mysql(4, 512)),
        ("Azure Managed Redis Balanced B1", "0,032 × 730", P["redis_b1_h"] * H),
        ("Container Apps, torre: plan y 2 nodos D4", "0,10 × 730 + 2 × (4 × 0,057077 + 16 × 0,004978) × 730", P["aca_plan_h"] * H + 2 * node_d4()),
        ("Container Apps, portal: 2 réplicas en espera (consumo)", "2 × 3 × 0,000003 × 2.628.000 s", 2 * idle_replica()),
        ("Application Gateway WAF v2 y DDoS de la IP del portal", "473,04 + 199 (firewall, 7.1)", FROM_DOCS["appgw_prod"] + FROM_DOCS["ddos_ip"]),
        ("Endpoints privados: 14", "14 × 0,01 × 730", 14 * P["pe_h"] * H),
        ("Máquinas de administración: 2 D2s v5", "2 × 0,096 × 730", 2 * P["vm_d2s_v5_h"] * H),
        ("Log Analytics: unos 60 GB al mes", "60 × 2,76", 60 * P["log_ingest_gb"]),
        ("Defender for Cloud, sin escaneo de malware", "Seguridad, 6.1", FROM_DOCS["defender_no_malware"]),
        ("Telemetría de producción", "Telemetría, 6.4", FROM_DOCS["telemetry_prod"]),
    ]
    dev_test = [
        ("Application Gateway de pruebas y desarrollo, con sus IP", "273,31 + 151,84 + 10,95", FROM_DOCS["appgw_test"] + FROM_DOCS["appgw_dev"] + FROM_DOCS["appgw_pips"]),
        ("MySQL Burstable B2s y 64 GB, en cada ambiente", "2 × (0,068 × 730 + 64 × 0,115)", 2 * (P["mysql_b2s_h"] * H + 64 * P["mysql_storage_gb"])),
        ("Managed Redis B0, en cada ambiente", "2 × 0,016 × 730", 2 * P["redis_b0_h"] * H),
        ("Container Apps: pruebas con plan y 1 nodo D4, desarrollo en consumo", "73 + 224,77 + 2 réplicas en espera", P["aca_plan_h"] * H + node_d4() + 2 * idle_replica()),
        ("Endpoints privados: 10 por ambiente", "20 × 0,01 × 730", 20 * P["pe_h"] * H),
        ("IoT Hub S1 de pruebas", "Telemetría, 6.4", FROM_DOCS["iot_hub_test"]),
    ]
    ha = [
        ("MySQL: alta disponibilidad zonal (servidor en espera)", "4 × 0,0855 × 730 + 512 × 0,115", mysql(4, 512)),
        ("MySQL: réplica de lectura en Central US", "4 × 0,096615 × 730 + 512 × 0,13", mysql(4, 512, cus=True)),
    ]
    return hub, prod, dev_test, ha


def archive_storage():
    """GB-days of the two archive accounts until the cutover, from the seeding schedule."""
    docs_ready, docs_tb = date(2026, 11, 26), 150
    video = [(date(2026, 12, 3), 180), (date(2026, 12, 10), 180), (date(2026, 12, 17), 180),
             (date(2026, 12, 24), 180), (date(2026, 12, 28), 180), (date(2027, 1, 3), 150)]
    delta_ready, delta_docs, delta_video = date(2027, 1, 23), 2.4, 22.8
    growth_tb_day, docs_share = 0.4, 1.1 / 12
    docs_cost = docs_tb * 1000 * P["cool_grs_gb"] * days(docs_ready) / DAY
    docs_cost += delta_docs * 1000 * P["cool_grs_gb"] * days(delta_ready) / DAY
    video_cost = sum(tb * 1000 * P["cold_lrs_gb"] * days(d) / DAY for d, tb in video)
    video_cost += delta_video * 1000 * P["cold_lrs_gb"] * days(delta_ready) / DAY
    # Network growth from day 0: on average half of it stored over the period.
    g = growth_tb_day * days(DAY0)
    docs_cost += g * docs_share * 1000 * P["cool_grs_gb"] * days(DAY0) / 2 / DAY
    video_cost += g * (1 - docs_share) * 1000 * P["cold_lrs_gb"] * days(DAY0) / 2 / DAY
    return docs_cost, video_cost


def seeding():
    # carga-c-siembra-1-2pb.md, 9.1
    return [
        ("Discos: 74 HDD de 20 TB", "74 × 450", 74 * 450),
        ("Cargo de Import/Export: 71 discos", "71 × 80", 71 * 80),
        ("Envío internacional de ida y vuelta, con aduana", "9 envíos × 2 × 600", 9 * 2 * 600),
        ("Escritura de los documentos al importar", "115 millones × 0,20 / 10.000", 115e6 * P["cool_grs_write_10k"] / 1e4),
        ("Escritura del video al importar", "250 millones de bloques × 0,18 / 10.000", 250e6 * P["cold_lrs_write_10k"] / 1e4),
        ("Fecha original e inmutabilidad por archivo", "117 millones × 2 × 0,10 / 10.000", 117e6 * 2 * 0.10 / 1e4),
        ("Estaciones de copia", "2 × 3.000", 2 * 3000),
    ]


def migration_services():
    copy_gb = 400 * days(DAY0, date(2027, 2, 15)) + 2800
    return [
        ("DMS Premium de 4 vCores", "0,308 × 730 al mes, sin costo los primeros 183 días", 0.0),
        ("MySQL a 16 vCores durante la carga inicial", "12 vCores extra × 0,0855 × 48 h", 12 * P["mysql_gp_vcore_h"] * 48),
        ("Servidor temporal del ensayo, 14 días", "4 × 0,0855 × 336 h + 512 × 0,115 × 14 / 30,4", 4 * P["mysql_gp_vcore_h"] * 336 + 512 * P["mysql_storage_gb"] * 14 / DAY),
        ("Copia continua: procesamiento del endpoint privado", f"{copy_gb:,.0f}".replace(",", ".") + " GB × 0,01", copy_gb * P["pe_gb"]),
        ("Copia continua: escrituras", "Unos 1,2 meses de documentos y video nuevos", 1.2 * (1.1e6 * P["cool_grs_write_10k"] / 1e4 + 11e12 / 4194304 * P["cold_lrs_write_10k"] / 1e4)),
        ("Conciliación: lectura de la muestra del 1 %", "10.500 GB de video × 0,03 + 1.100 GB × 0,01 + 11.600 GB × 0,01", 10500 * P["cold_retrieval_gb"] + 1100 * P["cool_retrieval_gb"] + 11600 * P["pe_gb"]),
        ("Base de datos: firewall por la carga inicial y la replicación", "Unos 500 GB × 0,016", 500 * P["fw_gb"]),
    ]


def transit():
    """Centre users reaching the Cali control tower through Azure (FW-401) until the cutover."""
    users, concurrency, kbps, hours = 180, 0.5, 300, 18
    gb_day = users * concurrency * kbps * 1e3 * hours * 3600 / 8 / 1e9
    d = days(date(2027, 1, 19))
    gb = gb_day * d
    return gb_day, d, gb, (gb - 100) * P["egress_gb"], 2 * gb * P["fw_gb"]


def people():
    rate = 120000 / COP_PER_USD          # COP 120,000 per hour, cost to the company
    night, sunday_night = 1.35, 2.25     # Law 2466 of 2025: +35 % night, +90 % Sunday from July 2026
    rows = [
        ("Siembra: preparación, copia, envíos, conciliación e inmutabilidad", "336 h diurnas", 336, 1.0),
        ("Compatibilidad de la base con MySQL 8.4 y parámetros", "40 h diurnas", 40, 1.0),
        ("Guion del corte, scripts de validación y aprobación", "60 h diurnas", 60, 1.0),
        ("Ventanas nocturnas de la convivencia: unas 15 noches", "15 × 2 personas × 6 h, nocturnas", 180, night),
        ("Ensayo: sábado 22:00 a domingo 06:00", "8 personas × (2 h nocturnas + 6 h de domingo nocturnas)", 8, 2 * night + 6 * sunday_night),
        ("Corte: sábado 22:00 a domingo 06:00", "Ídem", 8, 2 * night + 6 * sunday_night),
        ("Acompañamiento el domingo del corte, 06:00 a 10:00", "3 personas × 4 h de domingo diurnas", 12, 1.9),
        ("Apagado de Cali: 6 noches", "6 × 2 personas × 6 h, nocturnas", 72, night),
    ]
    out = [(a, b, h * f * rate) for a, b, h, f in rows]
    return rate, out


def fmt(x):
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def table(title, rows, extra=None):
    print(f"\n#### {title}\n\n| Concepto | Cálculo | USD |\n|---|---|---|")
    total = 0
    for a, b, c in rows:
        print(f"| {a} | {b} | {fmt(c)} |")
        total += c
    print(f"| **Subtotal** | | **{fmt(total)}** |")
    return total


def main():
    hub, prod, dev_test, ha = monthly_platform()
    m_hub = table("Hub, al mes", hub)
    m_prod = table("Producción, al mes", prod)
    m_dt = table("Pruebas y desarrollo, al mes", dev_test)
    m_ha = table("Alta disponibilidad y réplica de la base, al mes", ha)
    d_hub, d_dt, d_ha, d_isp = days(HUB_PROD_FROM), days(DEV_TEST_FROM), days(HA_FROM), days(ISP2_FROM)
    docs_st, video_st = archive_storage()
    isp_month = 3_000_000 / COP_PER_USD
    dual = [
        ("Hub", f"{fmt(m_hub)} × {d_hub} días", per_month(m_hub, d_hub)),
        ("Producción", f"{fmt(m_prod)} × {d_hub} días", per_month(m_prod, d_hub)),
        ("Pruebas y desarrollo", f"{fmt(m_dt)} × {d_dt} días", per_month(m_dt, d_dt)),
        ("Alta disponibilidad y réplica de la base", f"{fmt(m_ha)} × {d_ha} días", per_month(m_ha, d_ha)),
        ("Archivo: cuenta de documentos (Cool GRS)", "Por trabajo cargado, hasta el corte", docs_st),
        ("Archivo: cuenta de video (Cold LRS)", "Por trabajo cargado, hasta el corte", video_st),
        ("Segundo proveedor de internet en Cali", f"COP 3.000.000 al mes × {d_isp} días", per_month(isp_month, d_isp)),
    ]
    t_dual = table("Azure y red antes del corte", dual)
    t_seed = table("Siembra del archivo", seeding())
    t_svc = table("Servicios temporales de la migración", migration_services())
    gb_day, d, gb, egress, fw = transit()
    t_transit = table("Tránsito de los centros hacia la torre de Cali por Azure (FW-401)", [
        ("Salida de Azure por la VPN", f"({fmt(gb_day)} GB al día × {d} días − 100 GB gratis) × 0,087", egress),
        ("Procesamiento del Azure Firewall, ida y vuelta", f"2 × {fmt(gb)} GB × 0,016", fw),
    ])
    rate, ppl = people()
    print(f"\nTarifa: USD {fmt(rate)} por hora")
    t_ppl = table("Horas del equipo", ppl)
    one_off = [("Instalación del segundo proveedor", "COP 3.000.000, una vez", isp_month)]
    t_one = table("Otros costos únicos", one_off)
    subtotal = t_dual + t_seed + t_svc + t_transit + t_ppl + t_one
    print(f"\nSubtotal {fmt(subtotal)}; contingencia 15 % {fmt(0.15 * subtotal)}; total {fmt(1.15 * subtotal)}")
    print(f"Mensual del hub+prod+dev/test antes de HA: {fmt(m_hub + m_prod + m_dt)}")


if __name__ == "__main__":
    main()

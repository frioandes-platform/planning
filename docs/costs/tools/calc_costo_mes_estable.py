#!/usr/bin/env python3
"""Recurring monthly cost in steady state and campaign overhead (issue #26).

Every figure in docs/costs/costo-mes-estable-y-campana.md comes from this script. Unit prices are
Azure list prices for East US 2 (Central US where noted), taken from the public Azure Retail Prices
API (https://prices.azure.com/api/retail/prices) on 2026-10-19, with the same conventions as
calc_costo_migracion.py. Month 0 is the cutover (February 2027): from there the cost is recurring.

Usage:
    python3 calc_costo_mes_estable.py            # prints the tables in Markdown
"""
H = 730                 # hours per month
DAY = H / 24            # days per month
COP_PER_USD = 3311
YEARS = 5
CAMPAIGN_DAYS = 57 + 14 + 31   # 15 Nov-10 Jan, 15-28 Mar, 15 Jun-15 Jul (carga-c-migracion-y-campana.md, 4.1)
PEAK_H = 4                     # campaign peak of the portal, hours per campaign day
DISPATCH_H = 18                # 04:00 to 22:00

# --- Unit prices (USD), Azure Retail Prices API, 2026-10-19 -------------------------------
P = {
    "mysql_gp_vcore_h": 0.0855,
    "mysql_gp_vcore_h_cus": 0.096615,
    "mysql_storage_gb": 0.115,
    "mysql_storage_gb_cus": 0.13,
    "redis_b1_h": 0.032,
    "aca_plan_h": 0.10,
    "aca_vcpu_h": 0.057077,          # Dedicated
    "aca_gib_h": 0.004978,
    "aca_active_vcpu_s": 0.000024,   # Consumption
    "aca_active_gib_s": 0.000003,
    "aca_idle_s": 0.000003,          # per vCPU-second and per GiB-second
    "aca_requests_m": 0.40,
    "fw_std_h": 1.25,
    "fw_gb": 0.016,
    "vpngw1az_h": 0.21,
    "bastion_std_h": 0.29,
    "pip_h": 0.005,
    "dns_resolver_endpoint_m": 180.0,
    "dns_ruleset_m": 2.5,
    "pe_h": 0.01,
    "pe_gb": 0.01,
    "vm_d2s_v5_h": 0.096,
    "vm_d4s_v5_h": 0.192,
    "vm_b2s_h": 0.0416,
    "disk_e10_m": 9.60,
    "acr_premium_day": 1.6666,
    "acr_gb": 0.10,
    "egress_tiers": [(0, 0.0), (100, 0.087), (10_335, 0.083), (51_295, 0.07)],   # GB from, USD per GB
    "inter_region_gb": 0.02,
    "geo_rep_gb": 0.02,              # Geo-Replication v2 data transfer, GRS accounts
    "cool_grs_gb": 0.02,
    "cold_lrs_gb": 0.0036,
    "cold_grs_gb": 0.00803,
    "hot_lrs_gb": 0.0184,
    "cool_grs_write_10k": 0.20,
    "cold_lrs_write_10k": 0.18,
    "cool_read_10k": 0.01,
    "cold_read_10k": 0.10,
    "cool_retrieval_gb": 0.01,
    "cold_retrieval_gb": 0.03,
    "grs_tags_10k": 0.067,           # blob index tags, per 10,000 tags per month
    "cold_lrs_tags_10k": 0.03,
    "inventory_cool_m": 0.0025,      # blob inventory, per million objects
    "inventory_cold_m": 0.025,
    "log_ingest_gb": 2.76,
    "log_retention_gb": 0.12,        # interactive retention beyond 31 days
    "log_archive_gb": 0.02,          # long-term retention
}

# Monthly figures already computed by other designs (USD per month), reused as they are.
FROM_DOCS = {
    "appgw_prod": 473.04,       # red-firewall-y-publicacion.md, 7.1
    "ddos_ip": 199.00,
    "observability": 159.04,    # observabilidad-slo-zabbix.md, 9.2
    "dev_test": 1089.57,        # costo-migracion.md, 4.2
    "isp2_cop": 3_000_000,      # red-topologia-subnetting.md, 2.2
    "fabric_normal": 2891.89,   # costo-fabric.md, 2
    "fabric_campaign": 2938.13,
    "fabric_year": 34857.76,    # F16 all year
}

# --- Defender for Cloud (seguridad-datos-personales-perimetro.md, 6.1), with malware scanning on ---
DEFENDER = [
    ("Defender CSPM", 10 * 5.11),
    ("Defender for Storage", 5 * 9.78),
    ("Escaneo de malware de fotos y comprobantes", 1138 * 0.15),
    ("Defender para MySQL", 3 * 15),
    ("Defender for Resource Manager", 3 * 5.04),
    ("Defender for Servers, plan 1", 2 * 4.91),
    ("Defender for Key Vault", 0.25),
    ("Alertas propias del portal", 6.50),
]

# --- Telemetry (carga-b-telemetria.md, 6.4), without the history, which grows -------------
TELEMETRY_FIXED = 50.00 + 0.10 + 80.30 + 10.51 + 22.31 + 0.30
HISTORY_GB_MONTH = 15           # per copy (carga-b-telemetria.md, 4.7)
HISTORY_CAMPAIGN_GB = 5         # extra per copy in a campaign month (carga-b-telemetria.md, 6.3)

# --- Archive (carga-c-siembra-1-2pb.md, 4.1) ----------------------------------------------
# 1.2 PB at 12 TB a month is about 100 months of data. Assumption: every kind of content built up
# evenly over those 100 months, so 60 % of the seeded volume is under five years old at the cutover
# and expires evenly over the next 60 months, and 40 % is already older than five years.
ARCHIVE_MONTHS = 100
SEED_TB = {"fotos": 110, "temp": 40, "video": 1050}
NEW_TB_MONTH = {"fotos": 1.1, "temp": 0.0, "video": 10.9}   # temperature now goes to IoT Hub
SEED_FILES = {"docs": 115e6, "video": 2e6}                  # costo-migracion.md, 3
VIDEO_FILE_MB = 525                                         # 1.05 PB in about 2 million files


def within_share():
    return 60 / ARCHIVE_MONTHS


def seed_left(m):
    """Share of the seeded under-five-years part still stored at month m."""
    return max(0.0, 1 - m / 60)


def archive_tb(m, keep_old=True, purge=True):
    """TB stored in each account at month m after the cutover."""
    w = within_share()
    old = 1 - w if keep_old else 0.0
    if not purge:
        docs = SEED_TB["fotos"] + SEED_TB["temp"] + NEW_TB_MONTH["fotos"] * m
        video = SEED_TB["video"] + NEW_TB_MONTH["video"] * m
        return docs, video
    new_m = min(m, 60)
    docs = sum(SEED_TB[k] * (old + w * seed_left(m)) + NEW_TB_MONTH[k] * new_m for k in ("fotos", "temp"))
    video = SEED_TB["video"] * (old + w * seed_left(m)) + NEW_TB_MONTH["video"] * new_m
    return docs, video


def tagged_files(m, keep_old=True):
    w = within_share()
    share = (1 - w if keep_old else 0.0) + w * seed_left(m)
    return SEED_FILES["docs"] * share, SEED_FILES["video"] * share


def archive_rows(m, keep_old=True):
    docs_tb, video_tb = archive_tb(m, keep_old)
    docs_tags, video_tags = tagged_files(m, keep_old)
    new_docs_gb = NEW_TB_MONTH["fotos"] * 1000
    new_video_gb = NEW_TB_MONTH["video"] * 1000
    reads_video_gb, reads_docs_gb = 300, 100
    objects = SEED_FILES["docs"] + SEED_FILES["video"]
    return [
        ("Documentos: fotos, comprobantes e históricos de temperatura, Cool GRS",
         f"{fmt(docs_tb * 1000, 0)} GB × 0,02", docs_tb * 1000 * P["cool_grs_gb"]),
        ("Video de muelles y entregas, Cold LRS",
         f"{fmt(video_tb * 1000, 0)} GB × 0,0036", video_tb * 1000 * P["cold_lrs_gb"]),
        ("Etiquetas de índice con la fecha original de lo sembrado",
         f"{fmt(docs_tags / 1e6, 1)} millones × 0,067 + {fmt(video_tags / 1e6, 1)} millones × 0,03, por 10.000",
         docs_tags * P["grs_tags_10k"] / 1e4 + video_tags * P["cold_lrs_tags_10k"] / 1e4),
        ("Escritura de lo nuevo",
         "1,1 millones de archivos × 0,20 + 2,6 millones de bloques de 4 MiB × 0,18, por 10.000",
         new_docs_gb * 1e3 * P["cool_grs_write_10k"] / 1e4 + new_video_gb * 1e9 / 4194304 * P["cold_lrs_write_10k"] / 1e4),
        ("Copia geográfica de los documentos nuevos", "1.100 GB × 0,02", new_docs_gb * P["geo_rep_gb"]),
        ("Endpoint privado: lo que entra y sale del archivo",
         f"({fmt(new_docs_gb + new_video_gb, 0)} + {reads_video_gb + reads_docs_gb}) GB × 0,01",
         (new_docs_gb + new_video_gb + reads_video_gb + reads_docs_gb) * P["pe_gb"]),
        ("Lecturas: reclamos y comprobantes del portal",
         "300 GB de video × 0,03 + 100 GB de documentos × 0,01, con sus operaciones",
         reads_video_gb * P["cold_retrieval_gb"] + reads_video_gb * 1e9 / 4194304 * P["cold_read_10k"] / 1e4
         + reads_docs_gb * P["cool_retrieval_gb"] + reads_docs_gb * 1e3 * P["cool_read_10k"] / 1e4),
        ("Inventario mensual para el borrado a los cinco años",
         "117 millones de objetos",
         SEED_FILES["docs"] / 1e6 * P["inventory_cool_m"] + SEED_FILES["video"] / 1e6 * P["inventory_cold_m"]),
    ]


# --- Audit logs with five years of retention (gobierno-auditoria-facturacion.md) ----------
AUDIT_GB = {"business": 8, "blob": 8, "identity": 2}


def audit_rows(m):
    gb = sum(AUDIT_GB.values())
    archived = gb * min(max(m - 3, 0), 57)
    return [
        ("Ingesta de la auditoría: negocio, accesos a Blob e identidad", f"{gb} GB × 2,76", gb * P["log_ingest_gb"]),
        ("Retención consultable de 90 días", f"{gb} × 59/30 × 0,12", gb * 59 / 30 * P["log_retention_gb"]),
        ("Retención a largo plazo hasta cinco años", f"{fmt(archived, 0)} GB acumulados × 0,02", archived * P["log_archive_gb"]),
    ]


def history_cost(m):
    gb = HISTORY_GB_MONTH * min(m, 60)
    return gb * (P["cool_grs_gb"] + P["hot_lrs_gb"]) + HISTORY_GB_MONTH * P["geo_rep_gb"]


# --- Traffic -----------------------------------------------------------------------------
USERS, CONCURRENCY, KBPS = 450, 0.5, 300         # red-topologia-subnetting.md, same as #25
PORTAL_REQ_MONTH = 6.7e6                         # observabilidad-slo-zabbix.md, 9.1
PORTAL_KB = 100                                  # average response


def users_gb_month():
    return USERS * CONCURRENCY * KBPS * 1e3 * DISPATCH_H * 3600 / 8 / 1e9 * DAY


def egress(gb):
    tiers = P["egress_tiers"] + [(float("inf"), None)]
    total = 0.0
    for (start, price), (end, _) in zip(tiers, tiers[1:]):
        if gb > start:
            total += (min(gb, end) - start) * price
    return total


def node_d4():
    return (4 * P["aca_vcpu_h"] + 16 * P["aca_gib_h"]) * H


def replica_active_h():
    return (P["aca_active_vcpu_s"] + 2 * P["aca_active_gib_s"]) * 3600


def replica_idle_h():
    return 3 * P["aca_idle_s"] * 3600


def mysql(vcores, gb, cus=False):
    v = P["mysql_gp_vcore_h_cus" if cus else "mysql_gp_vcore_h"]
    s = P["mysql_storage_gb_cus" if cus else "mysql_storage_gb"]
    return vcores * v * H + gb * s


def monthly(m):
    """Steady-state month m after the cutover, by block."""
    users = users_gb_month()
    portal_gb = PORTAL_REQ_MONTH * PORTAL_KB / 1e6
    hub = [
        ("Azure Firewall Standard", "1,25 × 730", P["fw_std_h"] * H),
        ("Procesamiento del firewall: usuarios de Cali y los centros hacia la torre", f"{fmt(users, 0)} GB × 1,1 × 0,016", users * 1.1 * P["fw_gb"]),
        ("VPN Gateway VpnGw1AZ (10 túneles incluidos)", "0,21 × 730", P["vpngw1az_h"] * H),
        ("Azure Bastion Standard (2 instancias incluidas)", "0,29 × 730", P["bastion_std_h"] * H),
        ("DNS Private Resolver: entrada, salida y reglas", "180 + 180 + 2,50", 2 * P["dns_resolver_endpoint_m"] + P["dns_ruleset_m"]),
        ("IP públicas del hub", "4 × 0,005 × 730", 4 * P["pip_h"] * H),
        ("Salida de Azure: respuestas a los usuarios por la VPN y portal a internet",
         f"{fmt(users + portal_gb, 0)} GB por tramos (100 sin costo, 0,087 y 0,083)", egress(users + portal_gb)),
    ]
    portal_active = 4 * (DISPATCH_H / 24 * H * replica_active_h() + (24 - DISPATCH_H) / 24 * H * replica_idle_h())
    prod = [
        ("MySQL Flexible, principal: 4 vCores y 512 GB", "4 × 0,0855 × 730 + 512 × 0,115", mysql(4, 512)),
        ("MySQL: servidor en espera de la alta disponibilidad zonal", "Ídem", mysql(4, 512)),
        ("MySQL: réplica de lectura en Central US", "4 × 0,096615 × 730 + 512 × 0,13", mysql(4, 512, cus=True)),
        ("Replicación hacia Central US", "Unos 100 GB × 0,02", 100 * P["inter_region_gb"]),
        ("Azure Managed Redis Balanced B1", "0,032 × 730", P["redis_b1_h"] * H),
        ("Container Apps, torre: plan y 4 nodos D4", "73 + 4 × 224,81", P["aca_plan_h"] * H + 4 * node_d4()),
        ("Container Apps, portal: 4 réplicas de consumo, activas 18 h al día",
         "4 × (547,5 h × 0,108 + 182,5 h × 0,0324)", portal_active),
        ("Container Apps, solicitudes del portal", "6,7 millones × 0,40 por millón", PORTAL_REQ_MONTH / 1e6 * P["aca_requests_m"]),
        ("Application Gateway WAF v2 y DDoS de la IP del portal", "473,04 + 199", FROM_DOCS["appgw_prod"] + FROM_DOCS["ddos_ip"]),
        ("Endpoints privados: 14", "14 × 0,01 × 730", 14 * P["pe_h"] * H),
        ("Máquinas de administración: 2 D2s v5 con disco E10", "2 × (0,096 × 730 + 9,60)", 2 * (P["vm_d2s_v5_h"] * H + P["disk_e10_m"])),
        ("Ejecutor del pipeline de producción: B2s con disco E10", "0,0416 × 730 + 9,60", P["vm_b2s_h"] * H + P["disk_e10_m"]),
        ("Registro de contenedores Premium, con 50 GB", "1,6666 × 30,42 + 50 × 0,10", P["acr_premium_day"] * DAY + 50 * P["acr_gb"]),
    ]
    monitoring = [("Observabilidad de la plataforma", "Observabilidad, 9.2", FROM_DOCS["observability"])] + audit_rows(m)
    monitoring += [("Defender for Cloud, con el escaneo de malware encendido", "Seguridad, 6.1", sum(v for _, v in DEFENDER))]
    telemetry = [
        ("IoT Hub, Stream Analytics, función, Event Hub y transferencia", "Telemetría, 6.4", TELEMETRY_FIXED),
        ("Historial: las dos copias", f"{fmt(HISTORY_GB_MONTH * min(m, 60), 0)} GB × (0,02 + 0,0184) + copia geográfica", history_cost(m)),
    ]
    dev_test = [
        ("Pruebas y desarrollo, como en la migración", "Costo de la migración, 4.2", FROM_DOCS["dev_test"]),
        ("Ejecutores del pipeline de pruebas y desarrollo: 2 B2s con disco E10", "2 × (0,0416 × 730 + 9,60)", 2 * (P["vm_b2s_h"] * H + P["disk_e10_m"])),
    ]
    outside = [("Segundo proveedor de internet en Cali", "COP 3.000.000", FROM_DOCS["isp2_cop"] / COP_PER_USD)]
    return {
        "Hub y tráfico": hub,
        "Producción: aplicación y datos": prod,
        "Archivo histórico y evidencias": archive_rows(m),
        "Monitoreo, auditoría y seguridad": monitoring,
        "Telemetría": telemetry,
        "Pruebas y desarrollo": dev_test,
        "Fuera de Azure": outside,
    }


def total(blocks):
    return sum(c for rows in blocks.values() for _, _, c in rows)


# --- Campaign -----------------------------------------------------------------------------
def campaign_rows(tower_hours=PEAK_H):
    extra_req = (2000 - 800) * 60 * PEAK_H
    extra_msgs = 60 * (1 / 60 + 1 / 30) * DISPATCH_H * 3600
    log_kb = 1 + 4 * 0.1                         # gateway log plus sampled traces, per request
    return [
        ("Capa de aplicación: +40 %", "Torre de 4 a 6 nodos D4",
         f"2 nodos × {tower_hours} h × 0,308", 2 * tower_hours * node_d4() / H),
        ("Portal: 2.000 solicitudes por minuto", "Rastreo de 2 a 4 réplicas y front de 2 a 3",
         f"3 réplicas × {PEAK_H} h × 0,108", 3 * PEAK_H * replica_active_h()),
        ("Portal: 2.000 solicitudes por minuto", "Solicitudes de más",
         f"{fmt(extra_req, 0)} × 0,40 por millón", extra_req / 1e6 * P["aca_requests_m"]),
        ("Portal: 2.000 solicitudes por minuto", "Salida a internet de esas respuestas",
         f"{fmt(extra_req * PORTAL_KB / 1e6, 1)} GB × 0,083", extra_req * PORTAL_KB / 1e6 * 0.083),
        ("Portal: 2.000 solicitudes por minuto", "Registros del gateway y trazas",
         f"{fmt(extra_req * log_kb / 1e6, 2)} GB × 2,76", extra_req * log_kb / 1e6 * P["log_ingest_gb"]),
        ("Portal: 2.000 solicitudes por minuto", "Application Gateway",
         "Las 20 unidades reservadas cubren las 18 del pico", 0.0),
        ("Telemetría: 180 camiones", "IoT Hub y Stream Analytics",
         "Mismo tamaño: 2 unidades S1 reciben 800.000 mensajes al día", 0.0),
        ("Telemetría: 180 camiones", "Event Hub y historial",
         f"{fmt(extra_msgs, 0)} eventos × 0,028 por millón + 5 GB al mes por copia",
         extra_msgs / 1e6 * 0.028 + HISTORY_CAMPAIGN_GB / DAY * (P["cool_grs_gb"] + P["hot_lrs_gb"] + P["geo_rep_gb"])),
    ]


def load_test():
    h = 6
    return [
        ("Torre de pruebas de 1 a 6 nodos D4", f"5 × {h} h × 0,308", 5 * h * node_d4() / H),
        ("Portal de pruebas: 7 réplicas activas", f"7 × {h} h × 0,108", 7 * h * replica_active_h()),
        ("Application Gateway de pruebas: unas 18 unidades", f"18 × {h} h × 0,0144", 18 * h * 0.0144),
        ("Generador de carga: 2 máquinas D4s v5", f"2 × {h} h × 0,192", 2 * h * P["vm_d4s_v5_h"]),
    ]


def fmt(x, d=2):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def table(title, rows):
    print(f"\n#### {title}\n\n| Concepto | Cálculo | USD al mes |\n|---|---|---|")
    t = 0
    for a, b, c in rows:
        print(f"| {a} | {b} | {fmt(c)} |")
        t += c
    print(f"| **Subtotal** | | **{fmt(t)}** |")
    return t


def main():
    print("## Mes 1 (marzo de 2027)")
    blocks = monthly(1)
    for name, rows in blocks.items():
        table(name, rows)
    m1 = total(blocks)
    print(f"\nTotal mes 1: {fmt(m1)}")

    print("\n## Resumen por bloque en los meses 1, 12, 24, 36, 48 y 60\n")
    months = [1, 12, 24, 36, 48, 60]
    print("| Bloque | " + " | ".join(f"Mes {m}" for m in months) + " |")
    print("|---|" + "---|" * len(months))
    per = {m: monthly(m) for m in months}
    for name in blocks:
        print(f"| {name} | " + " | ".join(fmt(sum(c for _, _, c in per[m][name])) for m in months) + " |")
    print("| **Total** | " + " | ".join(f"**{fmt(total(per[m]))}**" for m in months) + " |")

    print("\n## Archivo: TB guardados y USD al mes de capacidad\n")
    print("| Mes | Docs TB | Video TB | Total TB | USD capacidad | Sin borrado TB | Sin borrado USD | Sin lo de +5 años TB | USD |")
    print("|---|---|---|---|---|---|---|---|---|")
    for m in [0, 12, 24, 36, 48, 60]:
        d, v = archive_tb(m)
        dn, vn = archive_tb(m, purge=False)
        do, vo = archive_tb(m, keep_old=False)
        cap = lambda a, b: a * 1000 * P["cool_grs_gb"] + b * 1000 * P["cold_lrs_gb"]
        print(f"| {m} | {fmt(d, 1)} | {fmt(v, 1)} | {fmt(d + v, 1)} | {fmt(cap(d, v))} | {fmt(dn + vn, 1)} | {fmt(cap(dn, vn))} | {fmt(do + vo, 1)} | {fmt(cap(do, vo))} |")

    print("\n## Campaña, por día de campaña\n")
    rows = campaign_rows()
    print("| Regla | Qué cambia | Cálculo | USD por día |\n|---|---|---|---|")
    for a, b, c, d in rows:
        print(f"| {a} | {b} | {c} | {fmt(d)} |")
    day = sum(r[3] for r in rows)
    by_rule = {}
    for a, _, _, d in rows:
        by_rule[a] = by_rule.get(a, 0) + d
    print(f"| **Total por día** | | | **{fmt(day)}** |")
    for k, v in by_rule.items():
        print(f"  {k}: día {fmt(v)}, mes de 30 días {fmt(30 * v)}, año ({CAMPAIGN_DAYS} días) {fmt(CAMPAIGN_DAYS * v)}")
    print(f"Mes de campaña (30 días): {fmt(30 * day)}; año ({CAMPAIGN_DAYS} días): {fmt(CAMPAIGN_DAYS * day)}")
    day18 = sum(r[3] for r in campaign_rows(DISPATCH_H))
    print(f"Con la torre +40 % de 04:00 a 22:00: día {fmt(day18)}, mes {fmt(30 * day18)}, año {fmt(CAMPAIGN_DAYS * day18)}")
    t_lt = table("Prueba de carga antes de cada campaña", load_test())
    print(f"Tres pruebas al año: {fmt(3 * t_lt)}")
    flat = 0.40 * (m1 - sum(c for _, _, c in blocks["Fuera de Azure"]))
    print(f"\n40 % plano sobre el mes de Azure: {fmt(flat)} al mes")

    print("\n## Presupuesto anual\n")
    print("| Año | Meses | Plataforma | Campaña (regla de 04:00 a 22:00) y pruebas de carga | Total | Fabric (F16, aparte) |")
    print("|---|---|---|---|---|---|")
    grand = 0
    fabric_year = FROM_DOCS["fabric_year"]
    for y in range(1, YEARS + 1):
        plat = sum(total(monthly(m)) for m in range(12 * (y - 1) + 1, 12 * y + 1))
        camp = CAMPAIGN_DAYS * day18 + 3 * t_lt
        grand += plat + camp
        print(f"| {y} | {12 * (y - 1) + 1} a {12 * y} | {fmt(plat)} | {fmt(camp)} | {fmt(plat + camp)} | {fmt(fabric_year)} |")
    print(f"| **Cinco años** | | | | **{fmt(grand)}** | {fmt(5 * fabric_year)} |")
    print(f"\nCOP mes 1: {fmt(m1 * COP_PER_USD / 1e6, 1)} millones; cinco años {fmt(grand * COP_PER_USD / 1e6, 0)} millones")

    print("\n## Decisiones\n")
    d0, v0 = archive_tb(1)
    print(f"Docs > 1 año a Cold GRS (mes 1): {fmt((d0 - 13.2) * 1000 * (P['cool_grs_gb'] - P['cold_grs_gb']))}")
    dt, vt = tagged_files(1)
    print(f"Etiquetas como metadatos (mes 1): {fmt(dt * P['grs_tags_10k'] / 1e4 + vt * P['cold_lrs_tags_10k'] / 1e4)}")
    do, vo = archive_tb(1, keep_old=False)
    print(f"Borrar lo de +5 años (mes 1): {fmt((d0 - do) * 1000 * P['cool_grs_gb'] + (v0 - vo) * 1000 * P['cold_lrs_gb'])}")
    print(f"Video en GRS (mes 1): {fmt(v0 * 1000 * (P['cold_grs_gb'] - P['cold_lrs_gb']))}")
    print(f"MySQL a 8 vCores en campaña, por mes: {fmt(4 * P['mysql_gp_vcore_h'] * H)}")
    print(f"Activación de Central US, por hora: {fmt((P['aca_plan_h'] * H + 4 * node_d4()) / H + 4 * replica_active_h())}")


if __name__ == "__main__":
    main()

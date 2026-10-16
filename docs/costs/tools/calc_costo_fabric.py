#!/usr/bin/env python3
"""Monthly cost of Microsoft Fabric, as a separate line from the platform (issue #27).

Every figure in docs/costs/costo-fabric.md comes from this script. Unit prices are Azure list
prices for East US 2 from the public Azure Retail Prices API (https://prices.azure.com/api/retail/prices),
queried on 2026-10-16, plus the Power BI Pro list price from Microsoft's Power BI pricing page.
Sizes and hours come from the Fabric design (fabric-workspaces-ingesta-region.md and
fabric-acceso-casos-uso-costo.md). Assumptions live next to the number they drive.

Usage:
    python3 calc_costo_fabric.py            # prints the tables in Markdown
"""

H = 730                    # hours per month, same convention as the other cost documents
DAYS = H / 24              # days per month
COP_PER_USD = 3311         # same rate as the migration cost

# --- Unit prices (USD) --------------------------------------------------------------------
P = {
    "cu_h": 0.18,                  # Fabric capacity, pay as you go, per CU-hour
    "cu_reserved_year": 938.0,     # Fabric capacity reservation, per CU, 1 year
    "spark_cu_per_vcore_h": 0.5,   # Spark consumes 0.5 CU-hour per vCore-hour
    "onelake_hot_gb": 0.023,       # OneLake storage, Hot, per GB-month
    "onelake_cold_gb": 0.004,      # OneLake storage, Cold, per GB-month
    "pro_user_m": 14.0,            # Power BI Pro, per user-month, paid yearly
    "cool_retrieval_gb": 0.01,     # Blob Cool data retrieval (documents account)
    "cool_read_10k": 0.01,         # Blob Cool read operations
    "cold_retrieval_gb": 0.03,     # Blob Cold data retrieval (video account)
    "cold_read_10k": 0.10,         # Blob Cold read operations
    "log_ingest_gb": 2.76,         # Log Analytics, as used by the observability design
}

# --- Quantities ---------------------------------------------------------------------------
PROD_SKU_CU = 16                       # fcfaprod at go-live, normal and campaign
PROD_SKU_CU_AFTER = 8                  # outside campaign, if the first month uses < 40 % of F16
NONPROD_SKU_CU = 4                     # fcfanoprod
NONPROD_HOURS = 12 * DAYS * 5 / 7      # Monday to Friday, 07:00 to 19:00
PRO_USERS = 40                         # data team, tower and quality leads, quality and night shift
SPARK_VCORE_H_NIGHT = 8 * 0.5 + 8 * 1.0  # table maintenance (8 vCores, 30 min) + image checks (8 vCores, 1 h);
                                         # runs inside fcfaprod, so it adds no line to the bill
ONELAKE_GB = 80 + 7.3 + 3              # operational views (<= 20 % of a 400 GB database), Activator events
                                       # kept 30 days (487,000 a day x 0.5 KB), results and curated tables
NEW_DOCS_GB_M = 1100                   # new photos and receipts a month (archive seeding assumption)
NEW_DOCS_FILES_M = 1_100_000           # 1 MB per file
LOG_GB_M = 10                          # model logs of the client and quality workspaces
CAMPAIGN_LOG_FACTOR = 2.5              # client report views in campaign (2,000 vs 800 requests a minute)
CAMPAIGN_SPARK_FACTOR = 1.4            # more photos and readings with 180 trucks

CAMPAIGN_DAYS_YEAR = 102               # year-end, Easter week and mid-year campaigns, as assumed by the migration plan
PRE_CAMPAIGN_DAYS_YEAR = 21            # one week at F16 before each campaign
RESERVED_CU = 8                        # one-year reservation for the floor that fcfaprod never goes below

# --- Copying the archive instead of reading it in place -----------------------------------
VIDEO_GB = 1_050_000
DOCS_GB = 150_000
GROWTH_GB_M = 12_000
BLOCK_MB = 4
ONELAKE_WRITE_CU_S_PER_10K_BLOCKS = 1626  # OneLake write, Hot


def num(x, dec=0):
    """Spanish number format: dot for thousands, comma for decimals."""
    return f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def usd(x):
    return num(x, 2)


def capacity(cu, hours):
    return cu * P["cu_h"] * hours


def month(prod_cu, campaign=False):
    log_gb = LOG_GB_M * (CAMPAIGN_LOG_FACTOR if campaign else 1)
    factor = CAMPAIGN_SPARK_FACTOR if campaign else 1
    docs_gb = NEW_DOCS_GB_M * factor
    docs_files = NEW_DOCS_FILES_M * factor
    rows = [
        ("`fcfaprod`", f"F{prod_cu}: {prod_cu} × 0,18 × 730", capacity(prod_cu, H), "Fabric"),
        ("`fcfanoprod`", f"F{NONPROD_SKU_CU}: {NONPROD_SKU_CU} × 0,18 × {num(NONPROD_HOURS)} horas",
         capacity(NONPROD_SKU_CU, NONPROD_HOURS), "Fabric"),
        ("Almacenamiento de OneLake", f"{num(ONELAKE_GB)} GB × 0,023", ONELAKE_GB * P["onelake_hot_gb"], "Fabric"),
        ("Licencias Pro", f"{PRO_USERS} × 14", PRO_USERS * P["pro_user_m"], "Microsoft 365"),
        ("Lecturas del archivo por atajo",
         f"{num(docs_gb)} GB × 0,01 + {num(docs_files / 1e6, 2)} millones de lecturas × 0,01 por 10.000",
         docs_gb * P["cool_retrieval_gb"] + docs_files / 10_000 * P["cool_read_10k"], "Cuenta de documentos"),
        ("Registros de los modelos", f"{num(log_gb)} GB × 2,76", log_gb * P["log_ingest_gb"], "Log Analytics"),
    ]
    return rows


def table(rows, title):
    total = sum(r[2] for r in rows)
    out = [f"### {title}", "", "| Partida | Cálculo | USD al mes | Quién lo cobra |", "|---|---|---|---|"]
    out += [f"| {a} | {b} | {usd(c)} | {d} |" for a, b, c, d in rows]
    cop = num(total * COP_PER_USD / 1e6, 1)
    out.append(f"| **Total** | | **{usd(total)}** | Unos COP {cop} millones |")
    return "\n".join(out), total


def copy_scenario(gb, growth_gb_m, retrieval_per_gb, read_per_10k):
    """One-off and monthly cost of keeping a second copy of `gb` in OneLake."""
    blocks = gb * 1024 / BLOCK_MB
    write_cu_h = blocks / 10_000 * ONELAKE_WRITE_CU_S_PER_10K_BLOCKS / 3600
    one_time = gb * retrieval_per_gb + blocks / 10_000 * read_per_10k + write_cu_h * P["cu_h"]
    hot_m = gb * P["onelake_hot_gb"]
    cold_m = gb * P["onelake_cold_gb"]
    year_hot = one_time + sum((gb + growth_gb_m * k) * P["onelake_hot_gb"] for k in range(12))
    year_cold = one_time + sum((gb + growth_gb_m * k) * P["onelake_cold_gb"] for k in range(12))
    return {"one_time": one_time, "write_cu_h": write_cu_h, "hot_m": hot_m, "cold_m": cold_m,
            "year_hot": year_hot, "year_cold": year_cold}


def comparison():
    video = copy_scenario(VIDEO_GB, GROWTH_GB_M * 10.9 / 12, P["cold_retrieval_gb"], P["cold_read_10k"])
    docs = copy_scenario(DOCS_GB, GROWTH_GB_M * 1.1 / 12, P["cool_retrieval_gb"], P["cool_read_10k"])
    full = {k: video[k] + docs[k] for k in video}
    shortcut_m = NEW_DOCS_GB_M * P["cool_retrieval_gb"] + NEW_DOCS_FILES_M / 10_000 * P["cool_read_10k"]
    rows = [
        ("Copiar el archivo completo (1,2 PB)", full),
        ("Copiar solo el video (1,05 PB)", video),
    ]
    out = ["| Escenario | Costo único (lectura del origen y escritura en OneLake) | OneLake Hot al mes | OneLake Cold al mes | Primer año en Hot | Primer año en Cold |",
           "|---|---|---|---|---|---|"]
    for name, r in rows:
        out.append(f"| {name} | {usd(r['one_time'])} | {usd(r['hot_m'])} | {usd(r['cold_m'])} | {usd(r['year_hot'])} | {usd(r['year_cold'])} |")
    out.append(f"| Atajos (elegido) | 0,00 | {usd(shortcut_m)} en lecturas | | {usd(shortcut_m * 12)} | |")
    saving_m_hot = full["hot_m"] - shortcut_m
    saving_m_cold = full["cold_m"] - shortcut_m
    saving_y_hot = full["year_hot"] - shortcut_m * 12
    saving_y_cold = full["year_cold"] - shortcut_m * 12
    out.append("")
    out.append(f"Ahorro frente al archivo completo: {usd(saving_m_hot)} al mes en Hot o {usd(saving_m_cold)} en Cold; "
               f"{usd(saving_y_hot)} o {usd(saving_y_cold)} el primer año.")
    out.append(f"Escribir la copia consume {num(full['write_cu_h'])} CU hora de capacidad: más de un mes completo de F16 "
               f"({num(16 * H)} CU hora).")
    return "\n".join(out)


def savings():
    f16 = capacity(16, H)
    f8 = capacity(8, H)
    f64 = capacity(64, H)
    nonprod_always = capacity(NONPROD_SKU_CU, H)
    nonprod_sched = capacity(NONPROD_SKU_CU, NONPROD_HOURS)
    reserved_cu_m = P["cu_reserved_year"] / 12
    reserve_saving = RESERVED_CU * (P["cu_h"] * H - reserved_cu_m)
    f16_days = CAMPAIGN_DAYS_YEAR + PRE_CAMPAIGN_DAYS_YEAR
    f8_months = (365 - f16_days) / 365 * 12
    pro = PRO_USERS * P["pro_user_m"]
    overage_cap_10 = 0.10 * 16 * 24 * P["cu_h"] * 3 * DAYS
    overage_cap_25 = 0.25 * 16 * 24 * P["cu_h"] * 3 * DAYS
    return {
        "nonprod": nonprod_always - nonprod_sched,
        "no_f64": f64 - (f16 + pro),
        "f8_month": f16 - f8,
        "f8_year": (f16 - f8) * f8_months,
        "f8_months": f8_months,
        "reserve_month": reserve_saving,
        "reserve_year": reserve_saving * 12,
        "reserved_cu_m": reserved_cu_m,
        "overage_cap_10": overage_cap_10,
        "overage_cap_25": overage_cap_25,
        "f64": f64,
    }


def year_total(prod_cu_normal):
    normal = sum(r[2] for r in month(prod_cu_normal))
    campaign = sum(r[2] for r in month(PROD_SKU_CU, campaign=True))
    camp_months = CAMPAIGN_DAYS_YEAR / 365 * 12
    pre = PRE_CAMPAIGN_DAYS_YEAR / 365 * 12 * (capacity(PROD_SKU_CU, H) - capacity(prod_cu_normal, H))
    return normal * (12 - camp_months) + campaign * camp_months + pre


def spark_inside():
    """CU-hours a month that the nightly Spark jobs add inside fcfaprod, and their 24-hour average."""
    cu_h = SPARK_VCORE_H_NIGHT * DAYS * P["spark_cu_per_vcore_h"]
    return cu_h, cu_h / H


if __name__ == "__main__":
    t_normal, n = table(month(PROD_SKU_CU), "Mes normal, al arranque")
    t_camp, c = table(month(PROD_SKU_CU, campaign=True), "Mes de campaña")
    t_after, a = table(month(PROD_SKU_CU_AFTER), "Mes normal con F8, si la medición lo permite")
    print(t_normal, "\n")
    print(t_camp, "\n")
    print(t_after, "\n")
    print("### Copiar el archivo frente a atajos\n")
    print(comparison(), "\n")
    sv = savings()
    print("### Decisiones que bajan gasto\n")
    print("| Decisión | Efecto en USD |")
    print("|---|---|")
    print(f"| Sin F64: licencias Pro | {usd(sv['no_f64'])} al mes (F64 cuesta {usd(sv['f64'])}) |")
    print(f"| fcfanoprod pausada fuera del horario | {usd(sv['nonprod'])} al mes |")
    print(f"| F8 fuera de campaña | {usd(sv['f8_month'])} por mes normal; {usd(sv['f8_year'])} al año ({num(sv['f8_months'], 1)} meses) |")
    print(f"| Reserva de {RESERVED_CU} CU por un año | {usd(sv['reserve_month'])} al mes; {usd(sv['reserve_year'])} al año ({usd(sv['reserved_cu_m'])} por CU al mes) |")
    print(f"| Sobreconsumo con umbral del 10 % | Tope de {usd(sv['overage_cap_10'])} al mes en vez de {usd(sv['overage_cap_25'])} |")
    print(f"\nAño con F16 siempre: {usd(year_total(16))}. Año con F8 fuera de campaña: {usd(year_total(8))}.")
    cu_h, avg = spark_inside()
    print(f"\n### Spark nocturno dentro de la capacidad: {num(cu_h, 1)} CU hora al mes, {num(avg, 2)} CU promedio")
    reserved_cu_m = P["cu_reserved_year"] / 12
    print(f"\nReserva: {usd(reserved_cu_m)} por CU al mes frente a {usd(P['cu_h'] * H)} en pago por uso;"
          f" F16 reservada completa {usd(16 * reserved_cu_m)} al mes.")

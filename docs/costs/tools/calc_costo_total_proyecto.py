#!/usr/bin/env python3
"""Total project cost, total cost of ownership and cost-saving decisions (issue #28).

Every figure in docs/costs/costo-total-proyecto.md and docs/costs/decisiones-ahorro.md comes from
this script. It reuses the figures of the other cost documents instead of computing them again:
the migration (#25, costo-migracion.md), the steady-state month (#26, calc_costo_mes_estable.py,
imported below) and Fabric (#27, costo-fabric.md). Team rate and exchange rate are the ones of #25.

Usage:
    python3 calc_costo_total_proyecto.py         # prints the tables in Markdown
"""
import sys

sys.dont_write_bytecode = True
import calc_costo_mes_estable as est  # noqa: E402

COP_PER_USD = 3311
RATE = 120000 / COP_PER_USD     # COP 120,000 per hour, cost to the company (#25)
FTE_H = 40 * 48                 # hours a year of one full-time person, without holidays and vacations
CONTINGENCY = 0.15              # same as #25, on the new one-off lines only
DAY = est.DAY

FROM_DOCS = {
    "migration_total": 153417.32,      # costo-migracion.md, 2 (with its own 15 % contingency)
    "pre_cutover_month": 1654.60 + 2318.82 + 1089.57 + 657.22,   # costo-migracion.md, 4.2
    "isp2_month": 906.07,
    "seeding": 64920.00,               # costo-migracion.md, 3
    "fabric_year": 34857.76,           # costo-fabric.md, 2
    "fabric_normal": 2891.89,
    "fabric_noprod": 187.71,           # costo-fabric.md, 3
}

# --- One-off: project team by role and phase --------------------------------------------
# (role, phase, people, weeks, share of their time). The hours already priced in #25 (seeding,
# MySQL 8.4 compatibility, cutover script, night windows, rehearsal, cutover and Cali shutdown)
# are left out here so that nothing is counted twice. Phases overlap in the calendar (design runs
# until 13 Nov while construction starts on 19 Oct), so a role that works in both counts each week once.
PHASES = ["Diseño", "Construcción", "Preparación del día 0", "Convivencia y corte", "Estabilización y cierre"]
TEAM = [
    ("Gestión del proyecto", "Diseño", 1, 7, 0.5),
    ("Gestión del proyecto", "Construcción", 1, 5, 0.5),
    ("Gestión del proyecto", "Preparación del día 0", 1, 3, 0.5),
    ("Gestión del proyecto", "Convivencia y corte", 1, 9, 0.5),
    ("Gestión del proyecto", "Estabilización y cierre", 1, 7, 0.5),
    ("Arquitectura", "Diseño", 1, 7, 1.0),
    ("Arquitectura", "Construcción", 1, 5, 0.25),
    ("Arquitectura", "Preparación del día 0", 1, 3, 0.25),
    ("Arquitectura", "Convivencia y corte", 1, 9, 0.25),
    ("Arquitectura", "Estabilización y cierre", 1, 7, 0.25),
    ("Redes y seguridad", "Construcción", 1, 7, 1.0),
    ("Redes y seguridad", "Preparación del día 0", 1, 3, 0.5),
    ("Redes y seguridad", "Convivencia y corte", 1, 9, 0.5),
    ("Ingeniería de IaC y pipeline", "Construcción", 2, 9, 1.0),
    ("Ingeniería de IaC y pipeline", "Preparación del día 0", 1, 3, 0.5),
    ("Ingeniería de IaC y pipeline", "Convivencia y corte", 1, 9, 0.25),
    ("Desarrollo de las adaptaciones", "Construcción", 2, 7, 1.0),
    ("Desarrollo de las adaptaciones", "Preparación del día 0", 2, 3, 0.5),
    ("Desarrollo de las adaptaciones", "Convivencia y corte", 1, 9, 0.25),
    ("Base de datos y migración", "Convivencia y corte", 1, 4, 0.5),
    ("Datos y Fabric", "Convivencia y corte", 2, 8, 0.75),
    ("Datos y Fabric", "Estabilización y cierre", 1, 4, 0.25),
    ("QA y pruebas de carga", "Construcción", 1, 2, 1.0),
    ("QA y pruebas de carga", "Preparación del día 0", 2, 2, 1.0),
    ("QA y pruebas de carga", "Convivencia y corte", 1, 4, 0.5),
    ("Gestión del cambio", "Construcción", 1, 3, 0.5),
    ("Gestión del cambio", "Preparación del día 0", 1, 3, 0.5),
    ("Gestión del cambio", "Convivencia y corte", 1, 9, 0.5),
    ("Gestión del cambio", "Estabilización y cierre", 1, 3, 0.25),
]


def team_hours():
    out = {}
    for role, phase, people, weeks, share in TEAM:
        out.setdefault(role, {p: 0.0 for p in PHASES})[phase] += people * weeks * 40 * share
    return out


TRAINING = [
    ("Cursos con instructor: administración de Azure, seguridad, Fabric, Terraform y GitHub Actions",
     "10 cupos × USD 1.200", 10 * 1200),
    ("Exámenes de certificación", "10 × USD 165", 10 * 165),
    ("Horas de quienes toman los cursos", "10 personas × 32 h × 36,24", 10 * 32 * RATE),
    ("Operación y guardia: runbooks y simulacro de alertas", "6 personas × 16 h × 36,24", 6 * 16 * RATE),
    ("Usuarios clave de despacho y facturación: pruebas con datos replicados", "20 personas × 8 h × 36,24", 20 * 8 * RATE),
    ("Sesión de cambios para los usuarios internos", "450 personas × 0,5 h × 36,24", 450 * 0.5 * RATE),
]

EXTERNAL = [
    ("Partner de Microsoft: revisión Well-Architected del diseño", "40 h × USD 100", 40 * 100),
    ("Partner de Microsoft: acompañamiento del ensayo y del corte", "2 noches × 2 personas × 8 h × USD 100", 2 * 2 * 8 * 100),
    ("Partner de Microsoft: soporte del primer mes en Azure", "24 h × USD 100", 24 * 100),
]

# --- Recurring --------------------------------------------------------------------------
LICENSES = {
    "entra_p1": 6.00,        # per user per month, annual commitment, list price
    "entra_p2": 9.00,
    "github_team": 4.00,
    "support_standard": 100.00,
    "sms": 0.08,             # per message to Colombian mobiles, by quote
}
INTERNAL_USERS, PRIVILEGED_USERS, GITHUB_USERS, SMS_MONTH = 450, 15, 12, 300

OPS_TEAM = [
    ("Ingeniería de plataforma: operación diaria, cambios en ventana, costos y respuesta a incidentes", 1.0),
    ("Seguridad e identidades: Defender, accesos, PIM y revisión de registros", 0.25),
    ("Base de datos: rendimiento, réplica, respaldos y pruebas de continuidad", 0.25),
    ("Datos y Fabric: modelos, Activator, capacidad y licencias", 0.25),
    ("FinOps y gobierno: presupuestos, conciliación mensual y reservas", 0.25),
]
ON_CALL_HOURS = 128 * 52        # nights and weekends of a year, one person available
ON_CALL_PAY = 0.10              # availability paid at 10 % of the hourly rate
INCIDENTS_YEAR, INCIDENT_H, INCIDENT_FACTOR = 24, 3, 1.6   # night or Sunday surcharges, on average


def licenses():
    return [
        ("Entra ID P1: MFA y acceso condicional para los usuarios internos",
         f"{INTERNAL_USERS - PRIVILEGED_USERS} × 6 × 12", (INTERNAL_USERS - PRIVILEGED_USERS) * LICENSES["entra_p1"] * 12),
        ("Entra ID P2: PIM para administradores y aprobadores", f"{PRIVILEGED_USERS} × 9 × 12", PRIVILEGED_USERS * LICENSES["entra_p2"] * 12),
        ("Entra External ID para los clientes del portal", "Sin costo hasta 50.000 usuarios activos al mes", 0.0),
        ("Power BI Pro", "En la línea de Fabric (#27): 40 × 14 × 12", 0.0),
        ("GitHub Team: repositorios, Actions y Environments", f"{GITHUB_USERS} × 4 × 12", GITHUB_USERS * LICENSES["github_team"] * 12),
        ("Terraform", "Versión abierta; el estado vive en Azure Storage (#26)", 0.0),
        ("Mensajes de texto de las alertas nocturnas", f"{SMS_MONTH} × 0,08 × 12", SMS_MONTH * LICENSES["sms"] * 12),
        ("Plan de soporte de Azure Standard", "100 × 12", LICENSES["support_standard"] * 12),
    ]


def operations():
    rows = [(name, f"{fte} × 1.920 h × 36,24", fte * FTE_H * RATE) for name, fte in OPS_TEAM]
    rows.append(("Guardia: disponibilidad de noche y fines de semana",
                 "6.656 h × 10 % × 36,24", ON_CALL_HOURS * ON_CALL_PAY * RATE))
    rows.append(("Guardia: incidentes atendidos", f"{INCIDENTS_YEAR} × {INCIDENT_H} h × 1,6 × 36,24",
                 INCIDENTS_YEAR * INCIDENT_H * INCIDENT_FACTOR * RATE))
    return rows


def cloud_year(y):
    plat = sum(est.total(est.monthly(m)) for m in range(12 * (y - 1) + 1, 12 * y + 1))
    day18 = sum(r[3] for r in est.campaign_rows(est.DISPATCH_H))
    lt = sum(c for _, _, c in est.load_test())
    return plat + est.CAMPAIGN_DAYS * day18 + 3 * lt


def bridge():
    """Costs between the cutover and month 1, and before the cutover, that no other document counts."""
    month1 = est.total(est.monthly(1))
    return [
        ("Plataforma del corte al mes 1: 14 al 28 de febrero de 2027", f"{fmt(month1)} × 14 / 30,42", month1 * 14 / DAY),
        ("Fabric de producción del 15 al 28 de febrero", f"{fmt(FROM_DOCS['fabric_normal'])} × 14 / 30,42", FROM_DOCS["fabric_normal"] * 14 / DAY),
        ("Fabric no productivo antes del corte: 18 de enero al 14 de febrero", "187,71 × 27 / 30,42", FROM_DOCS["fabric_noprod"] * 27 / DAY),
        ("Licencias antes del mes 1: Entra ID desde el día 0 y GitHub desde octubre",
         "(435 × 6 + 15 × 9) × 1,6 meses + 12 × 4 × 5 meses",
         ((INTERNAL_USERS - PRIVILEGED_USERS) * 6 + PRIVILEGED_USERS * 9) * 1.6 + GITHUB_USERS * 4 * 5),
    ]


# --- Savings, five-year sums from the steady-state model ---------------------------------
def five_year(fn):
    return sum(fn(m) for m in range(1, 61))


def cap(d, v):
    return d * 1000 * est.P["cool_grs_gb"] + v * 1000 * est.P["cold_lrs_gb"]


def savings():
    p = est.P
    purge = five_year(lambda m: cap(*est.archive_tb(m, purge=False)) - cap(*est.archive_tb(m)))
    lrs = five_year(lambda m: est.archive_tb(m)[1] * 1000 * (p["cold_grs_gb"] - p["cold_lrs_gb"]))
    old = five_year(lambda m: cap(*est.archive_tb(m)) - cap(*est.archive_tb(m, keep_old=False))
                    + (est.tagged_files(m)[0] - est.tagged_files(m, keep_old=False)[0]) * p["grs_tags_10k"] / 1e4
                    + (est.tagged_files(m)[1] - est.tagged_files(m, keep_old=False)[1]) * p["cold_lrs_tags_10k"] / 1e4)
    tags = five_year(lambda m: est.tagged_files(m)[0] * p["grs_tags_10k"] / 1e4 + est.tagged_files(m)[1] * p["cold_lrs_tags_10k"] / 1e4)
    cold_docs = five_year(lambda m: max(est.archive_tb(m)[0] - 13.2, 0) * 1000 * (p["cool_grs_gb"] - p["cold_grs_gb"]))
    tower = 5 * est.CAMPAIGN_DAYS * (sum(r[3] for r in est.campaign_rows(est.DISPATCH_H)) - sum(r[3] for r in est.campaign_rows()))
    fixed_portal = 3 * est.replica_active_h() * est.H
    portal = 60 * fixed_portal - 5 * est.CAMPAIGN_DAYS * 3 * est.PEAK_H * est.replica_active_h()
    m = 60
    # (decision, obvious alternative, avoided cost text, five-year USD, issue, source, decided?)
    return [
        ("Siembra del archivo con discos propios (Azure Import/Export)", "Copiar 1,2 PB por la red", "Ver sección 3", None, "#15 (F1-11)", "Siembra, 2 y 9.2", True),
        ("Accesos directos de Fabric sobre el archivo", "Copiar el archivo a OneLake", "4.787,90 al mes y 38.223,94 únicos, frente a una copia en Cold", 4787.90 * m + 38223.94, "#17 (F1-13)", "Fabric, 6", True),
        ("Capacidad de pruebas de Fabric pausada fuera del horario", "F4 encendida todo el mes", "337,89 al mes", 337.89 * m, "#18 (F1-14)", "Fabric, 7", True),
        ("Licencias Pro para quien ve reportes internos", "F64 para que todos vean sin licencia", "5.747,20 al mes", 5747.20 * m, "#18 (F1-14)", "Fabric, 7", True),
        ("Escaneo de malware apagado durante la siembra", "Escanear el 1,2 PB al importarlo", "Unos 180.000, una vez", 180000, "#10", "Seguridad, 6.3", True),
        ("Escanear solo fotos y comprobantes", "Escanear también el video", "Unos 1.800 al mes", 1800 * m, "#10", "Seguridad, 6.3", True),
        ("Video importado directo a Cold", "Importar a Hot y mover después", "Unos 15.540: un mes de Hot frente a Cold", 15540, "#15", "Siembra, 9.2", True),
        ("Video en Cold LRS", "Cold GRS", "4.653,27 al mes en el mes 1", lrs, "#15", "Mes estable, 10", True),
        ("Borrado mensual a los cinco años, con la fecha original", "Contar desde la importación o no borrar", "Hasta 4.068 al mes en el año 5", purge, "#15", "Mes estable, 4.3", True),
        ("DDoS IP Protection solo para la IP del portal", "DDoS Network Protection", "2.744,55 al mes", 2744.55 * m, "#9", "Firewall, 7.2", True),
        ("Azure Firewall Standard", "Premium desde el inicio", "365 al mes", 365 * m, "#9", "Firewall, 7.2", True),
        ("Application Gateway como única entrada del portal", "Front Door Premium delante", "Al menos 330 al mes", 330 * m, "#9", "Firewall, 7.2", True),
        ("Gateways de pruebas y desarrollo desde 0 instancias, y desarrollo sin WAF", "Una instancia reservada y WAF en cada uno", "210,24 + 116,80 al mes", (210.24 + 116.80) * m, "#9", "Firewall, 7.2", True),
        ("VPN Gateway con hub propio", "Virtual WAN Standard", "Al menos 562 al mes", 562 * m, "#8", "Red, 2.1", True),
        ("VPN con segundo proveedor en Cali", "ExpressRoute", "Unos 1.272 al mes", 1272 * m, "#8", "Red, 2.2", True),
        ("Historial de telemetría en el lago, leído por Fabric", "Clúster de Azure Data Explorer", "Más de 321 al mes", 321 * m, "#13", "Telemetría, 6.5", True),
        ("Stream Analytics de 1/3 de unidad", "Una unidad completa", "160,60 al mes", 160.60 * m, "#13", "Telemetría, 6.5", True),
        ("Muestreo del 10 % en las trazas", "Muestreo por defecto", "Unos 259 al mes", 259 * m, "#16", "Observabilidad, 9.3", True),
        ("Workbooks y vistas de Cost Management", "Managed Grafana", "Unos 115 al mes", 115 * m, "#16", "Observabilidad, 9.3", True),
        ("Portal en consumo, que escala solo con la concurrencia", "3 réplicas fijas para el pico de campaña", f"{fmt(fixed_portal)} al mes, menos las horas de pico", portal, "#14", "Mes estable, 3.3 y 5.2", True),
        ("Bases de pruebas y desarrollo en Burstable y sin datos de producción", "Dos servidores de 4 vCores", "Unos 500 al mes", 500 * m, "#14", "Migración, 9", True),
        ("Ensayo en un servidor temporal que se borra", "Preproducción permanente", "Unos 310 al mes", 310 * m, "#14", "Migración, 9", True),
        ("Plataforma al mínimo hasta el corte", "La torre con 4 nodos desde el despliegue", "Unos 920, una vez", 920, "#14", "Migración, 9", True),
        ("DMS dentro de los 183 días sin costo", "Crearlo antes o mantenerlo después", "224,84 por mes fuera del plazo", 224.84, "#14", "Migración, 9", True),
        ("Copia del archivo fuera del firewall durante la convivencia", "Pasarla por el firewall", "Unos 194 al mes, dos meses", 2 * 194, "#8", "Red, 6.3", True),
        ("Borrar lo de más de cinco años", "Guardarlo hasta que FríoAndes decida", "Unos 3.000 al mes", old, "#15 y #26", "Mes estable, 10", False),
        ("Fecha original como metadato, leída del inventario", "Etiqueta de índice por archivo", "768,74 al mes en el mes 1", tags, "#15 y #26", "Mes estable, 10", False),
        ("Documentos de más de un año a Cold GRS", "Todo en Cool GRS", "Unos 1.633 al mes", cold_docs, "#15 y #26", "Mes estable, 10", False),
        ("F8 fuera de campaña, si la medición lo permite", "F16 todo el año", "8.363,52 al año", 5 * 8363.52, "#18 y #27", "Fabric, 7", False),
        ("Reserva de 8 CU de Fabric por un año, renovada", "Todo en pago por uso", "5.110,40 al año", 5 * 5110.40, "#27", "Fabric, 7", False),
        ("Regla de la torre acotada a la franja del pico", "04:00 a 22:00", "Unos 880 al año", tower, "#14 y #26", "Mes estable, 5.4", False),
        ("Centros hacia la torre de Cali por su VPN hasta el corte", "Tránsito por Azure (FW-401)", "Unos 670, una vez", 670, "#8, #9 y #25", "Migración, 9", False),
    ]


def seeding_alternative():
    """What the network copy would have cost in Azure alone, if the 90 days did not exist."""
    extra_days = 278 - 62
    coexist = extra_days * (FROM_DOCS["pre_cutover_month"] + FROM_DOCS["isp2_month"]) / DAY
    pe = 1_200_000 * est.P["pe_gb"]
    vpn = 9 * 241
    return [
        ("Dos plataformas a la vez 216 días más (278 de copia frente a 62 hasta el apagado)",
         f"{fmt(FROM_DOCS['pre_cutover_month'] + FROM_DOCS['isp2_month'])} al mes × 216 días", coexist),
        ("Procesamiento del endpoint privado de 1,2 PB", "1.200.000 GB × 0,01", pe),
        ("VPN Gateway VpnGw2AZ durante la copia", "241 más al mes × 9 meses", vpn),
    ]


def fmt(x, d=2):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def table(title, rows, unit="USD"):
    print(f"\n#### {title}\n\n| Concepto | Cálculo | {unit} |\n|---|---|---|")
    t = 0
    for a, b, c in rows:
        print(f"| {a} | {b} | {fmt(c)} |")
        t += c
    print(f"| **Subtotal** | | **{fmt(t)}** |")
    return t


def main():
    print(f"Tarifa: USD {fmt(RATE)} por hora")
    hours = team_hours()
    print("\n#### Horas del equipo del proyecto por rol y fase\n")
    print("| Rol | " + " | ".join(PHASES) + " | Horas | USD |")
    print("|---|" + "---|" * (len(PHASES) + 2))
    t_hours = t_team = 0
    for role, ph in hours.items():
        h = sum(ph.values())
        t_hours += h
        t_team += h * RATE
        print(f"| {role} | " + " | ".join(fmt(ph[p], 0) if ph[p] else "—" for p in PHASES) + f" | {fmt(h, 0)} | {fmt(h * RATE)} |")
    col = {p: sum(ph[p] for ph in hours.values()) for p in PHASES}
    print("| **Total** | " + " | ".join(f"**{fmt(col[p], 0)}**" for p in PHASES) + f" | **{fmt(t_hours, 0)}** | **{fmt(t_team)}** |")
    t_train = table("Capacitación del equipo de FríoAndes", TRAINING)
    t_ext = table("Consultoría externa", EXTERNAL)
    t_bridge = table("Costos que caen entre documentos", bridge())
    new = t_team + t_train + t_ext + t_bridge
    cont = CONTINGENCY * new
    one_off = new + cont + FROM_DOCS["migration_total"]
    print(f"\nNuevos únicos {fmt(new)}; contingencia {fmt(cont)}; migración #25 {fmt(FROM_DOCS['migration_total'])}; total único {fmt(one_off)}")
    print(f"COP {fmt(one_off * COP_PER_USD / 1e6, 0)} millones")

    t_lic = table("Licencias, herramientas y soporte, al año", licenses())
    t_ops = table("Equipo de operación de la plataforma, al año", operations())
    print("\n#### Recurrente por año\n")
    print("| Año | Nube (#26) | Fabric (#27) | Licencias y soporte | Operación | Total |\n|---|---|---|---|---|---|")
    years = []
    for y in range(1, 6):
        c = cloud_year(y)
        r = c + FROM_DOCS["fabric_year"] + t_lic + t_ops
        years.append((c, r))
        print(f"| {y} | {fmt(c)} | {fmt(FROM_DOCS['fabric_year'])} | {fmt(t_lic)} | {fmt(t_ops)} | {fmt(r)} |")
    print("\n#### TCO\n")
    print("| Horizonte | Únicos | Recurrentes | Total | COP millones | Por mes |\n|---|---|---|---|---|---|")
    for n in (1, 3, 5):
        rec = sum(r for _, r in years[:n])
        tot = one_off + rec
        print(f"| {n} año(s) | {fmt(one_off)} | {fmt(rec)} | {fmt(tot)} | {fmt(tot * COP_PER_USD / 1e6, 0)} | {fmt(tot / (12 * n))} |")
    tco5 = one_off + sum(r for _, r in years)
    ops5 = 5 * t_ops
    print(f"\nPunto de equilibrio con Cali (sin operación): {fmt((tco5 - ops5) / 60)} al mes; con operación {fmt(tco5 / 60)}")
    shares = {"Nube": sum(c for c, _ in years), "Fabric": 5 * FROM_DOCS["fabric_year"], "Licencias": 5 * t_lic,
              "Operación": ops5, "Migración #25": FROM_DOCS["migration_total"], "Proyecto nuevo": new + cont}
    for k, v in shares.items():
        print(f"  {k}: {fmt(v)} ({v / tco5 * 100:.1f} %)")

    print("\n#### Decisiones\n")
    rows = savings()
    dec = sum(r[3] for r in rows if r[6] and r[3])
    prop = sum(r[3] for r in rows if not r[6])
    for r in rows:
        print(f"| {r[0]} | {r[1]} | {r[2]} | {fmt(r[3]) if r[3] is not None else '—'} | {r[4]} | {r[5]} | {'decidida' if r[6] else 'propuesta'} |")
    print(f"Decididas en 5 años: {fmt(dec)}; propuestas: {fmt(prop)}")
    table("Alternativa por red de la siembra, solo lo de Azure", seeding_alternative())


if __name__ == "__main__":
    main()

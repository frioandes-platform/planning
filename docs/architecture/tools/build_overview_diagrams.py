#!/usr/bin/env python3
"""Build the draw.io diagrams of the consolidated architecture document (issue #19):

- solucion-vista-general: the whole solution in one view, with the eight domains of the challenge numbered.
- ambientes-pipeline: the three environments and how the pipeline promotes a change between them.
- cronograma-proyecto: project schedule from the design to the closure, against campaigns and milestones.

Imports the Diagram helper and the Azure icon set from
docs/architecture/red/tools/build_drawio_diagrams.py, so all diagrams share one style.

Usage:
    python3 build_overview_diagrams.py --out ../diagramas

Export to PNG with the draw.io desktop CLI:

    drawio --disable-gpu -x -f png -e -b 20 -s 1.5 -o ../diagramas/NAME.drawio.png ../diagramas/NAME.drawio
"""
import argparse
import base64
import datetime as dt
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep red/tools free of __pycache__
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "red" / "tools"))
from build_drawio_diagrams import C_FABRIC, C_OK, C_TEMP, C_TRUCK, ICON, Diagram  # noqa: E402

LOGO = Path(__file__).resolve().parents[2] / "design" / "brand" / "logo" / "logo-principal.png"
AZ = "img/lib/azure2/"
ICON.update({
    "entra": AZ + "identity/Azure_Active_Directory.svg",
    "policy": AZ + "management_governance/Policy.svg",
    "mgmt_group": AZ + "general/Management_Groups.svg",
    "devops": AZ + "devops/Azure_DevOps.svg",
    "acr": AZ + "containers/Container_Registries.svg",
})

HEAD = "#455A64"
# Brand colors from docs/design/brand/tokens.json.
NAVY, TEAL, ICE = "#0A1F2E", "#0D7894", "#DDF3F8"


def badge(d, x, y, n):
    d.box(x, y, 26, 26, str(n), NAVY, NAVY, font=12, color="#FFFFFF", bold=True)


def logo(d, x, y, w):
    data = base64.b64encode(LOGO.read_bytes()).decode()
    h = round(w * 288 / 1077)
    d.cells.append(f'<mxCell id="logo" value="" style="shape=image;html=1;imageAspect=1;aspect=fixed;image=data:image/png,{data};" '
                   f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')


def solution_overview():
    d = Diagram()
    d.text(20, -50, 1500, 30, "FríoAndes en Azure: la solución completa y los ocho puntos del reto", font=16)

    # Colombia: the sites, the fleet and the people that reach the platform.
    d.zone(20, 40, 300, 1000, "Colombia", fill="#FAFAFA", stroke="#757575", font=13)
    d.zone(40, 80, 260, 290, "Datacenter de Cali (hasta el día 62)", fill="#FFFFFF", stroke="#9E9E9E", font=11)
    d.icon(70, 120, "server_farm", "VMware y núcleo\nactual", label_w=110)
    cali_fw = d.icon(200, 120, "cali_fw", "Firewall de Cali\n2 proveedores", label_w=110)
    cali_db = d.icon(70, 250, "mysql", "MySQL 5.7", label_w=110)
    cali_ar = d.icon(200, 250, "files", "Archivo de 1,2 PB\nFTP y NFS", label_w=120)
    d.zone(40, 400, 260, 150, "8 centros regionales", fill="#FFFFFF", stroke="#9E9E9E", font=11)
    d.icon(70, 440, "users_az", "Usuarios", label_w=100)
    centers = d.icon(200, 440, "sensor", "32 cuartos fríos", label_w=110)
    d.zone(40, 580, 260, 140, "Flota", fill="#FFFFFF", stroke="#9E9E9E", font=11)
    trucks = d.icon(140, 615, "mobile_az", "120 camiones (180 en campaña)\nred móvil del operador", label_w=200)
    d.zone(40, 750, 260, 130, "Internet", fill="#FFFFFF", stroke="#9E9E9E", font=11)
    clients = d.icon(140, 785, "browser", "2.000 clientes corporativos\nportal de rastreo", label_w=200)
    d.zone(40, 910, 260, 110, "Fuera de la sede", fill="#FFFFFF", stroke="#9E9E9E", font=11)
    remote = d.icon(140, 932, "users_az", "Desarrollo y operación remotos", label_w=200)

    # Azure East US 2.
    d.zone(380, 40, 960, 1000, "Azure · East US 2 (región principal)", fill="#F3F8FD", stroke="#1565C0", font=13)

    # 1. Governance band.
    d.zone(400, 76, 920, 110, "Gobierno: un tenant de Entra ID, mg-frioandes, cinco suscripciones, Azure Policy, etiquetas y presupuestos",
           fill="#FFFFFF", stroke=NAVY, font=11)
    badge(d, 1282, 82, 1)
    d.icon(420, 110, "entra", "", size=40)
    d.icon(470, 110, "mgmt_group", "", size=40)
    d.icon(520, 110, "policy", "", size=40)
    for i, s in enumerate(["sub-fa-security", "sub-fa-connectivity", "sub-fa-prod", "sub-fa-test", "sub-fa-dev"]):
        d.box(580 + i * 146, 116, 138, 34, s, ICE, TEAL, font=10)
    d.text(580, 154, 720, 26, "Auditoría de cinco años para datos de clientes, evidencias y temperatura · facturación interna por etiqueta", font=10)

    # 3. Hub.
    d.zone(400, 210, 270, 440, "Hub · sub-fa-connectivity\nvnet-hub 10.100.0.0/23", fill="#FFFFFF", stroke="#1565C0", font=11)
    badge(d, 632, 216, 3)
    vpngw = d.icon(430, 270, "vpngw", "VPN Gateway\nVpnGw1AZ", label_w=110)
    fw = d.icon(570, 270, "firewall", "Azure Firewall\nStandard", label_w=110)
    bastion = d.icon(430, 420, "bastion", "Bastion\nStandard", label_w=110)
    d.icon(570, 420, "dns", "DNS Private\nResolver", label_w=110)
    d.text(410, 560, 250, 80, "Punto de interconexión, DNS e identidad listos para una segunda nube a 24 meses", font=10, color="#455A64")

    # 5. Production spoke (part A and the cloud side of part B).
    d.zone(700, 210, 620, 440, "Producción · sub-fa-prod · 10.101.0.0/21", fill="#FFFFFF", stroke="#1565C0", font=11)
    badge(d, 1282, 216, 5)
    appgw = d.icon(730, 270, "appgw", "Application Gateway\nWAF v2", label_w=130)
    portal = d.icon(870, 270, "aca", "Portal\nContainer Apps", label_w=110)
    tower = d.icon(1000, 270, "aca", "Torre de control\nContainer Apps", label_w=120)
    asa = d.icon(1120, 270, "asa", "Stream Analytics\nreglas de alerta", label_w=120)
    db = d.icon(730, 420, "mysql", "MySQL Flexible 8.4\nHA zonal", label_w=130)
    d.icon(870, 420, "redis", "Managed Redis", label_w=110)
    archive = d.icon(1000, 420, "storage", "Archivo y evidencias\ninmutables, 5 años", label_w=130)
    d.icon(1240, 270, "func", "Función\nnotificadora", label_w=100)
    d.text(720, 560, 590, 80, "Torre solo desde la red corporativa · portal solo por el WAF · un Key Vault por ambiente · "
           "RPO y RTO con réplica en Central US", font=10, color="#455A64")

    # Non-production environments.
    d.zone(400, 680, 440, 100, "Pruebas 10.102.0.0/21 · Desarrollo 10.103.0.0/21", fill="#FFFFFF", stroke="#1565C0", font=11)
    d.text(415, 710, 410, 60, "La misma estructura que producción, desde el mismo código, con datos sintéticos y sin sensores reales", font=10)

    # 2 and 6. Security and observability.
    d.zone(870, 680, 450, 170, "Seguridad y observabilidad · sub-fa-security", fill="#FFFFFF", stroke=NAVY, font=11)
    badge(d, 1250, 686, 2)
    badge(d, 1282, 686, 6)
    d.icon(895, 725, "pim", "MFA, acceso\ncondicional y PIM", label_w=110)
    d.icon(1005, 725, "kv", "Key Vault\npor ambiente", label_w=100)
    d.icon(1110, 725, "defender", "Defender\nfor Cloud", label_w=100)
    d.icon(1215, 725, "monitor", "Log Analytics y\nAzure Monitor", label_w=110)

    # 4. Automation.
    d.zone(400, 810, 440, 210, "Automatización y cambio", fill="#FFFFFF", stroke=NAVY, font=11)
    badge(d, 802, 816, 4)
    steps = ["Build", "plan", "Aprobación", "apply"]
    for i, s in enumerate(steps):
        d.box(420 + i * 102, 850, 90, 34, s, ICE, TEAL, font=10)
    for i in range(3):
        d.edge(None, None, [(510 + i * 102, 867), (522 + i * 102, 867)], color=TEAL)
    d.text(420, 894, 405, 116, "GitHub Actions y Terraform (repo iac) · OIDC, sin secretos en el repo · "
           "dev → test → prod con aprobación · sin cambios productivos de 04:00 a 22:00 ni en campaña · "
           "release notes de aplicación y de infraestructura", font=10)

    # 5C. Migration.
    d.zone(870, 870, 450, 150, "Migración del núcleo: 90 días, corte el 14 de febrero de 2027", fill="#FFFFFF", stroke=C_TEMP, font=11)
    dms = d.icon(905, 910, "dms", "DMS en línea\nMySQL 5.7 → 8.4", label_w=100)
    disks = d.icon(1040, 910, "files", "Import/Export\n71 discos de 20 TB", label_w=150, side="right")

    # Central US.
    d.zone(1400, 40, 480, 300, "Azure · Central US (región pareja)", fill="#F3F8FD", stroke="#1565C0", font=13)
    iothub = d.icon(1440, 100, "iothub", "IoT Hub y DPS\nzonas de disponibilidad", label_w=150)
    d.icon(1600, 100, "mysql", "Réplica de\nMySQL", label_w=100)
    d.icon(1740, 100, "aca", "Front de continuidad\nse activa en el runbook", label_w=150)
    d.icon(1430, 230, "storage", "Evidencia cruda\nde temperatura", label_w=130)
    d.text(1580, 220, 290, 100, "Ingesta de la telemetría en la región con zonas; alerta visible en 60 segundos o menos", font=10, color="#455A64")

    # 7. Fabric.
    d.zone(1400, 370, 480, 360, "Microsoft Fabric · capacidad F16 en East US 2", fill="#F7F0FB", stroke=C_FABRIC, font=13)
    badge(d, 1842, 376, 7)
    copyjob = d.icon(1430, 430, "copyjob", "Copy Job desde\nla base, sin datos\nque no se usan", label_w=130)
    onelake = d.icon(1590, 430, "onelake", "OneLake\naccesos directos\nal archivo", label_w=130)
    d.icon(1750, 430, "alerts", "Activator\naviso temprano", label_w=110)
    d.icon(1430, 600, "pbi_embedded", "Reportes de torre,\ncalidad y cliente", label_w=130)
    d.icon(1590, 600, "semantic", "Hora estimada\nde llegada", label_w=120)
    d.icon(1750, 600, "storage", "Fotos ilegibles\no dañadas", label_w=110)

    # 8. Design system.
    d.zone(1400, 760, 480, 280, "Sistema de diseño", fill="#FFFFFF", stroke=NAVY, font=13)
    badge(d, 1842, 766, 8)
    logo(d, 1440, 810, 300)
    d.text(1430, 910, 430, 110, "Logo, paleta con los estados de la operación, tipografía, componentes y reglas de uso: "
           "la torre de noche, el portal de día y las notas de versión se reconocen como la misma empresa", font=10)

    # Flows. Steady state in green, migration in blue (dashed), telemetry in orange, Fabric in purple.
    d.edge(cali_fw[0], vpngw[0], [(256, 140), (345, 140), (345, 290), (430, 290)], color=C_OK,
           label="Túneles IPsec", label_pos=(255, 118, 90))
    d.edge(centers[0], vpngw[0], [(256, 468), (360, 468), (360, 310), (430, 310)], color=C_OK,
           label="VPN de cada centro", label_pos=(250, 444, 110))
    d.edge(clients[0], appgw[0], [(196, 813), (330, 813), (330, 198), (758, 198), (758, 270)], color=C_OK,
           label="HTTPS", label_pos=(335, 200, 60))
    d.edge(trucks[0], iothub[0], [(196, 643), (315, 643), (315, 24), (1385, 24), (1385, 112), (1440, 112)], color=C_TRUCK,
           label="MQTT sobre TLS por internet", label_pos=(700, 6, 220))
    d.edge(remote[0], bastion[0], [(196, 960), (370, 960), (370, 448), (430, 448)], color=C_OK,
           label="Entra ID y MFA", label_pos=(372, 640, 100))
    d.edge(vpngw[0], fw[0], [(486, 298), (570, 298)], color=C_OK)
    d.edge(fw[0], tower[0], [(626, 285), (685, 285), (685, 250), (1028, 250), (1028, 270)], color=C_OK,
           label="Solo red corporativa", label_pos=(860, 240, 130))
    d.edge(appgw[0], portal[0], [(786, 298), (870, 298)], color=C_OK)
    d.edge(iothub[0], asa[0], [(1440, 140), (1365, 140), (1365, 200), (1148, 200), (1148, 270)], color=C_TRUCK,
           label="Lecturas", label_pos=(1200, 180, 80))
    d.edge(db[0], copyjob[0], [(786, 440), (850, 440), (850, 395), (1390, 395), (1390, 458), (1430, 458)], color=C_FABRIC,
           label="Copia incremental", label_pos=(1240, 375, 120))
    d.edge(archive[0], onelake[0], [(1056, 448), (1375, 448), (1375, 410), (1618, 410), (1618, 430)], color=C_FABRIC,
           label="Sin copiar 1,2 PB", label_pos=(1230, 426, 120))
    d.edge(cali_db[0], dms[0], [(98, 306), (98, 352), (350, 352), (350, 1028), (880, 1028), (880, 938), (905, 938)], color=C_TEMP, dashed=True)
    d.edge(cali_ar[0], disks[0], [(256, 278), (338, 278), (338, 1034), (1020, 1034), (1020, 938), (1040, 938)], color=C_TEMP, dashed=True)

    ly = 1070
    for i, (color, dashed, txt) in enumerate([(C_OK, False, "Tráfico en estado estable"), (C_TRUCK, False, "Telemetría"),
                                             (C_FABRIC, False, "Datos hacia Fabric"), (C_TEMP, True, "Migración, temporal")]):
        d.edge(None, None, [(40 + i * 300, ly + 9), (90 + i * 300, ly + 9)], color=color, dashed=dashed)
        d.text(98 + i * 300, ly - 4, 200, 26, txt, font=10)
    badge(d, 1240, ly - 4, "n")
    d.text(1272, ly - 4, 520, 26, "Punto del reto que desarrolla cada capítulo del documento", font=10)
    return d


def environments_pipeline():
    d = Diagram()
    d.text(20, -40, 1500, 30, "Ambientes y promoción: el mismo código y la misma imagen, de desarrollo a producción", font=16)

    d.zone(20, 40, 300, 560, "GitHub · frioandes-platform", fill="#FAFAFA", stroke="#757575", font=12)
    d.box(40, 120, 125, 80, "Repositorio iac\nmódulos y\nenvironments/", "#FFFFFF", "#9E9E9E", font=10)
    d.box(175, 120, 125, 80, "Repositorio de\nla aplicación\ncontenedores", "#FFFFFF", "#9E9E9E", font=10)
    d.box(50, 290, 240, 110, "GitHub Actions\nvalidación, verificadores,\nplan, build, apply", ICE, TEAL, font=11, bold=True)
    d.box(50, 440, 240, 130, "Bloqueo de producción\nsolo de 22:00 a 04:00,\nfuera de campaña;\nincidente con aprobación\nde seguridad", "#FFEBEE", "#C62828", font=10)
    d.edge(None, None, [(102, 200), (102, 290)], color=HEAD)
    d.edge(None, None, [(238, 200), (238, 290)], color=HEAD)
    d.edge(None, None, [(170, 400), (170, 440)], color="#C62828", dashed=True)

    acr = d.icon(420, 80, "acr", "Registro de contenedores\nuna imagen, un digest", label_w=180)
    d.icon(420, 470, "entra", "Una identidad por ambiente\nfederada con OIDC", label_w=200)
    d.edge(None, None, [(290, 330), (380, 330), (380, 108), (420, 108)], color=HEAD, label="push", label_pos=(330, 310, 50))

    envs = [("Desarrollo", "sub-fa-dev", "10.103.0.0/21", "Datos sintéticos", 600, "Automático al merge"),
            ("Pruebas", "sub-fa-test", "10.102.0.0/21", "Sintéticos o anonimizados; sensores simulados", 990, "Automático, con pruebas"),
            ("Producción", "sub-fa-prod", "10.101.0.0/21", "Datos reales", 1380, "Aprobación de 2 personas del comité\ncon la release note")]
    for name, sub, net, data, x, gate in envs:
        d.zone(x, 180, 340, 420, f"{name} · {sub}\n{net}", fill="#F3F8FD", stroke="#1565C0", font=12)
        d.icon(x + 30, 250, "aca", "Container Apps", label_w=110)
        d.icon(x + 140, 250, "mysql", "MySQL Flexible", label_w=110)
        d.icon(x + 250, 250, "kv", "Key Vault", label_w=90)
        d.icon(x + 30, 370, "storage", "Estado de\nTerraform", label_w=100)
        d.icon(x + 140, 370, "firewall", "Reglas y NSG\ndel ambiente", label_w=110)
        d.icon(x + 250, 370, "vm", "Ejecutor en\nsnet-admin", label_w=90)
        d.text(x + 15, 480, 310, 40, data, font=10, color="#455A64")
        d.box(x + 15, 530, 310, 50, gate, ICE if name != "Producción" else "#FFEBEE", TEAL if name != "Producción" else "#C62828", font=10)
    d.edge(None, None, [(290, 345), (560, 345), (560, 430), (600, 430)], color=TEAL, label="apply", label_pos=(470, 325, 60))
    d.edge(None, None, [(940, 430), (990, 430)], color=TEAL, label="promoción", label_pos=(925, 405, 80))
    d.edge(None, None, [(1330, 430), (1380, 430)], color="#C62828", label="aprobación", label_pos=(1315, 405, 80))
    d.edge(None, None, [(476, 108), (1540, 108), (1540, 180)], color=HEAD, dashed=True,
           label="La misma imagen llega a los tres ambientes", label_pos=(900, 88, 300))
    d.edge(None, None, [(756, 108), (756, 180)], color=HEAD, dashed=True)
    d.edge(None, None, [(1146, 108), (1146, 180)], color=HEAD, dashed=True)
    return d


def project_schedule():
    d = Diagram()
    D = dt.date
    start, end = D(2026, 9, 28), D(2027, 5, 3)
    x0, px, y0, rh = 360, 7, 120, 34

    def x(day):
        return x0 + (day - start).days * px

    rows = [
        ("group", "Diseño y planeación"),
        ("Arquitectura, costos y cambio", "Arquitecto cloud"),
        ("Gestión del proyecto", "Gerente de proyecto"),
        ("group", "Plataforma"),
        ("Código de infraestructura y pipeline", "Equipo de plataforma"),
        ("Landing zone, identidades y políticas", "Equipo de plataforma"),
        ("Despliegue de los ambientes", "Equipo de plataforma"),
        ("Observabilidad en Azure y Zabbix", "Equipo de plataforma"),
        ("group", "Aplicación y datos"),
        ("Adaptaciones de la aplicación", "Equipo de aplicación"),
        ("Pruebas de carga, seguridad y continuidad", "QA"),
        ("Siembra del archivo de 1,2 PB", "Base de datos y migración"),
        ("group", "Migración"),
        ("Convivencia: centros y telemetría", "Equipo de plataforma"),
        ("Replicación de la base con DMS", "Base de datos y migración"),
        ("Ensayo y corte", "Líder del corte"),
        ("Vuelta atrás y apagado de Cali", "Equipo de plataforma"),
        ("group", "Fabric y cierre"),
        ("Microsoft Fabric, primer release", "Equipo de datos e IA"),
        ("Capacitación y gestión del cambio", "Gestión del cambio"),
        ("Estabilización y cierre", "Gerente de proyecto"),
    ]
    height = len(rows) * rh
    width = x(end) - x0
    d.text(20, -30, 1700, 30, "Cronograma general del proyecto, de septiembre de 2026 a mayo de 2027", font=16)

    for a, b, name in [(D(2026, 11, 15), D(2027, 1, 11), "Campaña de fin de año"), (D(2027, 3, 15), D(2027, 3, 29), "Semana Santa")]:
        d.zone(x(a), y0 - 10, x(b) - x(a), height + 20, name, fill="#FFEBEE", stroke="#FFCDD2", font=10, bold=False)
    d.zone(x(D(2027, 1, 11)), y0 - 38, x(D(2027, 4, 12)) - x(D(2027, 1, 11)), 22, "Convivencia: 90 días",
           fill="#E3F2FD", stroke="#BBDEFB", font=10, bold=False)

    months = [D(2026, 10, 1), D(2026, 11, 1), D(2026, 12, 1), D(2027, 1, 1), D(2027, 2, 1), D(2027, 3, 1), D(2027, 4, 1), D(2027, 5, 1)]
    names = ["octubre", "noviembre", "diciembre", "enero", "febrero", "marzo", "abril", "mayo"]
    for m, name in zip(months, names):
        d.box(x(m), 58, 1, 14, "", HEAD, HEAD)
        d.text(x(m) + 4, 50, 110, 22, name, font=11, color=HEAD)
    d.box(x0, 72, width, 2, "", HEAD, HEAD)

    d.text(20, 80, 200, 26, "Fase", font=11, color=HEAD)
    d.text(230, 80, 130, 26, "Responsable", font=11, color=HEAD)
    for r, (name, owner) in enumerate(rows):
        y = y0 + r * rh
        if name == "group":
            d.text(20, y, 330, rh, owner, font=11, color=NAVY)
            d.box(20, y + rh - 4, x0 - 30 + width, 1, "", "#B0BEC5", "#B0BEC5")
            continue
        d.text(30, y, 200, rh, name, font=10)
        d.text(230, y, 130, rh, owner, font=9, color="#455A64")
        d.box(x0, y + rh - 1, width, 1, "", "#EEEEEE", "#EEEEEE")

    plan = ("#ECEFF1", "#607D8B")
    build = ("#DCEDC8", "#558B2F")
    temp = ("#BBDEFB", "#1565C0")
    run = ("#C8E6C9", "#2E7D32")
    stand = ("#FFE0B2", "#EF6C00")
    fabric = ("#E1BEE7", "#6A1B9A")

    def bar(r, a, b, style, label=""):
        d.box(x(a), y0 + r * rh + 6, max(x(b) - x(a), 4), rh - 12, label, *style, font=9)

    milestones = [(D(2026, 11, 13), "Diseño\naprobado", HEAD), (D(2027, 1, 11), "Día 0", "#1565C0"),
                  (D(2027, 1, 31), "Ensayo", "#EF6C00"), (D(2027, 2, 14), "Corte", "#B71C1C"),
                  (D(2027, 3, 14), "Cali\napagada", "#424242"), (D(2027, 4, 11), "Día 90", "#1565C0"),
                  (D(2027, 4, 30), "Cierre", HEAD)]
    for m, label, color in milestones:
        d.box(x(m), y0 - 22, 2, height + 30, "", color, color)
        d.text(x(m) - 40, y0 + height + 10, 80, 34, label, font=10, color=color, align="center")

    bar(1, D(2026, 9, 28), D(2026, 10, 31), plan, "Fase 1: arquitectura")
    bar(1, D(2026, 10, 31), D(2026, 11, 14), plan, "Costos y cambio")
    bar(2, D(2026, 9, 28), D(2027, 4, 30), plan, "Seguimiento semanal, riesgos, presupuesto y comité de cambios")
    bar(4, D(2026, 10, 19), D(2026, 11, 28), build, "Terraform y GitHub Actions")
    bar(5, D(2026, 11, 2), D(2026, 11, 28), build, "Suscripciones, PIM")
    bar(6, D(2026, 12, 1), D(2026, 12, 5), build)
    bar(6, D(2026, 12, 14), D(2026, 12, 19), build)
    bar(6, D(2026, 12, 19), D(2027, 1, 11), ("#F5F5F5", "#BDBDBD"), "Prod sin usuarios")
    bar(7, D(2026, 12, 14), D(2027, 3, 14), run, "Azure Monitor en paralelo con Zabbix")
    bar(9, D(2026, 11, 2), D(2026, 12, 19), build, "Blob, MySQL 8.4, Fabric")
    bar(9, D(2026, 12, 19), D(2027, 1, 9), temp, "En pruebas")
    bar(10, D(2026, 12, 28), D(2027, 1, 9), temp, "2.000 rpm")
    bar(11, D(2026, 10, 13), D(2026, 10, 20), plan, "Preparación")
    bar(11, D(2026, 10, 20), D(2027, 1, 24), temp, "Nueve trabajos de discos")
    bar(11, D(2027, 1, 25), D(2027, 1, 30), fabric)
    bar(13, D(2027, 1, 11), D(2027, 1, 31), temp, "Centros y camiones")
    bar(14, D(2027, 1, 16), D(2027, 2, 14), temp, "Carga inicial y réplica")
    bar(15, D(2027, 1, 31), D(2027, 2, 1), stand)
    bar(15, D(2027, 2, 14), D(2027, 2, 15), ("#FFCDD2", "#B71C1C"))
    bar(16, D(2027, 2, 15), D(2027, 3, 8), stand, "Cali en espera")
    bar(16, D(2027, 3, 8), D(2027, 3, 15), ("#E0E0E0", "#757575"), "Apagado")
    bar(18, D(2027, 1, 18), D(2027, 2, 13), fabric, "En no productivo")
    bar(18, D(2027, 2, 15), D(2027, 3, 13), fabric, "Producción")
    bar(18, D(2027, 3, 29), D(2027, 4, 24), ("#F3E5F5", "#6A1B9A"), "Medición y tamaño")
    bar(19, D(2026, 11, 30), D(2027, 1, 9), build, "Operación y guardia")
    bar(19, D(2027, 1, 17), D(2027, 1, 31), temp, "Usuarios clave")
    bar(20, D(2027, 3, 15), D(2027, 4, 12), run, "Margen del día 90")
    bar(20, D(2027, 4, 12), D(2027, 5, 1), plan, "Cierre")

    ly = y0 + height + 60
    for i, (style, txt) in enumerate([(plan, "Planeación y gestión"), (build, "Construcción"), (temp, "Migración y pruebas"),
                                      (run, "En operación"), (stand, "En espera para volver atrás"), (fabric, "Fabric y conciliación")]):
        d.box(x0 + i * 230, ly, 24, 18, "", *style)
        d.text(x0 + i * 230 + 30, ly - 4, 196, 26, txt, font=10)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in [("solucion-vista-general", solution_overview),
                     ("ambientes-pipeline", environments_pipeline),
                     ("cronograma-proyecto", project_schedule)]:
        (out / f"{name}.drawio").write_text(fn().xml(), encoding="utf-8")
        print(out / f"{name}.drawio")


if __name__ == "__main__":
    main()

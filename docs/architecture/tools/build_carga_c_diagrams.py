#!/usr/bin/env python3
"""Build the draw.io diagrams of the core migration (issue #14) and the archive seeding (issue #15):

- carga-c-14-p1-de-cali-a-azure: decision and Azure destination of each Cali piece.
- carga-c-14-p2-calendario: state of each piece in each phase of the coexistence.
- carga-c-15-p1-caminos: the two paths of the archive, disks with Import/Export and the continuous copy.
- carga-c-15-p2-cronograma: seeding schedule, job by job, against the migration milestones.

Imports the Diagram helper and the Azure icon set from
docs/architecture/red/tools/build_drawio_diagrams.py, so all diagrams share one style.

Usage:
    python3 build_carga_c_diagrams.py --out ../diagramas

Export to PNG with the draw.io desktop CLI:

    drawio --disable-gpu -x -f png -e -b 20 -s 1.5 -o ../diagramas/NAME.drawio.png ../diagramas/NAME.drawio
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep red/tools free of __pycache__
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "red" / "tools"))
from build_drawio_diagrams import C_OK, C_TEMP, Diagram  # noqa: E402

HEAD = ("#455A64", "#455A64")
# Same palette as the Cali firewall transition diagram (firewall-9-p3).
S = {
    "move": ("#BBDEFB", "#1565C0"),     # moved as is (rehost / replatform)
    "redo": ("#DCEDC8", "#558B2F"),     # rebuilt in its final form
    "replace": ("#E1BEE7", "#6A1B9A"),  # replaced by a managed service
    "retire": ("#E0E0E0", "#9E9E9E"),   # retired
    "on": ("#C8E6C9", "#2E7D32"),       # active, serving
    "temp": ("#BBDEFB", "#1565C0"),     # temporary migration activity
    "stand": ("#FFE0B2", "#EF6C00"),    # standby, ready to roll back
    "off": ("#E0E0E0", "#9E9E9E"),      # off or not in use
    "idle": ("#F5F5F5", "#BDBDBD"),     # deployed, no users
}


def legend(d, x, y, items, step=250):
    for st, txt in items:
        fill, stroke = S[st]
        d.box(x, y, 24, 18, "", fill, stroke)
        d.text(x + 30, y - 4, step - 40, 26, txt, font=10)
        x += step


def cali_to_azure():
    d = Diagram()
    d.text(40, -40, 1300, 30, "De Cali a Azure: decisión, destino y momento de cada pieza", font=14)
    cols = [("Pieza en Cali", 70, 290), ("Decisión", 370, 190), ("Destino en Azure", 570, 400), ("Cuándo", 980, 330)]
    y0, rh = 40, 58
    for title, x, w in cols:
        d.box(x, y0 - 50, w - 6, 40, title, *HEAD, font=11, color="#FFFFFF", bold=True)
    label = {"move": "Se mueve tal cual", "redo": "Se rehace", "replace": "Se reemplaza", "retire": "Se retira"}
    rows = [
        ("vm", "despacho, inventario,\nfacturación corporativa", "move", "Entorno de la torre (Container Apps)", "Cambian juntos en el corte"),
        ("vm", "rastreo", "move", "Entorno del portal, detrás del\nApplication Gateway con WAF", "En el corte"),
        ("vm", "evidencias", "redo", "Entorno de la torre; lee y escribe en\nBlob Storage, sin NFS", "Ajuste probado antes del día 0;\ncambia en el corte"),
        ("vm", "Front (2 máquinas)", "redo", "Un contenedor de front por entorno", "En el corte"),
        ("lb", "Nginx (2 máquinas)", "replace", "Application Gateway v2 con WAF", "En el corte; Nginx se apaga\nal cerrar el plazo"),
        ("mysql", "MySQL 5.7 de producción", "redo", "MySQL Flexible Server 8.4,\nmigrado en línea con DMS", "Replicación desde el día 5;\ncambia en el corte"),
        ("mysql", "MySQL 5.7 de desarrollo y pruebas", "redo", "Bases nuevas vacías,\ncon datos inventados", "Antes del día 0"),
        ("redis", "Redis 5", "replace", "Azure Managed Redis", "En el corte; arranca vacía"),
        ("files", "FTP y NFS con 1,2 PB", "retire", "Cuentas de archivo y evidencias\n(siembra y copia continua, #15)", "Siembra conciliada antes del ensayo;\ncopia continua del día 0 al 35"),
        ("iothub", "Carga de temperatura por lote", "retire", "IoT Hub (#13)", "Centro por centro,\ndías 8 a 19"),
        ("monitor", "Zabbix", "retire", "Azure Monitor (#16)", "Día 61"),
        ("server_farm", "VMware (3 clústeres)", "retire", "—", "Día 62: Cali apagada"),
    ]
    for r, (kind, piece, dec, dest, when) in enumerate(rows):
        y = y0 + r * rh
        d.icon(70, y + 9, kind, "", size=40)
        d.text(120, y + 4, 234, rh - 8, piece, font=11)
        fill, stroke = S[dec]
        d.box(370, y + 6, 184, rh - 12, label[dec], fill, stroke, font=11, bold=True)
        d.box(570, y + 6, 394, rh - 12, dest, "#FFFFFF", "#9E9E9E", font=10)
        d.box(980, y + 6, 324, rh - 12, when, "#FFFFFF", "#9E9E9E", font=10)
    legend(d, 70, y0 + len(rows) * rh + 16, [
        ("move", "Se mueve tal cual (misma imagen, otra configuración)"),
        ("redo", "Se rehace en su forma final"),
        ("replace", "Se reemplaza por un servicio administrado"),
        ("retire", "Se retira"),
    ], step=310)
    return d


def calendar():
    d = Diagram()
    d.text(40, -40, 1500, 30, "Convivencia entre Cali y Azure, del 11 de enero al 11 de abril de 2027", font=14)
    phases = [
        "Preparación\nhasta el 10-ene",
        "Convivencia temprana\ndías 0 a 19 (11 al 30-ene)",
        "Ensayo\ndía 20 (31-ene)",
        "Corte\ndía 34 (14-feb)",
        "Plazo de vuelta atrás\ndías 34 a 55 (14-feb al 7-mar)",
        "Apagado\ndías 56 a 62 (8 al 14-mar)",
        "Margen y Semana Santa\ndías 63 a 90 (al 11-abr)",
    ]
    x0, w0, cw, rh, y0 = 40, 250, 180, 60, 90
    for i, p in enumerate(phases):
        fill = "#B71C1C" if i == 3 else HEAD[0]
        d.box(x0 + w0 + i * cw, y0 - 56, cw - 6, 50, p, fill, fill, font=10, color="#FFFFFF", bold=True)
    rows = [
        ("mysql", "Base de Cali (MySQL 5.7)", [("on", "En uso"), ("on", "En uso; binlog el día 1;\nesquema congelado"), ("on", "En uso"), ("stand", "Solo lectura desde\nlas 01:00"), ("stand", "Solo lectura,\ncontingencia"), ("off", "Último volcado\ny apagado"), ("off", "Apagada")]),
        ("dms", "DMS", [("off", "—"), ("temp", "Carga inicial el día 5\ny replicación"), ("temp", "Replica también al\nservidor temporal"), ("temp", "Retraso cero y corte"), ("off", "Eliminado"), ("off", "—"), ("off", "—")]),
        ("mysql", "Base en Azure (Flexible 8.4)", [("idle", "Desplegada, vacía"), ("temp", "Recibe la réplica;\nHA y réplica el día 13"), ("temp", "Recibe la réplica"), ("on", "Abre escrituras\na las 02:30"), ("on", "En uso"), ("on", "En uso"), ("on", "En uso")]),
        ("aca", "Torre y servicios", [("idle", "Desplegados,\nsin usuarios"), ("idle", "Pruebas de solo lectura"), ("idle", "Ensayo con\nnombre de prueba"), ("on", "Abre a las 02:30;\ndespacho a las 04:00"), ("on", "En uso"), ("on", "En uso"), ("on", "En uso")]),
        ("appgw", "Portal", [("idle", "Publicado,\nsin clientes"), ("idle", "Publicado,\nsin clientes"), ("idle", "Ensayo con\nnombre de prueba"), ("on", "DNS público al\nApplication Gateway"), ("on", "Única entrada;\nNAT de Cali en espera"), ("on", "NAT de Cali\nretirado"), ("on", "En uso")]),
        ("files", "Archivo de 1,2 PB", [("temp", "Siembra por discos\nen curso"), ("temp", "Copia continua\ndesde el día 0"), ("temp", "Siembra conciliada;\ncopia continua"), ("temp", "Última sincronización"), ("on", "Solo en Azure\ndesde el día 35"), ("off", "FTP y NFS de Cali\napagados"), ("on", "Solo en Azure")]),
        ("vpngw", "Centros", [("on", "Por Cali"), ("temp", "Piloto el día 1; todos\ndirecto el día 12"), ("on", "Directo a Azure"), ("on", "Directo a Azure"), ("stand", "VPN a Cali\nde respaldo"), ("off", "VPN a Cali\nretirada"), ("on", "Directo a Azure")]),
        ("iothub", "Telemetría", [("on", "IoT Hub listo"), ("temp", "Camiones y cuartos fríos\nen línea; FTP en paralelo"), ("on", "En línea;\nFTP retirado"), ("on", "Sin cambios"), ("on", "Sin cambios"), ("on", "Sin cambios"), ("on", "Sin cambios")]),
        ("fw_policy", "Reglas temporales\n(grupos 400 y 500)", [("off", "—"), ("temp", "Activas desde el día 0"), ("temp", "Activas"), ("temp", "FW-501 y 502\nse retiran"), ("temp", "Siguen FW-401,\n503 y 504"), ("off", "Retiradas el día 56"), ("off", "Revisión final")]),
        ("monitor", "Zabbix y VMware", [("on", "En uso"), ("on", "Vigila Cali"), ("on", "Vigila Cali"), ("on", "Vigila Cali"), ("on", "Vigila Cali"), ("off", "Zabbix día 61;\nVMware día 62"), ("off", "Apagados")]),
    ]
    for r, (kind, label, cells) in enumerate(rows):
        y = y0 + r * rh
        d.icon(x0, y + 10, kind, "", size=40)
        d.text(x0 + 50, y + 4, w0 - 60, rh - 8, label, font=11)
        for i, (st, txt) in enumerate(cells):
            fill, stroke = S[st]
            d.box(x0 + w0 + i * cw, y + 5, cw - 6, rh - 10, txt, fill, stroke, font=10)
    legend(d, x0, y0 + len(rows) * rh + 16, [
        ("on", "En uso"),
        ("temp", "Actividad temporal de la migración"),
        ("stand", "En espera, lista para volver atrás"),
        ("idle", "Desplegado, sin usuarios"),
        ("off", "Apagado o sin uso"),
    ])
    return d


def archive_paths():
    d = Diagram()
    d.text(20, -20, 1500, 30, "Archivo de 1,2 PB: siembra con discos (Import/Export) y copia continua por la VPN", font=14)
    d.zone(20, 40, 700, 600, "Cali · red del archivo (10.20.3.0/24)", fill="#FAFAFA", stroke="#757575")
    d.zone(1040, 40, 860, 600, "Azure · East US 2 · producción", fill="#F3F8FD", stroke="#1565C0")
    d.zone(1440, 200, 420, 230, "Dos cuentas del archivo: sin NFS, solo Entra ID, inmutables", fill="#E8F5E9", stroke="#2E7D32", font=11)
    d.zone(1440, 470, 420, 150, "snet-archive", fill="#FFFFFF", stroke="#1565C0", font=11)

    srv = d.icon(60, 250, "files", "Servidor de archivo\nFTP y NFS · 1,2 PB", label_w=170)
    sta = d.icon(300, 90, "vm", "2 estaciones de copia\nWAImportExport, BitLocker", label_w=200)
    d.box(480, 90, 200, 56, "71 discos HDD de 20 TB\n9 trabajos", "#FFFFFF", "#2E7D32", font=11)
    agt = d.icon(300, 500, "vm", "Agente de copia continua\nAzCopy, desde el día 0", label_w=200)
    fw = d.icon(560, 500, "cali_fw", "Firewall de Cali\n(túneles IPsec)", label_w=150)
    d.box(770, 90, 220, 60, "Transportador internacional\nunos 7 días con aduana", "#FFFFFF", "#757575", font=11)
    d.box(1080, 90, 240, 60, "Datacenter de Microsoft\nImport/Export: carga en unos 10 días", "#FFFFFF", "#1565C0", font=11)
    gw = d.icon(1080, 500, "vpngw", "VPN Gateway", label_w=120)
    d.icon(1520, 260, "storage", "Documentos\n150 TB · Cool · GRS", label_w=170)
    d.icon(1730, 260, "storage", "Video\n1.050 TB · Cold · LRS", label_w=170)
    pe = d.icon(1500, 500, "pe", "Endpoints privados de Blob", label_w=190)
    d.text(1150, 590, 270, 40, "La copia no pasa por el Azure Firewall\n(NSG-prod-11, solo HTTPS 443)", font=10, color=C_TEMP, align="center")

    d.edge(srv[0], sta[0], [(116, 270), (200, 270), (200, 118), (300, 118)], "NFS, solo lectura", color=C_OK, label_pos=(205, 180, 110))
    d.edge(sta[0], sta[0], [(356, 118), (480, 118)], color=C_OK)
    d.edge(sta[0], sta[0], [(680, 118), (770, 118)], color=C_OK)
    d.edge(sta[0], sta[0], [(990, 120), (1080, 120)], color=C_OK)
    d.edge(sta[0], sta[0], [(1320, 120), (1650, 120), (1650, 200)], "D1, V1 a V6 y el diferencial", color=C_OK, label_pos=(1360, 100, 230))
    d.edge(srv[0], agt[0], [(116, 286), (200, 286), (200, 528), (300, 528)], "NFS, solo lectura", color=C_TEMP, dashed=True, label_pos=(205, 400, 110))
    d.edge(agt[0], fw[0], [(356, 528), (560, 528)], color=C_TEMP, dashed=True)
    d.edge(fw[0], gw[0], [(616, 528), (1080, 528)], "Lo creado desde T1, solo HTTPS: unos 400 GB al día", color=C_TEMP, dashed=True, label_pos=(700, 505, 320))
    d.edge(gw[0], pe[0], [(1136, 528), (1500, 528)], color=C_TEMP, dashed=True)
    d.edge(pe[0], pe[0], [(1528, 500), (1528, 430)], color=C_TEMP, dashed=True)

    d.box(40, 660, 24, 4, "", C_OK, C_OK)
    d.text(72, 650, 360, 24, "Siembra con discos: todo lo creado antes de T1 (4 de enero)", font=10)
    d.box(470, 660, 24, 4, "", C_TEMP, C_TEMP)
    d.text(502, 650, 420, 24, "Copia continua por la red, temporal: desde el día 0 hasta la noche después del corte", font=10)
    return d


def seeding_schedule():
    d = Diagram()
    start, end = dt.date(2026, 10, 12), dt.date(2027, 2, 16)
    x0, px, y0, rh = 300, 9, 110, 40

    def x(day):
        return x0 + (day - start).days * px

    width = x(end) - x0
    d.text(20, -20, 1500, 30, "Cronograma de la siembra del archivo, de octubre de 2026 a febrero de 2027", font=14)
    rows = ["Preparación", "Prueba (1 disco)", "D1 · documentos", "V1 · video", "V2 · video", "V3 · video", "V4 · video",
            "V5 · video", "V6 · video más antiguo", "Diferencial (T0 a T1)", "Copia continua por la red", "Conciliación"]
    height = len(rows) * rh
    # Campaign band behind everything else.
    d.zone(x(dt.date(2026, 11, 15)), y0 - 10, x(dt.date(2027, 1, 11)) - x(dt.date(2026, 11, 15)), height + 20,
           "Campaña de fin de año: la copia solo lee, no es cambio productivo", fill="#FFEBEE", stroke="#FFCDD2", font=10, bold=False)
    for m, name in [(dt.date(2026, 10, 12), "octubre"), (dt.date(2026, 11, 1), "noviembre"), (dt.date(2026, 12, 1), "diciembre"),
                    (dt.date(2027, 1, 1), "enero"), (dt.date(2027, 2, 1), "febrero")]:
        d.box(x(m), 40, 6 if m.day == 1 and m != start else 0, 0, "", "#455A64", "#455A64")
        d.text(x(m) + 4, 40, 120, 22, name, font=11, color="#455A64")
    d.box(x0, 64, width, 2, "", "#455A64", "#455A64")
    for r, name in enumerate(rows):
        d.text(20, y0 + r * rh, x0 - 30, rh, name, font=11)
        d.box(x0, y0 + (r + 1) * rh - 1, width, 1, "", "#EEEEEE", "#EEEEEE")

    copy_, ship, load = ("#BBDEFB", "#1565C0"), ("#FFE0B2", "#EF6C00"), ("#C8E6C9", "#2E7D32")

    def bar(r, a, b, style, label=""):
        d.box(x(a), y0 + r * rh + 8, max(x(b) - x(a), 4), rh - 16, label, *style, font=9)

    D = dt.date
    bar(0, D(2026, 10, 13), D(2026, 10, 24), ("#F5F5F5", "#9E9E9E"), "Discos, estaciones, cuentas")
    jobs = [(1, D(2026, 10, 20), D(2026, 10, 22), D(2026, 10, 29), D(2026, 11, 8)),
            (2, D(2026, 11, 2), D(2026, 11, 9), D(2026, 11, 16), D(2026, 11, 26)),
            (3, D(2026, 11, 7), D(2026, 11, 16), D(2026, 11, 23), D(2026, 12, 3)),
            (4, D(2026, 11, 14), D(2026, 11, 23), D(2026, 11, 30), D(2026, 12, 10)),
            (5, D(2026, 11, 20), D(2026, 11, 30), D(2026, 12, 7), D(2026, 12, 17)),
            (6, D(2026, 11, 27), D(2026, 12, 7), D(2026, 12, 14), D(2026, 12, 24)),
            (7, D(2026, 12, 4), D(2026, 12, 11), D(2026, 12, 18), D(2026, 12, 28)),
            (8, D(2026, 12, 10), D(2026, 12, 17), D(2026, 12, 24), D(2027, 1, 3)),
            (9, D(2027, 1, 4), D(2027, 1, 6), D(2027, 1, 13), D(2027, 1, 23))]
    for r, c, s, a, ready in jobs:
        bar(r, c, s, copy_)
        bar(r, s, a, ship)
        bar(r, a, ready, load)
    bar(10, D(2027, 1, 11), D(2027, 2, 15), ("#BBDEFB", "#1565C0"), "Al día hacia el 15 de enero")
    bar(11, D(2027, 1, 25), D(2027, 1, 30), ("#E1BEE7", "#6A1B9A"))

    milestones = [(D(2026, 11, 2), "T0", "#455A64"), (D(2027, 1, 4), "T1", "#455A64"), (D(2027, 1, 11), "Día 0", "#1565C0"),
                  (D(2027, 1, 31), "Ensayo", "#EF6C00"), (D(2027, 2, 14), "Corte", "#B71C1C")]
    for m, label, color in milestones:
        d.box(x(m), y0 - 22, 2, height + 30, "", color, color)
        d.text(x(m) - 40, y0 + height + 10, 80, 20, label, font=10, color=color, align="center")

    ly = y0 + height + 50
    for i, (style, txt) in enumerate([(copy_, "Copia a los discos en Cali"), (ship, "Envío y aduana"),
                                      (load, "Carga en Azure"), (("#E1BEE7", "#6A1B9A"), "Conciliación")]):
        d.box(x0 + i * 260, ly, 24, 18, "", *style)
        d.text(x0 + i * 260 + 30, ly - 4, 220, 26, txt, font=10)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in [("carga-c-14-p1-de-cali-a-azure", cali_to_azure),
                     ("carga-c-14-p2-calendario", calendar),
                     ("carga-c-15-p1-caminos", archive_paths),
                     ("carga-c-15-p2-cronograma", seeding_schedule)]:
        (out / f"{name}.drawio").write_text(fn().xml(), encoding="utf-8")
        print(out / f"{name}.drawio")


if __name__ == "__main__":
    main()

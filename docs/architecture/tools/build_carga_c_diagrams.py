#!/usr/bin/env python3
"""Build the draw.io diagrams of the core migration and campaign plan (issue #14):

- carga-c-14-p1-de-cali-a-azure: decision and Azure destination of each Cali piece.
- carga-c-14-p2-calendario: state of each piece in each phase of the coexistence.

Imports the Diagram helper and the Azure icon set from
docs/architecture/red/tools/build_drawio_diagrams.py, so all diagrams share one style.

Usage:
    python3 build_carga_c_diagrams.py --out ../diagramas

Export to PNG with the draw.io desktop CLI:

    drawio --disable-gpu -x -f png -e -b 20 -s 1.5 -o ../diagramas/NAME.drawio.png ../diagramas/NAME.drawio
"""
import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep red/tools free of __pycache__
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "red" / "tools"))
from build_drawio_diagrams import Diagram  # noqa: E402

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
        ("files", "FTP y NFS con 1,2 PB", "retire", "Cuentas de archivo y evidencias\n(siembra y copia continua, #15)", "Siembra antes del día 0;\ncopia continua hasta el día 35"),
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
        ("files", "Archivo de 1,2 PB", [("temp", "Siembra cargada;\ncopia continua"), ("temp", "Copia continua"), ("temp", "Copia continua"), ("temp", "Última sincronización"), ("on", "Solo en Azure\ndesde el día 35"), ("off", "FTP y NFS de Cali\napagados"), ("on", "Solo en Azure")]),
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in [("carga-c-14-p1-de-cali-a-azure", cali_to_azure),
                     ("carga-c-14-p2-calendario", calendar)]:
        (out / f"{name}.drawio").write_text(fn().xml(), encoding="utf-8")
        print(out / f"{name}.drawio")


if __name__ == "__main__":
    main()

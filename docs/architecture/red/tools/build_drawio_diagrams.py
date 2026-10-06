#!/usr/bin/env python3
"""Build the draw.io diagrams of the cloud firewall and portal publication design.

Usage:
    python3 tools/build_drawio_diagrams.py --out ../diagramas   (desde la carpeta red/)

Writes one .drawio file per diagram. Shapes use the draw.io Azure library (img/lib/azure2) and the
network library for on-premises sites. Every edge is orthogonal with explicit waypoints so that lines
never cross shapes or labels; export to PNG with the draw.io desktop CLI:

    drawio --disable-gpu -x -f png -e -b 10 -o NAME.drawio.png NAME.drawio
"""
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

AZ = "img/lib/azure2/"
ICON = {
    "firewall": AZ + "networking/Firewalls.svg",
    "fw_policy": AZ + "networking/Azure_Firewall_Policy.svg",
    "appgw": AZ + "networking/Application_Gateways.svg",
    "waf": AZ + "networking/Web_Application_Firewall_Policies_WAF.svg",
    "pip": AZ + "networking/Public_IP_Addresses.svg",
    "ddos": AZ + "networking/DDoS_Protection_Plans.svg",
    "nsg": AZ + "networking/Network_Security_Groups.svg",
    "vpngw": AZ + "networking/Virtual_Network_Gateways.svg",
    "bastion": AZ + "networking/Bastions.svg",
    "dns": AZ + "networking/DNS_Private_Resolver.svg",
    "pe": AZ + "networking/Private_Endpoint.svg",
    "aca": AZ + "other/Container_App_Environments.svg",
    "mysql": AZ + "databases/Azure_Database_MySQL_Server.svg",
    "redis": AZ + "databases/Azure_Managed_Redis.svg",
    "dms": AZ + "databases/Azure_Database_Migration_Services.svg",
    "kv": AZ + "security/Key_Vaults.svg",
    "storage": AZ + "storage/Storage_Accounts.svg",
    "iothub": AZ + "iot/IoT_Hub.svg",
    "fabricgw": AZ + "networking/On_Premises_Data_Gateways.svg",
    "vm": AZ + "compute/Virtual_Machine.svg",
    "sensor": AZ + "other/Defender_Sensor.svg",
    "monitor": AZ + "management_governance/Log_Analytics_Workspaces.svg",
}
NET = "html=1;outlineConnect=0;fillColor=#CCCCCC;strokeColor=#6881B3;gradientColor=none;strokeWidth=2;shape=mxgraph.networks."

C_OK = "#2E7D32"
C_TEMP = "#1565C0"
C_EXC = "#C62828"
C_DENY = "#757575"


class Diagram:
    def __init__(self):
        self.cells = []
        self.n = 0

    def _id(self, prefix):
        self.n += 1
        return f"{prefix}{self.n}"

    def zone(self, x, y, w, h, label, fill="#F5F5F5", stroke="#9E9E9E", dashed=False, font=12, bold=True):
        # Zones are drawn first so that icons and edges stay on top.
        cid = self._id("z")
        style = (f"rounded=1;arcSize=4;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
                 f"verticalAlign=top;align=left;spacingLeft=8;spacingTop=4;fontSize={font};"
                 f"{'fontStyle=1;' if bold else ''}{'dashed=1;' if dashed else ''}")
        self.cells.append(f'<mxCell id="{cid}" value="{escape(label, {chr(10): "&lt;br&gt;"})}" style="{style}" vertex="1" parent="1">'
                          f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return cid

    def text(self, x, y, w, h, label, font=11, align="left", color="#212121", fill="none"):
        cid = self._id("t")
        style = (f"text;html=1;whiteSpace=wrap;align={align};verticalAlign=middle;fontSize={font};"
                 f"fontColor={color};fillColor={fill};")
        self.cells.append(f'<mxCell id="{cid}" value="{escape(label, {chr(10): "&lt;br&gt;"})}" style="{style}" vertex="1" parent="1">'
                          f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return cid

    def box(self, x, y, w, h, label, fill, stroke, font=11, color="#212121", bold=False):
        cid = self._id("b")
        style = (f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontSize={font};"
                 f"fontColor={color};{'fontStyle=1;' if bold else ''}")
        self.cells.append(f'<mxCell id="{cid}" value="{escape(label, {chr(10): "&lt;br&gt;"})}" style="{style}" vertex="1" parent="1">'
                          f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return cid

    def icon(self, x, y, kind, label, size=56, font=11, label_w=None):
        cid = self._id("i")
        if kind == "cali_fw":
            kind = "firewall_onprem"
        if kind in ICON:
            style = (f"image;aspect=fixed;html=1;points=[];align=center;verticalLabelPosition=bottom;"
                     f"verticalAlign=top;fontSize={font};image={ICON[kind]};")
        else:
            style = NET + kind.replace("firewall_onprem", "firewall") + f";verticalLabelPosition=bottom;verticalAlign=top;fontSize={font};"
        if label_w:
            style += f"labelWidth={label_w};whiteSpace=wrap;"
        self.cells.append(f'<mxCell id="{cid}" value="{escape(label, {chr(10): "&lt;br&gt;"})}" style="{style}" vertex="1" parent="1">'
                          f'<mxGeometry x="{x}" y="{y}" width="{size}" height="{size}" as="geometry"/></mxCell>')
        return cid, (x, y, size)

    def edge(self, src, tgt, points, label="", color=C_OK, dashed=False, label_pos=None, width=2, arrow_both=False, label_h=18):
        """points: list of (x, y) absolute waypoints, first is the exit point, last is the entry point."""
        cid = self._id("e")
        (sx, sy), (tx, ty) = points[0], points[-1]
        style = (f"edgeStyle=none;html=1;rounded=0;endArrow=block;endFill=1;strokeColor={color};strokeWidth={width};"
                 f"fontSize=10;fontColor={color};labelBackgroundColor=default;"
                 f"{'dashed=1;dashPattern=6 4;' if dashed else ''}{'startArrow=block;startFill=1;' if arrow_both else ''}")
        mids = "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in points[1:-1])
        geo = (f'<mxGeometry relative="1" as="geometry"><mxPoint x="{sx}" y="{sy}" as="sourcePoint"/>'
               f'<mxPoint x="{tx}" y="{ty}" as="targetPoint"/>'
               f'{"<Array as=" + chr(34) + "points" + chr(34) + ">" + mids + "</Array>" if mids else ""}</mxGeometry>')
        self.cells.append(f'<mxCell id="{cid}" value="" style="{style}" edge="1" parent="1">{geo}</mxCell>')
        if label:
            lx, ly, lw = label_pos
            self.text(lx, ly, lw, label_h, label, font=10, color=color, fill="default", align="center")
        return cid

    def xml(self):
        return ('<mxfile><diagram name="Página-1"><mxGraphModel adaptiveColors="auto" grid="0" page="0">'
                '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(self.cells) +
                "</root></mxGraphModel></diagram></mxfile>")


def center(ic):
    _, (x, y, s) = ic
    return x + s / 2, y + s / 2


def portal_publication():
    d = Diagram()
    d.zone(330, 60, 1010, 660, "Producción · vnet-prod 10.101.0.0/21", fill="#FAFAFA", font=13)
    d.zone(360, 110, 270, 290, "Zona pública\nsnet-ingress 10.101.0.0/24", fill="#FFF3E0", stroke="#EF6C00")
    d.zone(690, 110, 280, 290, "Zona privada del portal\nsnet-app-portal 10.101.1.128/25", fill="#E8F5E9", stroke="#2E7D32")
    d.zone(1030, 110, 280, 580, "Datos\nsnet-data y snet-data-pe", fill="#E3F2FD", stroke="#1565C0")
    d.zone(690, 450, 280, 240, "Torre de control\nsnet-app-torre 10.101.1.0/25", fill="#F3E5F5", stroke="#6A1B9A")
    d.zone(360, 450, 270, 240, "Pruebas y desarrollo", fill="#FFFFFF", stroke="#9E9E9E", dashed=True)
    d.text(372, 485, 250, 195,
           "Misma estructura en 10.102.0.0/21 y 10.103.0.0/21.\n\nEl NSG de snet-ingress solo acepta las IP públicas de Cali y la IP de salida del firewall.\n\nPruebas usa WAF v2 con la misma política; desarrollo usa Standard v2 sin WAF. Mínimo 0 instancias.",
           font=11)

    clients = d.icon(70, 180, "users", "Clientes corporativos\n(unos 2.000, por internet)", size=56, label_w=150)
    pip = d.icon(205, 180, "pip", "IP pública del portal\nDDoS IP Protection", size=56, label_w=130)
    appgw = d.icon(520, 170, "appgw", "Application Gateway WAF v2\n2 a 10 instancias, en zonas", size=64, label_w=170)
    d.icon(385, 300, "waf", "WAF: DRS 2.2 y\nBot Manager 1.1,\nprevención", size=44, label_w=120)
    d.icon(545, 300, "nsg", "NSG: 443 y 80,\nGatewayManager", size=44, label_w=110)
    portal = d.icon(798, 170, "aca", "Entorno interno de Container Apps\n(servicios del portal)", size=64, label_w=200)
    d.icon(808, 300, "nsg", "NSG: 443 solo\ndesde snet-ingress", size=44, label_w=130)
    kv = d.icon(1142, 170, "kv", "Key Vault: certificado\ndel portal y secretos", size=56, label_w=160)
    mysql = d.icon(1142, 314, "mysql", "MySQL Flexible,\nalta disponibilidad", size=56, label_w=160)
    redis = d.icon(1142, 470, "redis", "Caché del rastreo", size=56, label_w=150)
    d.text(1045, 600, 255, 70, "NSG por subred: solo torre, portal, gateway de Fabric y operación. El Application Gateway solo llega al Key Vault.", font=10)
    torre = d.icon(880, 520, "aca", "", size=64)
    d.text(700, 505, 170, 120, "Entorno interno de Container Apps de la torre. Sin IP pública ni regla en el Application Gateway. Usa la misma base por la red privada.", font=11)
    corp = d.icon(600, 776, "users", "Usuarios de Cali y de los centros\n(por la VPN)", size=56, label_w=190)
    fw = d.icon(880, 772, "firewall", "Azure Firewall (hub)", size=64, label_w=140)

    d.edge(clients[0], pip[0], [(126, 208), (205, 208)], "HTTPS 443", label_pos=(131, 186, 70))
    d.edge(pip[0], appgw[0], [(261, 208), (520, 208)])
    d.edge(appgw[0], portal[0], [(584, 202), (798, 202)], "HTTPS 443", label_pos=(632, 184, 56))
    d.edge(appgw[0], kv[0], [(552, 170), (552, 95), (1325, 95), (1325, 198), (1198, 198)], "Certificado TLS: 443", label_pos=(690, 86, 140))
    d.edge(portal[0], mysql[0], [(862, 190), (1012, 190), (1012, 342), (1142, 342)], "TCP 3306", label_pos=(1048, 324, 80))
    d.edge(portal[0], redis[0], [(862, 222), (1000, 222), (1000, 498), (1142, 498)], "TCP 10000", label_pos=(1048, 480, 80))
    d.edge(corp[0], fw[0], [(656, 804), (880, 804)], "Túneles IPsec", label_pos=(722, 786, 90))
    d.edge(fw[0], torre[0], [(912, 772), (912, 584)], "FW-201: 443", label_pos=(922, 698, 80))
    return d


def control_points():
    d = Diagram()
    d.zone(30, 120, 270, 330, "Cali", fill="#FFFDE7", stroke="#F9A825")
    d.zone(30, 490, 270, 250, "Ocho centros", fill="#FFFDE7", stroke="#F9A825")
    d.zone(360, 120, 320, 620, "Hub · vnet-hub 10.100.0.0/23", fill="#ECEFF1", stroke="#455A64")
    d.zone(740, 120, 790, 620, "Producción · vnet-prod 10.101.0.0/21", fill="#FAFAFA", stroke="#616161")

    d.icon(60, 165, "users", "Usuarios\n10.20.0.0/24", size=48, label_w=110)
    d.icon(60, 310, "server", "Servidores: aplicación,\nbase y archivo\n10.20.1 a 10.20.3", size=48, label_w=130)
    cali_fw = d.icon(205, 235, "firewall", "Firewall\nde Cali", size=56, label_w=80)
    d.icon(60, 530, "users", "Usuarios\n10.3X.0.0/24", size=48, label_w=110)
    d.icon(62, 640, "sensor", "Sensores de cuartos\nfríos 10.3X.1.0/24", size=44, label_w=130)
    c_vpn = d.icon(205, 595, "router", "Equipo VPN\ndel centro", size=48, label_w=90)
    trucks = d.icon(60, 815, "mobile", "Camiones\n(red móvil del operador)", size=48, label_w=150)
    internet = d.icon(1410, 20, "cloud", "Internet", size=70, label_w=80)
    d.cells[-1] = d.cells[-1].replace("verticalLabelPosition=bottom;verticalAlign=top;", "labelPosition=left;verticalLabelPosition=middle;align=right;verticalAlign=middle;")

    vpngw = d.icon(400, 170, "vpngw", "VPN Gateway", size=56, label_w=100)
    fw = d.icon(480, 380, "firewall", "Azure Firewall Standard", size=72, label_w=160)
    d.icon(600, 330, "fw_policy", "Política", size=44, label_w=70)
    d.text(380, 495, 290, 60, "Grupos 200 y 300: estables.\nGrupos 400 y 500: temporales de la convivencia.\nSin regla: se rechaza y se registra.", font=10)
    bastion = d.icon(400, 620, "bastion", "Bastion", size=48, label_w=80)
    d.icon(570, 620, "dns", "DNS Private\nResolver", size=48, label_w=100)

    col = [770, 1030, 1290]
    row = [170, 330, 490]

    def pz(c, r, title, kind, label):
        x, y = col[c], row[r]
        d.zone(x, y, 210, 130, title, fill="#FFFFFF", stroke="#9E9E9E", font=10)
        return d.icon(x + 81, y + 42, kind, label, size=48, font=10, label_w=200)

    torre = pz(0, 0, "Torre · snet-app-torre", "aca", "FW-201: 443 desde la red corporativa")
    ingest = pz(0, 1, "Ingesta · snet-ingest", "iothub", "FW-204: 8883, 5671 y 443")
    integ = pz(0, 2, "Integración con Cali", "dms", "FW-501 a 505 (temporales)")
    archive = pz(1, 0, "Archivo · snet-archive", "storage", "Copia desde Cali fuera del firewall.\nNSG temporal: solo 10.20.3.0/24")
    pz(1, 1, "Datos · snet-data y snet-data-pe", "mysql", "NSG: solo aplicaciones y Fabric")
    pz(1, 2, "Analítica · snet-fabric-egress", "fabricgw", "Lee base y archivo, sin internet")
    appgw = pz(2, 0, "Portal · snet-ingress", "appgw", "WAF v2")
    portal = pz(2, 1, "Portal · snet-app-portal", "aca", "NSG: solo desde snet-ingress")
    admin = pz(2, 2, "Administración · snet-admin", "vm", "NSG: 22 y 3389 desde Bastion")
    iot_pub = d.icon(1000, 815, "iothub", "IoT Hub, endpoint público", size=48, label_w=160)

    d.edge(cali_fw[0], vpngw[0], [(261, 263), (330, 263), (330, 190), (400, 190)], "4 túneles,\n2 proveedores", label_pos=(205, 172, 110), label_h=30)
    d.edge(c_vpn[0], vpngw[0], [(253, 619), (340, 619), (340, 215), (400, 215)], "2 túneles\npor centro", label_pos=(225, 455, 105), label_h=30)
    d.edge(vpngw[0], fw[0], [(456, 198), (516, 198), (516, 380)], "Todo lo que entra\npor la VPN", label_pos=(522, 270, 110), label_h=30)
    d.edge(fw[0], torre[0], [(552, 392), (720, 392), (720, 236), (851, 236)])
    d.edge(fw[0], ingest[0], [(552, 410), (735, 410), (735, 396), (851, 396)])
    d.edge(fw[0], integ[0], [(552, 446), (710, 446), (710, 556), (851, 556)], color=C_TEMP, dashed=True)
    d.edge(fw[0], internet[0], [(552, 428), (725, 428), (725, 475), (1545, 475), (1545, 55), (1480, 55)],
           "FW-301 a 318: salida a internet", label_pos=(1300, 466, 200))
    d.edge(vpngw[0], archive[0], [(456, 182), (560, 182), (560, 160), (1010, 160), (1010, 236), (1111, 236)],
           color=C_EXC, dashed=True)
    d.edge(internet[0], appgw[0], [(1445, 90), (1445, 236), (1419, 236)], "WAF: 443", label_pos=(1440, 120, 56))
    d.edge(appgw[0], portal[0], [(1419, 250), (1470, 250), (1470, 396), (1419, 396)], "443", label_pos=(1474, 300, 24))
    d.edge(bastion[0], admin[0], [(448, 644), (500, 644), (500, 725), (1260, 725), (1260, 556), (1371, 556)],
           "Bastion: NSG, 22 y 3389", label_pos=(880, 716, 160), color=C_EXC)
    d.edge(trucks[0], iot_pub[0], [(108, 839), (1000, 839)], "TLS y credencial por camión", label_pos=(470, 821, 180), color=C_EXC)

    d.text(30, 900, 1500, 60,
           "Verde: pasa por el Azure Firewall o por el WAF. Azul punteado: temporal de la migración. Rojo: controlado por NSG o por IoT Hub, sin pasar por el firewall. "
           "El DNS entre Cali y el resolver del hub también se controla con NSG (UDP y TCP 53). El tránsito entre centros y Cali durante la convivencia (FW-401 y FW-402) pasa por el firewall.",
           font=10)
    return d


def cali_transition():
    d = Diagram()
    phases = ["Antes del paso\nde cada centro", "Centro conectado\ndirecto a Azure", "Del corte al cierre\ndel plazo de vuelta atrás", "Estado estable\n(día 90 a más tardar)"]
    x0, w0, cw, rh = 40, 300, 210, 64
    y0 = 90
    d.text(40, -40, 1100, 30, "Funciones del firewall de Cali y reglas temporales de Azure, por etapa de la convivencia", font=14)
    for i, p in enumerate(phases):
        d.box(x0 + w0 + i * cw, y0 - 50, cw - 6, 44, p, "#455A64", "#455A64", font=11, color="#FFFFFF", bold=True)
    S = {"on": ("#C8E6C9", "#2E7D32"), "stand": ("#FFE0B2", "#EF6C00"), "off": ("#E0E0E0", "#9E9E9E"),
         "temp": ("#BBDEFB", "#1565C0"), "new": ("#DCEDC8", "#558B2F")}
    rows = [
        ("cali_fw", "Enrutamiento entre subredes de Cali", [("on", "Activo"), ("on", "Activo"), ("on", "Activo"), ("on", "Solo la sede")]),
        ("cali_fw", "VPN de Cali con los centros", [("on", "Activa"), ("stand", "Respaldo del centro"), ("stand", "Respaldo"), ("off", "Apagada")]),
        ("cali_fw", "NAT del portal hacia Nginx", [("on", "Publica el portal"), ("on", "Publica el portal"), ("stand", "Configurado, sin tráfico"), ("off", "Apagado")]),
        ("cali_fw", "Firewall de aplicaciones delante de Nginx", [("on", "Protege el portal"), ("on", "Protege el portal"), ("stand", "Configurado, sin tráfico"), ("off", "Apagado")]),
        ("cali_fw", "Políticas entre subredes de servidores", [("on", "Activas"), ("on", "Activas"), ("stand", "Se retiran al apagar cada servidor"), ("off", "Retiradas")]),
        ("cali_fw", "Salida de Cali hacia Azure (nueva)", [("new", "4 túneles, 2 proveedores"), ("new", "Activa"), ("new", "Activa"), ("new", "Permanente")]),
        ("fw_policy", "Azure: grupos temporales 400 y 500", [("temp", "Activos"), ("temp", "Activos, más tránsito\nFW-401 y FW-402"), ("temp", "FW-501 y 502 se retiran\nen el corte"), ("off", "Borrados completos")]),
        ("nsg", "Azure: NSG temporales (copia del archivo, migración)", [("temp", "Activos"), ("temp", "Activos"), ("temp", "Hasta terminar la copia\ny el plazo"), ("off", "Retirados")]),
        ("appgw", "Azure: portal en el Application Gateway", [("off", "Publicado, sin clientes"), ("off", "Publicado, sin clientes"), ("on", "Recibe a los clientes"), ("on", "Única entrada del portal")]),
    ]
    for r, (kind, label, cells) in enumerate(rows):
        y = y0 + r * rh
        d.icon(x0, y + 10, kind, "", size=40)
        d.text(x0 + 50, y + 4, w0 - 60, rh - 8, label, font=11)
        for i, (st, txt) in enumerate(cells):
            fill, stroke = S[st]
            d.box(x0 + w0 + i * cw, y + 6, cw - 6, rh - 12, txt, fill, stroke, font=10)
    ly = y0 + len(rows) * rh + 16
    legend = [("on", "Activo"), ("stand", "Respaldo o sin tráfico, listo para volver atrás"), ("off", "Apagado o sin uso"), ("temp", "Regla temporal de la migración"), ("new", "Función nueva permanente")]
    x = x0
    for st, txt in legend:
        fill, stroke = S[st]
        d.box(x, ly, 24, 18, "", fill, stroke)
        d.text(x + 30, ly - 4, 190, 26, txt, font=10)
        x += 230
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in [("firewall-9-p1-publicacion-portal", portal_publication),
                     ("firewall-9-p2-puntos-de-control", control_points),
                     ("firewall-9-p3-transicion-cali", cali_transition)]:
        (out / f"{name}.drawio").write_text(fn().xml(), encoding="utf-8")
        print(out / f"{name}.drawio")


if __name__ == "__main__":
    main()

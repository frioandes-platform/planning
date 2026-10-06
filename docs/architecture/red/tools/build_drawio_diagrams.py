#!/usr/bin/env python3
"""Build the draw.io diagrams of the network designs: hybrid network and subnets, cloud firewall, portal publication
and telemetry.

Usage:
    python3 tools/build_drawio_diagrams.py --out ../diagramas   (desde la carpeta red/)

Writes one .drawio file per diagram. Shapes use the draw.io Azure library (img/lib/azure2) and the
network library for on-premises sites. Every edge is orthogonal with explicit waypoints so that lines
never cross shapes or labels; export to PNG with the draw.io desktop CLI:

    drawio --disable-gpu -x -f png -e -b 10 -o NAME.drawio.png NAME.drawio
"""
import argparse
import csv
from pathlib import Path
from xml.sax.saxutils import escape

DATA = Path(__file__).resolve().parent.parent / "data"
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
    "dps": AZ + "iot/Device_Provisioning_Services.svg",
    "iot_edge": AZ + "iot/IoT_Edge.svg",
    "asa": AZ + "iot/Stream_Analytics_Jobs.svg",
    "func": AZ + "iot/Function_Apps.svg",
    "eventhub": AZ + "analytics/Event_Hubs.svg",
    "acs": AZ + "other/Azure_Communication_Services.svg",
    "datalake": AZ + "storage/Data_Lake_Storage_Gen1.svg",
    "onelake": AZ + "analytics/Data_Lake_Store_Gen1.svg",
    "semantic": AZ + "analytics/Analysis_Services.svg",
    "pbi_embedded": AZ + "analytics/Power_BI_Embedded.svg",
    "mobile_az": AZ + "general/Mobile.svg",
    "browser": AZ + "general/Browser.svg",
    "users_az": AZ + "identity/Users.svg",
    "server_farm": AZ + "general/Server_Farm.svg",
    "files": AZ + "general/Files.svg",
    "lb": AZ + "networking/Load_Balancers.svg",
    "lng": AZ + "networking/Local_Network_Gateways.svg",
    "iiot": AZ + "iot/Industrial_IoT.svg",
    "vrouter": AZ + "networking/Virtual_Router.svg",
    "connections": AZ + "networking/Connections.svg",
    "aks": AZ + "containers/Kubernetes_Services.svg",
    "route_table": AZ + "networking/Route_Tables.svg",
    "vnet": AZ + "networking/Virtual_Networks.svg",
    "subnet": AZ + "networking/Subnet.svg",
    "subscription": AZ + "general/Subscriptions.svg",
}
NET = "html=1;outlineConnect=0;fillColor=#CCCCCC;strokeColor=#6881B3;gradientColor=none;strokeWidth=2;shape=mxgraph.networks."

C_OK = "#2E7D32"
C_TEMP = "#1565C0"
C_EXC = "#C62828"
C_DENY = "#757575"
C_TRUCK = "#EF6C00"
C_FABRIC = "#6A1B9A"
SIDE = {
    "bottom": "verticalLabelPosition=bottom;verticalAlign=top;",
    "right": "labelPosition=right;verticalLabelPosition=middle;align=left;verticalAlign=middle;spacingLeft=4;",
    "left": "labelPosition=left;verticalLabelPosition=middle;align=right;verticalAlign=middle;spacingRight=4;",
    "top": "verticalLabelPosition=top;verticalAlign=bottom;",
}


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

    def icon(self, x, y, kind, label, size=56, font=11, label_w=None, side="bottom"):
        cid = self._id("i")
        if kind == "cali_fw":
            kind = "firewall_onprem"
        if kind in ICON:
            style = (f"image;aspect=fixed;html=1;points=[];align=center;verticalLabelPosition=bottom;"
                     f"verticalAlign=top;fontSize={font};image={ICON[kind]};")
        else:
            style = NET + kind.replace("firewall_onprem", "firewall") + f";verticalLabelPosition=bottom;verticalAlign=top;fontSize={font};"
        if side != "bottom":
            style = style.replace(SIDE["bottom"], SIDE[side]).replace("align=center;", "")
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
    d.zone(740, 120, 790, 790, "Producción · vnet-prod 10.101.0.0/21", fill="#FAFAFA", stroke="#616161")

    d.icon(60, 165, "users", "Usuarios\n10.20.0.0/24", size=48, label_w=110)
    d.icon(60, 310, "server", "Servidores: aplicación,\nbase y archivo\n10.20.1 a 10.20.3", size=48, label_w=130)
    cali_fw = d.icon(205, 235, "firewall", "Firewall\nde Cali", size=56, label_w=80)
    d.icon(60, 530, "users", "Usuarios\n10.3X.0.0/24", size=48, label_w=110)
    d.icon(62, 640, "sensor", "Sensores de cuartos\nfríos 10.3X.1.0/24", size=44, label_w=130)
    c_vpn = d.icon(205, 595, "router", "Equipo VPN\ndel centro", size=48, label_w=90)
    trucks = d.icon(60, 985, "mobile", "Camiones\n(red móvil del operador)", size=48, label_w=150)
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
    iot_pub = d.icon(1000, 985, "iothub", "IoT Hub y DPS, endpoints públicos\n(Central US)", size=48, label_w=200)
    d.zone(col[0], 650, 470, 130, "Telemetría · snet-telemetry-func", fill="#FFFFFF", stroke="#9E9E9E", font=10)
    d.icon(col[0] + 30, 692, "func", "Función notificadora", size=48, font=10, label_w=130)
    d.text(col[0] + 170, 680, 290, 90, "NSG de la torre: 443 desde esta subred, solo para entregar alertas.\n"
           "Salida por el firewall: FW-319 a 321 (Teams, correo y SMS).", font=10)

    d.edge(cali_fw[0], vpngw[0], [(261, 263), (330, 263), (330, 190), (400, 190)], "4 túneles,\n2 proveedores", label_pos=(205, 172, 110), label_h=30)
    d.edge(c_vpn[0], vpngw[0], [(253, 619), (340, 619), (340, 215), (400, 215)], "2 túneles\npor centro", label_pos=(225, 455, 105), label_h=30)
    d.edge(vpngw[0], fw[0], [(456, 198), (516, 198), (516, 380)], "Todo lo que entra\npor la VPN", label_pos=(522, 270, 110), label_h=30)
    d.edge(fw[0], torre[0], [(552, 392), (720, 392), (720, 236), (851, 236)])
    d.edge(fw[0], ingest[0], [(552, 410), (735, 410), (735, 396), (851, 396)])
    d.edge(fw[0], integ[0], [(552, 446), (710, 446), (710, 556), (851, 556)], color=C_TEMP, dashed=True)
    d.edge(fw[0], internet[0], [(552, 428), (725, 428), (725, 475), (1545, 475), (1545, 55), (1480, 55)],
           "FW-301 a 321: salida a internet", label_pos=(1300, 466, 200))
    d.edge(vpngw[0], archive[0], [(456, 182), (560, 182), (560, 160), (1010, 160), (1010, 236), (1111, 236)],
           color=C_EXC, dashed=True)
    d.edge(internet[0], appgw[0], [(1445, 90), (1445, 236), (1419, 236)], "WAF: 443", label_pos=(1440, 120, 56))
    d.edge(appgw[0], portal[0], [(1419, 250), (1470, 250), (1470, 396), (1419, 396)], "443", label_pos=(1474, 300, 24))
    d.edge(bastion[0], admin[0], [(448, 644), (500, 644), (500, 870), (1260, 870), (1260, 556), (1371, 556)],
           "Bastion: NSG, 22 y 3389", label_pos=(880, 861, 160), color=C_EXC)
    d.edge(trucks[0], iot_pub[0], [(108, 1009), (1000, 1009)], "TLS y credencial por camión", label_pos=(470, 991, 180), color=C_EXC)

    d.text(30, 1080, 1500, 60,
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


def telemetry_ingest_alert():
    d = Diagram()
    d.text(30, 10, 1200, 30, "Telemetría: los dos caminos de ingesta y el camino de la alerta", font=14)
    d.zone(30, 70, 300, 320, "Ocho centros · camino 1", fill="#FFFDE7", stroke="#F9A825")
    d.zone(30, 470, 300, 230, "Camiones · camino 2", fill="#FFF3E0", stroke="#EF6C00")
    d.zone(390, 70, 280, 240, "Hub · East US 2", fill="#ECEFF1", stroke="#455A64")
    d.zone(390, 330, 280, 120, "vnet-prod\nsnet-ingest", fill="#E3F2FD", stroke="#1565C0", font=11)
    d.zone(710, 70, 300, 560, "Central US", fill="#E8EAF6", stroke="#3949AB")
    d.zone(1040, 70, 460, 640, "Producción East US 2 · vnet-prod", fill="#FAFAFA", stroke="#616161")
    d.zone(1550, 70, 220, 640, "Canales por internet\n(salida por el Azure Firewall)", fill="#F3E5F5", stroke="#6A1B9A", font=11)

    sensor = d.icon(60, 124, "sensor", "Sensores de cuartos fríos\n32 (4 por centro)\nuna lectura cada 30 s", size=48, label_w=150)
    router = d.icon(220, 124, "router", "Equipo VPN\ndel centro", size=48, label_w=100)
    d.icon(50, 280, "iot_edge", "", size=40)
    d.text(100, 262, 220, 76, "Recolector opcional por centro con IoT Edge, si los sensores no hablan MQTT o AMQP con TLS", font=10)
    truck = d.icon(100, 520, "mobile", "120 camiones (180 en campaña)\ntemperatura cada 60 s\nposición cada 30 s\nguardan 18 h sin señal", size=48, label_w=180)
    vpngw = d.icon(410, 110, "vpngw", "VPN Gateway", size=56, label_w=100)
    fw = d.icon(560, 110, "firewall", "Azure Firewall\nFW-204", size=56, label_w=76)
    pe = d.icon(560, 372, "pe", "Endpoints privados\nde IoT Hub y DPS", size=44, label_w=120)
    internet = d.icon(470, 500, "cloud", "Internet", size=70, label_w=80)
    dps = d.icon(832, 150, "dps", "DPS: alta automática\ncon certificados X.509", size=48, label_w=120, side="right")
    iot = d.icon(820, 350, "iothub", "IoT Hub S1 × 2 unidades\n800.000 mensajes al día\nredundante entre zonas", size=72, label_w=170)
    d.text(720, 560, 280, 60, "Si cae la región, IoT Hub se conmuta a mano a East US 2. Los dispositivos guardan sus lecturas hasta confirmar que llegaron.", font=10)

    ref = d.icon(1110, 150, "storage", "Rangos por cuarto frío\ny por tipo de carga\n(los mantiene calidad)", size=48, label_w=150, side="right")
    asa = d.icon(1100, 352, "asa", "Stream Analytics\nreglas de alerta\n1/3 SU V2 esperado", size=68, label_w=140)
    func = d.icon(1320, 352, "func", "Función notificadora\nFlex Consumption\nsnet-telemetry-func", size=68, label_w=160)
    eh = d.icon(1100, 560, "eventhub", "Event hub de estado\nen vivo para el mapa", size=56, label_w=150)
    eh_alert = d.icon(1224, 368, "eventhub", "Event hub\nde alertas", size=36, label_w=90, side="top")
    torre = d.icon(1320, 560, "aca", "API y consola de la torre\nsnet-app-torre", size=64, label_w=170)

    teams = d.icon(1636, 150, "laptop", "Teams (Workflows)\ncomputador y teléfono", size=48, label_w=150)
    mail = d.icon(1636, 290, "acs", "Correo: Azure\nCommunication Services", size=48, label_w=150)
    sms = d.icon(1636, 430, "mobile", "SMS: proveedor con\ncobertura en Colombia", size=48, label_w=150)

    d.edge(sensor[0], router[0], [(108, 148), (220, 148)], color=C_TEMP)
    d.edge(router[0], vpngw[0], [(268, 138), (410, 138)], "IPsec", label_pos=(318, 118, 50), color=C_TEMP)
    d.edge(vpngw[0], fw[0], [(466, 138), (560, 138)], color=C_TEMP)
    d.edge(fw[0], pe[0], [(616, 138), (640, 138), (640, 350), (582, 350), (582, 372)], color=C_TEMP)
    d.edge(pe[0], iot[0], [(604, 394), (820, 394)], "Privado, entre regiones", label_pos=(614, 374, 140), color=C_TEMP)
    d.edge(truck[0], internet[0], [(148, 544), (470, 544)], "Red móvil del operador", label_pos=(220, 524, 150), color=C_TRUCK)
    d.edge(internet[0], iot[0], [(540, 535), (760, 535), (760, 412), (820, 412)], "TLS y credencial por camión",
           label_pos=(562, 515, 170), color=C_TRUCK)
    d.edge(dps[0], iot[0], [(856, 198), (856, 350)], color=C_DENY, dashed=True)
    d.edge(iot[0], asa[0], [(892, 386), (1100, 386)], "Endpoint de eventos", label_pos=(915, 366, 130), color=C_OK)
    d.edge(ref[0], asa[0], [(1134, 198), (1134, 352)], color=C_DENY, dashed=True)
    d.edge(asa[0], eh_alert[0], [(1168, 386), (1224, 386)], color=C_EXC)
    d.edge(eh_alert[0], func[0], [(1260, 386), (1320, 386)], color=C_EXC)
    d.edge(asa[0], eh[0], [(1100, 400), (1070, 400), (1070, 588), (1100, 588)], color=C_OK)
    d.edge(eh[0], torre[0], [(1156, 588), (1320, 588)], "Mapa en vivo", label_pos=(1190, 568, 100), color=C_OK)
    d.edge(func[0], torre[0], [(1388, 404), (1470, 404), (1470, 592), (1384, 592)], "Alerta", label_pos=(1420, 500, 46), color=C_EXC)
    d.edge(func[0], teams[0], [(1388, 358), (1530, 358), (1530, 174), (1636, 174)], color=C_EXC)
    d.edge(func[0], mail[0], [(1388, 372), (1540, 372), (1540, 314), (1636, 314)], color=C_EXC)
    d.edge(func[0], sms[0], [(1388, 386), (1530, 386), (1530, 454), (1636, 454)], color=C_EXC)

    d.box(30, 740, 560, 80, "Volumen declarado (mensajes de 1 KB)\nNormal: 7,2 mensajes por segundo, unos 486.000 al día\n"
          "Campaña con 180 camiones: 10,2 por segundo, unos 682.000 al día", "#FFFFFF", "#9E9E9E", font=11)
    d.box(620, 740, 560, 80, "Presupuesto de la alerta: hasta 40 s desde la hora de la lectura del sensor\nhasta que se ve en pantalla "
          "(5 + 10 + 10 + 5 + 10 s), con 20 s de margen dentro del minuto", "#FFFFFF", "#9E9E9E", font=11)
    d.box(1210, 740, 560, 80, "Destinatario según la hora de Colombia\n04:00 a 22:00: torre de control (consola y Teams), copia a calidad\n"
          "22:00 a 04:00: guardia de calidad (Teams, correo y SMS). Escala a los 5 y a los 15 minutos", "#FFFFFF", "#9E9E9E", font=11)
    d.text(30, 840, 1740, 30,
           "Azul: camino 1, cuartos fríos por la VPN y el Azure Firewall. Naranja: camino 2, camiones por internet. Verde: lecturas hacia el procesamiento y el mapa. "
           "Rojo: alertas. Gris punteado: configuración. Stream Analytics también escribe el historial (ver el diagrama del historial).", font=10)
    return d


def telemetry_history_dashboards():
    d = Diagram()
    d.text(30, 10, 1200, 30, "Telemetría: historial de cinco años y tableros", font=14)
    d.zone(30, 70, 340, 560, "Central US", fill="#E8EAF6", stroke="#3949AB")
    d.zone(420, 70, 520, 620, "Producción East US 2 · vnet-prod", fill="#FAFAFA", stroke="#616161")
    d.zone(1000, 70, 460, 620, "Microsoft Fabric", fill="#F3E5F5", stroke="#6A1B9A")

    iot = d.icon(130, 150, "iothub", "IoT Hub", size=64, label_w=90, side="left")
    evid = d.icon(130, 330, "datalake", "Evidencia cruda\nADLS Gen2, JSON\nretención bloqueada\n5 años, GRS", size=64, label_w=150, side="right")
    d.text(40, 540, 320, 76, "Cuenta propia, separada del archivo. Nadie puede modificar ni borrar los archivos, ni siquiera un administrador. Vale en reclamos.", font=10)
    asa = d.icon(490, 150, "asa", "Stream Analytics", size=64, label_w=140, side="top")
    delta = d.icon(490, 330, "datalake", "Tabla de análisis (Delta)\ndetalle, resumen de 5 min\ny alertas", size=64, label_w=170)
    eh = d.icon(650, 154, "eventhub", "Event Hub\nestado en vivo", size=56, label_w=120)
    torre = d.icon(820, 150, "aca", "Consola de\nla torre", size=64, label_w=100)
    func = d.icon(820, 450, "func", "Función\nnotificadora", size=64, label_w=100)
    portal = d.icon(820, 600, "aca", "Portal de rastreo\nsnet-app-portal", size=64, label_w=130, side="left")
    clients = d.icon(828, 760, "users", "Clientes corporativos:\nsolo sus guías, sin la flota\nni la posición exacta", size=48, label_w=170, side="right")

    short = d.icon(1060, 330, "onelake", "Acceso directo\nde OneLake", size=64, label_w=120)
    model = d.icon(1230, 330, "semantic", "Modelo semántico\nDirect Lake\nseguridad por filas", size=64, label_w=140)
    reports = d.icon(1238, 150, "laptop", "Tableros de calidad\nen Power BI", size=48, label_w=130, side="right")
    emb = d.icon(1230, 520, "pbi_embedded", "Reporte insertado\ntoken V2 con la\nidentidad del cliente", size=64, label_w=150)

    d.edge(iot[0], evid[0], [(162, 214), (162, 330)], "Enrutamiento\na almacenamiento", label_pos=(172, 256, 120), label_h=30, color=C_TEMP)
    d.edge(iot[0], asa[0], [(194, 182), (490, 182)], "Endpoint de eventos", label_pos=(270, 162, 140), color=C_TEMP)
    d.edge(asa[0], delta[0], [(522, 214), (522, 330)], "Salida Delta", label_pos=(530, 262, 80), color=C_TEMP)
    d.edge(asa[0], eh[0], [(554, 182), (650, 182)], color=C_OK)
    d.edge(eh[0], torre[0], [(706, 182), (820, 182)], "Mapa en vivo", label_pos=(716, 162, 96), color=C_OK)
    d.edge(func[0], evid[0], [(820, 482), (162, 482), (162, 394)], "Alertas y acuses, con quién y cuándo", label_pos=(560, 462, 230), color=C_EXC)
    d.edge(delta[0], short[0], [(554, 362), (1060, 362)], "Fabric lee sin copiar", label_pos=(740, 342, 140), color=C_FABRIC)
    d.edge(short[0], model[0], [(1124, 362), (1230, 362)], color=C_FABRIC)
    d.edge(model[0], reports[0], [(1262, 330), (1262, 198)], color=C_FABRIC)
    d.edge(model[0], emb[0], [(1294, 370), (1430, 370), (1430, 552), (1294, 552)], color=C_FABRIC)
    d.edge(emb[0], portal[0], [(1230, 552), (1150, 552), (1150, 632), (884, 632)], "Inserta el reporte", label_pos=(1015, 612, 120), color=C_FABRIC)
    d.edge(portal[0], clients[0], [(852, 664), (852, 760)], "Por el WAF", label_pos=(862, 700, 80), color=C_FABRIC)

    d.text(30, 860, 1430, 46,
           "Azul: lecturas. Verde: estado en vivo. Rojo: alertas. Morado: lectura de Fabric. Cinco años de detalle son unos 890 millones de filas; el resumen de 5 minutos, "
           "unos 64 millones, queda bajo el tope de Direct Lake de las capacidades pequeñas (300 millones de filas por tabla en F2 a F32). Los tableros usan el resumen.", font=10)
    return d


# ---------------------------------------------------------------------------------------------------------------
# Hybrid network and subnet diagrams. The layout is the hand-placed grid first validated in Lucidchart: every
# connector is made of horizontal and vertical segments that enter icons from the side or from the top, never
# through the label under an icon.

NICON = 70
N_SOLID = "#1F3A5F"
N_DASH = "#5F6368"
N_BLUE = "#1E88E5"

CLS = {
    "vehicle": "mobile", "mobile": "mobile_az", "browser": "browser", "users": "users_az", "farm": "server_farm",
    "files": "files", "lb": "lb", "lng": "lng", "iiot": "iiot", "edge": "iot_edge", "vrouter": "vrouter",
    "connections": "connections", "dns": "dns", "bastion": "bastion", "vpngw": "vpngw", "fw": "firewall",
    "fwpol": "fw_policy", "appgw": "appgw", "aks": "aks", "aca": "aca", "pe": "pe", "mysql": "mysql",
    "fabgw": "fabricgw", "dms": "dms", "vm": "vm", "iothub": "iothub", "dps": "dps", "storage": "storage",
    "fabric": "pbi_embedded", "pip": "pip", "rt": "route_table", "waf": "waf", "redis": "redis", "kv": "kv",
    "func": "func", "cali_fw": "cali_fw",
}


class NetPage(Diagram):
    """Diagram with named shapes, relative anchor points and segment-labelled connectors."""

    def __init__(self):
        super().__init__()
        self.bb = {}
        self.cid = {}

    def ic(self, sid, cls, x, y, label, label_w=200, font=15):
        cid, _ = self.icon(x, y, CLS[cls], label, size=NICON, font=font, label_w=label_w)
        self.bb[sid], self.cid[sid] = (x, y, NICON, NICON), cid

    def _container(self, sid, x, y, w, h, label, stroke, fill, dashed, icon, font=17, bottom=False):
        self.zone(x, y, w, h, label, fill=fill, stroke=stroke, dashed=dashed, font=font, bold=False)
        self.cells[-1] = self.cells[-1].replace("spacingLeft=8;", "spacingLeft=36;spacingTop=6;")
        if bottom:
            self.cells[-1] = self.cells[-1].replace("verticalAlign=top;", "verticalAlign=bottom;spacingBottom=8;")
        if icon:
            self.icon(x + 8, y + 8, icon, "", size=24)
        self.bb[sid] = (x, y, w, h)

    def vnet(self, sid, x, y, w, h, label, dashed=False):
        self._container(sid, x, y, w, h, label, N_BLUE, "none", True, "vnet")

    def region(self, sid, x, y, w, h, label, dashed=False, bottom=False):
        self._container(sid, x, y, w, h, label, N_BLUE, "none", dashed, "subscription", bottom=bottom)

    def subnet(self, sid, x, y, w, h, label):
        self._container(sid, x, y, w, h, label, "#BDBDBD", "#F5F5F5", False, "subnet", font=16)

    def group(self, sid, x, y, w, h, label, dashed=False):
        self.zone(x, y, w, h, label, fill="none", stroke="#212121", dashed=dashed, font=17, bold=True)
        self.bb[sid] = (x, y, w, h)

    def cloud(self, sid, x, y, w, h, label, dashed=False, font=14):
        cid = self._id("c")
        style = (f"ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor={N_DASH if dashed else N_SOLID};"
                 f"strokeWidth=2;fontSize={font};{'dashed=1;' if dashed else ''}")
        self.cells.append(f'<mxCell id="{cid}" value="{escape(label, {chr(10): "&lt;br&gt;"})}" style="{style}" vertex="1" parent="1">'
                          f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        self.bb[sid] = (x, y, w, h)

    def table(self, x, y, col_w, row_h, rows):
        for yi, row in enumerate(rows):
            cx = x
            for xi, val in enumerate(row):
                self.box(cx, y + yi * row_h, col_w[xi], row_h, val, "#DCE6F2" if yi == 0 else "#FFFFFF", "#212121",
                         font=13, bold=yi == 0)
                self.cells[-1] = self.cells[-1].replace("rounded=1;", "rounded=0;")
                cx += col_w[xi]

    def at(self, sid, rx, ry):
        x, y, w, h = self.bb[sid]
        return (x + rx * w, y + ry * h)

    def link(self, a, pa, b, pb, via=(), label=None, seg=-1, pos=0.5, side="top", dashed=False, arrow=True):
        pts = [self.at(a, *pa)] + list(via) + [self.at(b, *pb)]
        self.poly(pts, dashed=dashed, arrow=arrow)
        if label:
            segs = list(zip(pts[:-1], pts[1:]))
            (x1, y1), (x2, y2) = segs[seg]
            px, py = x1 + (x2 - x1) * pos, y1 + (y2 - y1) * pos
            w = max(50, int(8.4 * max(len(t) for t in label.split("\n")))) + 12
            h = 22 * (label.count("\n") + 1)
            if y1 == y2:   # horizontal segment
                ly = py - h - 2 if side == "top" else (py + 2 if side == "bottom" else py - h / 2)
                lx = px - w / 2
            else:          # vertical segment: label on the line
                lx, ly = px - w / 2, py - h / 2
            self.text(lx, ly, w, h, label, font=14, color=N_DASH if dashed else N_SOLID, fill="default", align="center")

    def poly(self, pts, dashed=False, arrow=True):
        cid = self._id("e")
        color = N_DASH if dashed else N_SOLID
        style = (f"edgeStyle=none;html=1;rounded=0;endArrow={'block' if arrow else 'none'};endFill=1;strokeColor={color};"
                 f"strokeWidth=2;{'dashed=1;dashPattern=8 6;' if dashed else ''}")
        (sx, sy), (tx, ty) = pts[0], pts[-1]
        mids = "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in pts[1:-1])
        geo = (f'<mxGeometry relative="1" as="geometry"><mxPoint x="{sx}" y="{sy}" as="sourcePoint"/>'
               f'<mxPoint x="{tx}" y="{ty}" as="targetPoint"/>'
               f'{"<Array as=" + chr(34) + "points" + chr(34) + ">" + mids + "</Array>" if mids else ""}</mxGeometry>')
        self.cells.append(f'<mxCell id="{cid}" value="" style="{style}" edge="1" parent="1">{geo}</mxCell>')


NL, NR, NT, NB = (0, 0.5), (1, 0.5), (0.5, 0), (0.5, 1)
R0, R1, R2, R3 = 500, 760, 1000, 1240
CY = {r: r + NICON / 2 for r in (R0, R1, R2, R3)}
LNG_X, JOG_X = 1660, 1820
CA, CB = 1980, 2240
C8, C9, C10, C11, C12, C13 = 2900, 3160, 3420, 3680, 3940, 4200
UP_X, DOWN_X = 2460, 2500
COPY_Y, COPY_X = 1400, 3620


def net_title(d, text, sub):
    d.text(0, -170, 2600, 40, text, font=26, color="#212121")
    d.cells[-1] = d.cells[-1].replace("fontSize=26;", "fontSize=26;fontStyle=1;")
    d.text(0, -125, 2600, 30, sub, font=18, color="#212121")


def network_overview(steady, aks=False):
    d = NetPage()
    phase = "Estado estable (después del día 90)" if steady else "Convivencia (máximo 90 días)"
    if aks:
        net_title(d, f"FríoAndes · Alternativa con Kubernetes (AKS) · {phase}",
                  "Cambia solo la plataforma de aplicación; la red común es la misma")
    else:
        net_title(d, f"FríoAndes · Red híbrida · {phase}",
                  "Plan de direcciones verificado sin solapamiento con las 23 subredes on-premises")

    # Containers first, so icons and lines stay on top
    d.group("ext", 1580, 0, 2760, 300, "Internet y terceros")
    d.group("onprem", 0, 560, 1250, 1620, "On-premises FríoAndes")
    d.group("cali", 40, 620, 1170, 480, "Sede Cali · 10.20.0.0/16" + ("" if steady else " · datacenter en convivencia"))
    d.group("centros", 40, 1200, 1170, 940, "8 centros · 10.31.0.0/16 a 10.38.0.0/16")
    d.group("ctipo", 80, 1640, 1090, 460, "Centro tipo (igual en los 8)")
    d.region("azure", 1580, 440, 2760, 1260, "Azure · East US 2 · 10.100.0.0/14")
    d.vnet("hub", 1880, 660, 680, 720, "vnet-hub · 10.100.0.0/23")
    d.vnet("prod", 2640, 660, 1300, 800, "vnet-prod · 10.101.0.0/21")
    d.vnet("test", 1960, 1480, 230, 160, "vnet-test · 10.102.0.0/21")
    d.text(1980, 1550, 190, 60, "Mismo módulo de subredes", font=15)
    d.vnet("dev", 2230, 1480, 230, 160, "vnet-dev · 10.103.0.0/21")
    d.text(2250, 1550, 190, 60, "Mismo módulo de subredes", font=15)
    d.region("cus", 4400, 560, 400, 380, "Azure · Central US\nPaaS de la telemetría, sin red virtual", bottom=True)
    d.group("fabbox", 4420, 970, 320, 260, "Microsoft Fabric (SaaS)")
    if steady:
        d.region("pareja", 2520, 1780, 520, 160, "Central US · 10.104.0.0/15 (reserva)", dashed=True)

    # Internet and third parties
    d.ic("camion", "vehicle", 1660, 65, "Camiones\n120, 180 en campaña")
    d.ic("movil", "mobile", 1960, 65, "Red móvil\ndel operador")
    d.cloud("inet", 2400, 40, 300, 200, "Internet", font=22)
    d.ic("clientes", "browser", 2900, 65, "Clientes del portal\nunos 2.000")
    d.ic("remotos", "users", 3200, 165, "Equipos remotos\nacceso administrativo")

    # On-premises
    d.ic("cali-usr", "users", 100, R1, "Usuarios y torre\n10.20.0.0/24")
    if not steady:
        d.ic("cali-app", "farm", 290, R1, "App y front\n10.20.1.0/24")
        d.ic("cali-db", "farm", 480, R1, "MySQL 5.7 y Redis 5\n10.20.2.0/24")
        d.ic("cali-arc", "files", 670, R1, "Archivo NFS 1,2 PB\n10.20.3.0/24")
        d.ic("cali-pub", "lb", 860, R1, "Nginx del rastreo\n10.20.5.0/24")
    d.ic("cali-fw", "cali_fw", 1050, R1, "Firewall de Cali\non-premises")
    centres = [("Buenaventura", "10.31"), ("Bogotá", "10.32"), ("Medellín", "10.33"), ("Barranquilla", "10.34"),
               ("Bucaramanga", "10.35"), ("Pereira", "10.36"), ("Pasto", "10.37"), ("Neiva", "10.38")]
    for k, (name, net) in enumerate(centres):
        d.ic(f"c{k}", "lng", 100 + (k % 4) * 280, 1290 if k < 4 else 1470, f"{name}\n{net}.0.0/16")
    d.ic("ct-usr", "users", 140, 1720, "Usuarios\n10.3X.0.0/24")
    d.ic("ct-sen", "iiot", 140, 1960, "Sensores cuartos fríos\n10.3X.1.0/24")
    d.ic("ct-edge", "edge", 520, 1960, "Recolector local\nsi existe")
    d.ic("ct-vpn", "vrouter", 940, 1960, "Equipo VPN\nIKEv2 y BGP")
    d.cloud("isp1", 1330, CY[R1] - 50, 190, 100, "ISP 1 · 400 Mbps")
    d.cloud("isp2", 1330, CY[R2] - 50, 190, 100, "ISP 2 · respaldo\notra ruta física", font=12)

    # Azure East US 2
    d.ic("conn", "connections", LNG_X, R0, "10 conexiones sitio a sitio\nCali cuenta 2")
    d.ic("lng1", "lng", LNG_X, R1, "Cali por ISP 1\n2 túneles y BGP")
    d.ic("lng2", "lng", LNG_X, R2, "Cali por ISP 2\n2 túneles, respaldo")
    d.ic("lngc", "lng", LNG_X, R3, "8 centros\n2 túneles y BGP cada uno")
    d.ic("dnsin", "dns", CA, R1, "DNS Resolver\nentrada", label_w=150)
    d.ic("bastion", "bastion", CB, R1, "Azure Bastion\nEntra ID y MFA", label_w=150)
    d.ic("vpngw", "vpngw", CA, R2, "VPN Gateway\nVpnGw1AZ activo-activo", label_w=170)
    d.ic("azfw", "fw", CB, R2, "Azure Firewall\nStandard", label_w=150)
    d.ic("dnsout", "dns", CA, R3, "DNS Resolver\nsalida a Cali", label_w=150)
    d.ic("fwpol", "fwpol", CB, R3, "Política del firewall\nreglas por zona", label_w=170)
    d.ic("appgw", "appgw", C8, R1, "App Gateway v2 con WAF\nsnet-ingress")
    if aks:
        d.ic("caepor", "aks", C9, R1, "Clúster AKS del portal\nsnet-app-portal")
        d.ic("caetor", "aks", C8, R2, "Clúster AKS de la torre\nsnet-app-torre")
    else:
        d.ic("caepor", "aca", C9, R1, "Apps del portal\nsnet-app-portal")
        d.ic("caetor", "aca", C8, R2, "Consola de la torre\nsnet-app-torre")
    d.ic("func", "func", C11, R1, "Función notificadora\nsnet-telemetry-func", label_w=180)
    d.ic("peing", "pe", C12, R1, "Ingesta privada\nsnet-ingest", label_w=150)
    d.ic("mysql", "mysql", C10, R2, "MySQL Flexible HA\nsnet-data", label_w=170)
    d.ic("fabgw", "fabgw", C11, R2, "Gateway de datos Fabric\nsnet-fabric-egress", label_w=190)
    d.ic("pearc", "pe", C12, R3, "Archivo privado\nsnet-archive", label_w=150)
    if aks:
        d.ic("apisrv", "lb", C10, R3, "API privada de AKS\nsnet-aks-apiserver")
    if not steady:
        d.ic("dms", "dms", C9, R3, "DMS (temporal)\nsnet-cali-integration")
        d.ic("vmcopy", "vm", C11, R3, "Copia del archivo\ntemporal", label_w=160)
    d.ic("saarc", "storage", C13, R3, "Archivo en Blob\nNFS 3.0 privado", label_w=150)
    d.ic("iothub", "iothub", 4440, R1, "IoT Hub\ningesta de telemetría", label_w=160)
    d.ic("dps", "dps", 4640, R1, "DPS\nalta de dispositivos", label_w=140)
    d.ic("fabric", "fabric", 4545, R2 + 60, "Capacidad F\nIA de la torre", label_w=150)

    d.cloud("nube2", 1760, 1780, 300, 130, "Segunda nube · 10.110.0.0/15\nreserva a 24 meses", dashed=True, font=12)
    if not steady:
        d.text(620, 1110, 560, 60, "VPN actual de los centros a Cali (línea punteada):\nse retira centro por centro, a más tardar el día 90", font=15)
    d.text(3300, 1740, 1040, 230,
           "Leyenda\nLínea continua: tráfico vigente\n"
           + ("Línea punteada: conexión futura (segunda nube y región pareja)\n" if steady else
              "Línea punteada: tráfico temporal de la convivencia o conexión futura\n")
           + "Líneas sin flecha entre redes virtuales: peering con el hub\n"
           "IoT Hub y DPS viven en Central US, donde IoT Hub es redundante entre zonas; sus endpoints privados están en snet-ingest\n"
           "La función notificadora entrega las alertas a la torre (ver los diagramas de la telemetría)", font=17)

    # Top band
    d.link("camion", NR, "movil", NL, label="Red celular")
    d.link("movil", NR, "inet", (0, 0.3), label="Operador")
    d.link("clientes", NL, "inet", (1, 0.3), label="HTTPS")
    d.link("remotos", NL, "inet", (1, 0.8))
    bx = d.at("bastion", 0.5, 0)[0]
    d.link("inet", (0.2, 1), "bastion", NT, via=[(2460, 330), (bx, 330)])
    ax = d.at("appgw", 0.5, 0)[0]
    d.link("inet", (0.5, 1), "appgw", NT, via=[(2550, 360), (ax, 360)], label="HTTPS 443, única entrada pública",
           seg=2, pos=0.45, side="middle")
    ix = d.at("iothub", 0.5, 0)[0]
    d.link("inet", (0.8, 1), "iothub", NT, via=[(2640, 390), (ix, 390)], label="Camino 2: camiones (TLS)",
           seg=1, pos=0.85, side="top")

    # Cali: servers on a bus above the row, into the top of the firewall
    srcs = ["cali-usr"] + ([] if steady else ["cali-app", "cali-db", "cali-arc"])
    fw_top = d.at("cali-fw", 0.5, 0)
    bus_y = R1 - 40
    for sname in srcs:
        sx = d.at(sname, 0.5, 0)[0]
        d.poly([(sx, R1), (sx, bus_y)], arrow=False)
    d.poly([(d.at(srcs[0], 0.5, 0)[0], bus_y), (fw_top[0], bus_y), fw_top])
    if not steady:
        d.link("cali-fw", NL, "cali-pub", NR, label="NAT", dashed=True)
        d.link("centros", (560 / 1170, 0), "cali", (560 / 1170, 1), dashed=True)
    d.link("cali-fw", NR, "isp1", NL, label="Salida principal", pos=0.5)
    y2 = d.at("cali-fw", 1, 0.8)[1]
    d.link("cali-fw", (1, 0.8), "isp2", NL, via=[(1290, y2), (1290, CY[R2])])
    d.link("isp1", NR, "lng1", NL)
    d.link("isp2", NR, "lng2", NL)
    d.link("centros", (1, (CY[R3] - 1200) / 940), "lngc", NL, label="IPsec directo a Azure")
    vx = d.at("ct-vpn", 0.5, 0)[0]
    d.link("ct-usr", NR, "ct-vpn", NT, via=[(vx, 1755)])
    d.link("ct-sen", NR, "ct-edge", NL, label="Lecturas cada 30 s")
    d.link("ct-edge", NR, "ct-vpn", NL)

    # Gateways into the VPN Gateway
    for lng, ry in (("lng1", 0.25), ("lngc", 0.75)):
        y_in = d.at("vpngw", 0, ry)[1]
        d.link(lng, NR, "vpngw", (0, ry), via=[(JOG_X, d.at(lng, 1, 0.5)[1]), (JOG_X, y_in)])
    d.link("lng2", NR, "vpngw", NL)
    d.link("vpngw", NR, "azfw", NL, label="UDR")

    # Firewall into prod
    d.link("azfw", NR, "caetor", NL, label="Torre: 443, solo red corporativa", pos=0.62, side="bottom")
    up_y = d.at("azfw", 1, 0.2)[1]
    px = d.at("peing", 0.5, 0)[0]
    d.link("azfw", (1, 0.2), "peing", NT, via=[(UP_X, up_y), (UP_X, R1 - 40), (px, R1 - 40)],
           label="Camino 1: sensores por la VPN y el firewall", seg=2, pos=0.55)
    if not steady:
        dn_y = d.at("azfw", 1, 0.8)[1]
        d.link("azfw", (1, 0.8), "dms", NL, via=[(DOWN_X, dn_y), (DOWN_X, CY[R3])], dashed=True)
        dx = d.at("dms", 0.5, 0)[0]
        my = d.at("mysql", 0, 0.8)[1]
        d.link("dms", NT, "mysql", (0, 0.8), via=[(dx, my)], label="Carga en línea", seg=0, dashed=True)
        cy0 = d.at("vpngw", 1, 0.85)[1]
        d.link("vpngw", (1, 0.85), "vmcopy", NL, via=[(2145, cy0), (2145, COPY_Y), (COPY_X, COPY_Y), (COPY_X, CY[R3])],
               label="Copia del archivo, unos 37 Mbps, fuera del firewall", seg=2, pos=0.5, dashed=True)
        d.link("vmcopy", NR, "pearc", NL, dashed=True)

    # Prod
    d.link("appgw", NR, "caepor", NL, label="HTTPS")
    d.link("caetor", NR, "mysql", NL, label="MySQL 3306", pos=0.3)
    mx = d.at("mysql", 0.5, 0)[0]
    d.link("caepor", NR, "mysql", NT, via=[(mx, CY[R1])], label="Lectura 3306", seg=1, pos=0.6)
    d.link("fabgw", NL, "mysql", NR, label="Lectura 3306")
    fy = d.at("fabric", 0, 0.5)[1]
    d.link("fabgw", (1, 0.35), "fabric", NL, via=[(4370, d.at("fabgw", 1, 0.35)[1]), (4370, fy)], label="Salida a Fabric", seg=0, pos=0.75)
    ax2 = d.at("pearc", 0.5, 0)[0]
    d.link("fabgw", (1, 0.75), "pearc", NT, via=[(ax2, d.at("fabgw", 1, 0.75)[1])], label="Lectura 443", seg=1, pos=0.5)
    d.link("pearc", NR, "saarc", NL, label="Private Link")
    d.link("peing", NR, "iothub", NL, label="Private Link, entre regiones", pos=0.5)

    # Peering and future connections
    d.link("hub", (1, (1155 - 660) / 720), "prod", (0, (1155 - 660) / 800), arrow=False)
    d.link("hub", ((2075 - 1880) / 680, 1), "test", NT, arrow=False)
    d.link("hub", ((2345 - 1880) / 680, 1), "dev", NT, arrow=False)
    d.link("nube2", NT, "hub", ((1910 - 1880) / 680, 1), label="Futuro: VPN o ExpressRoute", pos=0.3, dashed=True)
    if steady:
        hy = d.at("hub", 1, 0.97)[1]
        d.link("hub", (1, 0.97), "pareja", ((2600 - 2520) / 520, 0), via=[(2600, hy)],
               label="Futuro: peering global o VPN", seg=1, pos=0.7, dashed=True)
    return d


def network_subnets(aks=False):
    d = NetPage()
    if aks:
        net_title(d, "FríoAndes · Alternativa con Kubernetes (AKS) · Hub y prod: subredes, CIDR y servicios",
                  "Pruebas y desarrollo repiten el mismo módulo · plan de direcciones verificado sin solapamiento")
    else:
        net_title(d, "FríoAndes · Hub y prod: subredes, CIDR y servicios",
                  "Pruebas y desarrollo repiten el mismo módulo · plan de direcciones verificado sin solapamiento")
    plan = list(csv.DictReader(open(DATA / ("ip-plan-aks.csv" if aks else "ip-plan.csv"), encoding="utf-8")))
    cidr = {(r["vnet"], r["subnet"]): r["cidr"] for r in plan}

    cols, prod_h = 5, 1090
    prod_w = 40 + cols * 465
    d.vnet("hub", 0, 0, 900, 1130, "vnet-hub · 10.100.0.0/23")
    d.vnet("prod", 1000, 0, prod_w, prod_h, "vnet-prod · 10.101.0.0/21")
    hub_subnets = [
        ("GatewaySubnet", [("vpngw", "vpngw", "VPN Gateway\nVpnGw1AZ")]),
        ("AzureFirewallSubnet", [("azfw", "fw", "Azure Firewall\nStandard")]),
        ("AzureFirewallManagementSubnet", [("fwmip", "pip", "IP de gestión\ndel firewall")]),
        ("AzureBastionSubnet", [("bastion", "bastion", "Azure Bastion\nEntra ID y MFA")]),
        ("snet-dns-inbound", [("dnsin", "dns", "DNS Resolver\nentrada")]),
        ("snet-dns-outbound", [("dnsout", "dns", "DNS Resolver\nsalida")]),
    ]
    prod_subnets = [
        ("snet-ingress", [("waf", "waf", "Política WAF\nOWASP y límite"), ("pip", "pip", "IP pública\ndel portal"),
                          ("appgw", "appgw", "App Gateway v2\nhasta 10 instancias")]),
        ("snet-app-portal", [("caepor", "aks" if aks else "aca", "Nodos AKS\nclúster del portal" if aks else "Container Apps\nportal")]),
        ("snet-app-torre", [("caetor", "aks" if aks else "aca", "Nodos AKS\nclúster de la torre" if aks else "Container Apps\ntorre (interno)")]),
        ("snet-data", [("mysql", "mysql", "MySQL Flexible\nHA entre zonas")]),
        ("snet-data-pe", [("pedat", "pe", "Endpoints privados: Redis, Key Vault,\nEvent Hubs y cuenta de la función")]),
        ("snet-archive", [("pearc", "pe", "Endpoints privados Blob y DFS:\narchivo e historial de telemetría")]),
        ("snet-ingest", [("peing", "pe", "Endpoints privados\nIoT Hub y DPS")]),
        ("snet-admin", [("vmadm", "vm", "Agentes\ndespliegue y operación")]),
        ("snet-cali-integration", [("dms", "dms", "DMS\ntemporal"), ("vmcopy", "vm", "Copia del archivo\ntemporal")]),
        ("snet-fabric-egress", [("fabgw", "fabgw", "Gateway de datos\nFabric")]),
    ]
    extra = [(2, 2, "snet-aks-apiserver", [("apisrv", "lb", "API privada\nde los clústeres")])] if aks else []
    extra.append((4, 2, "snet-telemetry-func", [("func", "func", "Función notificadora\nFlex Consumption")]))

    for k, (name, icons) in enumerate(hub_subnets):
        x, y = 40 + (k % 2) * 440, 80 + (k // 2) * 300
        short = "Gestión del firewall" if name == "AzureFirewallManagementSubnet" else name
        d.subnet(f"sh{k}", x, y, 400, 240, f"{short} · {cidr[('vnet-hub', name)]}")
        for sid, cls, label in icons:
            d.ic(sid, cls, x + 165, y + 80, label, label_w=200)
    placed = [(k % cols, k // cols, name, icons) for k, (name, icons) in enumerate(prod_subnets)] + extra
    for col, row, name, icons in placed:
        x, y = 1040 + col * 465, 80 + row * 330
        d.subnet(f"sp-{name}", x, y, 425, 270, f"{name} · {cidr[('vnet-prod', name)]}")
        n = len(icons)
        for j, (sid, cls, label) in enumerate(icons):
            ix = x + (425 - (n * NICON + (n - 1) * 70)) // 2 + j * (NICON + 70)
            d.ic(sid, cls, ix, y + 90, label, label_w=130 if n > 1 else 300)
    d.ic("rt", "rt", 80, 1000, "Rutas al firewall\nUDR", label_w=160)

    side_x = 1000 + prod_w + 100
    d.ic("redis", "redis", side_x, 170, "Azure Managed Redis\ncaché del rastreo")
    d.ic("kv", "kv", side_x, 500, "Key Vault\nsecretos y llaves")
    low_y = prod_h + 120
    d.ic("saarc", "storage", 1150, low_y, "Cuentas del archivo\ny del historial de telemetría", label_w=220)
    d.ic("iothub", "iothub", 1615, low_y, "IoT Hub y DPS\nen Central US", label_w=160)

    d.link("pip", NR, "appgw", NL)
    d.link("appgw", NR, "caepor", NL, label="HTTPS")
    d.link("caetor", NR, "mysql", NL, label="3306")
    d.link("pedat", NR, "redis", NL, label="Private Link", pos=0.45)
    gap_x = 1000 + prod_w + 40
    ry, ky = d.at("pedat", 1, 0.5)[1], d.at("kv", 0, 0.5)[1]
    d.poly([(gap_x, ry), (gap_x, ky), d.at("kv", 0, 0.5)])
    for pe, target, x_side in (("pearc", "saarc", 1065), ("peing", "iothub", 1530)):
        ty = d.at(target, 0, 0.5)[1]
        d.link(pe, NL, target, NL, via=[(x_side, d.at(pe, 0, 0.5)[1]), (x_side, ty)],
               label="Private Link", seg=1, pos=0.8)
    d.link("vpngw", NR, "azfw", NL, label="UDR")
    d.link("hub", (1, 720 / 1130), "prod", (0, 720 / prod_h), arrow=False)

    rows = [["Subred", "prod", "test", "dev"], ["Red virtual", "10.101.0.0/21", "10.102.0.0/21", "10.103.0.0/21"]]
    names = [n for n, _ in prod_subnets] + [e[2] for e in extra]
    for name in names:
        rows.append([name] + [cidr[(v, name)] for v in ("vnet-prod", "vnet-test", "vnet-dev")])
    table_y = low_y + 220
    d.table(2000, table_y, [230, 150, 150, 150], 34, rows)
    reserves = [["Reserva", "Rango"]] + [[r["vnet"], r["cidr"]] for r in plan if r["env"] == "reserva"]
    reserves.append(["on-premises (crecimiento)", "10.20 y 10.31 a 10.38 (cada uno /16)"])
    d.table(1000, table_y, [260, 420], 34, reserves)
    d.text(0, 1200, 900, 120, "Cómo leer esta página\nCada recuadro es una subred con su CIDR. Pruebas y desarrollo repiten "
           "el mismo módulo (tabla). El verificador comprueba que ningún rango choca con las 23 subredes on-premises.", font=16)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in [("red-8-p1-convivencia", lambda: network_overview(steady=False)),
                     ("red-8-p2-estado-estable", lambda: network_overview(steady=True)),
                     ("red-8-p3-subredes", network_subnets),
                     ("red-8-b1-estado-estable-aks", lambda: network_overview(steady=True, aks=True)),
                     ("red-8-b2-subredes-aks", lambda: network_subnets(aks=True)),
                     ("firewall-9-p1-publicacion-portal", portal_publication),
                     ("firewall-9-p2-puntos-de-control", control_points),
                     ("firewall-9-p3-transicion-cali", cali_transition),
                     ("telemetria-13-p1-ingesta-y-alerta", telemetry_ingest_alert),
                     ("telemetria-13-p2-historial-y-tableros", telemetry_history_dashboards)]:
        (out / f"{name}.drawio").write_text(fn().xml(), encoding="utf-8")
        print(out / f"{name}.drawio")


if __name__ == "__main__":
    main()

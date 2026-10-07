#!/usr/bin/env python3
"""Build the draw.io diagram of the logistics platform (issue #12): front, services,
data, security and continuity, in production (East US 2) and the paired region
(Central US).

Reuses the Diagram helper and Azure icon set from
docs/architecture/red/tools/build_drawio_diagrams.py.

Usage:
    python3 build_carga_a_diagram.py --out diagramas

Export to PNG with the draw.io desktop CLI:

    drawio --disable-gpu -x -f png -e -b 20 -s 1.5 -o diagramas/carga-a-plataforma.drawio.png diagramas/carga-a-plataforma.drawio
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
    "defender": AZ + "security/Security_Center.svg",
    "alerts": AZ + "management_governance/Alerts.svg",
    "privacy": AZ + "management_governance/User_Privacy.svg",
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
def logistics_platform():
    d = Diagram()

    d.zone(30, 30, 1010, 820, "Producción · East US 2 (vnet-prod 10.101.0.0/21)", fill="#FAFAFA", stroke="#616161", font=13)
    d.zone(1090, 30, 420, 820, "Continuidad · Central US, región pareja (vnet-prod 10.104.0.0/15)", fill="#ECEFF1", stroke="#455A64", font=13)

    d.zone(60, 80, 460, 210, "Front · Azure Container Apps\nsnet-app-torre y snet-app-portal", fill="#F3E5F5", stroke="#6A1B9A")
    d.zone(60, 310, 460, 190, "Servicios de negocio\n(dentro de los mismos entornos de Container Apps)", fill="#FFFDE7", stroke="#F9A825")
    d.zone(560, 80, 450, 240, "Datos · snet-data y snet-data-pe", fill="#E3F2FD", stroke="#1565C0")
    d.zone(560, 340, 450, 230, "Seguridad · toda la plataforma", fill="#E8F5E9", stroke="#2E7D32")
    d.zone(60, 620, 950, 190, "Clientes y usuarios", fill="#FFFFFF", stroke="#9E9E9E", dashed=True)

    users = d.icon(100, 650, "users_az", "450 usuarios internos\n(despacho, vía Entra ID)", size=56, label_w=150)
    clients = d.icon(300, 650, "users", "~2.000 clientes corporativos\n(portal, por internet)", size=56, label_w=160)

    torre = d.icon(100, 130, "aca", "Consola de despacho (torre)\nContainer Apps, snet-app-torre", size=64, label_w=190)
    portal = d.icon(380, 130, "aca", "Servicios del portal\nContainer Apps, snet-app-portal", size=64, label_w=190)

    d.text(90, 345, 410, 150,
           "Guías · inventario · asignación de muelle y ruta ·\nfacturación corporativa.\n\n"
           "Los cuatro servicios corren en los mismos entornos\nde Container Apps de arriba; aquí se muestran\naparte solo para separarlos del front.",
           font=11)

    mysql = d.icon(610, 130, "mysql", "MySQL Flexible Server\nHA zonal, 2 réplicas, snet-data", size=64, label_w=190)
    redis = d.icon(850, 130, "redis", "Azure Managed Redis\nsnet-data-pe", size=56, label_w=150)

    kv = d.icon(610, 390, "kv", "Key Vault\nsecretos y certificados", size=56, label_w=160)
    entra = d.icon(850, 390, "users_az", "Microsoft Entra ID\nMFA para administradores", size=56, label_w=170)

    mysql_dr = d.icon(1140, 130, "mysql", "Réplica geo-redundante\nRPO 15 min", size=64, label_w=180)
    aca_dr = d.icon(1140, 340, "aca", "Entornos en espera\nfailover manual, RTO 4h", size=64, label_w=180)
    d.text(1125, 480, 360, 300,
           "El failover no es automático: el runbook de continuidad\n"
           "promueve la réplica de Central US a primaria y activa\n"
           "los entornos de Container Apps en espera.\n\n"
           "El RPO de 15 min lo cumple la replicación geo-redundante\n"
           "de MySQL Flexible Server. El RTO de 4h es el tiempo del\n"
           "runbook, no una conmutación automática.\n\n"
           "La caché no se replica: al activar la región de respaldo\n"
           "arranca vacía y se llena con el primer tráfico.",
           font=11)

    d.edge(torre[0], mysql[0], [(164, 162), (270, 162), (270, 230), (610, 230)], "TCP 3306", label_pos=(233, 200, 75))
    d.edge(portal[0], mysql[0], [(444, 162), (520, 162), (520, 190), (610, 190)], "TCP 3306", label_pos=(460, 170, 70))
    d.edge(portal[0], redis[0], [(444, 194), (520, 194), (520, 162), (850, 162)], "TCP 10000", label_pos=(640, 140, 80))
    d.edge(torre[0], entra[0], [(132, 194), (132, 418), (850, 418)], "Autenticación, MFA", color=C_TEMP, label_pos=(300, 400, 110))
    d.edge(portal[0], kv[0], [(412, 194), (412, 418), (610, 418)], "Secretos y certificado", color=C_TEMP, label_pos=(430, 400, 130))
    d.edge(mysql[0], mysql_dr[0], [(674, 130), (674, 60), (1172, 60), (1172, 130)], "Replicación geo-redundante", dashed=True, color=C_FABRIC, label_pos=(760, 42, 220))
    d.edge(clients[0], portal[0], [(356, 650), (412, 650), (412, 194)], "HTTPS, vía Application Gateway (#9)", color=C_OK, label_pos=(430, 540, 220))
    d.edge(users[0], torre[0], [(156, 650), (132, 650), (132, 194)], "Red corporativa, vía Azure Firewall (#9)", color=C_OK, label_pos=(10, 560, 200))

    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "carga-a-plataforma.drawio").write_text(logistics_platform().xml(), encoding="utf-8")
    print("wrote", out / "carga-a-plataforma.drawio")


if __name__ == "__main__":
    main()

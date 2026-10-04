#!/usr/bin/env python3
"""Build the Lucid Standard Import JSON for the #8 network diagrams with Azure 2024 icons.

Usage:
    python3 build_lucid_diagrams.py --variant container-apps --out ../drafts/diagramas/red-8-lucid.json
    python3 build_lucid_diagrams.py --variant aks --out ../drafts/diagramas/red-8-lucid-aks.json

The layout is a hand-placed grid. Every connector is drawn as straight horizontal and vertical segments
(a polyline built from pinned endpoints and waypoints), so crossings happen at right angles and no line runs
through an icon label: lines enter icons from the side or from the top, never through the label under the icon.
A local preflight reports icon collisions before the JSON is sent to Lucid's validator.
"""
import argparse
import csv
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
ICON = 70  # icon size in px; Lucid draws the label under the icon

GREY = "#9AA0A6"
DASH = {"color": "#5F6368", "width": 2, "style": "dashed"}
SOLID = {"color": "#1F3A5F", "width": 2, "style": "solid"}


class Page:
    def __init__(self, pid, title):
        self.id, self.title = pid, title
        self.shapes, self.lines = [], []
        self.bb = {}

    def _add(self, s):
        self.shapes.append(s)
        self.bb[s["id"]] = s["boundingBox"]

    def icon(self, sid, cls, x, y, label, grey=False):
        s = {"id": sid, "type": "namedShape", "className": cls,
             "boundingBox": {"x": x, "y": y, "w": ICON, "h": ICON}, "text": label}
        if grey:
            s["style"] = {"fill": {"type": "color", "color": GREY}}
        self._add(s)

    def vnet(self, sid, cls, x, y, w, h, label, dashed=False):
        s = {"id": sid, "type": "namedContainer", "className": cls,
             "boundingBox": {"x": x, "y": y, "w": w, "h": h}, "text": label}
        if dashed:
            s["style"] = {"stroke": {"color": "#5F6368", "width": 2, "style": "dashed"}}
        self._add(s)

    def box(self, sid, x, y, w, h, title, dashed=False):
        s = {"id": sid, "type": "roundedRectangleContainer", "boundingBox": {"x": x, "y": y, "w": w, "h": h},
             "containerTitle": {"text": title}}
        if dashed:
            s["style"] = {"stroke": {"color": "#5F6368", "width": 2, "style": "dashed"}}
        self._add(s)

    def cloud(self, sid, x, y, w, h, label, dashed=False, size=10):
        s = {"id": sid, "type": "cloud", "boundingBox": {"x": x, "y": y, "w": w, "h": h},
             "text": f'<p style="font-size:{size}pt;text-align:center">{label}</p>',
             "style": {"fill": {"type": "color", "color": "#FFFFFF"},
                       "stroke": DASH if dashed else {"color": "#1F3A5F", "width": 2, "style": "solid"}}}
        self._add(s)

    def text(self, sid, x, y, w, h, html):
        self._add({"id": sid, "type": "text", "boundingBox": {"x": x, "y": y, "w": w, "h": h}, "text": html})

    def table(self, sid, x, y, col_w, row_h, rows, header_fill="#DCE6F2"):
        cells = []
        for yi, row in enumerate(rows):
            for xi, val in enumerate(row):
                c = {"xPosition": xi, "yPosition": yi, "text": val}
                if yi == 0:
                    c["style"] = {"fill": {"type": "color", "color": header_fill}}
                cells.append(c)
        self._add({"id": sid, "type": "table", "rowCount": len(rows), "colCount": len(rows[0]),
                   "boundingBox": {"x": x, "y": y, "w": sum(col_w), "h": row_h * len(rows)}, "cells": cells})

    def at(self, sid, rx, ry):
        """Absolute canvas point at relative position (rx, ry) of a shape."""
        b = self.bb[sid]
        return (b["x"] + rx * b["w"], b["y"] + ry * b["h"])

    def link(self, a, pa, b, pb, via=(), label=None, seg=-1, pos=0.5, side="top", dashed=False, arrow=True):
        """Connector from shape a (relative point pa) to shape b (relative point pb) through absolute waypoints.

        Every segment is straight; waypoints are chosen so each segment is horizontal or vertical. The label goes on
        segment `seg` (index into the list of segments; -1 is the last one).
        """
        pts = [("shape", a, pa)] + [("pos", p) for p in via] + [("shape", b, pb)]
        segs = []
        for k in range(len(pts) - 1):
            ends = []
            for j, pt in enumerate((pts[k], pts[k + 1])):
                last = (k == len(pts) - 2 and j == 1)
                style = "arrow" if (last and arrow) else "none"
                if pt[0] == "shape":
                    ends.append({"type": "shapeEndpoint", "style": style, "shapeId": pt[1],
                                 "position": {"x": pt[2][0], "y": pt[2][1]}})
                else:
                    ends.append({"type": "positionEndpoint", "style": style,
                                 "position": {"x": pt[1][0], "y": pt[1][1]}})
            ln = {"id": f"{self.id}-l{len(self.lines) + 1}", "lineType": "straight",
                  "endpoint1": ends[0], "endpoint2": ends[1]}
            if dashed:
                ln["stroke"] = DASH
            segs.append(ln)
            self.lines.append(ln)
        if label:
            segs[seg]["text"] = [{"text": label, "position": pos, "side": side}]

    def dump(self):
        return {"id": self.id, "title": self.title, "shapes": self.shapes, "lines": self.lines}


L, R, T, B, C = (0, 0.5), (1, 0.5), (0.5, 0), (0.5, 1), (0.5, 0.5)


def lbl(name, detail=None):
    return f"{name}<br>{detail}" if detail else name


def title(p, text, sub):
    p.text(f"{p.id}-title", 0, -170, 2600, 130,
           f'<p style="font-size:14pt;text-align:left"><span style="font-size:18pt"><b>{text}</b></span><br>{sub}</p>')


# Grid of the overview pages (icon top-left corners)
R0, R1, R2, R3 = 500, 760, 1000, 1240           # rows inside Azure
CY = {r: r + ICON / 2 for r in (R0, R1, R2, R3)}  # row centre lines
LNG_X, JOG_X = 1660, 1820                        # local network gateways and the vertical jog into the VPN Gateway
CA, CB = 1980, 2240                              # hub columns
C8, C9, C10, C11, C12, C13 = 2900, 3160, 3420, 3680, 3940, 4200   # prod columns and the PaaS column
UP_X, DOWN_X = 2460, 2500                        # corridors inside the hub, right of the firewall
COPY_Y, COPY_X = 1400, 3620                      # corridor under prod for the archive copy


def overview(p, steady, aks=False):
    """Overview pages: Cali, the 8 centres, the two ISPs, Azure and third parties."""
    i = p.id
    phase = "Estado estable (después del día 90)" if steady else "Convivencia (máximo 90 días)"
    if aks:
        title(p, f"FríoAndes · Alternativa con Kubernetes (AKS) · {phase}",
              "Historia #8 · cambia solo la plataforma de aplicación; la red común es la misma")
    else:
        title(p, f"FríoAndes · Red híbrida · {phase}",
              "Historia #8 · plan de direcciones verificado sin solapamiento con las 23 subredes on-premises")

    # Internet and third parties (top band)
    p.box(f"{i}-ext", 1580, 0, 2760, 300, "Internet y terceros")
    p.icon(f"{i}-camion", "ConnectedVehiclePlatformAzure2024", 1660, 65, lbl("Camiones", "120, 180 en campaña"))
    p.icon(f"{i}-movil", "MobileAzure2024", 1960, 65, lbl("Red móvil", "del operador"))
    p.cloud(f"{i}-inet", 2400, 40, 300, 200, "Internet", size=16)
    p.icon(f"{i}-clientes", "BrowserAzure2024", 2900, 65, lbl("Clientes del portal", "unos 2.000"))
    p.icon(f"{i}-remotos", "UsersAzure2024", 3200, 165, lbl("Equipos remotos", "acceso administrativo"))

    # On-premises
    p.box(f"{i}-onprem", 0, 560, 1250, 1620, "On-premises FríoAndes")
    p.box(f"{i}-cali", 40, 620, 1170, 480,
          "Sede Cali · 10.20.0.0/16" + ("" if steady else " · datacenter en convivencia"))
    p.icon(f"{i}-cali-usr", "UsersAzure2024", 100, R1, lbl("Usuarios y torre", "10.20.0.0/24"))
    if not steady:
        p.icon(f"{i}-cali-app", "ServerFarmAzure2024", 290, R1, lbl("App y front", "10.20.1.0/24"))
        p.icon(f"{i}-cali-db", "ServerFarmAzure2024", 480, R1, lbl("MySQL 5.7 y Redis 5", "10.20.2.0/24"))
        p.icon(f"{i}-cali-arc", "FilesAzure2024", 670, R1, lbl("Archivo NFS 1,2 PB", "10.20.3.0/24"))
        p.icon(f"{i}-cali-pub", "LoadBalancersAzure2024", 860, R1, lbl("Nginx del rastreo", "10.20.5.0/24"))
    p.icon(f"{i}-cali-fw", "FirewallsAzure2024", 1050, R1, lbl("Firewall de Cali", "on-premises"), grey=True)

    p.box(f"{i}-centros", 40, 1200, 1170, 940, "8 centros · 10.31.0.0/16 a 10.38.0.0/16")
    centres = [("bun", "Buenaventura", "10.31"), ("bog", "Bogotá", "10.32"), ("med", "Medellín", "10.33"),
               ("baq", "Barranquilla", "10.34"), ("bga", "Bucaramanga", "10.35"), ("per", "Pereira", "10.36"),
               ("pso", "Pasto", "10.37"), ("nei", "Neiva", "10.38")]
    for k, (cid, name, net) in enumerate(centres):
        p.icon(f"{i}-c-{cid}", "LocalNetworkGatewaysAzure2024", 100 + (k % 4) * 280, 1290 if k < 4 else 1470,
               lbl(name, f"{net}.0.0/16"))
    p.box(f"{i}-ctipo", 80, 1640, 1090, 460, "Centro tipo (igual en los 8)")
    p.icon(f"{i}-ct-usr", "UsersAzure2024", 140, 1720, lbl("Usuarios", "10.3X.0.0/24"))
    p.icon(f"{i}-ct-sen", "IndustrialIoTAzure2024", 140, 1960, lbl("Sensores cuartos fríos", "10.3X.1.0/24"))
    p.icon(f"{i}-ct-edge", "IoTEdgeAzure2024", 520, 1960, lbl("Recolector local", "si existe"))
    p.icon(f"{i}-ct-vpn", "VirtualRouterAzure2024", 940, 1960, lbl("Equipo VPN", "IKEv2 y BGP"))

    # Two internet providers in Cali, aligned with their local network gateways
    p.cloud(f"{i}-isp1", 1330, CY[R1] - 50, 190, 100, "ISP 1 · 400 Mbps")
    p.cloud(f"{i}-isp2", 1330, CY[R2] - 50, 190, 100, "ISP 2 · respaldo<br>otra ruta física", size=9)

    # Azure
    p.vnet(f"{i}-azure", "SubscriptionContainerAzure2024", 1580, 440, 2760, 1260, "Azure · East US 2 · 10.100.0.0/14")
    p.icon(f"{i}-conn", "ConnectionsAzure2024", LNG_X, R0, lbl("10 conexiones sitio a sitio", "Cali cuenta 2"))
    p.icon(f"{i}-lng1", "LocalNetworkGatewaysAzure2024", LNG_X, R1, lbl("Cali por ISP 1", "2 túneles y BGP"))
    p.icon(f"{i}-lng2", "LocalNetworkGatewaysAzure2024", LNG_X, R2, lbl("Cali por ISP 2", "2 túneles, respaldo"))
    p.icon(f"{i}-lngc", "LocalNetworkGatewaysAzure2024", LNG_X, R3, lbl("8 centros", "2 túneles y BGP cada uno"))

    p.vnet(f"{i}-hub", "VirtualNetworkContainerAzure2024", 1880, 660, 680, 720, "vnet-hub · 10.100.0.0/23")
    p.icon(f"{i}-dnsin", "DNSPrivateResolverAzure2024", CA, R1, lbl("DNS Resolver", "entrada"))
    p.icon(f"{i}-bastion", "BastionsAzure2024", CB, R1, lbl("Azure Bastion", "Entra ID y MFA"))
    p.icon(f"{i}-vpngw", "VirtualNetworkGatewaysAzure2024", CA, R2, lbl("VPN Gateway", "VpnGw1AZ activo-activo"))
    p.icon(f"{i}-azfw", "FirewallsAzure2024", CB, R2, lbl("Azure Firewall", "Standard"))
    p.icon(f"{i}-dnsout", "DNSPrivateResolverAzure2024", CA, R3, lbl("DNS Resolver", "salida a Cali"))
    p.icon(f"{i}-fwpol", "AzureFirewallPolicyAzure2024", CB, R3, lbl("Política del firewall", "reglas por zona"))

    p.vnet(f"{i}-prod", "VirtualNetworkContainerAzure2024", 2640, 660, 1300, 800, "vnet-prod · 10.101.0.0/21")
    p.icon(f"{i}-appgw", "ApplicationGatewaysAzure2024", C8, R1, lbl("App Gateway v2 con WAF", "snet-ingress"))
    if aks:
        p.icon(f"{i}-caepor", "KubernetesServicesAzure2024", C9, R1, lbl("Clúster AKS del portal", "snet-app-portal"))
        p.icon(f"{i}-caetor", "KubernetesServicesAzure2024", C8, R2, lbl("Clúster AKS de la torre", "snet-app-torre"))
    else:
        p.icon(f"{i}-caepor", "ContainerAppsEnvironmentsAzure2024", C9, R1, lbl("Apps del portal", "snet-app-portal"))
        p.icon(f"{i}-caetor", "ContainerAppsEnvironmentsAzure2024", C8, R2, lbl("Consola de la torre", "snet-app-torre"))
    p.icon(f"{i}-peing", "PrivateEndpointsAzure2024", C12, R1, lbl("Ingesta privada", "snet-ingest"))
    p.icon(f"{i}-mysql", "AzureDatabaseMySQLServerAzure2024", C10, R2, lbl("MySQL Flexible HA", "snet-data"))
    p.icon(f"{i}-fabgw", "OnPremisesDataGatewaysAzure2024", C11, R2, lbl("Gateway de datos Fabric", "snet-fabric-egress"))
    p.icon(f"{i}-pearc", "PrivateEndpointsAzure2024", C12, R3, lbl("Archivo privado", "snet-archive"))
    if aks:
        p.icon(f"{i}-apisrv", "LoadBalancersAzure2024", C10, R3, lbl("API privada de AKS", "snet-aks-apiserver"))
    if not steady:
        p.icon(f"{i}-dms", "AzureDatabaseMigrationServicesAzure2024", C9, R3,
               lbl("DMS (temporal)", "snet-cali-integration"))
        p.icon(f"{i}-vmcopy", "VirtualMachineAzure2024", C11, R3, lbl("Copia del archivo", "temporal"))
    p.icon(f"{i}-iothub", "IoTHubAzure2024", C13, R1, lbl("IoT Hub", "ingesta de telemetría"))
    p.icon(f"{i}-saarc", "StorageAccountsAzure2024", C13, R3, lbl("Archivo en Blob", "NFS 3.0 privado"))

    p.vnet(f"{i}-test", "VirtualNetworkContainerAzure2024", 1960, 1480, 230, 160, "vnet-test · 10.102.0.0/21")
    p.text(f"{i}-test-t", 1980, 1560, 190, 50, '<p style="font-size:9pt">Mismo módulo de subredes</p>')
    p.vnet(f"{i}-dev", "VirtualNetworkContainerAzure2024", 2230, 1480, 230, 160, "vnet-dev · 10.103.0.0/21")
    p.text(f"{i}-dev-t", 2250, 1560, 190, 50, '<p style="font-size:9pt">Mismo módulo de subredes</p>')

    p.box(f"{i}-fabbox", 4420, CY[R2] - 150, 300, 260, "Microsoft Fabric (SaaS)")
    p.icon(f"{i}-fabric", "PowerBIEmbeddedAzure2024", 4535, R2, lbl("Capacidad F", "IA de la torre"))

    p.cloud(f"{i}-nube2", 1760, 1780, 300, 130, "Segunda nube · 10.110.0.0/15<br>reserva a 24 meses",
            dashed=True, size=9)
    if steady:
        p.vnet(f"{i}-pareja", "SubscriptionContainerAzure2024", 2520, 1780, 520, 160,
               "Central US · 10.104.0.0/15 (reserva)", dashed=True)
    else:
        p.text(f"{i}-vpnold-t", 620, 1110, 560, 80,
               '<p style="font-size:9pt;text-align:left">VPN actual de los centros a Cali (línea punteada):'
               '<br>se retira centro por centro, a más tardar el día 90</p>')
    p.text(f"{i}-leyenda", 3300, 1760, 1000, 200,
           '<p style="font-size:10pt;text-align:left"><b>Leyenda</b><br>Línea continua: tráfico vigente<br>'
           + ('Línea punteada: conexión futura (segunda nube y región pareja)<br>' if steady else
              'Línea punteada: tráfico temporal de la convivencia o conexión futura<br>')
           + 'Líneas sin flecha entre redes virtuales: peering con el hub<br>'
           'Firewall de Cali: equipo on-premises de la sede</p>')

    # Top band
    p.link(f"{i}-camion", R, f"{i}-movil", L, label="Red celular")
    p.link(f"{i}-movil", R, f"{i}-inet", (0, 0.3), label="Operador")
    p.link(f"{i}-clientes", L, f"{i}-inet", (1, 0.3), label="HTTPS")
    p.link(f"{i}-remotos", L, f"{i}-inet", (1, 0.8))
    # From Internet down into Azure: three buses at different heights, entering each target from the top
    bx = p.at(f"{i}-bastion", 0.5, 0)[0]
    p.link(f"{i}-inet", (0.2, 1), f"{i}-bastion", T, via=[(2460, 330), (bx, 330)])
    ax = p.at(f"{i}-appgw", 0.5, 0)[0]
    p.link(f"{i}-inet", (0.5, 1), f"{i}-appgw", T, via=[(2550, 360), (ax, 360)],
           label="HTTPS 443, única entrada pública", pos=0.45, side="middle")
    ix = p.at(f"{i}-iothub", 0.5, 0)[0]
    p.link(f"{i}-inet", (0.8, 1), f"{i}-iothub", T, via=[(2640, 390), (ix, 390)],
           label="Camino 2: camiones (TLS)", pos=0.45, side="middle")

    # Cali: servers on a bus above the row, into the top of the firewall
    srcs = ["cali-usr"] + ([] if steady else ["cali-app", "cali-db", "cali-arc"])
    fw_top = p.at(f"{i}-cali-fw", 0.5, 0)
    bus_y = R1 - 40
    for s in srcs:
        sx = p.at(f"{i}-{s}", 0.5, 0)[0]
        p.lines.append({"id": f"{i}-l{len(p.lines) + 1}", "lineType": "straight",
                        "endpoint1": {"type": "shapeEndpoint", "style": "none", "shapeId": f"{i}-{s}",
                                      "position": {"x": 0.5, "y": 0}},
                        "endpoint2": {"type": "positionEndpoint", "style": "none",
                                      "position": {"x": sx, "y": bus_y}}})
    first_x = p.at(f"{i}-{srcs[0]}", 0.5, 0)[0]
    p.lines.append({"id": f"{i}-l{len(p.lines) + 1}", "lineType": "straight",
                    "endpoint1": {"type": "positionEndpoint", "style": "none", "position": {"x": first_x, "y": bus_y}},
                    "endpoint2": {"type": "positionEndpoint", "style": "none", "position": {"x": fw_top[0], "y": bus_y}}})
    p.lines.append({"id": f"{i}-l{len(p.lines) + 1}", "lineType": "straight",
                    "endpoint1": {"type": "positionEndpoint", "style": "none", "position": {"x": fw_top[0], "y": bus_y}},
                    "endpoint2": {"type": "shapeEndpoint", "style": "arrow", "shapeId": f"{i}-cali-fw",
                                  "position": {"x": 0.5, "y": 0}}})
    if not steady:
        p.link(f"{i}-cali-fw", L, f"{i}-cali-pub", R, label="NAT", dashed=True)
        p.link(f"{i}-centros", (560 / 1170, 0), f"{i}-cali", (560 / 1170, 1), dashed=True)
    p.link(f"{i}-cali-fw", R, f"{i}-isp1", L, label="Salida principal", pos=0.6)
    y2 = p.at(f"{i}-cali-fw", 1, 0.8)[1]
    p.link(f"{i}-cali-fw", (1, 0.8), f"{i}-isp2", L, via=[(1290, y2), (1290, CY[R2])])
    p.link(f"{i}-isp1", R, f"{i}-lng1", L)
    p.link(f"{i}-isp2", R, f"{i}-lng2", L)
    p.link(f"{i}-centros", (1, (CY[R3] - 1200) / 940), f"{i}-lngc", L, label="IPsec directo a Azure")
    # Centre template
    vx = p.at(f"{i}-ct-vpn", 0.5, 0)[0]
    p.link(f"{i}-ct-usr", R, f"{i}-ct-vpn", T, via=[(vx, 1755)])
    p.link(f"{i}-ct-sen", R, f"{i}-ct-edge", L, label="Lecturas cada 30 s")
    p.link(f"{i}-ct-edge", R, f"{i}-ct-vpn", L)

    # Gateways into the VPN Gateway (left side, three entry points)
    for lng, ry in (("lng1", 0.25), ("lngc", 0.75)):
        y_in = p.at(f"{i}-vpngw", 0, ry)[1]
        p.link(f"{i}-{lng}", R, f"{i}-vpngw", (0, ry), via=[(JOG_X, p.at(f"{i}-{lng}", 1, 0.5)[1]), (JOG_X, y_in)])
    p.link(f"{i}-lng2", R, f"{i}-vpngw", L)
    p.link(f"{i}-vpngw", R, f"{i}-azfw", L, label="UDR")

    # Firewall to prod: torre straight, sensors through the upper corridor, DMS through the lower one
    p.link(f"{i}-azfw", R, f"{i}-caetor", L, label="Torre: 443, solo red corporativa", pos=0.6, side="bottom")
    up_y = p.at(f"{i}-azfw", 1, 0.2)[1]
    px = p.at(f"{i}-peing", 0.5, 0)[0]
    p.link(f"{i}-azfw", (1, 0.2), f"{i}-peing", T, via=[(UP_X, up_y), (UP_X, R1 - 40), (px, R1 - 40)],
           label="Camino 1: sensores por la VPN y el firewall", seg=2, pos=0.6)
    if not steady:
        dn_y = p.at(f"{i}-azfw", 1, 0.8)[1]
        p.link(f"{i}-azfw", (1, 0.8), f"{i}-dms", L, via=[(DOWN_X, dn_y), (DOWN_X, CY[R3])], dashed=True)
        dx = p.at(f"{i}-dms", 0.5, 0)[0]
        my = p.at(f"{i}-mysql", 0, 0.8)[1]
        p.link(f"{i}-dms", T, f"{i}-mysql", (0, 0.8), via=[(dx, my)], label="Carga en línea", seg=0,
               side="middle", dashed=True)
        cy0 = p.at(f"{i}-vpngw", 1, 0.85)[1]
        p.link(f"{i}-vpngw", (1, 0.85), f"{i}-vmcopy", L,
               via=[(2145, cy0), (2145, COPY_Y), (COPY_X, COPY_Y), (COPY_X, CY[R3])],
               label="Copia del archivo, unos 37 Mbps, fuera del firewall", seg=2, pos=0.5, dashed=True)
        p.link(f"{i}-vmcopy", R, f"{i}-pearc", L, dashed=True)

    # Prod
    p.link(f"{i}-appgw", R, f"{i}-caepor", L, label="HTTPS")
    p.link(f"{i}-caetor", R, f"{i}-mysql", L, label="MySQL 3306", pos=0.3)
    mx = p.at(f"{i}-mysql", 0.5, 0)[0]
    p.link(f"{i}-caepor", R, f"{i}-mysql", T, via=[(mx, CY[R1])], label="Lectura 3306", seg=1, side="middle")
    p.link(f"{i}-fabgw", L, f"{i}-mysql", R, label="Lectura 3306")
    p.link(f"{i}-fabgw", (1, 0.35), f"{i}-fabric", (0, 0.35), label="Salida a Fabric", pos=0.6)
    ax2 = p.at(f"{i}-pearc", 0.5, 0)[0]
    p.link(f"{i}-fabgw", (1, 0.75), f"{i}-pearc", T, via=[(ax2, p.at(f"{i}-fabgw", 1, 0.75)[1])],
           label="Lectura 443", seg=1, side="middle")
    p.link(f"{i}-pearc", R, f"{i}-saarc", L, label="Private Link")
    p.link(f"{i}-peing", R, f"{i}-iothub", L, label="Private Link")

    # Peering and future connections
    p.link(f"{i}-hub", (1, (1155 - 660) / 720), f"{i}-prod", (0, (1155 - 660) / 800), arrow=False)
    p.link(f"{i}-hub", ((2075 - 1880) / 680, 1), f"{i}-test", T, arrow=False)
    p.link(f"{i}-hub", ((2345 - 1880) / 680, 1), f"{i}-dev", T, arrow=False)
    p.link(f"{i}-nube2", T, f"{i}-hub", ((1910 - 1880) / 680, 1), label="Futuro: VPN o ExpressRoute", pos=0.12,
           side="middle", dashed=True)
    if steady:
        hy = p.at(f"{i}-hub", 1, 0.97)[1]
        p.link(f"{i}-hub", (1, 0.97), f"{i}-pareja", ((2600 - 2520) / 520, 0), via=[(2600, hy)],
               label="Futuro: peering global o VPN", seg=1, pos=0.85, side="middle", dashed=True)


def detail(p, plan_file="ip-plan.csv", aks=False):
    """Detail page: hub and prod with every subnet as a container, CIDR and icons; tables for test, dev and reserves."""
    if aks:
        title(p, "FríoAndes · Alternativa con Kubernetes (AKS) · Hub y prod: subredes, CIDR y servicios",
              "Historia #8 · test y dev repiten el mismo módulo · plan de direcciones verificado sin solapamiento")
    else:
        title(p, "FríoAndes · Hub y prod: subredes, CIDR y servicios",
              "Historia #8 · test y dev repiten el mismo módulo · plan de direcciones verificado sin solapamiento")
    plan = list(csv.DictReader(open(DATA / plan_file, encoding="utf-8")))
    cidr = {(r["vnet"], r["subnet"]): r["cidr"] for r in plan}

    p.vnet("p3-hub", "VirtualNetworkContainerAzure2024", 0, 0, 900, 1130, "vnet-hub · 10.100.0.0/23")
    hub_subnets = [
        ("GatewaySubnet", [("p3-vpngw", "VirtualNetworkGatewaysAzure2024", lbl("VPN Gateway", "VpnGw1AZ"))]),
        ("AzureFirewallSubnet", [("p3-azfw", "FirewallsAzure2024", lbl("Azure Firewall", "Standard"))]),
        ("AzureFirewallManagementSubnet", [("p3-fwmip", "PublicIPAddressesAzure2024", lbl("IP de gestión", "del firewall"))]),
        ("AzureBastionSubnet", [("p3-bastion", "BastionsAzure2024", lbl("Azure Bastion", "Entra ID y MFA"))]),
        ("snet-dns-inbound", [("p3-dnsin", "DNSPrivateResolverAzure2024", lbl("DNS Resolver", "entrada"))]),
        ("snet-dns-outbound", [("p3-dnsout", "DNSPrivateResolverAzure2024", lbl("DNS Resolver", "salida"))]),
    ]
    for k, (name, icons) in enumerate(hub_subnets):
        x, y = 40 + (k % 2) * 440, 80 + (k // 2) * 300
        short = "Gestión del firewall" if name == "AzureFirewallManagementSubnet" else name
        p.vnet(f"p3-sh{k}", "SubnetContainerAzure2024", x, y, 400, 240, f"{short} · {cidr[('vnet-hub', name)]}")
        for sid, cls, label in icons:
            p.icon(sid, cls, x + 165, y + 80, label)
    p.icon("p3-rt", "RouteTablesAzure2024", 80, 1000, lbl("Rutas al firewall", "UDR"))

    cols = 5
    prod_w = 40 + cols * 465
    prod_h = 1090 if aks else 760
    p.vnet("p3-prod", "VirtualNetworkContainerAzure2024", 1000, 0, prod_w, prod_h, "vnet-prod · 10.101.0.0/21")
    prod_subnets = [
        ("snet-ingress", [("p3-waf", "WebApplicationFirewallPoliciesWAFAzure2024", lbl("Política WAF", "OWASP y límite")),
                          ("p3-pip", "PublicIPAddressesAzure2024", lbl("IP pública", "del portal")),
                          ("p3-appgw", "ApplicationGatewaysAzure2024", lbl("App Gateway v2", "hasta 10 instancias"))]),
        ("snet-app-portal", [("p3-caepor", "ContainerAppsEnvironmentsAzure2024", lbl("Container Apps", "portal"))]),
        ("snet-app-torre", [("p3-caetor", "ContainerAppsEnvironmentsAzure2024", lbl("Container Apps", "torre (interno)"))]),
        ("snet-data", [("p3-mysql", "AzureDatabaseMySQLServerAzure2024", lbl("MySQL Flexible", "HA entre zonas"))]),
        ("snet-data-pe", [("p3-pedat", "PrivateEndpointsAzure2024", lbl("Endpoints privados", "Redis y Key Vault"))]),
        ("snet-archive", [("p3-pearc", "PrivateEndpointsAzure2024", lbl("Endpoints privados", "Blob y DFS"))]),
        ("snet-ingest", [("p3-peing", "PrivateEndpointsAzure2024", lbl("Endpoint privado", "IoT Hub"))]),
        ("snet-admin", [("p3-vmadm", "VirtualMachineAzure2024", lbl("Agentes", "despliegue y operación"))]),
        ("snet-cali-integration", [("p3-dms", "AzureDatabaseMigrationServicesAzure2024", lbl("DMS", "temporal")),
                                   ("p3-vmcopy", "VirtualMachineAzure2024", lbl("Copia del archivo", "temporal"))]),
        ("snet-fabric-egress", [("p3-fabgw", "OnPremisesDataGatewaysAzure2024", lbl("Gateway de datos", "Fabric"))]),
    ]
    if aks:
        prod_subnets[1] = ("snet-app-portal", [("p3-caepor", "KubernetesServicesAzure2024", lbl("Nodos AKS", "clúster del portal"))])
        prod_subnets[2] = ("snet-app-torre", [("p3-caetor", "KubernetesServicesAzure2024", lbl("Nodos AKS", "clúster de la torre"))])
        x, y = 1040 + 2 * 465, 80 + 2 * 330
        p.vnet("p3-sp-api", "SubnetContainerAzure2024", x, y, 425, 270,
               f"snet-aks-apiserver · {cidr[('vnet-prod', 'snet-aks-apiserver')]}")
        p.icon("p3-apisrv", "LoadBalancersAzure2024", x + 177, y + 90, lbl("API privada", "de los clústeres"))
    for k, (name, icons) in enumerate(prod_subnets):
        x, y = 1040 + (k % cols) * 465, 80 + (k // cols) * 330
        p.vnet(f"p3-sp{k}", "SubnetContainerAzure2024", x, y, 425, 270, f"{name} · {cidr[('vnet-prod', name)]}")
        n = len(icons)
        for j, (sid, cls, label) in enumerate(icons):
            ix = x + (425 - (n * ICON + (n - 1) * 70)) // 2 + j * (ICON + 70)
            p.icon(sid, cls, ix, y + 90, label)

    # PaaS reached through private endpoints: Redis and Key Vault right of prod, archive and IoT Hub below
    side_x = 1000 + prod_w + 100
    p.icon("p3-redis", "AzureManagedRedisAzure2024", side_x, 170, lbl("Azure Managed Redis", "caché del rastreo"))
    p.icon("p3-kv", "KeyVaultsAzure2024", side_x, 500, lbl("Key Vault", "secretos y llaves"))
    low_y = prod_h + 120
    p.icon("p3-saarc", "StorageAccountsAzure2024", 1150, low_y, lbl("Cuentas del archivo", "Blob NFS 3.0"))
    p.icon("p3-iothub", "IoTHubAzure2024", 1615, low_y, lbl("IoT Hub", "ingesta"))

    p.link("p3-pip", R, "p3-appgw", L)
    p.link("p3-appgw", R, "p3-caepor", L, label="HTTPS")
    p.link("p3-caetor", R, "p3-mysql", L, label="3306")
    p.link("p3-pedat", R, "p3-redis", L, label="Private Link", pos=0.35)
    # Key Vault: a branch of the same Private Link line, going down from the gap right of prod
    gap_x = 1000 + prod_w + 40
    ry, ky = p.at("p3-pedat", 1, 0.5)[1], p.at("p3-kv", 0, 0.5)[1]
    p.lines.append({"id": f"{p.id}-l{len(p.lines) + 1}", "lineType": "straight",
                    "endpoint1": {"type": "positionEndpoint", "style": "none", "position": {"x": gap_x, "y": ry}},
                    "endpoint2": {"type": "positionEndpoint", "style": "none", "position": {"x": gap_x, "y": ky}}})
    p.lines.append({"id": f"{p.id}-l{len(p.lines) + 1}", "lineType": "straight",
                    "endpoint1": {"type": "positionEndpoint", "style": "none", "position": {"x": gap_x, "y": ky}},
                    "endpoint2": {"type": "shapeEndpoint", "style": "arrow", "shapeId": "p3-kv",
                                  "position": {"x": 0, "y": 0.5}}})
    for pe, target, x_side in (("p3-pearc", "p3-saarc", 1065), ("p3-peing", "p3-iothub", 1530)):
        ty = p.at(target, 0, 0.5)[1]
        p.link(pe, L, target, L, via=[(x_side, p.at(pe, 0, 0.5)[1]), (x_side, ty)],
               label="Private Link", seg=1, pos=0.75, side="middle")
    p.link("p3-vpngw", R, "p3-azfw", L, label="UDR")
    p.link("p3-hub", (1, 720 / 1130), "p3-prod", (0, 720 / prod_h), arrow=False)

    # Tables: test and dev use the same module; reserves
    rows = [["Subred", "prod", "test", "dev"]]
    for name, _ in prod_subnets:
        rows.append([name, cidr[("vnet-prod", name)], cidr[("vnet-test", name)], cidr[("vnet-dev", name)]])
    rows.insert(1, ["Red virtual", "10.101.0.0/21", "10.102.0.0/21", "10.103.0.0/21"])
    if aks:
        rows.append(["snet-aks-apiserver"] + [cidr[(v, "snet-aks-apiserver")] for v in ("vnet-prod", "vnet-test", "vnet-dev")])
    table_y = low_y + 220
    p.table("p3-module", 2000, table_y, [230, 150, 150, 150], 34, rows)
    reserves = [["Reserva", "Rango"]] + [[r["vnet"], r["cidr"]] for r in plan if r["env"] == "reserva"]
    reserves.append(["on-premises (crecimiento)", "10.20 y 10.31 a 10.38 (cada uno /16)"])
    p.table("p3-reserves", 1000, table_y, [260, 420], 34, reserves)
    p.text("p3-note", 0, 1200, 900, 160,
           '<p style="font-size:10pt;text-align:left"><b>Cómo leer esta página</b><br>Cada recuadro es una subred con su CIDR. '
           'test y dev repiten el mismo módulo (tabla). El verificador comprueba que ningún rango choca con las '
           '23 subredes on-premises.</p>')


def rename(page, old, new):
    """Give a reused page builder its own id prefix (ids must be unique across the document)."""
    for sh in page.shapes:
        sh["id"] = sh["id"].replace(old, new, 1)
    for ln in page.lines:
        ln["id"] = ln["id"].replace(old, new, 1)
        for ep in ("endpoint1", "endpoint2"):
            if "shapeId" in ln[ep]:
                ln[ep]["shapeId"] = ln[ep]["shapeId"].replace(old, new, 1)


def preflight(pages):
    problems = []
    for pg in pages:
        boxes = [(s["id"], s["boundingBox"]) for s in pg.shapes
                 if s["type"] in ("namedShape", "cloud", "text", "table")]
        for i, (a, ba) in enumerate(boxes):
            for b, bb in boxes[i + 1:]:
                sep_x = ba["x"] + ba["w"] + 40 <= bb["x"] or bb["x"] + bb["w"] + 40 <= ba["x"]
                sep_y = ba["y"] + ba["h"] + 40 <= bb["y"] or bb["y"] + bb["h"] + 40 <= ba["y"]
                if not (sep_x or sep_y):
                    problems.append(f"{pg.id}: {a} choca con {b}")
        ids = {s["id"] for s in pg.shapes}
        for ln in pg.lines:
            for ep in ("endpoint1", "endpoint2"):
                if "shapeId" in ln[ep] and ln[ep]["shapeId"] not in ids:
                    problems.append(f"{pg.id}: línea {ln['id']} apunta a {ln[ep]['shapeId']}, que no existe")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--variant", choices=("container-apps", "aks"), default="container-apps")
    args = ap.parse_args()
    if args.variant == "aks":
        p4, p5 = Page("p4", "B1 · Estado estable con AKS"), Page("p5", "B2 · Subredes hub y prod con AKS")
        overview(p4, steady=True, aks=True)
        detail(p5, plan_file="ip-plan-aks.csv", aks=True)
        rename(p5, "p3-", "p5-")
        pages = [p4, p5]
    else:
        p1, p2, p3 = Page("p1", "1 · Convivencia"), Page("p2", "2 · Estado estable"), Page("p3", "3 · Subredes hub y prod")
        overview(p1, steady=False)
        overview(p2, steady=True)
        detail(p3)
        pages = [p1, p2, p3]
    for msg in preflight(pages):
        print("PREFLIGHT:", msg)
    doc = {"version": 1, "pages": [pg.dump() for pg in pages]}

    def dumps(o):
        return json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    parts = []
    for pg in doc["pages"]:
        shapes = ",\n".join(dumps(s) for s in pg["shapes"])
        lines = ",\n".join(dumps(ln) for ln in pg["lines"])
        parts.append(f'{{"id":{dumps(pg["id"])},"title":{dumps(pg["title"])},"shapes":[\n{shapes}],"lines":[\n{lines}]}}')
    text = '{"version":1,"pages":[\n' + ",\n".join(parts) + "]}"
    json.loads(text)
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"{args.out}: {len(text)} bytes · " + " · ".join(f"{pg.id}: {len(pg.shapes)} figuras, {len(pg.lines)} líneas"
                                                          for pg in pages))


if __name__ == "__main__":
    main()

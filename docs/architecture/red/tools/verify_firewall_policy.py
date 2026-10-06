#!/usr/bin/env python3
"""Verify the FríoAndes cloud firewall policy table against the IP plan and the design rules.

Usage:
    python3 verify_firewall_policy.py [--policy ../data/firewall-policy.csv] [--out ../verification/reporte-firewall-policy.md]

Inputs (all in ../data): firewall-policy.csv, firewall-settings.csv, ip-plan.csv, onprem-inventory.csv.
Exit code 0 when every check passes, 1 otherwise. The report is written in Spanish because it goes
into the client deliverable.
"""
import argparse
import csv
import hashlib
import ipaddress
import sys
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
CLOUD_ENVS = ("prod", "test", "dev")
VIGENCIAS = ("estable", "temporal")
REQUIRED_FLOWS = ("torre", "portal", "sensores", "flota", "integracion-cali", "administracion",
                  "salida-internet", "dns", "copia-archivo", "datos", "archivo")
TEMPORAL_GROUPS = ("400 transito-convivencia", "500 migracion")
ALLOW = ("Permitir",)
TORRE_CLOUD_SOURCE = "snet-telemetry-func"


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tokens(field):
    return field.split()


def cidrs(field):
    out = []
    for t in tokens(field):
        try:
            out.append(ipaddress.ip_network(t))
        except ValueError:
            pass
    return out


def is_symbolic(t):
    return (t in ("any", "internet") or t.startswith("tag:") or t.startswith("fqdn:")
            or (t.startswith("<") and t.endswith(">")))


def verify(policy_path, settings_path, plan_path, onprem_path):
    policy = load_csv(policy_path)
    settings = {r["clave"]: r["valor"] for r in load_csv(settings_path)}
    plan = load_csv(plan_path)
    onprem = load_csv(onprem_path)

    subnets = []  # (network, env, subnet name, service)
    vnets = {}  # network -> (env, vnet name)
    for r in plan:
        if r["env"] == "reserva":
            continue
        subnets.append((ipaddress.ip_network(r["cidr"]), r["env"], r["subnet"], r["service"]))
        vnets[ipaddress.ip_network(r["vnet_cidr"])] = (r["env"], r["vnet"])
    onprem_nets = [ipaddress.ip_network(r["cidr"]) for r in onprem]
    sensors = [ipaddress.ip_network(r["cidr"]) for r in onprem if "Sensores" in r["use"]]

    def owner(net):
        for sn, env, name, service in subnets:
            if net.subnet_of(sn):
                return env, name, service
        for vn, (env, name) in vnets.items():
            if net.subnet_of(vn):
                return env, name, "vnet"
        return None

    checks = []

    def check(name, problems):
        checks.append((name, problems))

    # 1. Campos y vigencia
    probs = []
    for r in policy:
        for k in ("id", "flujo", "punto_control", "grupo", "origen_rangos", "destino_rangos", "puertos", "accion", "vigencia"):
            if not r[k].strip():
                probs.append(f"{r['id'] or '(sin id)'}: falta `{k}`")
        if r["vigencia"] not in VIGENCIAS:
            probs.append(f"{r['id']}: vigencia `{r['vigencia']}` no válida")
        if r["vigencia"] == "temporal" and not r["se_retira"].strip():
            probs.append(f"{r['id']}: regla temporal sin momento de retiro")
        if r["vigencia"] == "estable" and r["se_retira"].strip():
            probs.append(f"{r['id']}: regla estable con momento de retiro")
    check("Cada regla tiene sus campos, una vigencia válida y, si es temporal, cuándo se retira", probs)

    # 2. Identificadores únicos
    dup = [k for k, v in Counter(r["id"] for r in policy).items() if v > 1]
    check("Identificadores únicos", [f"`{d}` repetido" for d in dup])

    # 3. Rangos conocidos
    probs = []
    for r in policy:
        for side in ("origen_rangos", "destino_rangos"):
            for t in tokens(r[side]):
                if is_symbolic(t):
                    continue
                try:
                    net = ipaddress.ip_network(t)
                except ValueError:
                    probs.append(f"{r['id']}: `{t}` no es un rango ni un símbolo conocido")
                    continue
                if not owner(net) and not any(net.subnet_of(o) for o in onprem_nets):
                    probs.append(f"{r['id']}: `{t}` no pertenece al plan de direcciones ni al inventario on-premises")
    check("Todos los rangos existen en `ip-plan.csv` o en el inventario on-premises", probs)

    allow_rows = [r for r in policy if r["accion"] in ALLOW]

    # 4. Torre fuera de internet. La única fuente de la nube admitida es la función de alertas
    # de su mismo ambiente, que entrega las alertas a la consola.
    probs = []
    for r in allow_rows:
        for d in cidrs(r["destino_rangos"]):
            o = owner(d)
            if not o or o[1] != "snet-app-torre":
                continue
            if any(t in ("internet", "any") for t in tokens(r["origen_rangos"])):
                probs.append(f"{r['id']}: permite internet hacia la torre")
            for s in cidrs(r["origen_rangos"]):
                so = owner(s)
                if so and not (so[1] == TORRE_CLOUD_SOURCE and so[0] == o[0]):
                    probs.append(f"{r['id']}: `{s}` de la nube llega a la torre")
    check("La torre solo recibe tráfico de las redes corporativas y de la función de alertas de su ambiente", probs)

    # 5. Sin cruce de ambientes
    probs = []
    for r in allow_rows:
        src_envs = {owner(s)[0] for s in cidrs(r["origen_rangos"]) if owner(s)} & set(CLOUD_ENVS)
        dst_envs = {owner(d)[0] for d in cidrs(r["destino_rangos"]) if owner(d)} & set(CLOUD_ENVS)
        # Un servicio compartido del hub (por ejemplo el DNS) puede atender a los tres ambientes.
        if src_envs and dst_envs and (src_envs != dst_envs or len(src_envs) > 1):
            probs.append(f"{r['id']}: conecta {sorted(src_envs)} con {sorted(dst_envs)}")
    check("Ninguna regla conecta producción, pruebas y desarrollo entre sí", probs)

    # 6. Sensores reales solo a producción
    probs = []
    for r in allow_rows:
        if any(s.subnet_of(x) for s in cidrs(r["origen_rangos"]) for x in sensors):
            for d in cidrs(r["destino_rangos"]):
                o = owner(d)
                if o and o[0] in ("test", "dev"):
                    probs.append(f"{r['id']}: sensores reales hacia {o[0]}")
    check("Los sensores reales solo llegan a producción (pruebas y desarrollo usan datos simulados)", probs)

    # 7. Analítica sin salida a internet
    probs = []
    for r in allow_rows:
        if any(owner(s) and owner(s)[1] == "snet-fabric-egress" for s in cidrs(r["origen_rangos"])):
            if any(t == "internet" or t.startswith(("fqdn:", "tag:")) for t in tokens(r["destino_rangos"])):
                probs.append(f"{r['id']}: el gateway de Fabric sale a internet")
    check("El gateway de Fabric no tiene salida a internet", probs)

    # 8. Cobertura de flujos
    present = {r["flujo"] for r in policy}
    check("Están todos los flujos del diseño", [f"falta el flujo `{f}`" for f in REQUIRED_FLOWS if f not in present])

    # 9. Reglas de cierre
    probs = []
    if not any(r["punto_control"] == "azure-firewall" and r["accion"] == "Denegar" and r["origen_rangos"] == "any" for r in policy):
        probs.append("falta la regla implícita de denegación del firewall")
    for env in CLOUD_ENVS:
        if not any(r["punto_control"] == "nsg" and r["ambiente"] == env and r["accion"] == "Denegar" for r in policy):
            probs.append(f"falta la denegación final de los NSG en {env}")
    check("El firewall y los NSG terminan en denegar", probs)

    # 10. Temporales agrupadas
    probs = []
    for r in policy:
        if r["punto_control"] != "azure-firewall":
            continue
        if r["grupo"] in TEMPORAL_GROUPS and r["vigencia"] != "temporal":
            probs.append(f"{r['id']}: regla estable dentro de un grupo temporal")
        if r["vigencia"] == "temporal" and r["grupo"] not in TEMPORAL_GROUPS:
            probs.append(f"{r['id']}: regla temporal fuera de los grupos temporales")
    check("Las reglas temporales del firewall están en grupos que se borran completos", probs)

    # 11. SNAT hacia endpoints privados
    probs = []
    no_snat = [ipaddress.ip_network(t) for t in settings["snat_private_ranges"].split()]
    for r in allow_rows:
        if r["punto_control"] != "azure-firewall" or r["tipo"] != "red":
            continue
        for d in cidrs(r["destino_rangos"]):
            o = owner(d)
            if o and o[2] == "private-endpoints" and any(d.subnet_of(n) or d.overlaps(n) for n in no_snat):
                probs.append(f"{r['id']}: va a endpoints privados ({o[1]}) sin traducir el origen")
    for d_sub, env, name, service in subnets:
        if service == "private-endpoints" and any(d_sub.overlaps(n) for n in no_snat):
            probs.append(f"`{d_sub}` ({env} {name}) está en la lista sin traducción")
    check("El firewall traduce el origen hacia los endpoints privados (la respuesta vuelve por el mismo camino)", probs)

    # 12. Proxy DNS
    probs = []
    if settings.get("dns_proxy", "").lower().startswith("desactivado"):
        for r in policy:
            if r["punto_control"] == "azure-firewall" and r["tipo"] == "red" and "fqdn:" in r["destino_rangos"]:
                probs.append(f"{r['id']}: regla de red con nombres de dominio y proxy DNS desactivado")
    check("Las reglas de red no usan nombres de dominio sin proxy DNS", probs)

    return policy, checks


def render(policy, checks, policy_path):
    digest = hashlib.sha256(Path(policy_path).read_bytes()).hexdigest()
    ok = all(not p for _, p in checks)
    by_point = Counter(r["punto_control"] for r in policy)
    by_vig = Counter(r["vigencia"] for r in policy)
    lines = [
        "# Verificación de la tabla de políticas del firewall de nube",
        "",
        f"Resultado: **{'aprobada' if ok else 'con problemas'}** ({sum(1 for _, p in checks if not p)} de {len(checks)} comprobaciones).",
        "",
        f"- Archivo: `{Path(policy_path).name}`, {len(policy)} reglas.",
        f"- SHA-256: `{digest}`",
        "- Por punto de control: " + ", ".join(f"{k} {v}" for k, v in sorted(by_point.items())) + ".",
        "- Por vigencia: " + ", ".join(f"{k} {v}" for k, v in sorted(by_vig.items())) + ".",
        "",
        "| Comprobación | Resultado |",
        "|---|---|",
    ]
    for name, probs in checks:
        lines.append(f"| {name} | {'Cumple' if not probs else 'No cumple: ' + '; '.join(probs)} |")
    lines += ["", "## Reglas temporales y cuándo se retiran", "", "| Regla | Punto de control | Origen | Destino | Se retira |", "|---|---|---|---|---|"]
    for r in policy:
        if r["vigencia"] == "temporal":
            lines.append(f"| {r['id']} | {r['punto_control']} | {r['origen']} | {r['destino']} | {r['se_retira']} |")
    return "\n".join(lines) + "\n", ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(DATA / "firewall-policy.csv"))
    ap.add_argument("--settings", default=str(DATA / "firewall-settings.csv"))
    ap.add_argument("--plan", default=str(DATA / "ip-plan.csv"))
    ap.add_argument("--onprem", default=str(DATA / "onprem-inventory.csv"))
    ap.add_argument("--out")
    args = ap.parse_args()
    policy, checks = verify(args.policy, args.settings, args.plan, args.onprem)
    text, ok = render(policy, checks, args.policy)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

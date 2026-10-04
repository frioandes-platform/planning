#!/usr/bin/env python3
"""Verify a FríoAndes cloud IP plan against the on-premises inventory and the acceptance criteria of issue #8.

Usage:
    python3 verify_ip_plan.py --plan ../data/ip-plan.csv [--out ../verification/reporte-ip-plan.md]

Exit code 0 when every check passes, 1 otherwise. The report is written in Spanish because it goes
straight into the #8 deliverable.
"""
import argparse
import csv
import hashlib
import ipaddress
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
ENVS = ("prod", "test", "dev")
CATEGORIES = ("ingreso", "aplicacion", "datos", "archivo", "ingesta", "administracion",
              "integracion-cali", "salida-fabric")
ZONES = ("torre", "portal", "ingesta", "analitica")
EXPECTED_ONPREM = 23

# Which internet exposure each kind of subnet may have (criterion 7).
INTERNET_RULES = {
    "entrada-portal": lambda r: r["category"] == "ingreso" and r["zone"] == "portal",
    "entrada-admin": lambda r: r["service"] == "bastion",
    "tunel-vpn": lambda r: r["service"] == "vpn-gateway",
    "salida": lambda r: r["service"] == "firewall",
    "ninguno": lambda r: True,
}


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def prefix(size):
    return int(size.lstrip("/")) if size else None


class Report:
    def __init__(self):
        self.checks = []  # (name, criterion, ok, details)

    def add(self, name, criterion, problems, blocking=True):
        self.checks.append((name, criterion, not problems or not blocking, problems))

    @property
    def ok(self):
        return all(c[2] for c in self.checks)


def verify(plan_path, onprem_path, constraints_path):
    rep = Report()
    onprem = load_csv(onprem_path)
    plan = load_csv(plan_path)
    constraints = load_csv(constraints_path)

    rep.add("El inventario on-premises tiene las 23 subredes del enunciado", "3",
            [] if len(onprem) == EXPECTED_ONPREM else [f"El inventario tiene {len(onprem)} filas, no {EXPECTED_ONPREM}"])

    bad = []
    for r in onprem + plan:
        for key in ("cidr", "vnet_cidr"):
            if key in r and r[key]:
                try:
                    r[key + "_net"] = ipaddress.ip_network(r[key], strict=True)
                except ValueError as e:
                    bad.append(f"`{r.get('subnet', r.get('use'))}` {key}={r[key]}: {e}")
    rep.add("Todos los CIDR son válidos", "2", bad)
    if bad:
        return rep, onprem, plan, {}

    onprem_nets = [(r["site"], r["use"], r["cidr_net"]) for r in onprem]
    reserved_onprem = sorted({ipaddress.ip_network(f"{n.network_address}/16", strict=False) for _, _, n in onprem_nets})
    subnets = [r for r in plan if r["category"] != "reserva"]
    reserves = [r for r in plan if r["category"] == "reserva"]

    # Criterion 3: every cloud range against each of the 23 on-prem subnets.
    per_range = {}
    problems = []
    for r in plan:
        for key in ("vnet_cidr_net", "cidr_net"):
            net = r[key]
            hits = [f"{site} {n} ({use})" for site, use, n in onprem_nets if net.overlaps(n)]
            per_range[str(net)] = hits
            if hits:
                problems.append(f"`{net}` ({r['subnet']}) se solapa con: " + "; ".join(hits))
    rep.add("Ningún rango de nube se solapa con las 23 subredes on-premises", "3", sorted(set(problems)))

    problems = sorted({f"`{r['cidr']}` ({r['subnet']}) invade la reserva de crecimiento {res}"
                       for r in plan for res in reserved_onprem if r["cidr_net"].overlaps(res)})
    rep.add("La nube respeta la reserva de crecimiento on-premises (los /16 completos de Cali y los centros)", "11", problems)

    vnets = {}
    for r in plan:
        vnets.setdefault(r["vnet"], r["vnet_cidr_net"])
    names = sorted(vnets)
    problems = [f"`{a}` {vnets[a]} se solapa con `{b}` {vnets[b]}"
                for i, a in enumerate(names) for b in names[i + 1:] if vnets[a].overlaps(vnets[b])]
    rep.add("Las redes virtuales de la nube no se solapan entre sí (dev, test y prod en rangos distintos)", "2", problems)

    problems = [f"`{r['subnet']}` {r['cidr']} no está dentro de `{r['vnet']}` {r['vnet_cidr']}"
                for r in subnets if not r["cidr_net"].subnet_of(r["vnet_cidr_net"])]
    rep.add("Cada subred está dentro de su red virtual", "2", problems)

    problems = []
    for i, a in enumerate(subnets):
        for b in subnets[i + 1:]:
            if a["cidr_net"].overlaps(b["cidr_net"]):
                problems.append(f"`{a['vnet']}/{a['subnet']}` {a['cidr']} se solapa con `{b['vnet']}/{b['subnet']}` {b['cidr']}")
    rep.add("Las subredes de la nube no se solapan entre sí", "2", problems)

    by_env = defaultdict(list)
    for r in subnets:
        by_env[r["env"]].append(r)
    problems = []
    for env in ENVS:
        missing = [c for c in CATEGORIES if c not in {r["category"] for r in by_env[env]}]
        if missing:
            problems.append(f"`{env}` no tiene: {', '.join(missing)}")
    rep.add("Cada ambiente (prod, test, dev) tiene las 8 categorías mínimas", "2", problems)

    problems = []
    if not reserves:
        problems.append("No hay ningún bloque con categoría `reserva` para la segunda nube")
    for res in reserves:
        clash = [f"`{r['subnet']}` {r['cidr']}" for r in subnets if r["cidr_net"].overlaps(res["cidr_net"])]
        if clash:
            problems.append(f"La reserva {res['cidr']} se solapa con " + ", ".join(clash))
    rep.add("Hay un bloque reservado para la segunda nube, libre de solapes", "11", problems)

    problems = []
    for env in ENVS:
        zones = {r["zone"] for r in by_env[env]}
        missing = [z for z in ZONES if z not in zones]
        if missing:
            problems.append(f"`{env}` no tiene subred propia para la zona: {', '.join(missing)}")
    rep.add("Torre, portal, ingesta y analítica tienen subredes propias en cada ambiente", "6", problems)

    problems = []
    for r in subnets:
        rule = INTERNET_RULES.get(r["internet"])
        if rule is None:
            problems.append(f"`{r['subnet']}`: valor de internet desconocido `{r['internet']}`")
        elif not rule(r):
            problems.append(f"`{r['vnet']}/{r['subnet']}` tiene `{r['internet']}`, que no le corresponde")
        if r["zone"] == "torre" and r["internet"] != "ninguno":
            problems.append(f"`{r['vnet']}/{r['subnet']}` es de la torre y tiene exposición `{r['internet']}`")
    rep.add("Despacho fuera de internet: la única entrada pública de aplicación es el ingreso del portal", "7", problems)

    errors, warnings = [], []
    for c in constraints:
        for r in [r for r in subnets if r["service"] == c["service"]]:
            plen = r["cidr_net"].prefixlen
            msgs = []
            if c["required_name"] and r["subnet"] != c["required_name"]:
                msgs.append(f"debe llamarse `{c['required_name']}`")
            if c["min_size"] and plen > prefix(c["min_size"]):
                msgs.append(f"es /{plen} y el mínimo es {c['min_size']}")
            if c["max_size"] and plen < prefix(c["max_size"]):
                msgs.append(f"es /{plen} y el máximo es {c['max_size']}")
            for m in msgs:
                line = f"`{r['vnet']}/{r['subnet']}` ({c['service']}) {m} [{c['status']}]"
                (errors if c["severity"] == "error" else warnings).append(line)
    rep.add("Las subredes respetan los nombres y tamaños que exige Azure", "12", errors)
    if warnings:
        rep.add("Recomendaciones de tamaño de Azure (no bloquean)", "12", warnings, blocking=False)

    return rep, onprem, plan, per_range


def render(rep, plan, per_range, plan_path):
    digest = hashlib.sha256(Path(plan_path).read_bytes()).hexdigest()[:12]
    out = [
        "# Verificación del plan de direcciones de nube",
        "",
        f"- Fecha: {date.today().isoformat()}",
        f"- Plan verificado: `{Path(plan_path).name}` (sha256 `{digest}`)",
        f"- Inventario on-premises: `onprem-inventory.csv` ({EXPECTED_ONPREM} subredes del enunciado)",
        "",
        "## Resumen",
        "",
        "| Comprobación | Resultado |",
        "|---|---|",
    ]
    for name, crit, ok, details in rep.checks:
        status = "Cumple" if ok and not details else ("Cumple, con avisos" if ok else f"No cumple: {len(details)} problema(s)")
        out.append(f"| {name} | {status} |")
    out += ["", "## Detalle de problemas y avisos", ""]
    any_detail = False
    for name, crit, ok, details in rep.checks:
        if details:
            any_detail = True
            out.append(f"**{name}**")
            out += [f"- {d}" for d in details]
            out.append("")
    if not any_detail:
        out += ["Ninguno.", ""]
    out += ["## Rango por rango contra las 23 subredes on-premises", "",
            "| Rango de nube | Red virtual / subred | Resultado |", "|---|---|---|"]
    for r in plan:
        for label, key in (("red virtual", "vnet_cidr"), ("subred", "cidr")):
            if label == "red virtual" and r["vnet_cidr"] == r["cidr"]:
                continue
            hits = per_range.get(r[key], [])
            result = "sin solapamiento" if not hits else "**se solapa con** " + "; ".join(hits)
            where = f"`{r['vnet']}`" if label == "red virtual" else f"`{r['vnet']}/{r['subnet']}`"
            row = f"| `{r[key]}` | {where} | {result} |"
            if row not in out:
                out.append(row)
    out += ["", "## Conclusión", "",
            "**Sin solapamiento y todas las comprobaciones cumplidas.**" if rep.ok
            else "**El plan no cumple:** revisar los problemas listados arriba."]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--onprem", default=str(DATA / "onprem-inventory.csv"))
    ap.add_argument("--constraints", default=str(DATA / "azure-subnet-constraints.csv"))
    ap.add_argument("--out", help="Markdown report path (default: print to stdout)")
    args = ap.parse_args()

    rep, _, plan, per_range = verify(args.plan, args.onprem, args.constraints)
    text = render(rep, plan, per_range, args.plan)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Reporte escrito en {args.out}")
    else:
        print(text)
    for name, _, ok, details in rep.checks:
        print(("OK   " if ok else "FALLA") + f"  {name}" + (f" ({len(details)})" if details else ""), file=sys.stderr)
    sys.exit(0 if rep.ok else 1)


if __name__ == "__main__":
    main()

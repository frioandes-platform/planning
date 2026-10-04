#!/usr/bin/env python3
"""Compare the networks in a Terraform plan with ip-plan.csv (issue #39: "verify against the code, not the paper").

Usage:
    terraform show -json plan.tfplan > plan.json
    python3 compare_tfplan.py --tfplan plan.json [--plan ../data/ip-plan.csv] [--out-csv tf-ip-plan.csv]

It reads every azurerm_virtual_network and azurerm_subnet in planned_values (root and child modules) and reports:
- virtual networks or subnets that are in ip-plan.csv but not in Terraform, and the reverse;
- CIDRs that differ.
With --out-csv it writes the Terraform CIDRs in the ip-plan.csv schema (category, zone, service and internet are taken
from ip-plan.csv by vnet and subnet name), so verify_ip_plan.py can check the code itself against the 23 on-premises
subnets. Exit code 0 only when Terraform and ip-plan.csv match exactly.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def modules(module):
    yield module
    for child in module.get("child_modules", []):
        yield from modules(child)


def read_tfplan(path):
    root = json.loads(Path(path).read_text(encoding="utf-8"))["planned_values"]["root_module"]
    vnets, subnets = {}, {}
    for mod in modules(root):
        for res in mod.get("resources", []):
            v = res.get("values", {})
            if res["type"] == "azurerm_virtual_network":
                vnets[v["name"]] = v.get("address_space", [])
            elif res["type"] == "azurerm_subnet":
                subnets[(v["virtual_network_name"], v["name"])] = v.get("address_prefixes", [])
    return vnets, subnets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tfplan", required=True)
    ap.add_argument("--plan", default=str(DATA / "ip-plan.csv"))
    ap.add_argument("--out-csv")
    args = ap.parse_args()

    rows = [r for r in csv.DictReader(open(args.plan, encoding="utf-8")) if r["category"] != "reserva"]
    tf_vnets, tf_subnets = read_tfplan(args.tfplan)
    plan_vnets = {r["vnet"]: r["vnet_cidr"] for r in rows}
    plan_subnets = {(r["vnet"], r["subnet"]): r["cidr"] for r in rows}

    problems = []
    for name, cidr in sorted(plan_vnets.items()):
        if name not in tf_vnets:
            problems.append(f"Red virtual `{name}` está en ip-plan.csv y no en Terraform")
        elif tf_vnets[name] != [cidr]:
            problems.append(f"Red virtual `{name}`: ip-plan.csv dice {cidr}, Terraform dice {', '.join(tf_vnets[name])}")
    for name in sorted(set(tf_vnets) - set(plan_vnets)):
        problems.append(f"Red virtual `{name}` está en Terraform y no en ip-plan.csv")
    for key, cidr in sorted(plan_subnets.items()):
        if key not in tf_subnets:
            problems.append(f"Subred `{key[0]}/{key[1]}` está en ip-plan.csv y no en Terraform")
        elif tf_subnets[key] != [cidr]:
            problems.append(f"Subred `{key[0]}/{key[1]}`: ip-plan.csv dice {cidr}, "
                            f"Terraform dice {', '.join(tf_subnets[key])}")
    for key in sorted(set(tf_subnets) - set(plan_subnets)):
        problems.append(f"Subred `{key[0]}/{key[1]}` está en Terraform y no en ip-plan.csv")

    if args.out_csv:
        by_key = {(r["vnet"], r["subnet"]): r for r in rows}
        fields = list(rows[0].keys())
        with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for (vnet, subnet), prefixes in sorted(tf_subnets.items()):
                base = by_key.get((vnet, subnet), {k: "" for k in fields})
                for prefix in prefixes:
                    w.writerow({**base, "vnet": vnet, "subnet": subnet, "cidr": prefix,
                                "vnet_cidr": (tf_vnets.get(vnet) or [""])[0]})
            reserves = [r for r in csv.DictReader(open(args.plan, encoding="utf-8")) if r["category"] == "reserva"]
            w.writerows(reserves)
        print(f"CSV con los CIDR de Terraform escrito en {args.out_csv}", file=sys.stderr)

    print(f"Terraform: {len(tf_vnets)} redes virtuales, {len(tf_subnets)} subredes · "
          f"ip-plan.csv: {len(plan_vnets)} redes virtuales, {len(plan_subnets)} subredes")
    if problems:
        print("Diferencias:")
        for p in problems:
            print(f"- {p}")
        sys.exit(1)
    print("Terraform y ip-plan.csv coinciden: mismas redes virtuales, mismas subredes, mismos CIDR.")


if __name__ == "__main__":
    main()

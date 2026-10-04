#!/usr/bin/env python3
"""Measure TCP connect time (≈ 1 network round trip) from this machine to one endpoint per candidate Azure region.

Usage:
    python3 measure_latency.py --targets ../data/latency-targets.csv --place "Icesi, red cableada" [--samples 30]

targets CSV columns: region,host  (host = DNS name that lives in that region, port 443)
Prints a Markdown table (Spanish) ready to paste into the #8 deliverable.
"""
import argparse
import csv
import socket
import statistics
import time
from datetime import datetime


def connect_ms(host, port=443, timeout=5.0):
    start = time.perf_counter()
    with socket.create_connection((host, port), timeout=timeout):
        pass
    return (time.perf_counter() - start) * 1000


def measure(host, samples, pause):
    # Resolve once so DNS time is not counted in the samples.
    ip = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)[0][4][0]
    values, failures = [], 0
    for _ in range(samples):
        try:
            values.append(connect_ms(ip))
        except OSError:
            failures += 1
        time.sleep(pause)
    return ip, values, failures


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--targets", required=True)
    ap.add_argument("--place", required=True, help="Where the measurement is taken, e.g. 'Icesi, wifi'")
    ap.add_argument("--samples", type=int, default=30)
    ap.add_argument("--pause", type=float, default=0.5, help="Seconds between samples")
    args = ap.parse_args()

    with open(args.targets, newline="", encoding="utf-8") as f:
        targets = [r for r in csv.DictReader(f) if r["host"] and not r["host"].startswith("<")]

    print(f"Medición: {datetime.now().isoformat(timespec='minutes')} · Lugar: {args.place} · "
          f"{args.samples} conexiones TCP por región\n")
    print("| Región | Host (IP) | Mínimo ms | Mediana ms | p90 ms | Fallos |")
    print("|---|---|---|---|---|---|")
    for t in targets:
        try:
            ip, values, failures = measure(t["host"], args.samples, args.pause)
        except OSError as e:
            print(f"| {t['region']} | {t['host']} | — | — | — | no resuelve: {e} |")
            continue
        if not values:
            print(f"| {t['region']} | {t['host']} ({ip}) | — | — | — | {failures} |")
            continue
        values.sort()
        p90 = values[min(len(values) - 1, int(round(0.9 * (len(values) - 1))))]
        print(f"| {t['region']} | {t['host']} ({ip}) | {values[0]:.1f} | {statistics.median(values):.1f} "
              f"| {p90:.1f} | {failures} |")


if __name__ == "__main__":
    main()

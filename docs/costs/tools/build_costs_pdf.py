#!/usr/bin/env python3
"""Compile the cost document delivered to the client (issue #28) into one PDF.

It puts in one body the total project cost, the three cost documents of Phase 3 (F3-01 migration,
F3-02 steady-state month and campaign, F3-03 Fabric) and the list of cost-saving decisions, and
adds as an annex the assumptions of the cost documents, taken from the assumptions log. The
Markdown is prepared the same way as the architecture PDF (build_architecture_pdf.py), whose
functions and styles are reused here.

Requires pandoc (3.x) and typst. Usage, from the repository root:

    python3 docs/costs/tools/build_costs_pdf.py

Writes docs/costs/costs-frioandes.pdf.
"""
import argparse
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("arch", ROOT / "docs/architecture/tools/build_architecture_pdf.py")
arch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arch)

OUT = ROOT / "docs" / "costs" / "costs-frioandes.pdf"
CHAPTERS = [
    ("Costo total del proyecto y costo total de propiedad", ["docs/costs/costo-total-proyecto.md"]),
    ("1. Costo de la migración", ["docs/costs/costo-migracion.md"]),
    ("2. Costo mensual en estado estable y escenario de campaña", ["docs/costs/costo-mes-estable-y-campana.md"]),
    ("3. Costo de Microsoft Fabric, en línea aparte", ["docs/costs/costo-fabric.md"]),
    ("4. Decisiones de diseño que bajan el costo", ["docs/costs/decisiones-ahorro.md"]),
]
COST_ISSUES = ("#25", "#26", "#27", "#28")

COVER = {
    "kind": "Documento de costos",
    "title": "Costo total del proyecto, de la migración y de la operación",
    "subtitle": "Migración con la siembra de 1,2 PB, mes estable y campaña, Microsoft Fabric aparte, costo total de "
                "propiedad y decisiones que bajan el costo",
    "header": "Costos de la plataforma cloud de FríoAndes",
    "footer": "Documento de costos",
}


def promote(text, title):
    """Undo the heading shift of prepare() and put the chapter title in place of the document title."""
    out, in_code, first = [], False, True
    for line in text.splitlines():
        if arch.FENCE.match(line):
            in_code = not in_code
        elif not in_code and arch.HEADING.match(line):
            if first:
                line, first = f"# {title}", False
            else:
                line = line[1:]
        out.append(line)
    return "\n".join(out) + "\n"


def annex():
    """The rows of the assumptions log that come from the cost documents."""
    lines = (ROOT / "docs/cross-cutting/assumptions-log.md").read_text(encoding="utf-8").splitlines()
    head = [l for l in lines if l.startswith("|")][:2]
    rows = [l for l in lines if l.startswith("| ") and l.split("|")[3].strip() in COST_ISSUES]
    intro = ("Supuestos que sostienen las cifras de este documento, tal como están en el registro de supuestos del "
             "proyecto (`docs/cross-cutting/assumptions-log.md`). Cada documento repite los suyos en su sección de "
             "supuestos, junto a la cifra que afectan.\n")
    return intro + "\n" + "\n".join(head + rows) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--keep", help="also write the intermediate Typst file to this path")
    args = ap.parse_args()
    for tool in ("pandoc", "typst"):
        if not shutil.which(tool):
            sys.exit(f"{tool} no está instalado")

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
              "noviembre", "diciembre"]
    today = arch.dt.date.today()
    date = f"{today.day} de {months[today.month - 1]} de {today.year}"

    parts = [arch.BODY_START]
    for title, files in CHAPTERS:
        # One document per chapter: its own title becomes the chapter and its sections go back up one level,
        # so the contents list them.
        for f in files:
            parts.append(promote(arch.prepare(f), title))
    parts.append("# Anexo. Supuestos de los costos\n")
    parts.append(annex())
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "doc.md").write_text("\n".join(parts), encoding="utf-8")
        (tmp / "before.typ").write_text(arch.preamble(COVER, date, commit), encoding="utf-8")
        typ = tmp / "doc.typ"
        subprocess.run(["pandoc", str(tmp / "doc.md"), "-f", "gfm+raw_attribute", "-t", "typst", "-s", "-o", str(typ),
                        "--toc", "--toc-depth=2", "-B", str(tmp / "before.typ"),
                        "-V", "papersize=a4", "-V", "fontsize=9.8pt", "-V", "mainfont=Helvetica Neue", "-V", "codefont=Menlo",
                        "-M", "lang=es"], check=True)
        text = typ.read_text(encoding="utf-8").replace("title: auto,", "title: [Contenido],", 1)
        if args.keep:
            Path(args.keep).write_text(text, encoding="utf-8")
        # The Typst source goes through stdin: Typst only reads files under --root, and the temp folder is outside it.
        subprocess.run(["typst", "compile", "--root", str(ROOT), "-", args.out], input=text, text=True, check=True)
    print(args.out)


if __name__ == "__main__":
    main()

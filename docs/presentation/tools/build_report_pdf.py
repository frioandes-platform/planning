#!/usr/bin/env python3
"""Compile the strategy report for FríoAndes' cloud architect (issue #36) into one PDF.

The report is written for the PDF (docs/presentation/informe-estrategia.md); it is not a merge of the design
documents. The cover letter comes from docs/presentation/carta-presentacion.md. Both go through Pandoc to
Typst and are laid out with the shared template docs/presentation/tools/frioandes.typ: cover, letter,
document information, contents and the body with "Página n de N".

Images are handled as in the architecture PDF (build_architecture_pdf.py, whose figure() is reused): a wide
draw.io diagram gets a landscape page of its own so its labels stay readable.

Requires pandoc (3.x) and typst. Usage, from the repository root:

    python3 docs/presentation/tools/build_report_pdf.py

Writes docs/presentation/report.pdf.
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

PRES = ROOT / "docs" / "presentation"
OUT = PRES / "report.pdf"
REPORT = PRES / "informe-estrategia.md"
LETTER = PRES / "carta-presentacion.md"

TITLE = "Estrategia de la plataforma cloud de FríoAndes"
SUBTITLE = ("Gobierno, seguridad, red híbrida, cargas de trabajo, migración, observabilidad, Microsoft Fabric, "
            "infraestructura como código, costos, gestión del cambio y sistema de diseño")
PREPARED_FOR = "Arquitecto cloud de FríoAndes"
PREPARED_BY = "Equipo de arquitectura cloud del proyecto"
VERSION = "1.0"
HISTORY = [
    ("1.0", "20 de octubre de 2026", "Primera edición, para la revisión del arquitecto cloud antes de la aprobación "
                                     "del diseño y el presupuesto del 13 de noviembre"),
]
PACKAGE = [
    ("Informe de la estrategia (este documento)", "La estrategia completa en un solo documento: decisiones, cifras, "
     "riesgos y lo que FríoAndes tiene que confirmar", "Arquitecto cloud y gerencia"),
    ("Documento de arquitectura", "El diseño detallado de los ocho puntos del reto, con todos sus diagramas, tablas "
     "y supuestos", "Arquitecto cloud y equipos técnicos"),
    ("Documento de costos", "Costo de la migración, del mes estable y de campaña, de Fabric, del proyecto completo y "
     "costo total de propiedad", "Gerencia y finanzas"),
    ("Repositorio de infraestructura como código", "Módulos de Terraform, ambientes y pipeline de despliegue",
     "Equipo de plataforma"),
    ("Plantillas de notas de versión", "Plantillas de aplicación y de infraestructura, cada una con su ejemplo",
     "Comité de cambios y operación"),
    ("Sistema de diseño", "Logo, paleta, tipografía, componentes y reglas de uso", "Diseño y desarrollo"),
]


def typst_string(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def typst_rows(rows):
    return ", ".join("(" + ", ".join(f"[#{typst_string(c)}]" for c in row) + ")" for row in rows)


def prepare_report(path):
    """Resolve image paths against the repository root and turn standalone images into figures."""
    base = path.parent.relative_to(ROOT)
    out, in_code = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if arch.FENCE.match(line):
            in_code = not in_code
        elif not in_code:
            def image(mi):
                target = mi.group(2)
                if not target.startswith(("http://", "https://", "/")):
                    target = "/" + (base / target).resolve().relative_to(ROOT).as_posix()
                return f"![{mi.group(1)}]({target})"
            line = arch.IMAGE.sub(image, line)
            alone = arch.ALONE.match(line)
            if alone:
                line = arch.figure(alone.group(1), alone.group(2))
        out.append(line)
    return "\n".join(out) + "\n"


def assumption_counts():
    """Entries of the assumptions log, and how many wait for FríoAndes, so the report never quotes stale counts."""
    rows = [l for l in (ROOT / "docs/cross-cutting/assumptions-log.md").read_text(encoding="utf-8").splitlines()
            if l.startswith("| ") and not l.startswith("| Supuesto |")]
    pending = [l for l in rows if l.rstrip(" |").split("|")[-1].strip().startswith("Por confirmar con el cliente")]
    return len(rows), len(pending)


def to_typst(markdown):
    """Pandoc fragment (no template) for content that goes inside a Typst function."""
    return subprocess.run(["pandoc", "-f", "gfm", "-t", "typst"], input=markdown, capture_output=True, text=True,
                          check=True).stdout


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

    fields = [("Documento", TITLE), ("Versión", f"{VERSION}, generada desde el commit {commit}"), ("Fecha", date),
              ("Preparado para", PREPARED_FOR), ("Preparado por", PREPARED_BY),
              ("Clasificación", "Uso interno de FríoAndes"),
              ("Fuente", "Repositorio frioandes-platform/planning, carpeta docs/. El informe se vuelve a generar "
                         "con docs/presentation/tools/build_report_pdf.py")]
    before = f"""#import "/docs/presentation/tools/frioandes.typ": *
#show: frioandes.with(header-title: [{TITLE}], footer-label: [Informe de la estrategia · Versión {VERSION}],
                      chapter-break: false)

#cover(kind: "Informe de la estrategia", title: [{TITLE}], subtitle: [{SUBTITLE}],
       prepared-for: [{PREPARED_FOR}], prepared-by: [{PREPARED_BY}], date: [{date}], version: [{VERSION}])

#letter(place-date: [Cali, {date}])[
{to_typst(LETTER.read_text(encoding="utf-8"))}
]

#set page(numbering: "i")
#counter(page).update(1)
#doc-info(fields: ({typst_rows(fields)},), history: ({typst_rows(HISTORY)},), package: ({typst_rows(PACKAGE)},))
"""
    total, pending = assumption_counts()
    body = ("```{=typst}\n#pagebreak(weak: true)\n#set page(numbering: \"1\")\n#start-body()\n```\n\n"
            + prepare_report(REPORT).replace("{{supuestos}}", str(total)).replace("{{por_confirmar}}", str(pending)))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "doc.md").write_text(body, encoding="utf-8")
        (tmp / "before.typ").write_text(before, encoding="utf-8")
        typ = tmp / "doc.typ"
        subprocess.run(["pandoc", str(tmp / "doc.md"), "-f", "gfm+raw_attribute", "-t", "typst", "-s", "-o", str(typ),
                        "--toc", "--toc-depth=2", "-B", str(tmp / "before.typ"),
                        "-V", "papersize=a4", "-V", "fontsize=9.8pt", "-V", "mainfont=Helvetica Neue",
                        "-V", "codefont=Menlo", "-M", "lang=es"], check=True)
        text = typ.read_text(encoding="utf-8").replace("title: auto,", "title: [Contenido],", 1)
        if args.keep:
            Path(args.keep).write_text(text, encoding="utf-8")
        # The Typst source goes through stdin: Typst only reads files under --root, and the temp folder is outside it.
        subprocess.run(["typst", "compile", "--root", str(ROOT), "-", args.out], input=text, text=True, check=True)
    print(args.out)


if __name__ == "__main__":
    main()

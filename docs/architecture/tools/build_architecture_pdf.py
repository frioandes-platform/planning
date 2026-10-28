#!/usr/bin/env python3
"""Compile the consolidated architecture document (issue #19) into one PDF.

The chapters follow the eight points of the challenge. Each chapter takes the design documents as they
are in docs/architecture/ and prepares a copy for the PDF:

- headings move down one level, so that each document becomes a section of its chapter;
- the "Contenido" list of each document is dropped, because the PDF has its own table of contents;
- links to other Markdown files keep only their text, since the PDF must be read on its own;
- image paths become relative to the repository root, which is the Typst root.

Requires pandoc (3.x) and typst. Usage, from the repository root:

    python3 docs/architecture/tools/build_architecture_pdf.py

Writes docs/architecture/architecture-frioandes.pdf.
"""
import argparse
import datetime as dt
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARCH = ROOT / "docs" / "architecture"
OUT = ARCH / "architecture-frioandes.pdf"

CHAPTERS = [
    ("Visión general", ["docs/architecture/vista-general.md"]),
    ("1. Gobierno de la plataforma", ["docs/architecture/gobierno-landing-zone.md",
                                      "docs/architecture/gobierno-auditoria-facturacion.md"]),
    ("2. Seguridad", ["docs/architecture/seguridad-iam-cifrado.md",
                      "docs/architecture/seguridad-datos-personales-perimetro.md"]),
    ("3. Red híbrida y preparación para una segunda nube", ["docs/architecture/red-topologia-subnetting.md",
                                                            "docs/architecture/red-firewall-y-publicacion.md",
                                                            "docs/architecture/red-acceso-remoto-segunda-nube.md"]),
    ("4. Automatización y DevOps", ["docs/architecture/automatizacion-devops.md"]),
    ("5. Cargas de trabajo", ["docs/architecture/carga-a-plataforma-logistica.md",
                              "docs/architecture/carga-b-telemetria.md",
                              "docs/architecture/carga-c-migracion-y-campana.md",
                              "docs/architecture/carga-c-siembra-1-2pb.md"]),
    ("6. Observabilidad", ["docs/architecture/observabilidad-slo-zabbix.md"]),
    ("7. Inteligencia artificial de la torre de control, sobre Microsoft Fabric",
     ["docs/architecture/fabric-workspaces-ingesta-region.md",
      "docs/architecture/fabric-acceso-casos-uso-costo.md"]),
    ("8. Sistema de diseño", ["docs/design/sistema-de-diseno-frioandes.md",
                              "docs/design/logo-y-paleta.md",
                              "docs/design/tipografia-espaciado.md",
                              "docs/design/componentes-y-reglas-de-uso.md"]),
    ("9. Cronograma general del proyecto", ["docs/architecture/cronograma-proyecto.md"]),
    ("Anexo. Registro de supuestos", ["docs/cross-cutting/assumptions-log.md"]),
]

FENCE = re.compile(r"^(```|~~~)")
HEADING = re.compile(r"^(#{1,5}) ")
LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)\)")
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
ALONE = re.compile(r"^\s*!\[([^\]]*)\]\(([^)\s]+)\)\s*$")
# Large diagrams (2.000 px wide or more) wider than this ratio go on a landscape page of their own,
# so that their labels stay readable.
LANDSCAPE = 1.45

# Cover and document information, laid out with the shared template of the delivery package
# (docs/presentation/tools/frioandes.typ). build_costs_pdf.py calls preamble() with its own texts.
COVER = {
    "kind": "Documento de arquitectura",
    "title": "Plataforma cloud para la operación de cadena de frío",
    "subtitle": "Gobierno, seguridad, red híbrida, automatización, cargas de trabajo, migración, observabilidad, "
                "Microsoft Fabric y sistema de diseño",
    "header": "Arquitectura de la plataforma cloud de FríoAndes",
    "footer": "Documento de arquitectura",
}
PREPARED_FOR = "Arquitecto cloud de FríoAndes"
PREPARED_BY = "Equipo de arquitectura cloud del proyecto"
BODY_START = "```{=typst}\n#pagebreak(weak: true)\n#set page(numbering: \"1\")\n#start-body()\n```\n"


def preamble(cover, date, commit):
    """Typst that goes before the contents: template, cover, document information and front-matter numbering."""
    def q(text):
        return "[#" + '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"' + "]"
    fields = [("Documento", cover["title"]), ("Versión", f"Generada desde el commit {commit}"), ("Fecha", date),
              ("Preparado para", PREPARED_FOR), ("Preparado por", PREPARED_BY),
              ("Clasificación", "Uso interno de FríoAndes"),
              ("Fuente", "Repositorio frioandes-platform/planning, carpeta docs/")]
    rows = ", ".join(f"({q(k)}, {q(v)})" for k, v in fields)
    return f"""#import "/docs/presentation/tools/frioandes.typ": *
#show: frioandes.with(header-title: {q(cover["header"])}, footer-label: {q(cover["footer"])})

#cover(kind: {q(cover["kind"])}, title: {q(cover["title"])}, subtitle: {q(cover["subtitle"])},
       prepared-for: {q(PREPARED_FOR)}, prepared-by: {q(PREPARED_BY)}, date: {q(date)}, version: {q(commit)})

#set page(numbering: "i")
#counter(page).update(1)
#doc-info(fields: ({rows},), history: (({q(commit)}, {q(date)}, {q("Versión generada desde el repositorio")}),))
"""


def png_size(path):
    with open(path, "rb") as f:
        return struct.unpack(">II", f.read(24)[16:24])


def ratio(size):
    return size[0] / size[1]


def figure(alt, target):
    """Raw Typst for a standalone image: a captioned figure, alone on a landscape page when it is a wide diagram."""
    caption = alt.replace("\\", "\\\\").replace('"', '\\"')
    if target.endswith(".drawio.png") and png_size(ROOT / target.lstrip("/"))[0] >= 2000 \
            and ratio(png_size(ROOT / target.lstrip("/"))) >= LANDSCAPE:
        body = (f'#page(flipped: true, header: none, footer: none, margin: 1.2cm)[#align(center + horizon)['
                f'#figure(image("{target}", width: 100%, height: 92%, fit: "contain"), caption: [#"{caption}"])]]')
    else:
        body = f'#figure(image("{target}", width: 100%), caption: [#"{caption}"])'
    return f"```{{=typst}}\n{body}\n```"


def prepare(path):
    """Return the Markdown of one design document, ready to be a section of a chapter."""
    src = ROOT / path
    base = src.parent.relative_to(ROOT)
    out, in_code, skip = [], False, False
    for line in src.read_text(encoding="utf-8").splitlines():
        if FENCE.match(line):
            in_code = not in_code
            out.append(line)
            continue
        if in_code:
            out.append(line)
            continue
        m = HEADING.match(line)
        if m:
            skip = len(m.group(1)) == 2 and line[3:].strip() == "Contenido"
            if skip:
                continue
            line = "#" + line
        elif skip:
            if line.strip() == "---":
                skip = False
            continue

        def image(mi):
            target = mi.group(2)
            if not target.startswith(("http://", "https://", "/")):
                target = "/" + (base / target).as_posix()
            return f"![{mi.group(1)}]({target})"

        def link(ml):
            text, target = ml.group(1), ml.group(2)
            if target.startswith(("http://", "https://", "mailto:")):
                return ml.group(0)
            return text

        line = IMAGE.sub(image, line)
        alone = ALONE.match(line)
        if alone:
            out.append(figure(alone.group(1), alone.group(2)))
            continue
        line = LINK.sub(link, line)
        out.append(line)
    return "\n".join(out) + "\n"


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
    today = dt.date.today()
    date = f"{today.day} de {months[today.month - 1]} de {today.year}"

    parts = [BODY_START]
    for title, files in CHAPTERS:
        parts.append(f"# {title}\n")
        parts.extend(prepare(f) for f in files)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "doc.md").write_text("\n".join(parts), encoding="utf-8")
        (tmp / "before.typ").write_text(preamble(COVER, date, commit), encoding="utf-8")
        typ = tmp / "doc.typ"
        subprocess.run(["pandoc", str(tmp / "doc.md"), "-f", "gfm+raw_attribute", "-t", "typst", "-s", "-o", str(typ),
                        "--toc", "--toc-depth=2", "-B", str(tmp / "before.typ"),
                        "-V", "papersize=a4", "-V", "fontsize=9.8pt", "-V", "mainfont=Helvetica Neue", "-V", "codefont=Menlo",
                        "-M", "lang=es"], check=True)
        text = typ.read_text(encoding="utf-8").replace("title: auto,", "title: [Contenido],", 1)
        typ.write_text(text, encoding="utf-8")
        if args.keep:
            shutil.copy(typ, args.keep)
        # The Typst source goes through stdin: Typst only reads files under --root, and the temp folder is outside it.
        subprocess.run(["typst", "compile", "--root", str(ROOT), "-", args.out], input=text, text=True, check=True)
    print(args.out)


if __name__ == "__main__":
    main()

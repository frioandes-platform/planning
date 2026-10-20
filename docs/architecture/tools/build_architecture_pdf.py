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
    ("8. Sistema de diseño", ["docs/design/logo-y-paleta.md"]),
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

PREAMBLE = r"""
#let navy = rgb("#0A1F2E")
#let teal = rgb("#0D7894")
#let ice = rgb("#DDF3F8")
#let mist = rgb("#F2F6F8")
#let grey = rgb("#52646F")

#set text(lang: "es", region: "co")
#set par(justify: false, leading: 0.62em)
#set heading(numbering: none)
#show link: set text(fill: teal)

#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  block(width: 100%, fill: navy, inset: (x: 14pt, y: 18pt), radius: 3pt,
        text(fill: white, size: 20pt, weight: "bold", it.body))
  v(10pt)
}
#show heading.where(level: 2): it => {
  v(14pt)
  block(width: 100%, stroke: (bottom: 1.5pt + teal), inset: (bottom: 6pt),
        text(fill: navy, size: 15pt, weight: "bold", it.body))
  v(4pt)
}
#show heading.where(level: 3): set text(fill: navy, size: 12pt)
#show heading.where(level: 4): set text(fill: teal, size: 10.5pt)
#show heading.where(level: 5): set text(fill: grey, size: 10pt)

#show figure.where(kind: table): set block(breakable: true)
#show table: set text(size: 7.8pt)
#show table: set align(left)
#show table: set par(justify: false)
#set table(inset: 4pt, fill: (_, y) => if y == 0 { ice })
#show raw.where(block: true): it => block(width: 100%, fill: mist, inset: 8pt, radius: 3pt, text(size: 7.8pt, it))

#set page(
  header: context {
    if counter(page).get().first() > 1 {
      set text(size: 8pt, fill: grey)
      grid(columns: (1fr, auto), align: (left, right),
           [Arquitectura de la plataforma cloud de FríoAndes], image("/docs/design/brand/logo/logo-principal.png", height: 12pt))
      line(length: 100%, stroke: 0.4pt + rgb("#C9D4DA"))
    }
  },
  footer: context {
    if counter(page).get().first() > 1 {
      set text(size: 8pt, fill: grey)
      align(center, counter(page).display("1"))
    }
  },
)

#page(header: none, footer: none, margin: 0pt)[
  #block(width: 100%, height: 100%, fill: navy, inset: (x: 2.4cm, y: 2.6cm))[
    #image("/docs/design/brand/logo/logo-negativo.png", width: 7cm)
    #v(5cm)
    #text(fill: rgb("#1FB5D6"), size: 13pt, weight: "bold")[DOCUMENTO DE ARQUITECTURA]
    #v(4pt)
    #text(fill: white, size: 30pt, weight: "bold")[Plataforma cloud para la operación de cadena de frío]
    #v(10pt)
    #text(fill: rgb("#DDF3F8"), size: 13pt)[Gobierno, seguridad, red híbrida, automatización, cargas de trabajo, migración, observabilidad, Microsoft Fabric y sistema de diseño]
    #v(1fr)
    #line(length: 100%, stroke: 0.6pt + rgb("#1FB5D6"))
    #v(6pt)
    #text(fill: white, size: 10pt)[FríoAndes · Azure, East US 2 y Central US · $DATE$ · $COMMIT$]
    #linebreak()
    #text(fill: rgb("#A0AAB0"), size: 9pt)[Caso de estudio académico · Universidad Icesi]
  ]
]
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

    parts = []
    for title, files in CHAPTERS:
        parts.append(f"# {title}\n")
        parts.extend(prepare(f) for f in files)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "doc.md").write_text("\n".join(parts), encoding="utf-8")
        (tmp / "before.typ").write_text(PREAMBLE.replace("$DATE$", date).replace("$COMMIT$", f"versión {commit}"),
                                        encoding="utf-8")
        typ = tmp / "doc.typ"
        subprocess.run(["pandoc", str(tmp / "doc.md"), "-f", "gfm+raw_attribute", "-t", "typst", "-s", "-o", str(typ),
                        "--toc", "--toc-depth=2", "-B", str(tmp / "before.typ"),
                        "-V", "papersize=a4", "-V", "margin.x=2cm", "-V", "margin.y=2.2cm",
                        "-V", "fontsize=9.5pt", "-V", "mainfont=Helvetica Neue", "-V", "codefont=Menlo",
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

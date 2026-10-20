// Shared Typst template for the documents FríoAndes receives (issue #36): the strategy report, the
// architecture document and the cost document. It holds the brand colours of docs/design/brand/tokens.json,
// the cover, the cover letter, the document information page and the page, heading, table and callout styles.
//
// The build scripts import it from the Typst root (the repository) and apply it with
// `#show: frioandes.with(...)` before the cover, so the same look reaches every page.

#let navy = rgb("#0A1F2E")
#let panel = rgb("#10304A")
#let teal = rgb("#0D7894")
#let cyan = rgb("#1FB5D6")
#let ice = rgb("#DDF3F8")
#let mist = rgb("#F2F6F8")
#let grey6 = rgb("#52646F")
#let grey4 = rgb("#A0AAB0")
#let grey2 = rgb("#C9D4DA")

#let logo = "/docs/design/brand/logo/logo-principal.png"
#let logo-negative = "/docs/design/brand/logo/logo-negativo.png"

// True from the first chapter on: the footer then reads "Página n de N" and counts only the body.
#let in-body = state("fa-in-body", false)

// The isotype idea at cover size: a mountain crest drawn as a temperature trace that ends in the sensor dot.
#let crest(width: 17cm, height: 3.2cm, stroke: 2.4pt + teal, dot: cyan) = {
  let p(x, y) = (x * width, (1 - y) * height)
  let points = ((0, 0.18), (0.16, 0.30), (0.27, 0.22), (0.43, 0.62), (0.52, 0.48), (0.66, 0.92),
                (0.78, 0.55), (0.88, 0.66), (1, 0.40))
  box(width: width, height: height, {
    place(curve(stroke: (paint: stroke.paint, thickness: stroke.thickness, cap: "round", join: "round"),
                curve.move(p(..points.first())), ..points.slice(1).map(q => curve.line(p(..q)))))
    let (x, y) = p(0.66, 0.92)
    place(dx: x - 6pt, dy: y - 6pt, circle(radius: 6pt, fill: dot))
  })
}

#let cover(kind: "", title: "", subtitle: "", prepared-for: "", prepared-by: "", date: "", version: "",
           note: "Caso de estudio académico · Universidad Icesi") = page(
  margin: 0pt, header: none, footer: none, fill: navy,
)[
  #block(width: 100%, height: 100%, inset: (x: 2.4cm, top: 2.4cm, bottom: 2cm))[
    #image(logo-negative, width: 6.2cm)
    #v(1fr)
    #text(fill: cyan, size: 10.5pt, weight: "bold", tracking: 2pt, upper(kind))
    #v(8pt)
    #set par(justify: false)
    #text(fill: white, size: 30pt, weight: "bold", hyphenate: false)[#title]
    #v(12pt)
    #block(width: 88%, text(fill: ice, size: 12.5pt, hyphenate: false)[#subtitle])
    #v(1.4cm)
    #crest()
    #v(1fr)
    #line(length: 100%, stroke: 0.6pt + cyan)
    #v(10pt)
    #set text(size: 9pt)
    #grid(columns: (1fr, 1fr, auto, auto), column-gutter: 18pt, row-gutter: 5pt,
      text(fill: grey4)[Preparado para], text(fill: grey4)[Preparado por], text(fill: grey4)[Fecha],
      text(fill: grey4)[Versión],
      text(fill: white, weight: "bold")[#prepared-for], text(fill: white, weight: "bold")[#prepared-by],
      text(fill: white, weight: "bold")[#date], text(fill: white, weight: "bold")[#version])
    #v(14pt)
    #text(fill: grey4, size: 8pt)[#note]
  ]
]

// A one-page letter on letterhead, before the table of contents.
#let letter(place-date: "", body) = page(header: none, footer: none, margin: (x: 2.6cm, top: 2.2cm, bottom: 2.2cm))[
  #grid(columns: (1fr, auto), align: (left + horizon, right + horizon),
        image(logo, height: 1.1cm), text(size: 8.5pt, fill: grey6)[#place-date])
  #v(4pt)
  #line(length: 100%, stroke: 1.2pt + teal)
  #v(1.1cm)
  #set par(justify: true, leading: 0.72em, spacing: 1.05em)
  #set text(size: 10.5pt)
  #body
  #v(1fr)
  #line(length: 100%, stroke: 0.4pt + grey2)
  #v(4pt)
  #text(size: 8pt, fill: grey6)[FríoAndes · Plataforma cloud para la operación de cadena de frío · Caso de estudio académico, Universidad Icesi]
]

// Document information, version history and the documents that travel with this one.
#let doc-info(fields: (), history: (), package: ()) = {
  let label(t) = text(fill: grey6, size: 8.5pt, t)
  heading(level: 2, outlined: false, numbering: none)[Información del documento]
  {
    show table.cell.where(y: 0): set text(fill: navy, weight: "regular")
    table(columns: (4.2cm, 1fr), stroke: (x, y) => (bottom: 0.5pt + grey2), fill: none,
          inset: (x: 6pt, y: 6pt),
          ..fields.map(((k, v)) => (label(k), v)).flatten())
  }
  v(14pt)
  heading(level: 2, outlined: false, numbering: none)[Historial de versiones]
  table(columns: (1.6cm, 3.6cm, 1fr), table.header([Versión], [Fecha], [Cambios]), ..history.flatten())
  if package.len() > 0 {
    v(14pt)
    heading(level: 2, outlined: false, numbering: none)[Documentos del paquete de entrega]
    table(columns: (5.2cm, 1fr, 3.4cm), table.header([Documento], [Qué contiene], [Para quién]),
          ..package.flatten())
  }
  pagebreak()
}

// chapter-break: whether each level-1 heading starts a page. The long documents do; the report flows on.
#let frioandes(header-title: "", footer-label: "", font: ("Helvetica Neue",), chapter-break: true, body) = {
  set text(lang: "es", region: "co", font: font, size: 9.8pt, fill: navy)
  set par(justify: true, leading: 0.66em, spacing: 1.05em)
  set list(indent: 4pt, body-indent: 6pt, marker: text(fill: teal)[•])
  set enum(indent: 4pt, body-indent: 6pt)
  show link: set text(fill: teal)
  show strong: set text(fill: navy)

  set page(
    paper: "a4",
    margin: (x: 2.2cm, top: 2.6cm, bottom: 2.3cm),
    header: context {
      set text(size: 8pt, fill: grey6)
      grid(columns: (1fr, auto), align: (left + horizon, right + horizon),
           header-title, image(logo, height: 11pt))
      v(-4pt)
      line(length: 100%, stroke: 0.4pt + grey2)
    },
    footer: context {
      set text(size: 8pt, fill: grey6)
      let n = counter(page).display()
      grid(columns: (1fr, auto), align: (left, right),
           footer-label,
           if in-body.get() { [Página #n de #counter(page).final().first()] } else { n })
    },
  )

  set heading(numbering: none)
  show heading: set par(justify: false)
  show heading.where(level: 1): it => {
    if chapter-break { pagebreak(weak: true) } else { v(18pt, weak: true) }
    block(sticky: true, below: 10pt, {
      v(6pt)
      block(width: 100%, inset: (left: 12pt, y: 4pt), stroke: (left: 4pt + teal),
            text(fill: navy, size: if chapter-break { 21pt } else { 18pt }, weight: "bold", hyphenate: false, it.body))
      v(2pt)
      line(length: 100%, stroke: 0.6pt + grey2)
    })
  }
  show heading.where(level: 2): it => {
    v(12pt)
    block(sticky: true, text(fill: navy, size: 13.5pt, weight: "bold", hyphenate: false, it.body))
    v(2pt)
  }
  show heading.where(level: 3): it => {
    v(8pt)
    block(sticky: true, text(fill: teal, size: 11pt, weight: "bold", it.body))
  }
  show heading.where(level: 4): set text(fill: grey6, size: 10pt)

  show outline.entry.where(level: 1): set block(above: 1.1em)
  show outline.entry.where(level: 1): set text(weight: "bold")

  set table(inset: (x: 6pt, y: 5pt), stroke: (x, y) => (bottom: 0.5pt + grey2),
            fill: (x, y) => if y == 0 { navy } else if calc.even(y) { mist })
  show table.cell.where(y: 0): set text(fill: white, weight: "bold")
  show table: set text(size: 8.4pt)
  show table: set align(left)
  show table: set par(justify: false)
  show figure.where(kind: table): set block(breakable: true)
  show figure.caption: set text(size: 8.4pt, fill: grey6)

  show quote.where(block: true): it => block(width: 100%, fill: ice, stroke: (left: 3pt + teal),
                                              inset: (x: 12pt, y: 9pt), radius: (right: 3pt), it.body)
  show raw.where(block: true): it => block(width: 100%, fill: mist, inset: 8pt, radius: 3pt, text(size: 8pt, it))

  body
}

// Raw block at the start of the body: arabic page numbers from 1 and the "Página n de N" footer.
#let start-body() = {
  in-body.update(true)
  counter(page).update(1)
}

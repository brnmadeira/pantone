#!/usr/bin/env python3
"""Converte uma minuta em Markdown para .docx com formatação forense.

Formatação: A4, margens 3 cm (sup./esq.) e 2 cm (inf./dir.), fonte 12, espaçamento 1,5,
parágrafos justificados com recuo de primeira linha de 2 cm, citações (>) com recuo de 4 cm,
fonte 10 e espaçamento simples, numeração de página no rodapé e cabeçalho opcional.

Convenções (ver references/estilo.md):
  # Título          → centralizado, negrito, caixa como escrita
  ## Seção          → negrito, à esquerda
  ### Subseção      → negrito + itálico
  > citação         → bloco recuado
  - item / 1. item  → lista
  ---               → quebra de página
  <center>x</center>→ linha centralizada
  **negrito**, *itálico*; [PREENCHER...] e [VERIFICAR...] destacados em amarelo.
  Tudo a partir de um título "Notas para o advogado" é descartado (notas internas).

Uso:
  gerar_docx.py minuta.md saida.docx [--cabecalho "Escritório X — OAB/UF"] [--fonte "Times New Roman"]
"""
from __future__ import annotations

import argparse
import re
import sys

try:
    from docx import Document
    from docx.enum.section import WD_SECTION  # noqa: F401
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt
except ImportError:
    sys.exit("python-docx não instalado. Rode: pip install python-docx")

INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|\[(?:PREENCHER|VERIFICAR)[^\]]*\])")
NOTAS = re.compile(r"^#{1,6}\s*notas para o advogado", re.IGNORECASE)


def add_runs(par, texto: str, base_bold=False, base_italic=False, size=None):
    for parte in INLINE.split(texto):
        if not parte:
            continue
        bold, italic, destaque = base_bold, base_italic, False
        if parte.startswith("**") and parte.endswith("**"):
            parte, bold = parte[2:-2], True
        elif parte.startswith("*") and parte.endswith("*") and len(parte) > 2:
            parte, italic = parte[1:-1], True
        elif parte.startswith("[PREENCHER") or parte.startswith("[VERIFICAR"):
            destaque, bold = True, True
        run = par.add_run(parte)
        run.bold = bold
        run.italic = italic
        if size:
            run.font.size = Pt(size)
        if destaque:
            run.font.highlight_color = WD_COLOR_INDEX.YELLOW


def campo_pagina(par):
    run = par.add_run()
    for tipo, texto in (("begin", None), (None, "PAGE"), ("end", None)):
        if tipo:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tipo)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = texto
        run._r.append(el)


def configurar(doc, fonte: str, cabecalho: str | None):
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    sec.top_margin, sec.left_margin = Cm(3), Cm(3)
    sec.bottom_margin, sec.right_margin = Cm(2), Cm(2)

    normal = doc.styles["Normal"]
    normal.font.name = fonte
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), fonte)
    pf = normal.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(6)

    if cabecalho:
        hp = sec.header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_runs(hp, cabecalho, size=10)
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    campo_pagina(fp)


def converter(md: str, saida: str, fonte: str, cabecalho: str | None):
    linhas = md.splitlines()
    for i, l in enumerate(linhas):
        if NOTAS.match(l.strip()):
            linhas = linhas[:i]
            break
    while linhas and linhas[-1].strip() in ("", "---"):
        linhas.pop()

    doc = Document()
    configurar(doc, fonte, cabecalho)
    buffer: list[str] = []

    def flush():
        if not buffer:
            return
        texto = " ".join(s.strip() for s in buffer)
        buffer.clear()
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(2)
        add_runs(p, texto)

    citacao: list[str] = []

    def flush_citacao():
        if not citacao:
            return
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(4)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(12)
        add_runs(p, " ".join(citacao), size=10)
        citacao.clear()

    for bruto in linhas:
        l = bruto.rstrip()
        s = l.strip()
        if not s.startswith(">"):
            flush_citacao()
        if not s:
            flush()
            continue
        if s == "---":
            flush()
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            flush()
            nivel, texto = len(m.group(1)), m.group(2)
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.keep_with_next = True
            if nivel == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                add_runs(p, texto, base_bold=True)
            else:
                add_runs(p, texto, base_bold=True, base_italic=(nivel >= 3))
            continue
        if s.startswith(">"):
            flush()
            citacao.append(s.lstrip(">").strip())
            continue
        m = re.match(r"^<center>(.*)</center>$", s, re.IGNORECASE)
        if m:
            flush()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            add_runs(p, m.group(1))
            continue
        m = re.match(r"^([-*•]|\d+[.)]|[a-z][)])\s+(.*)$", s)
        if m:
            flush()
            marcador = m.group(1)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Cm(1.5)
            p.paragraph_format.first_line_indent = Cm(-0.75)
            prefixo = "•" if marcador in "-*•" else marcador
            add_runs(p, f"{prefixo}\t{m.group(2)}" if prefixo == "•" else f"{prefixo} {m.group(2)}")
            continue
        buffer.append(l)
    flush()
    flush_citacao()
    doc.save(saida)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", help="Arquivo .md da minuta")
    ap.add_argument("saida", help="Arquivo .docx a gerar")
    ap.add_argument("--cabecalho", help="Texto do cabeçalho (ex.: nome do escritório e OAB)")
    ap.add_argument("--fonte", default="Times New Roman", help="Fonte (padrão: Times New Roman)")
    a = ap.parse_args(argv)
    with open(a.entrada, encoding="utf-8") as f:
        md = f.read()
    converter(md, a.saida, a.fonte, a.cabecalho)
    print(f"Gerado: {a.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

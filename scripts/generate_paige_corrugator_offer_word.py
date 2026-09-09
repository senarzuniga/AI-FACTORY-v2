from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "PAIGE_CORRUGATOR_AREA_INGECART_PROPOSAL_2026-08-26.docx"

SOURCE_PAIGE_OFFER = Path(
    r"C:\Users\Inaki Senar\Documents\INGECART\COMMERCIAL\PROYECTOS"
    r"\Sterner Global\Paige"
    r"\PAGE PROJECT INGECART AUTOMATIC REEL LOADING SYSTEM PROPOSAL.docx"
)
LOGO_PATH = Path(r"C:\Users\Inaki Senar\Documents\INGECART\MARKETING\LOGOS\FULLOB.png")

CLIENT = "Sterner Global"
PROJECT = "PAIGE Project - Corrugator Area"
PROPOSAL_REFERENCE = "PAIGE-CORR-2026-08-R1"
PROPOSAL_DATE = date(2026, 8, 26)

ORANGE = "F36B21"
DARK = "171717"
MID_GREY = "5C5C5C"
LIGHT_GREY = "EDEDED"
VERY_LIGHT_GREY = "F7F7F7"
WHITE = "FFFFFF"
GREEN = "2E7D5B"
RED = "A63D40"


@dataclass(frozen=True)
class ProductBlock:
    code: str
    name: str
    supply_price: Decimal
    installation_price: Decimal

    @property
    def total(self) -> Decimal:
        return self.supply_price + self.installation_price


PRODUCT_BLOCKS = (
    ProductBlock(
        "A",
        "INGETRANS automatic reel loading and return system",
        Decimal("869396.91"),
        Decimal("270161.27"),
    ),
    ProductBlock(
        "B",
        "Crawler chain conveyor tracks for reel stands - 10 units",
        Decimal("341466.42"),
        Decimal("20754.27"),
    ),
    ProductBlock(
        "C",
        "148 m incoming reel conveyor line with integrated RFID station",
        Decimal("600018.34"),
        Decimal("41534.26"),
    ),
    ProductBlock(
        "D",
        "Corrugator scrap intralogistics package with one KUKA AMR",
        Decimal("174152.63"),
        Decimal("46014.89"),
    ),
)

INSTALLATION_LINES = (
    ("A1", "INGETRANS mechanical assembly", 28, 4, Decimal("143096.00"), Decimal("23234.50")),
    ("A2", "INGETRANS commissioning", 14, 1, Decimal("14469.00"), Decimal("6282.09")),
    ("A3", "INGETRANS start-up and training", 28, 2, Decimal("66976.00"), Decimal("16103.68")),
    ("B1", "INGETRANS reel-stand conveyor installation", 14, 1, Decimal("14469.00"), Decimal("6285.27")),
    ("C1", "148 m metallic conveyor + RFID start-up and commissioning", 14, 2, Decimal("34398.00"), Decimal("7136.26")),
    ("D1", "AMR intralogistics turnkey installation", 31, 1, Decimal("38083.50"), Decimal("7931.39")),
)


def format_eur(value: Decimal) -> str:
    amount = f"{value:,.2f}"
    amount = amount.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{amount} EUR"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")


def set_cell_margins(cell, *, top=90, start=110, bottom=90, end=110) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_cell_border(cell, color: str = "D0D0D0", size: str = "4") -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:color"), color)


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_cell_width(cell, width_cm: float) -> None:
    cell.width = Cm(width_cm)


def set_table_column_widths(table, widths_cm: tuple[float, ...]) -> None:
    if len(table.columns) != len(widths_cm):
        raise ValueError("Table column count does not match width specification")
    for grid_column, width_cm in zip(table._tbl.tblGrid.gridCol_lst, widths_cm):
        grid_column.set(qn("w:w"), str(Cm(width_cm).twips))
    for row in table.rows:
        for cell, width_cm in zip(row.cells, widths_cm):
            set_cell_width(cell, width_cm)


def style_cell_text(cell, *, bold=False, color=DARK, size=8.5, align=None) -> None:
    for paragraph in cell.paragraphs:
        if align is not None:
            paragraph.alignment = align
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)
        for run in paragraph.runs:
            run.font.name = "Arial"
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = RGBColor.from_string(color)


def configure_styles(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(9.5)
    normal.font.color.rgb = RGBColor.from_string(DARK)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.08

    title = doc.styles["Title"]
    title.font.name = "Arial"
    title.font.size = Pt(27)
    title.font.bold = True
    title.font.color.rgb = RGBColor.from_string(WHITE)

    for name, size, color in (
        ("Heading 1", 18, ORANGE),
        ("Heading 2", 13, DARK),
        ("Heading 3", 10.5, ORANGE),
    ):
        style = doc.styles[name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(9)
        style.paragraph_format.space_after = Pt(4)
        style.paragraph_format.keep_with_next = True

    doc.styles["List Bullet"].font.name = "Arial"
    doc.styles["List Bullet"].font.size = Pt(9.25)


def add_page_field(paragraph) -> None:
    run = paragraph.add_run("Page ")
    run.font.name = "Arial"
    run.font.size = Pt(7)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    field.set(qn("w:dirty"), "true")
    paragraph._p.append(field)
    total_run = paragraph.add_run(" / ")
    total_run.font.name = "Arial"
    total_run.font.size = Pt(7)
    total = OxmlElement("w:fldSimple")
    total.set(qn("w:instr"), "NUMPAGES")
    total.set(qn("w:dirty"), "true")
    paragraph._p.append(total)


def configure_header_footer(doc: Document) -> None:
    section = doc.sections[0]
    header = section.header
    table = header.add_table(rows=1, cols=2, width=Inches(6.7))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_column_widths(table, (11.0, 6.0))
    set_cell_width(table.cell(0, 0), 11.0)
    set_cell_width(table.cell(0, 1), 6.0)
    left = table.cell(0, 0)
    right = table.cell(0, 1)
    if LOGO_PATH.exists():
        left.paragraphs[0].add_run().add_picture(str(LOGO_PATH), width=Inches(1.05))
    right.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    text = right.paragraphs[0].add_run(PROPOSAL_REFERENCE)
    text.font.name = "Arial"
    text.font.size = Pt(7)
    text.font.bold = True
    text.font.color.rgb = RGBColor.from_string(MID_GREY)

    footer = section.footer
    table = footer.add_table(rows=1, cols=2, width=Inches(6.7))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_column_widths(table, (12.0, 5.0))
    set_cell_width(table.cell(0, 0), 12.0)
    set_cell_width(table.cell(0, 1), 5.0)
    left = table.cell(0, 0)
    right = table.cell(0, 1)
    left.paragraphs[0].add_run(
        f"CONFIDENTIAL | {CLIENT} | {PROJECT}"
    )
    style_cell_text(left, color=MID_GREY, size=7)
    right.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_page_field(right.paragraphs[0])


def add_section_title(doc: Document, number: str, title: str):
    p = doc.add_paragraph(style="Heading 1")
    p.paragraph_format.space_before = Pt(12)
    run = p.add_run(f"{number}  {title.upper()}")
    run.font.color.rgb = RGBColor.from_string(ORANGE)
    p_pr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "16")
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), ORANGE)
    pbdr.append(bottom)
    p_pr.append(pbdr)
    return p


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent = Cm(0.55)
        p.paragraph_format.first_line_indent = Cm(-0.25)
        p.paragraph_format.space_after = Pt(2.5)
        p.add_run(item)


def add_callout(doc: Document, title: str, body: str, *, fill="FFF1E7") -> None:
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_column_widths(table, (16.5,))
    cell = table.cell(0, 0)
    set_cell_width(cell, 16.5)
    set_cell_shading(cell, fill)
    set_cell_border(cell, ORANGE, "8")
    set_cell_margins(cell, top=130, bottom=130, start=160, end=160)
    p = cell.paragraphs[0]
    r = p.add_run(title.upper())
    r.font.name = "Arial"
    r.font.size = Pt(9)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(ORANGE)
    p = cell.add_paragraph(body)
    p.paragraph_format.space_after = Pt(0)
    for run in p.runs:
        run.font.name = "Arial"
        run.font.size = Pt(9)


def add_two_column_table(
    doc: Document,
    rows: list[tuple[str, str]],
    *,
    headers=("Item", "Description"),
    widths=(5.2, 11.3),
) -> None:
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_column_widths(table, widths)
    header = table.rows[0].cells
    for idx, value in enumerate(headers):
        header[idx].text = value
        set_cell_shading(header[idx], DARK)
        set_cell_border(header[idx], WHITE)
        set_cell_margins(header[idx])
        style_cell_text(header[idx], bold=True, color=WHITE, size=8.5)
        set_cell_width(header[idx], widths[idx])
    set_repeat_table_header(table.rows[0])

    for row_index, (label, description) in enumerate(rows):
        cells = table.add_row().cells
        cells[0].text = label
        cells[1].text = description
        for idx, cell in enumerate(cells):
            set_cell_width(cell, widths[idx])
            set_cell_margins(cell)
            set_cell_border(cell)
            if row_index % 2:
                set_cell_shading(cell, VERY_LIGHT_GREY)
        style_cell_text(cells[0], bold=True, color=DARK, size=8.4)
        style_cell_text(cells[1], size=8.4)


def add_price_table(doc: Document) -> None:
    headers = ("Block", "Supply (EXW)")
    widths = (12.0, 4.5)
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_column_widths(table, widths)
    for idx, value in enumerate(headers):
        cell = table.rows[0].cells[idx]
        cell.text = value
        set_cell_width(cell, widths[idx])
        set_cell_shading(cell, DARK)
        set_cell_border(cell, WHITE)
        set_cell_margins(cell)
        style_cell_text(cell, bold=True, color=WHITE, size=8.1)
    set_repeat_table_header(table.rows[0])

    for row_index, block in enumerate(PRODUCT_BLOCKS):
        cells = table.add_row().cells
        values = (f"{block.code}. {block.name}", format_eur(block.supply_price))
        for idx, value in enumerate(values):
            cells[idx].text = value
            set_cell_width(cells[idx], widths[idx])
            set_cell_border(cells[idx])
            set_cell_margins(cells[idx])
            if row_index % 2:
                set_cell_shading(cells[idx], VERY_LIGHT_GREY)
            style_cell_text(
                cells[idx],
                bold=idx == 0,
                size=8.0,
                align=WD_ALIGN_PARAGRAPH.RIGHT if idx else WD_ALIGN_PARAGRAPH.LEFT,
            )

    supply_total = sum((block.supply_price for block in PRODUCT_BLOCKS), Decimal("0"))
    cells = table.add_row().cells
    values = ("TOTAL EQUIPMENT SUPPLY", format_eur(supply_total))
    for idx, value in enumerate(values):
        cells[idx].text = value
        set_cell_width(cells[idx], widths[idx])
        set_cell_shading(cells[idx], ORANGE)
        set_cell_border(cells[idx], WHITE)
        set_cell_margins(cells[idx], top=120, bottom=120)
        style_cell_text(
            cells[idx],
            bold=True,
            color=WHITE,
            size=8.4,
            align=WD_ALIGN_PARAGRAPH.RIGHT if idx else WD_ALIGN_PARAGRAPH.LEFT,
        )


def add_installation_table(doc: Document) -> None:
    headers = (
        "Ref.",
        "Service package",
        "Days",
        "Tech.",
        "Labour",
        "Associated costs",
        "Subtotal",
    )
    widths = (1.1, 6.1, 1.2, 1.2, 2.3, 2.6, 2.3)
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_column_widths(table, widths)
    for idx, value in enumerate(headers):
        cell = table.rows[0].cells[idx]
        cell.text = value
        set_cell_width(cell, widths[idx])
        set_cell_shading(cell, DARK)
        set_cell_border(cell, WHITE)
        set_cell_margins(cell, start=70, end=70)
        style_cell_text(cell, bold=True, color=WHITE, size=7.5)
    set_repeat_table_header(table.rows[0])

    for row_index, (ref, name, days, technicians, labour, associated) in enumerate(INSTALLATION_LINES):
        subtotal = labour + associated
        values = (
            ref,
            name,
            str(days),
            str(technicians),
            format_eur(labour),
            format_eur(associated),
            format_eur(subtotal),
        )
        cells = table.add_row().cells
        for idx, value in enumerate(values):
            cells[idx].text = value
            set_cell_width(cells[idx], widths[idx])
            set_cell_border(cells[idx])
            set_cell_margins(cells[idx], start=70, end=70)
            if row_index % 2:
                set_cell_shading(cells[idx], VERY_LIGHT_GREY)
            style_cell_text(
                cells[idx],
                bold=idx in (0, 6),
                size=7.4,
                align=WD_ALIGN_PARAGRAPH.RIGHT if idx >= 2 else WD_ALIGN_PARAGRAPH.LEFT,
            )

    total = sum((line[4] + line[5] for line in INSTALLATION_LINES), Decimal("0"))
    cells = table.add_row().cells
    cells[0].merge(cells[5])
    cells[0].text = "TOTAL INSTALLATION, COMMISSIONING, START-UP AND TRAINING"
    cells[6].text = format_eur(total)
    for idx, cell in enumerate(cells):
        set_cell_shading(cell, ORANGE)
        set_cell_border(cell, WHITE)
        set_cell_margins(cell)
        style_cell_text(
            cell,
            bold=True,
            color=WHITE,
            size=8.0,
            align=WD_ALIGN_PARAGRAPH.RIGHT if idx == 6 else WD_ALIGN_PARAGRAPH.LEFT,
        )


def add_kpi_table(doc: Document) -> None:
    rows = (
        ("Annual production", "56.4 M m", "63.6 M m", "+7.2 M m / +12.8%"),
        ("OEE", "80%", "88%", "+8 points"),
        ("Average delivery time", "128 s", "54 s", "-57.8%"),
        ("Starvation events", "1,260/year", "170/year", "-86.5%"),
        ("Corrugator downtime", "86 h/year", "21 h/year", "65 h saved"),
        ("Modelled operating impact", "-", "EUR 368,000/year", "Scenario output"),
    )
    headers = ("KPI", "Forklift logistics", "INGETRANS", "Modelled change")
    widths = (4.4, 3.8, 3.8, 4.5)
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_column_widths(table, widths)
    for idx, value in enumerate(headers):
        cell = table.rows[0].cells[idx]
        cell.text = value
        set_cell_width(cell, widths[idx])
        set_cell_shading(cell, DARK)
        set_cell_border(cell, WHITE)
        set_cell_margins(cell)
        style_cell_text(cell, bold=True, color=WHITE, size=8)
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for idx, value in enumerate(row):
            cells[idx].text = value
            set_cell_width(cells[idx], widths[idx])
            set_cell_border(cells[idx])
            set_cell_margins(cells[idx])
            if row_index % 2:
                set_cell_shading(cells[idx], VERY_LIGHT_GREY)
            style_cell_text(
                cells[idx],
                bold=idx in (0, 3),
                size=7.9,
                align=WD_ALIGN_PARAGRAPH.RIGHT if idx else WD_ALIGN_PARAGRAPH.LEFT,
            )


def add_picture(doc: Document, image: Path | None, caption: str, *, width=6.15) -> None:
    if image is None or not image.exists():
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    try:
        p.add_run().add_picture(str(image), width=Inches(width))
    except Exception:
        return
    cap = doc.add_paragraph(caption)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(5)
    for run in cap.runs:
        run.font.name = "Arial"
        run.font.size = Pt(7.5)
        run.font.italic = True
        run.font.color.rgb = RGBColor.from_string(MID_GREY)


@contextmanager
def extracted_reference_images():
    with TemporaryDirectory(prefix="paige-offer-media-") as temp:
        images: dict[str, Path] = {}
        if SOURCE_PAIGE_OFFER.exists():
            with ZipFile(SOURCE_PAIGE_OFFER) as archive:
                for name in (
                    "word/media/image6.jpeg",
                    "word/media/image12.jpeg",
                    "word/media/image13.png",
                    "word/media/image14.png",
                    "word/media/image15.png",
                    "word/media/image16.jpeg",
                    "word/media/image18.png",
                ):
                    try:
                        destination = Path(temp) / Path(name).name
                        destination.write_bytes(archive.read(name))
                        images[Path(name).name] = destination
                    except KeyError:
                        continue
        yield images


def add_cover(doc: Document, images: dict[str, Path]) -> None:
    doc.add_paragraph()
    if LOGO_PATH.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(LOGO_PATH), width=Inches(2.25))

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), DARK)
    p_pr.append(shd)
    r = p.add_run("\nINTEGRATED CORRUGATOR AREA\nAUTOMATION PROPOSAL\n")
    r.font.name = "Arial"
    r.font.size = Pt(25)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(WHITE)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(12)
    p_pr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), ORANGE)
    p_pr.append(shd)
    r = p.add_run("INGETRANS  |  REEL CONVEYORS  |  RFID  |  AMR SCRAP LOGISTICS")
    r.font.name = "Arial"
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(WHITE)

    add_picture(
        doc,
        images.get("image6.jpeg"),
        "INGECART integrated reel logistics platform - reference image",
        width=5.8,
    )

    info = doc.add_table(rows=5, cols=2)
    info.alignment = WD_TABLE_ALIGNMENT.CENTER
    info.autofit = False
    set_table_column_widths(info, (5.0, 11.5))
    rows = (
        ("Customer", CLIENT),
        ("Project", PROJECT),
        ("Proposal reference", PROPOSAL_REFERENCE),
        ("Date", PROPOSAL_DATE.strftime("%B %d, %Y")),
        ("Commercial basis", "EUR | Equipment EXW Barcelona, Spain"),
    )
    for row_index, (label, value) in enumerate(rows):
        left, right = info.rows[row_index].cells
        left.text = label
        right.text = value
        set_cell_width(left, 5.0)
        set_cell_width(right, 11.5)
        set_cell_shading(left, DARK)
        set_cell_shading(right, VERY_LIGHT_GREY)
        set_cell_border(left, WHITE)
        set_cell_border(right, WHITE)
        set_cell_margins(left)
        set_cell_margins(right)
        style_cell_text(left, bold=True, color=WHITE, size=8.5)
        style_cell_text(right, bold=row_index == 1, size=8.5)

def add_toc(doc: Document) -> None:
    heading = add_section_title(doc, "", "Contents")
    heading.paragraph_format.page_break_before = True
    p = doc.add_paragraph()
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), 'TOC \\o "1-3" \\h \\z \\u')
    field.set(qn("w:dirty"), "true")
    p._p.append(field)


def build_offer() -> Document:
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(1.7)
    section.bottom_margin = Cm(1.55)
    section.left_margin = Cm(2.1)
    section.right_margin = Cm(2.1)
    section.header_distance = Cm(0.65)
    section.footer_distance = Cm(0.65)
    section.start_type = WD_SECTION.NEW_PAGE

    configure_styles(doc)
    configure_header_footer(doc)

    with extracted_reference_images() as images:
        add_cover(doc, images)
        add_toc(doc)

        offer_heading = add_section_title(doc, "1", "Offer Letter")
        offer_heading.paragraph_format.page_break_before = True
        doc.add_paragraph("Dear Sterner Global Team,")
        doc.add_paragraph(
            "Following the PAIGE project development discussions, INGECART is pleased to submit "
            "this integrated proposal for the corrugator area. The proposed architecture combines "
            "automatic reel feeding and return, dedicated crawler chain conveyor tracks, an incoming "
            "reel conveyor line with RFID validation, and autonomous scrap intralogistics."
        )
        doc.add_paragraph(
            "The objective is to make reel supply, traceability and scrap removal part of the "
            "production system rather than independent manual logistics activities. The result is "
            "a controlled material flow designed to reduce forklift exposure, avoid corrugator "
            "starvation, improve inventory visibility and keep waste collection synchronized with "
            "production demand."
        )
        add_section_title(doc, "2", "Executive Summary")
        add_bullets(
            doc,
            [
                "Automatic delivery and return of paper reels between the exchange area and the corrugator consumption points.",
                "Ten dedicated crawler chain conveyor tracks for reel-stand loading and unloading.",
                "A 148 m crawler chain conveyor route from the train-platform reel reception area, with the RFID validation station included in the package price.",
                "One KUKA Master AMR for corrugator scrap logistics, eight customized mobile waste cages, one load-cell weighing station and two five-belt trident transfer conveyors for automated integration with the main belt-conveyor equipment.",
                "A common controls and interface philosophy connecting equipment status, reel identity, production demand, mission execution and exception handling.",
                "Site services split into transparent mechanical assembly, commissioning, start-up/training, rail installation, conveyor start-up and AMR turnkey installation blocks.",
            ],
        )
        add_callout(
            doc,
            "Design principle",
            "The solution protects the corrugator by preparing the correct reel before demand "
            "becomes urgent and by removing scrap before accumulation becomes a production constraint.",
            fill="E9F4EE",
        )

        add_section_title(doc, "3", "Integrated Operating Concept")
        add_two_column_table(
            doc,
            [
                ("1. Reel reception", "Reels arriving at the train platform are transferred onto the 148 m crawler chain conveyor route."),
                ("2. RFID validation", "The reel identity is read and validated; weighing, dimensional data and ERP/MES exchange are completed according to the approved interface specification."),
                ("3. Exchange buffer", "Validated reels are presented to the INGETRANS exchange position with destination and production requirement known."),
                ("4. Automatic delivery", "INGETRANS moves the selected reel to one of the ten reel-stand tracks and confirms transfer completion."),
                ("5. Partial reel return", "Unused or partially consumed reels are returned through the controlled route while preserving reel identity and remnant data."),
                ("6. Scrap collection", "The AMR exchanges mobile waste cages at corrugator collection points, weighs the load and transports it to the designated waste accumulation area."),
                ("7. Production data", "PLC, HMI, RFID/MES and AMR mission records provide the event history needed for traceability, alarms and operating KPIs."),
            ],
            headers=("Process stage", "Target operating logic"),
        )

        add_section_title(doc, "4", "Scope and Price Overview")
        add_price_table(doc)
        doc.add_paragraph(
            "The RFID validation station price is included in Block C and is not charged as a "
            "separate commercial line. Supply prices are EXW Barcelona, Spain. Site services and "
            "associated personnel expenses are presented separately in Section 10."
        )

        add_section_title(doc, "5", "Block A - INGETRANS Automatic Reel Loading System")
        add_picture(doc, images.get("image6.jpeg"), "INGETRANS automatic reel handling - reference configuration")
        doc.add_paragraph(
            "INGETRANS is a surface rail-guided system designed to automate reel transport, "
            "delivery and return between a controlled exchange point and the corrugator roll stands. "
            "The system removes routine forklift movements from the point-of-consumption area and "
            "coordinates physical reel handling with the production schedule."
        )
        doc.add_heading("5.1 Functional scope", level=2)
        add_bullets(
            doc,
            [
                "Automatic pickup of validated reels from the exchange position.",
                "Automatic delivery to the selected roll-stand track.",
                "Automatic return of unused or partially consumed reels.",
                "Fully automatic, semi-automatic and maintenance/manual operating modes.",
                "Destination management through the approved production-planning/MES interface.",
                "Central HMI, sequence control, alarms, diagnostics and movement history.",
                "Safety interlocks between transfer car, fixed tracks and protected operating zones.",
                "Factory testing of critical assemblies before shipment.",
            ],
        )
        doc.add_heading("5.2 INGETRANS operating areas and material-flow scheme", level=2)
        doc.add_paragraph(
            "The INGETRANS installation is organized as a coordinated set of functional areas. "
            "Each area has a defined transfer condition, physical interface and control handshake so "
            "that inbound reels, returned reels and corrugator demand cannot create conflicting movements."
        )
        add_two_column_table(
            doc,
            [
                (
                    "Inbound exchange area",
                    "Receives identified reels from the warehouse or the 148 m incoming conveyor, "
                    "positions them at the controlled handover point and confirms identity, destination "
                    "and readiness before INGETRANS collects the reel.",
                ),
                (
                    "Return exchange area",
                    "Receives unused or partially consumed reels from INGETRANS and transfers them to "
                    "the return conveyor or warehouse flow. Reel identity and remnant information are "
                    "preserved while inbound and return movements remain physically and logically separated.",
                ),
                (
                    "INGETRANS travel corridor",
                    "Runs parallel to the corrugator and covers every reel inlet and outlet lane. The "
                    "surface rail-guided carriage travels inside a protected operating envelope and "
                    "connects both exchange areas with all roll-stand transfer lanes.",
                ),
                (
                    "Roll-stand transfer lanes",
                    "Ten metallic crawler-chain conveyor lanes connect INGETRANS to the corrugator reel "
                    "stands. Each lane is based on an approximate 14 m length, subject to the final approved "
                    "layout, and supports controlled bidirectional delivery and return.",
                ),
            ],
            headers=("Functional area", "Function and interface"),
            widths=(5.2, 11.3),
        )
        add_callout(
            doc,
            "Material-flow scheme",
            "Inbound: warehouse / RFID conveyor -> inbound exchange -> INGETRANS corridor -> selected "
            "roll-stand lane. Return: roll stand -> INGETRANS corridor -> return exchange -> conveyor / warehouse.",
            fill="E9F4EE",
        )
        doc.add_heading("5.3 Technical basis", level=2)
        add_two_column_table(
            doc,
            [
                ("System type", "Surface rail-guided transfer carriage with dedicated fixed reel tracks."),
                ("Transfer speed", "Reference nominal value up to 80 m/min; final value subject to approved layout and safety zones."),
                ("Track speed", "Reference nominal value up to 59 m/min."),
                ("Acceleration/deceleration", "Reference ramp approximately 4.5 seconds."),
                ("Pickup/drop-off", "Reference transfer action approximately 6 seconds per interface."),
                ("Reel envelope", "Up to 1,500 mm diameter, up to 2,800 mm width/length and below 3,500 kg, subject to final approved reel matrix."),
                ("Controls", "Industrial PLC/HMI architecture, PROFINET/industrial communications and interface signals defined during engineering."),
                ("Safety", "Safety PLC functions, area scanners, interlocks, emergency stops and protected access according to the final risk assessment."),
            ],
            headers=("Parameter", "Proposal basis"),
        )
        doc.add_heading("5.4 Operational value", level=2)
        add_bullets(
            doc,
            [
                "Reduces forklift traffic and uncontrolled movement around the corrugator.",
                "Makes reel changes repeatable and measurable through request-to-delivery timestamps.",
                "Reduces search, waiting and late reel preparation during high-mix or short-run production.",
                "Preserves identity and return information for partially consumed reels.",
                "Provides a controlled link between production demand and physical material execution.",
            ],
        )
        doc.add_heading("5.5 Internal scenario benchmark", level=2)
        add_bullets(
            doc,
            [
                "The internal analysis is based on a high-mix production model with one corrugator, five roll stands and ten reel tracks, a line speed of 220 m/min, two shifts per day and 330 operating days per year. It assumes average consumption of 8.8 reels/hour, with reel changes every 5-12 minutes.",
                "Under these operating conditions, the modelled comparison between conventional forklift-based logistics and INGETRANS shows the potential production improvements summarized below.",
            ],
        )
        add_kpi_table(doc)
        add_callout(
            doc,
            "Qualification",
            "The KPI table is an internal digital-twin scenario for a high-mix plant. It is included "
            "to explain the value mechanism, not as a contractual PAIGE performance guarantee. "
            "PAIGE acceptance targets will be established from the approved layout, production data, "
            "reel matrix and FAT/SAT protocol.",
        )
        add_section_title(doc, "6", "Block B - Ten Crawler Chain Conveyor Tracks")
        add_picture(doc, images.get("image13.png"), "Crawler chain conveyor / reel feeding arrangement - reference drawing")
        doc.add_paragraph(
            "Ten metallic crawler chain conveyor tracks are included for loading and unloading "
            "paper reels at the corrugator reel stands. Final track lengths, elevations, interfaces "
            "and orientation will follow the approved PAIGE layout and roll-stand geometry."
        )
        doc.add_heading("6.1 Mechanical and performance basis", level=2)
        add_two_column_table(
            doc,
            [
                ("Quantity", "10 complete reel-stand conveyor tracks."),
                ("Conveyor principle", "Multiple V-shaped plate-chain sections with geared drive and heavy-duty steel support frame."),
                ("Plate-chain width", "Reference 250 mm."),
                ("Chain capacity", "Reference ultimate tensile load 170 kN; final structural verification by configured track."),
                ("Speed", "Up to 24 m/min, reversible, with frequency-converter speed regulation."),
                ("Chain material", "Stainless steel, heat treated according to supplier reference design."),
                ("Lubrication", "Reference gear oil ISO VG220."),
                ("Drive", "Industrial geared motor; final approved manufacturer according to detailed engineering."),
                ("Maintainability", "Draw-out bearing arrangement and accessible chain-tensioning/greasing points."),
                ("Impact/load design", "Reference design considers heavy corrugator cassette interaction up to 8 t; actual reel and cassette load cases require final engineering approval."),
            ],
            headers=("Parameter", "Technical description"),
        )
        doc.add_heading("6.2 Included functions", level=2)
        add_bullets(
            doc,
            [
                "Bidirectional reel transport between INGETRANS and each roll stand.",
                "Mechanical interfaces, supports, anchors and protective plates defined by the final layout.",
                "Drive assemblies, local sensors and control interface required for coordinated automatic transfer.",
                "Interlocks preventing transfer unless both INGETRANS and the destination track confirm readiness.",
                "Access points and maintenance provisions incorporated into the detailed design.",
            ],
        )
        add_callout(doc, "Block B price", f"Supply EXW: {format_eur(PRODUCT_BLOCKS[1].supply_price)}")

        add_section_title(doc, "7", "Block C - 148 m Incoming Reel Conveyor and RFID")
        add_picture(doc, images.get("image12.jpeg"), "RFID-enabled reel reception and validation concept - reference image")
        doc.add_paragraph(
            "This package receives reels from the train-platform unloading area and transports them "
            "through approximately 148 m of metallic crawler chain conveyor to the controlled reel "
            "exchange/validation area. The RFID validation station is commercially included in this "
            "block."
        )
        doc.add_heading("7.1 Conveyor scope", level=2)
        add_bullets(
            doc,
            [
                "Approximately 148 m total crawler chain conveyor route, subject to final measured layout.",
                "V-shaped plate-chain conveyor modules designed for cylindrical paper-reel handling.",
                "Reversible, frequency-controlled movement and zone-based sequence control.",
                "Heavy-duty support structure, floor protection and guarding according to the final arrangement.",
                "Reel separation, centering, transfer and return devices where required by the approved process.",
                "Electrical control, sensors and interface signals required to coordinate the line with RFID and INGETRANS.",
            ],
        )
        doc.add_heading("7.2 RFID validation and reel data management", level=2)
        add_picture(doc, images.get("image18.png"), "RFID, weighing and data-management arrangement - reference drawing")
        add_two_column_table(
            doc,
            [
                ("Automatic identification", "RFID reading at the defined validation and transfer positions without manual barcode scanning."),
                ("Dimensional validation", "Diameter and width detection according to the final selected hardware and approved reel envelope."),
                ("Weighing/remnant logic", "Integration of weighing information to update remaining reel quantity according to the agreed ERP/MES calculation method."),
                ("Data writing/labeling", "RFID/data update and label printing functions as defined during interface engineering."),
                ("Operator station", "Local HMI for validation status, exceptions, manual confirmation and diagnostics."),
                ("ERP/MES interface", "Exchange of reel master data, warehouse status, production demand, consumption and return events."),
                ("Traceability", "Event history from reception and validation through delivery, consumption and partial-reel return."),
            ],
            headers=("Function", "Included operating concept"),
        )
        add_section_title(doc, "8", "Block D - AMR Scrap Intralogistics")
        add_picture(doc, images.get("image16.jpeg") or images.get("image15.png"), "AMR intralogistics for corrugator waste cages - reference concept")
        doc.add_paragraph(
            "The corrugator scrap intralogistics package automates the exchange, transport and "
            "weighing of mobile waste cages. A KUKA Master AMR executes missions between corrugator "
            "collection points, the load-cell weighing station and the waste accumulation area."
        )
        doc.add_heading("8.1 Included equipment", level=2)
        add_bullets(
            doc,
            [
                "One (1) KUKA Master autonomous mobile robot configured for the approved waste-cage load.",
                "Eight (8) customized mobile waste cages with heavy-duty casters: two for Corrugator 1, two for Corrugator 2, two for splicer waste and two for the stacker area.",
                "One (1) load-cell weighing station with load sensors and data interface for material-weight transmission.",
                "Two (2) transfer conveyors, each with five motorized belt lines in trident configuration for automatic cage loading and unloading.",
                "Electrical/electronic interface between the trident conveyors, transfer stations and AMR mission control.",
                "Plant mapping, mission configuration, traffic rules, station handshakes, commissioning and production fine tuning.",
            ],
        )
        doc.add_heading("8.2 Operating sequence", level=2)
        add_two_column_table(
            doc,
            [
                ("Request", "A full-cage signal or operator/system request creates a transport mission."),
                ("Assignment", "Mission control checks AMR state, battery, route availability and priority."),
                ("Pickup", "The AMR aligns below the five-belt trident conveyor and lifts the cage vertically through the belt openings."),
                ("Weighing", "The loaded cage is delivered to the load-cell station and the measured weight is transmitted to the agreed data destination."),
                ("Disposal", "The cage is moved to the designated waste area."),
                ("Replenishment", "An empty cage is collected and returned to the requesting corrugator point."),
                ("Completion", "The station, cage and mission status are updated for traceability and the AMR becomes available."),
            ],
            headers=("Step", "Automatic logic"),
        )
        doc.add_heading("8.3 Technical improvements and future scalability", level=2)
        doc.add_paragraph(
            "The AMR system converts scrap removal from an operator-dependent transport activity into "
            "an event-driven intralogistics process. Full-cage requests, mission priority, route status, "
            "battery condition, station readiness and weighing results are managed as traceable events. "
            "Repeatable docking and interlocked handshakes with the trident conveyors reduce manual handling, "
            "unplanned waiting and the risk of scrap accumulation affecting corrugator operation."
        )
        add_bullets(
            doc,
            [
                "Automatic mission dispatch decouples cage exchange from forklift and operator availability.",
                "Priority rules allow urgent corrugator requests to be executed before lower-priority transfers.",
                "Load-cell data creates a consistent waste record by source, mission and time period for production and sustainability KPIs.",
                "Fleet supervision provides alarms, mission history, blocked-route status, battery management and recovery information.",
                "Standardized docking and station handshakes make each transfer repeatable and verifiable.",
            ],
        )
        doc.add_paragraph(
            "The same navigation map and mission-control architecture can be expanded in phases. Subject "
            "to a capacity and safety study, additional AMRs, pickup stations and load interfaces can support "
            "parallel scrap missions and other plant logistics without replacing the initial control concept."
        )
        add_two_column_table(
            doc,
            [
                ("Additional scrap capacity", "Add AMRs, cages, charging capacity and collection stations to increase throughput and provide vehicle redundancy."),
                ("Tooling and maintenance", "Transport maintenance tools, change parts, consumables and prepared kits between workshops, stores and production areas."),
                ("Printing dies and plates", "Move printing dies, cutting tools, printing plates/cliches and dedicated carriers between storage, preparation and converting machines."),
                ("Production supplies", "Deliver approved pallets, cores, inks, adhesives, spare parts or other compatible materials using purpose-designed carriers or top modules."),
                ("Digital integration", "Extend WMS/MES work orders, priorities, material identity and completion records through the existing mission interface."),
            ],
            headers=("Expansion path", "Future operating concept"),
        )
        add_callout(
            doc,
            "Scalability principle",
            "Every new mission must be validated for payload, load geometry, center of gravity, carrier "
            "interface, route width, pedestrian interaction, docking tolerance, charging demand and fleet capacity.",
            fill="E9F4EE",
        )
        doc.add_heading("8.4 Engineering qualification", level=2)
        add_bullets(
            doc,
            [
                "Fleet capacity is subject to validation of mission rate, route distance, pickup/drop time, charging strategy and production peaks.",
                "Cage mass, center of gravity, wheel geometry, floor condition and trident tolerances must be approved before final manufacture.",
                "Safety zoning, speed fields, pedestrian crossings and recovery modes are finalized through the application risk assessment.",
            ],
        )
        add_callout(doc, "Block D price", f"Supply: {format_eur(PRODUCT_BLOCKS[3].supply_price)}")

        add_section_title(doc, "9", "Controls, Integration and Safety")
        doc.add_heading("9.1 Control architecture", level=2)
        add_two_column_table(
            doc,
            [
                ("ERP / production planning", "Order, reel master data, production sequence and demand."),
                ("MES / reel management", "Reel identity, inventory state, consumption, remnant and production status."),
                ("INGECART orchestration", "Reel movement requests, destination reservation, sequencing, exceptions and event history."),
                ("INGETRANS PLC", "Transfer-car movement, fixed-track handshakes, interlocks and local diagnostics."),
                ("RFID and conveyor PLC", "Reception, validation, zone control, weighing and data confirmation."),
                ("AMR mission control", "Mission assignment, navigation, station handshakes, battery and route status."),
                ("Equipment layer", "Sensors, drives, safety devices, trident conveyors, scales and operator stations."),
            ],
            headers=("Layer", "Responsibility"),
        )
        doc.add_heading("9.2 Minimum interface principles", level=2)
        add_bullets(
            doc,
            [
                "No reel or cage is released until the destination confirms capacity and readiness.",
                "Identity, destination and transfer completion are confirmed at each automatic handoff.",
                "Safety functions remain in the local certified control layer; business systems do not bypass safety interlocks.",
                "Loss of communication produces a controlled stop or approved degraded mode without losing logical inventory.",
                "All external protocols, tag structures, I/O lists and cybersecurity requirements are frozen in the Functional Design Specification.",
            ],
        )
        doc.add_heading("9.3 Safety basis", level=2)
        add_bullets(
            doc,
            [
                "Application-level risk assessment covering reel movement, transfer points, AMR traffic and maintenance access.",
                "Emergency stops, guarded areas, safety scanners, access interlocks and safe-speed zones as required by the final design.",
                "Validation of reel/cage mass, center of gravity, overhang, floor flatness and traction conditions.",
                "Lockout/tagout, manual recovery and rescue procedures supplied before SAT.",
                "Final regulatory marking and documentation according to the contractually agreed destination requirements.",
            ],
        )

        add_section_title(doc, "10", "Installation, Commissioning and Training")
        add_installation_table(doc)
        doc.add_paragraph(
            "Associated costs include the hotel, flights, local transport and subsistence amounts "
            "listed in the approved scope basis. Durations are working-day estimates and assume "
            "continuous access to a ready site, required lifting equipment and timely customer support."
        )
        doc.add_heading("10.1 Service deliverables", level=2)
        add_bullets(
            doc,
            [
                "Mechanical supervision/assembly according to the responsibility matrix.",
                "Cold commissioning, I/O checks and station handshake verification.",
                "Software start-up, sequence tuning and production-mode testing.",
                "RFID/MES interface support within the agreed protocol and data scope.",
                "AMR mapping, route and station setup under actual plant conditions.",
                "Operator and maintenance training for normal operation, alarms and recovery.",
                "SAT support and closure of agreed punch-list items.",
            ],
        )

        add_section_title(doc, "11", "Project Execution and Acceptance")
        add_two_column_table(
            doc,
            [
                ("1. Kick-off and data freeze", "Approved layout, reel matrix, utility data, interfaces, site constraints and responsibility matrix."),
                ("2. Detailed engineering", "Mechanical/electrical design, safety concept, control narrative, I/O and ERP/MES interface specification."),
                ("3. Design review", "Customer approval of the Functional Design Specification and manufacturing-release package."),
                ("4. Manufacturing and integration", "Fabrication, purchased equipment, software development and internal integration."),
                ("5. FAT", "Functional tests, safety/interlock tests, simulated interface tests and documented punch list."),
                ("6. Shipment and site readiness", "Customer confirms foundations, utilities, access, lifting resources and production window."),
                ("7. Installation and commissioning", "Mechanical/electrical work, cold commissioning and live production start-up."),
                ("8. SAT and handover", "Performance verification against the agreed acceptance matrix, training and documentation handover."),
            ],
            headers=("Gate", "Required outcome"),
        )
        doc.add_heading("11.1 Acceptance KPIs to be agreed during engineering", level=2)
        add_bullets(
            doc,
            [
                "INGETRANS request-to-delivery P50/P95 and transfer success without intervention.",
                "Reel identity and destination accuracy.",
                "RFID read/write success rate and inventory reconciliation.",
                "Conveyor zone transfer and fault-recovery performance.",
                "AMR mission cycle, station docking success and cage-weight data transfer.",
                "Automatic-mode availability during the agreed SAT observation window.",
                "Safe stop, communication-loss and approved degraded-mode recovery tests.",
            ],
        )

        add_section_title(doc, "12", "Commercial Conditions")
        add_two_column_table(
            doc,
            [
                ("Currency", "Euro (EUR)."),
                ("Equipment Incoterm", "EXW Barcelona, Spain (Incoterms 2020), unless amended in the final order."),
                (
                    "Payment",
                    "30% by bank transfer with the purchase order; 20% by bank transfer ten weeks after "
                    "the purchase order; 40% by bank transfer upon notification that the goods are ready "
                    "for collection at INGECART's workshops; 10% by bank transfer at commissioning, and "
                    "no later than 90 days from the Certificate of Loading / check-in.",
                ),
                ("Delivery", "Target equipment readiness: eight (8) months from receipt of down payment, approved technical data and design freeze. Final date confirmed after kick-off and supplier scheduling."),
                ("Validity", "30 calendar days from proposal date, subject to material and supplier price availability."),
                ("Warranty", "12 months from commissioning or 12 months from delivery under the agreed Incoterm, whichever occurs first."),
                ("Retention of title", "Equipment remains property of INGECART until full payment has been received."),
            ],
            headers=("Commercial item", "Condition"),
        )
        doc.add_heading("12.1 Price inclusions", level=2)
        add_bullets(
            doc,
            [
                "Equipment and functions specifically described in Blocks A-D.",
                "Engineering required to complete the described scope.",
                "Control software use license for the supplied equipment.",
                "Installation, commissioning, start-up and training services priced in Section 10.",
                "Associated personnel travel/accommodation costs explicitly priced in Section 10.",
                "Standard technical documentation, operating instructions and agreed FAT/SAT records.",
            ],
        )
        doc.add_heading("12.2 Exclusions", level=2)
        add_bullets(
            doc,
            [
                "Any work, equipment or material not expressly described in this proposal.",
                "Transport from the EXW delivery point, export packaging unless specifically agreed, cargo insurance, duties, taxes and customs clearance.",
                "Civil works, foundations, embedded plates, trenches, floor repair, structural reinforcement and building modifications.",
                "Site power distribution, field cabling outside supplied equipment, compressed air, network infrastructure and other plant utilities unless expressly included.",
                "Cranes, forklifts, lifting platforms, rigging equipment, unloading and internal transport at site.",
                "Customer ERP/MES licenses, servers, client computers, database work or third-party software changes not specifically included.",
                "RFID consumable tags beyond the agreed commissioning quantity and printer consumables.",
                "Production losses, overtime, weekend/night work or additional days caused by customer request, site delay or unavailable production windows.",
                "Additional AMR redundancy. The priced system contains one AMR and requires the agreed fallback procedure.",
                "Performance guarantees not explicitly written into the final FAT/SAT acceptance matrix.",
            ],
        )
        doc.add_heading("12.3 Customer responsibilities", level=2)
        add_bullets(
            doc,
            [
                "Provide accurate as-built layouts, reel/cage data and operating requirements.",
                "Provide prepared foundations/floors, utilities, network, safe site access and lifting resources on schedule.",
                "Provide ERP/MES interface documentation, test environment and responsible IT/OT contacts.",
                "Provide mechanical/electrical maintenance support during installation and start-up.",
                "Provide representative products, production plans and operators for FAT/SAT and training.",
                "Maintain insurance for equipment from transfer of risk under the agreed Incoterm.",
            ],
        )

        add_section_title(doc, "13", "Warranty and General Sales Conditions")
        general_conditions = [
            ("Scope and precedence", "The signed proposal and purchase order accepted by INGECART define the contract. Customer purchasing conditions apply only when expressly accepted in writing by INGECART."),
            ("Engineering and intellectual property", "All designs, drawings, software, source code, bills of material and know-how remain INGECART property. The customer receives the operating license required for the supplied equipment."),
            ("Changes", "Any change to layout, interfaces, product data, schedule or responsibility after design freeze may change price and delivery."),
            ("Warranty coverage", "Manufacturing and material defects preventing normal operation of the new supplied equipment, subject to correct use and maintenance."),
            ("Warranty exclusions", "Wear parts, routine adjustments, misuse, insufficient maintenance, unauthorized modification, incorrect utilities and damage caused by external equipment or force majeure."),
            ("Warranty execution", "Repair or replacement is at INGECART's discretion. Freight, duties, local labor and personnel travel are excluded unless expressly agreed."),
            ("Liability", "INGECART is not liable for indirect or consequential loss, lost production, lost profit or third-party claims. Aggregate liability is limited to the contract amount paid, except where prohibited by applicable law."),
            ("Force majeure", "Delivery is extended for events outside reasonable control, including material/electronic shortages, transport interruption, regulatory restrictions, strikes, war, epidemic or natural disaster."),
            ("Governing law", "Spanish law. Exclusive jurisdiction of the courts of Barcelona, Spain, unless amended by a mutually signed contract."),
        ]
        add_two_column_table(doc, general_conditions, headers=("Clause", "Condition"))

        doc.add_page_break()
        add_section_title(doc, "14", "Offer Acceptance")
        doc.add_paragraph(
            "Acceptance of this proposal authorizes INGECART to begin project kick-off, data "
            "collection and detailed engineering subject to receipt of the agreed down payment."
        )
        table = doc.add_table(rows=6, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        set_table_column_widths(table, (8.25, 8.25))
        acceptance_rows = (
            ("For INGECART S.L.", "For Sterner Global"),
            ("Name: Diego Garcia", "Name:"),
            ("Title:", "Title:"),
            ("Signature:", "Signature:"),
            ("Date:", "Date:"),
            ("Proposal reference:", PROPOSAL_REFERENCE),
        )
        for row_index, values in enumerate(acceptance_rows):
            for col_index, value in enumerate(values):
                cell = table.rows[row_index].cells[col_index]
                cell.text = value
                set_cell_width(cell, 8.25)
                set_cell_margins(cell, top=140, bottom=140)
                set_cell_border(cell)
                if row_index == 0:
                    set_cell_shading(cell, DARK)
                    style_cell_text(cell, bold=True, color=WHITE, size=9)
                else:
                    style_cell_text(cell, size=8.7)

        doc.add_paragraph()
        p = doc.add_paragraph("INGECART S.L. | C/ Aldaravi 9-10, 08739 Subirats, Barcelona, Spain | sales@ingecart.es")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.name = "Arial"
            run.font.size = Pt(7.5)
            run.font.color.rgb = RGBColor.from_string(MID_GREY)

    doc.core_properties.title = "PAIGE Corrugator Area Integrated Automation Proposal"
    doc.core_properties.subject = "INGETRANS, reel conveyors, RFID and AMR scrap logistics"
    doc.core_properties.author = "INGECART S.L."
    doc.core_properties.keywords = "PAIGE, Sterner Global, INGETRANS, RFID, AMR, corrugator"
    return doc


def validate_financials() -> None:
    supply = sum((block.supply_price for block in PRODUCT_BLOCKS), Decimal("0"))
    installation = sum((block.installation_price for block in PRODUCT_BLOCKS), Decimal("0"))
    installation_detail = sum((line[4] + line[5] for line in INSTALLATION_LINES), Decimal("0"))
    total = supply + installation
    assert supply == Decimal("1985034.30")
    assert installation == Decimal("378464.69")
    assert installation_detail == installation
    assert total == Decimal("2363498.99")


def main() -> None:
    validate_financials()
    document = build_offer()
    document.save(OUTPUT_PATH)
    print(f"Generated: {OUTPUT_PATH}")
    print(f"Supply subtotal: {format_eur(Decimal('1985034.30'))}")
    print(f"Installation subtotal: {format_eur(Decimal('378464.69'))}")
    print(f"Grand total: {format_eur(Decimal('2363498.99'))}")


if __name__ == "__main__":
    main()

"""Generate the PAIGE corrugator-area executive summary (English) for Victor Pinto.

Content and figures are taken from the approved proposal
"PAIGE_CORRUGATOR_AREA_INGECART_PROPOSAL_2026-08-26 re2.docx" and from the
corrected installation pricing workbook "PRECIOS INSTALACIION.xlsx".
The source proposal is never modified.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


PAIGE_DIR = Path(
    r"C:\Users\Inaki Senar\Documents\INGECART\COMMERCIAL\PROYECTOS\Sterner Global\Paige"
)
OUTPUT_PATH = PAIGE_DIR / "PAIGE_EXECUTIVE_SUMMARY_VICTOR_PINTO_EN.docx"
LOGO_PATH = Path(r"C:\Users\Inaki Senar\Documents\INGECART\MARKETING\LOGOS\FULLOB.png")

CLIENT = "Sterner Global"
PROJECT = "PAIGE Project - Corrugator Area"
PROPOSAL_REFERENCE = "PAIGE-CORR-2026-08-R1"
ATTENTION = "Victor Pinto - Project Director"
SUMMARY_DATE = date(2026, 9, 3)

ORANGE = "F36B21"
DARK = "171717"
MID_GREY = "5C5C5C"
VERY_LIGHT_GREY = "F7F7F7"
WHITE = "FFFFFF"

EQUIPMENT_LINES = (
    ("A", "INGETRANS automatic reel loading and return system", Decimal("869396.91")),
    ("B", "Motorized tracks for reel stands - 10 units", Decimal("222941.00")),
    ("C", "Crawler chain conveyor tracks for reel stands - 10 units", Decimal("380490.00")),
    ("D", "148 m incoming reel conveyor line + weighing / RFID station", Decimal("652610.00")),
    ("E", "Corrugator scrap and cliche intralogistics package with KUKA AMR", Decimal("315035.00")),
)
EQUIPMENT_TOTAL = Decimal("2058982.91")

SERVICE_LINES = (
    ("A1", "INGETRANS & auxiliary equipment - mechanical assembly", 24, 4, Decimal("95040.00"), Decimal("15779.63")),
    ("A2", "INGETRANS & auxiliary equipment - commissioning", 14, 2, Decimal("27720.00"), Decimal("8210.91")),
    ("A3", "INGETRANS & auxiliary equipment - start-up and training", 20, 2, Decimal("39600.00"), Decimal("10405.66")),
    ("B1", "Tracks - connection and commissioning", 6, 2, Decimal("11880.00"), Decimal("5289.65")),
    ("C1", "Train unloading conveyor - installation and start-up", 25, 3, Decimal("74250.00"), Decimal("11508.06")),
    ("D1", "AMR intralogistics - turnkey installation", 25, 3, Decimal("74250.00"), Decimal("11509.13")),
)
SERVICE_LABOUR_TOTAL = Decimal("322740.00")
SERVICE_ASSOCIATED_TOTAL = Decimal("62703.04")
SERVICE_TOTAL = Decimal("385443.04")
DAY_RATE = Decimal("990.00")


def format_eur(value: Decimal) -> str:
    amount = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
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
    tc_pr = cell._tc.get_or_add_tcPr()
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


def set_table_column_widths(table, widths_cm: tuple[float, ...]) -> None:
    for grid_column, width_cm in zip(table._tbl.tblGrid.gridCol_lst, widths_cm):
        grid_column.set(qn("w:w"), str(Cm(width_cm).twips))
    for row in table.rows:
        for cell, width_cm in zip(row.cells, widths_cm):
            cell.width = Cm(width_cm)


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

    for name, size, color in (("Heading 1", 16, ORANGE), ("Heading 2", 11.5, DARK)):
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
    paragraph._p.append(field)
    sep = paragraph.add_run(" / ")
    sep.font.name = "Arial"
    sep.font.size = Pt(7)
    total = OxmlElement("w:fldSimple")
    total.set(qn("w:instr"), "NUMPAGES")
    paragraph._p.append(total)


def configure_header_footer(doc: Document) -> None:
    section = doc.sections[0]
    header_table = section.header.add_table(rows=1, cols=2, width=Inches(6.7))
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_table.autofit = False
    set_table_column_widths(header_table, (11.0, 6.0))
    if LOGO_PATH.exists():
        header_table.cell(0, 0).paragraphs[0].add_run().add_picture(str(LOGO_PATH), width=Inches(1.05))
    right = header_table.cell(0, 1)
    right.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = right.paragraphs[0].add_run(PROPOSAL_REFERENCE)
    run.font.name = "Arial"
    run.font.size = Pt(7)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string(MID_GREY)

    footer_table = section.footer.add_table(rows=1, cols=2, width=Inches(6.7))
    footer_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    footer_table.autofit = False
    set_table_column_widths(footer_table, (12.0, 5.0))
    left = footer_table.cell(0, 0)
    left.paragraphs[0].add_run(f"CONFIDENTIAL | {CLIENT} | {PROJECT}")
    style_cell_text(left, color=MID_GREY, size=7)
    right = footer_table.cell(0, 1)
    right.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_page_field(right.paragraphs[0])


def add_section_title(doc: Document, number: str, title: str):
    p = doc.add_paragraph(style="Heading 1")
    p.paragraph_format.space_before = Pt(12)
    p.add_run(f"{number}  {title.upper()}".strip())
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


def add_bullets(doc: Document, items) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent = Cm(0.55)
        p.paragraph_format.first_line_indent = Cm(-0.25)
        p.paragraph_format.space_after = Pt(2.5)
        p.add_run(item)


def add_callout(doc: Document, title: str, body: str, *, fill="FFF1E7", border=ORANGE) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_column_widths(table, (16.5,))
    cell = table.cell(0, 0)
    set_cell_shading(cell, fill)
    set_cell_border(cell, border, "8")
    set_cell_margins(cell, top=130, bottom=130, start=160, end=160)
    run = cell.paragraphs[0].add_run(title.upper())
    run.font.name = "Arial"
    run.font.size = Pt(9)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string(border)
    p = cell.add_paragraph(body)
    p.paragraph_format.space_after = Pt(0)
    for r in p.runs:
        r.font.name = "Arial"
        r.font.size = Pt(9)


def add_grid_table(doc: Document, headers, rows, widths, *, highlight_last=False, numeric_from=1) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_column_widths(table, widths)
    for idx, value in enumerate(headers):
        cell = table.rows[0].cells[idx]
        cell.text = value
        set_cell_shading(cell, DARK)
        set_cell_border(cell, WHITE)
        set_cell_margins(cell, start=70, end=70)
        style_cell_text(cell, bold=True, color=WHITE, size=7.8)
    set_repeat_table_header(table.rows[0])

    last_index = len(rows) - 1
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        is_total = highlight_last and row_index == last_index
        for idx, value in enumerate(values):
            cells[idx].text = value
            set_cell_border(cells[idx], WHITE if is_total else "D0D0D0")
            set_cell_margins(cells[idx], start=70, end=70)
            if is_total:
                set_cell_shading(cells[idx], ORANGE)
            elif row_index % 2:
                set_cell_shading(cells[idx], VERY_LIGHT_GREY)
            style_cell_text(
                cells[idx],
                bold=is_total or idx == 0,
                color=WHITE if is_total else DARK,
                size=8.0,
                align=WD_ALIGN_PARAGRAPH.RIGHT if idx >= numeric_from else WD_ALIGN_PARAGRAPH.LEFT,
            )


def add_cover(doc: Document) -> None:
    if LOGO_PATH.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(LOGO_PATH), width=Inches(2.1))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(0)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), DARK)
    p._p.get_or_add_pPr().append(shd)
    run = p.add_run("\nEXECUTIVE SUMMARY\nCORRUGATOR AREA AUTOMATION\n")
    run.font.name = "Arial"
    run.font.size = Pt(23)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string(WHITE)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), ORANGE)
    p._p.get_or_add_pPr().append(shd)
    run = p.add_run("INGETRANS  |  REEL CONVEYORS  |  RFID  |  AMR SCRAP LOGISTICS")
    run.font.name = "Arial"
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string(WHITE)

    info = doc.add_table(rows=6, cols=2)
    info.alignment = WD_TABLE_ALIGNMENT.CENTER
    info.autofit = False
    set_table_column_widths(info, (5.0, 11.5))
    rows = (
        ("Customer", CLIENT),
        ("Attention", ATTENTION),
        ("Project", PROJECT),
        ("Proposal reference", PROPOSAL_REFERENCE),
        ("Summary date", SUMMARY_DATE.strftime("%B %d, %Y")),
        ("Commercial basis", "EUR | Equipment EXW Barcelona, Spain"),
    )
    for row_index, (label, value) in enumerate(rows):
        left, right = info.rows[row_index].cells
        left.text = label
        right.text = value
        set_cell_shading(left, DARK)
        set_cell_shading(right, VERY_LIGHT_GREY)
        set_cell_border(left, WHITE)
        set_cell_border(right, WHITE)
        set_cell_margins(left)
        set_cell_margins(right)
        style_cell_text(left, bold=True, color=WHITE, size=8.5)
        style_cell_text(right, bold=row_index in (1, 2), size=8.5)


def build() -> Document:
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

    configure_styles(doc)
    configure_header_footer(doc)
    add_cover(doc)

    # 1 Purpose
    heading = add_section_title(doc, "1", "Purpose of this summary")
    heading.paragraph_format.page_break_before = True
    doc.add_paragraph(
        "This document summarizes, block by block, the INGECART proposal for the PAIGE corrugator "
        "area. It is intended for project-management review and decision preparation, and it keeps "
        "the same technical basis, scope and commercial figures as proposal "
        f"{PROPOSAL_REFERENCE}. Full technical detail remains in the complete proposal."
    )
    add_callout(
        doc,
        "Project statement in one sentence",
        "Reel supply, reel identity and scrap removal become part of the production system instead "
        "of independent manual logistics activities, so the corrugator is protected from starvation, "
        "forklift dependency and uncontrolled waste accumulation.",
        fill="E9F4EE",
        border="2E7D5B",
    )

    # 2 Value logic
    add_section_title(doc, "2", "Value logic")
    add_bullets(
        doc,
        [
            "Availability: reels are prepared and delivered before demand becomes urgent, and scrap is removed before accumulation constrains production.",
            "Traceability: each reel is weighed, measured and digitally registered at plant entry, creating a reliable data foundation for inventory and consumption.",
            "Safety and traffic: routine forklift movements are removed from the point-of-consumption area and replaced by interlocked, guided transfers.",
            "Scalability: the same navigation map, control concept and interface philosophy can be extended in phases without replacing the initial architecture.",
            "Transparency: supply and site services are quoted as separate, auditable blocks with day, technician and cost detail.",
        ],
    )

    # 3 Block summaries
    add_section_title(doc, "3", "Executive summary by block")

    doc.add_heading("Block A - INGETRANS automatic reel loading and return system", level=2)
    doc.add_paragraph(
        "Surface rail-guided system that automates reel transport, delivery and return between the "
        "controlled exchange point and the corrugator roll stands, coordinated with the production "
        "schedule through the approved planning/MES interface."
    )
    add_bullets(
        doc,
        [
            "Automatic pickup of validated reels, delivery to the selected roll-stand track and return of partially consumed reels with identity and remnant data preserved.",
            "Automatic, semi-automatic and maintenance modes, central HMI, sequence control, alarms, diagnostics and movement history.",
            "Safety interlocks between transfer car, fixed tracks and protected zones; factory testing of critical assemblies before shipment.",
            "Executive value: repeatable and measurable reel changes, less search and waiting time in high-mix production, and a controlled link between demand and physical execution.",
        ],
    )
    doc.add_paragraph(
        "Internal digital-twin benchmark (one corrugator, five roll stands, ten tracks, 220 m/min, "
        "two shifts, 330 days) models +12.8% annual production, OEE from 80% to 88%, delivery time "
        "from 128 s to 54 s, starvation events -86.5% and 65 h/year of downtime saved. These figures "
        "are a scenario output to explain the value mechanism, not a contractual guarantee."
    )

    doc.add_heading("Block B - Ten motorized in-floor tracks (16 m)", level=2)
    add_bullets(
        doc,
        [
            "Ten flush-to-floor conveyor sections of 16 m, configured for five roll stands with two independent tracks per stand (active feeding plus prepared standby).",
            "Structural capacity up to 4,500 kg per trolley/track section; embedded steel channel framework with non-slip checker-plate covers.",
            "In-floor motorized drag chain in high-tensile case-hardened alloy steel with heavy-duty low-friction wear strips.",
            "Ten ultra-low-profile trolleys with 130-degree V cradle for passive gravity self-centering (reel diameters 500-1,600 mm) and ten independent gearmotors.",
        ],
    )

    doc.add_heading("Block C - Ten metallic crawler chain conveyor tracks (16 m)", level=2)
    add_bullets(
        doc,
        [
            "Alternative track configuration for loading and unloading reels at the corrugator reel stands, with lengths, elevations and orientation following the approved PAIGE layout.",
            "Bidirectional transport between INGETRANS and each roll stand, with drives, local sensors and the control interface required for coordinated automatic transfer.",
            "Interlocks that block any transfer unless both INGETRANS and the destination track confirm readiness.",
            "Mechanical interfaces, supports, anchors, protective plates, access points and maintenance provisions integrated in the detailed design.",
        ],
    )

    doc.add_heading("Block D - 148 m incoming reel conveyor and weighing/RFID station", level=2)
    add_bullets(
        doc,
        [
            "Approximately 148 m of V-shaped plate-chain conveyor from the train-platform unloading area to the controlled reel exchange and validation area, with four reel feeding platforms.",
            "Reversible frequency-controlled movement up to 24 m/min, zone-based sequence control, heavy-duty structure, floor protection and guarding.",
            "Weighing and data-acquisition station at the end of the line: automatic weighing (0.5 kg sensor accuracy, reels up to 5 t), dimensional measurement, printing unit, RFID scanner and industrial software creating the digital reel record.",
            "RFID-ready and Industry 4.0-ready architecture prepared for future real-time location, remnant management, consumption analytics and MES/ERP/WMS exchange.",
        ],
    )
    add_callout(
        doc,
        "Scope qualification",
        "Data management, MES/ERP/WMS integration and warehouse-management functionality are outside "
        "the current scope of supply. The technology is configured and enabled for future customer use.",
    )

    doc.add_heading("Block E - AMR scrap and cliche intralogistics", level=2)
    add_bullets(
        doc,
        [
            "Two KUKA Master AMRs configured for the approved waste-cage load and cliche management.",
            "Eight customized mobile waste cages (two per corrugator, two for splicer waste, two for the stacker area), one load-cell weighing station and two five-belt trident transfer conveyors.",
            "Event-driven missions: full-cage requests, priority rules, route status, battery condition, station readiness and weighing results are managed as traceable events.",
            "Load-cell data builds a consistent waste record by source, mission and period, supporting production and sustainability KPIs.",
            "Phased scalability: additional AMRs, pickup stations and load interfaces can be added on the same map and mission-control architecture, subject to capacity and safety study.",
        ],
    )

    doc.add_heading("Controls, integration and safety", level=2)
    add_bullets(
        doc,
        [
            "No reel or cage is released until the destination confirms capacity and readiness; identity, destination and completion are confirmed at every automatic handoff.",
            "Safety functions stay in the local certified control layer; business systems never bypass safety interlocks.",
            "Communication loss produces a controlled stop or approved degraded mode without losing logical inventory.",
            "Protocols, tag structures, I/O lists and cybersecurity requirements are frozen in the Functional Design Specification.",
            "Application-level risk assessment, emergency stops, guarded areas, scanners, safe-speed zones, LOTO and rescue procedures delivered before SAT.",
        ],
    )

    doc.add_heading("Installation, commissioning and training", level=2)
    add_bullets(
        doc,
        [
            "Mechanical supervision/assembly per responsibility matrix, cold commissioning, I/O checks and station handshake verification.",
            "Software start-up, sequence tuning, production-mode testing and RFID/MES interface support within the agreed data scope.",
            "AMR mapping, route and station setup under real plant conditions.",
            "Operator and maintenance training for normal operation, alarms and recovery, plus SAT support and punch-list closure.",
            "Associated costs cover hotel, flights, local transport and subsistence. Durations assume continuous access to a ready site, lifting equipment and timely customer support.",
        ],
    )

    # 4 Equipment price table
    heading = add_section_title(doc, "4", "Final equipment price table")
    heading.paragraph_format.page_break_before = True
    equipment_rows = [
        (f"{code}. {name}", format_eur(price)) for code, name, price in EQUIPMENT_LINES
    ]
    equipment_rows.append(
        ("TOTAL EQUIPMENT SUPPLY (considering motorized tracks for roll-stand feeding)", format_eur(EQUIPMENT_TOTAL))
    )
    add_grid_table(doc, ("Block", "Supply (EXW)"), equipment_rows, (12.0, 4.5), highlight_last=True)
    doc.add_paragraph(
        "Supply prices are EXW Barcelona, Spain. The RFID/weighing station is included in the 148 m "
        "conveyor package and is not charged as a separate commercial line. Blocks B and C are the "
        "two alternative track configurations for roll-stand feeding."
    )

    # 5 Services price table
    add_section_title(doc, "5", "Final installation and services price table")
    service_rows = []
    for ref, name, days, techs, labour, associated in SERVICE_LINES:
        service_rows.append(
            (
                ref,
                name,
                str(days),
                str(techs),
                format_eur(DAY_RATE),
                format_eur(labour),
                format_eur(associated),
                format_eur(labour + associated),
            )
        )
    total_days = sum(line[2] for line in SERVICE_LINES)
    total_techs = sum(line[3] for line in SERVICE_LINES)
    service_rows.append(
        (
            "TOTAL",
            "INSTALLATION, COMMISSIONING, START-UP AND TRAINING",
            str(total_days),
            str(total_techs),
            format_eur(DAY_RATE),
            format_eur(SERVICE_LABOUR_TOTAL),
            format_eur(SERVICE_ASSOCIATED_TOTAL),
            format_eur(SERVICE_TOTAL),
        )
    )
    add_grid_table(
        doc,
        ("Ref.", "Service package", "Days", "Tech.", "Day rate", "Labour", "Associated costs", "Subtotal"),
        service_rows,
        (1.0, 5.0, 1.0, 1.0, 1.9, 2.2, 2.2, 2.2),
        highlight_last=True,
        numeric_from=2,
    )
    doc.add_paragraph(
        "Labour is calculated at 990.00 EUR per technician-day. Associated costs include hotel, "
        "flights, local transport and subsistence. Days are working-day estimates and assume a ready "
        "site, available lifting equipment and customer mechanical/electrical support."
    )

    add_section_title(doc, "6", "Commercial headline")
    add_grid_table(
        doc,
        ("Concept", "Amount"),
        [
            ("Equipment supply (EXW Barcelona)", format_eur(EQUIPMENT_TOTAL)),
            ("Installation, commissioning, start-up and training", format_eur(SERVICE_TOTAL)),
            ("TOTAL PROJECT VALUE", format_eur(EQUIPMENT_TOTAL + SERVICE_TOTAL)),
        ],
        (12.0, 4.5),
        highlight_last=True,
    )
    doc.add_paragraph(
        "Payment: 30% with purchase order, 20% with completion of the engineering package, 45% on "
        "notification that goods are ready for collection, 5% at commissioning and no later than 90 "
        "days from the Certificate of Loading. Validity 30 calendar days. Warranty 12 months from "
        "commissioning or delivery, whichever occurs first."
    )

    doc.add_paragraph()
    footer = doc.add_paragraph("INGECART S.L. | C/ Aldaravi 9-10, 08739 Subirats, Barcelona, Spain | sales@ingecart.es")
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in footer.runs:
        run.font.size = Pt(7.5)
        run.font.color.rgb = RGBColor.from_string(MID_GREY)

    return doc


def main() -> None:
    document = build()
    document.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

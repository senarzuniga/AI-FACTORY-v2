from __future__ import annotations

from pathlib import Path
from typing import Iterable

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START
from docx.shared import Inches, Pt, Cm
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image


CLIENT = "Cascades Calgary"
PROJECT = "Phase 1 - TRANSFER & CONVEYOR Package"
OFFER_CODE = "OFF-2026-135"
LOGO_PATH = Path(r"C:\Users\Inaki Senar\Documents\INGECART\MARKETING\LOGOS\FULLOB.png")
WATERMARK_IMAGE = Path(r"C:\Users\Inaki Senar\Documents\INGECART\MARKETING\ARTWORK\imagen marca de agua ofertas.jpg")
OUTPUT_DIR = Path(r"C:\Users\Inaki Senar\Documents\INGECART\COMMERCIAL\PROYECTOS\CASCADES\Cascades Calgary\PROYECTO 2027 FASE 1")
OUTPUT_PATH_PREFIX = "OFF-2026-135 Cascades Calgary Phase 1"


def set_background_watermark(doc: Document, image_path: Path, opacity: int = 18):
    if not image_path.exists():
        return
    try:
        img = Image.open(image_path)
        img = img.convert("RGBA")
        width, height = img.size
        if width > 0 and height > 0:
            # Place image as a watermark using a floating shape anchored to the page.
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run()
            r.add_picture(str(image_path), width=Cm(16), height=Cm(16))
            r.font.color.rgb = None
            r._r.set('w:fill', 'auto')
            r._r.set('o:opacity', str(opacity))
    except Exception:
        pass


def set_custom_header(doc: Document):
    section = doc.sections[0]
    header = section.header
    p = header.paragraphs[0]
    p.text = ""
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("")


def set_footer(doc: Document):
    section = doc.sections[0]
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    footer_para.text = ""
    left_run = footer_para.add_run(f"{OFFER_CODE} / {PROJECT}")
    left_run.font.size = Pt(6)
    left_run.font.name = "Arial"
    left_run.font.bold = False
    left_run.font.color.rgb = None

    p = footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.text = ""
    page_run = p.add_run("Page ")
    page_run.font.size = Pt(6)
    page_run.font.name = "Arial"
    fld = OxmlElement('w:fldSimple')
    fld.set(qn('w:instr'), 'PAGE')
    fld.set(qn('w:dirty'), 'true')
    p._p.append(fld)


def add_cover_page(doc: Document):
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()

    p_box = doc.add_paragraph()
    p_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_box.paragraph_format.left_indent = Inches(0.4)
    p_box.paragraph_format.right_indent = Inches(0.4)
    p_box.paragraph_format.space_before = Pt(18)
    p_box.paragraph_format.space_after = Pt(18)
    p_box.paragraph_format.keep_together = True

    shading = p_box._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), '000000')
    shd.set(qn('w:val'), 'clear')
    shading.append(shd)

    run_txt = p_box.add_run("Client: " + CLIENT + "\nProject: " + PROJECT + "\n" + OFFER_CODE)
    run_txt.font.name = "Arial"
    run_txt.font.size = Pt(12)
    run_txt.font.bold = True
    run_txt.font.color.rgb = None


def add_section_heading(doc: Document, title: str):
    p = doc.add_paragraph()
    p.style = doc.styles["Heading 1"]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.add_run(title)


def add_table(doc: Document, rows: Iterable[Iterable[str]]):
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    for i, r in enumerate(rows):
        if i == 0:
            header_cells = table.rows[0].cells
            for idx, v in enumerate(r):
                header_cells[idx].text = v
            continue
        row_cells = table.add_row().cells
        for idx, v in enumerate(r):
            row_cells[idx].text = v


def build_offer_content(doc: Document, *, offer_kind: str = "complete"):
    add_section_heading(doc, "Cascades Calgary - Phase 1: Transfer & Conveyor Package")
    if offer_kind == "engineering":
        doc.add_paragraph("This engineering and prioritization offer covers the detailed engineering, design validation, supplier capacity protection, and project coordination required to fully unlock the Calgary Phase 1 transfer and conveyor package without delays.")
        doc.add_paragraph("The proposal is framed to secure the engineering basis, define the exact interfaces, enable early procurement, and guarantee an accelerated readiness path for the transfer, conveyors, controls and plant integration activities.")
    elif offer_kind == "equipment":
        doc.add_paragraph("This offer covers the remaining supply, fabrication, installation and commissioning scope required to complete the transfer and conveyor package from detailed engineering approval through start-up support.")
        doc.add_paragraph("It includes the balance of the project scope to achieve the fully integrated automatic material flow between the three RDC discharges, second-pass machinery and final shipping dispatch, while maintaining the current manual conveyor route for the final conveyor leg as specified by the customer.")
    else:
        doc.add_paragraph("This proposal covers the installation of a coordinated transfer and conveyor package for the conversion area, with WIP located on the right side and the converting machines on the left. The new design introduces automated transfer flows between the three RDC outputs and the second-pass equipment or final shipment line.")

    doc.add_paragraph("The package includes the following equipment and operating logic:")
    bullets = [
        "Automatic transfer car / shuttle system between the three RDC outlets.",
        "Automated conveyors synchronized under INGECART control software.",
        "Automatic delivery to the FG miniline and Automatic Two-Piece Folder Gluer & Stitcher line.",
        "Automatic routing to the final shipping conveyor.",
        "Interface with the current production management system and plant signal logic.",
    ]
    for item in bullets:
        doc.add_paragraph(item, style="List Bullet")

    add_section_heading(doc, "Operating Concept")
    if offer_kind == "engineering":
        doc.add_paragraph("The present layout retains the existing downstream manual conveyor for the final dispatch lane, while the new transfer and conveyors are introduced as a controlled automatic logic for the three RDC outputs. The system is designed to reduce manual handling, improve flow continuity, protect the second-pass sequence and provide a clear interface with the customer production control systems.")
    elif offer_kind == "equipment":
        doc.add_paragraph("The proposed supply execution is based on a controlled automatic flow between the three RDC discharges, the second-pass lines and the final dispatch conveyor. The transfer equipment is designed to receive material from the right side and move it to the left side with software-based coordination, allowing the system to feed the FG miniline, the Automatic Two-Piece Folder Gluer & Stitcher machine and the shipping conveyor without operational dependence on manual forklift or operator intervention.")
    else:
        doc.add_paragraph("The existing manual transfer operations are replaced by a coordinated automatic flow. Each RDC output is connected to an automated conveyor controlled through the same management software. The transfer car moves product from right to left and directs material to the second-pass machines or to the shipping conveyor, eliminating operator dependency at the critical discharge points.")

    add_section_heading(doc, "Technical Data")
    doc.add_paragraph("Transfer car / automatic shuttle:")
    for line in [
        "Maximum load capacity: 3,000 to 5,000 kg.",
        "Lateral travel speed: 1.5 to 2.5 m/s.",
        "Roller bed speed: 0.3 to 0.5 m/s.",
        "Usable bed width: 1,800 to 2,800 mm.",
        "Usable bed length: 3,000 to 5,500 mm.",
        "Transport height: 300 to 450 mm.",
        "Positioning accuracy: ±2 mm to ±5 mm.",
    ]:
        doc.add_paragraph(line, style="List Bullet")

    add_section_heading(doc, "Typical PLC Inputs and Outputs")
    doc.add_paragraph("Inputs:")
    for line in [
        "Load position sensors",
        "Safety scanner / laser area detection",
        "Encoder / telescope laser distance for exact position",
        "Fixed-line load and discharge requests",
        "End-of-travel switches",
    ]:
        doc.add_paragraph(line, style="List Bullet")
    doc.add_paragraph("Outputs:")
    for line in [
        "Drive direction and speed command",
        "Roller bed control",
        "Brake actuation",
        "Signal tower alarm command",
        "Interlock release to the fixed line",
        "Equipment status and system interface signals",
    ]:
        doc.add_paragraph(line, style="List Bullet")

    add_section_heading(doc, "Scope and Commercial Proposal")
    add_table(doc, [
        ["Package", "Price"],
        ["Transfer & Conveyor", "€476,059"],
        ["Engineering & Prioritization", "$95,000 USD (~€87,500)"],
        ["Equipment, installation and commissioning", "Remainder of agreed scope"],
    ])

    doc.add_paragraph("The complete package is proposed with equipment, installation and travel included. Taxes, transport and packaging are excluded.")

    if offer_kind == "engineering":
        add_section_heading(doc, "Commercial Summary")
        doc.add_paragraph("Scope: detailed engineering for Calgary Phase 1 transfer and conveyor, including detailed design, supplier coordination, interface definition and accelerated validation management for the equipment package.")
        doc.add_paragraph("Amount: USD 95,000 (approximately €87,500).")
        doc.add_paragraph("Conditions: direct order with payment within 30 days.")
        doc.add_paragraph("Impact: immediate start of engineering, supplier capacity protection and guaranteed reduction of approximately 60 days in the delivery schedule.")
        doc.add_paragraph("Validity: 15 days.")
    elif offer_kind == "equipment":
        add_section_heading(doc, "Commercial Summary")
        doc.add_paragraph("Scope: balance of the project scope required to complete the transfer and conveyor package, including the remaining supply, fabrication, installation and commissioning work until the total agreed value is reached.")
        doc.add_paragraph("Conditions: governed entirely by the terms and conditions of the current framework agreement between Cascades and RBI.")
        doc.add_paragraph("Pricing: remaining amount of the project scope after engineering package approval and release to manufacturing.")
    else:
        add_section_heading(doc, "Commercial Summary")
        doc.add_paragraph("Package price: €476,059 including equipment, installation and travel. Taxes, transport and packaging are excluded.")
        doc.add_paragraph("Engineering and fabrication lead time: approximately 9 months from INGECART Barcelona.")
        doc.add_paragraph("The offer includes the transfer and conveyor package, software coordination and project support for the automatic flow between RDCs, second-pass machinery and shipping.")

    add_section_heading(doc, "Commercial Conditions")
    doc.add_paragraph("The equipment remains property of INGECART until full payment is received.")
    doc.add_paragraph("Offer validity: as defined in the proposal. Payment terms: as defined in the proposal. Delivery time: approximately 9 months from INGECART Barcelona, plus transport and installation.")
    doc.add_paragraph("The offer excludes works and materials not specifically described, project utilities not included in the scope, transport and packaging, and any additional labor with customer-requested extra time, which will be charged separately.")

    add_section_heading(doc, "General Sales Conditions")
    for idx, item in enumerate([
        "Scope of application and precedence.",
        "Industrial and intellectual property remains with INGECART.",
        "Price and payment conditions.",
        "Delivery deadlines and notice period.",
        "Retention of title and insurance.",
        "Transport, packaging and cargo insurance.",
        "Commercial and technical warranty.",
        "Limitation of liability.",
        "Force majeure.",
        "Jurisdiction and applicable law.",
    ], start=1):
        doc.add_paragraph(f"{idx}. {item}")

    add_section_heading(doc, "Signature")
    doc.add_paragraph("For and on behalf of INGECART")
    doc.add_paragraph("Signature: ______________________")
    doc.add_paragraph("Name: Diego García")
    doc.add_paragraph("Date: ________________________")


def create_offer_document(offer_name: str, file_suffix: str, offer_kind: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = Document()

    section = doc.sections[0]
    section.start_type = WD_SECTION_START.NEW_PAGE
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    add_cover_page(doc)
    add_section_heading(doc, offer_name)
    build_offer_content(doc, offer_kind=offer_kind)

    set_footer(doc)
    set_custom_header(doc)

    output_path = OUTPUT_DIR / f"{OUTPUT_PATH_PREFIX} {file_suffix}.docx"
    doc.save(output_path)
    print(f"Created: {output_path}")


def create_offer_package():
    create_offer_document("Offer - Engineering & Prioritization", "Engineering Prioritization Offer", "engineering")
    create_offer_document("Offer - Equipment Supply, Installation & Commissioning", "Equipment Installation Offer", "equipment")


if __name__ == "__main__":
    create_offer_package()

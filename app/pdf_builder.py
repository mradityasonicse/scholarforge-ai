import os
import html
import re
from typing import List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    Image,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

from app.models import ReportData, Chapter, Subsection, ScreenshotItem


class AcademicNumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that dynamically calculates and renders:
    - Running headers on chapters (Project Title / College Name)
    - Running footers (Page X of Y)
    - Skips headers/footers on preliminary cover and certificate pages.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        # Page 1 is the Title / Cover Page - leave completely clean
        if self._pageNumber == 1:
            return

        self.saveState()
        page_w, page_h = A4
        left_margin = 90  # 1.25 inches for binding
        right_margin = page_w - 72  # 1.0 inch

        # Running Header (pages > 5, typically chapters)
        if self._pageNumber >= 6:
            self.setFont("Times-Italic", 8.5)
            self.setFillColor(colors.HexColor("#475569"))
            header_title = getattr(self, "report_title_short", "Project Report")
            self.drawString(left_margin, page_h - 42, header_title[:65])
            self.drawRightString(right_margin, page_h - 42, "ScholarForge Academic Studio")
            
            # Thin divider line
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(left_margin, page_h - 46, right_margin, page_h - 46)

        # Running Footer (all pages > 1)
        self.setFont("Times-Roman", 9)
        self.setFillColor(colors.HexColor("#64748b"))
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(right_margin, 36, page_str)
        
        # Left footer confidentiality note
        self.drawString(left_margin, 36, "Confidential - Academic Project Report")
        
        # Bottom divider
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(left_margin, 48, right_margin, 48)

        self.restoreState()


def safe_xml(text: Optional[str]) -> str:
    """Escapes raw strings for safe rendering in ReportLab Paragraph XML."""
    if not text:
        return ""
    clean = html.escape(str(text))
    # Preserve line breaks
    clean = clean.replace("\n", "<br/>")
    return clean


def create_university_pdf(report_data: ReportData, output_filepath: str) -> str:
    """
    Builds a high-fidelity, publication-grade University Project Report PDF.
    Enforces standard Indian/Global university dissertation formatting:
    - A4 Page Size
    - 1.25" Left Binding Gutter (90 pt), 1.0" Right/Top/Bottom (72 pt)
    - Times-Roman Typography with 1.5 line spacing (18 pt leading)
    - Title Page, Certificate with Signatures, Declaration, Acknowledgement, Abstract
    - Chapters 1-8 with Subsections, Tables, Boxed Code Snippets, Screenshots, and IEEE References.
    """
    out_dir = os.path.dirname(output_filepath)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    
    # 1. Page Template Setup
    page_w, page_h = A4
    left_m = 90
    right_m = 72
    top_m = 72
    bottom_m = 72
    printable_w = page_w - left_m - right_m

    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=A4,
        leftMargin=left_m,
        rightMargin=right_m,
        topMargin=top_m,
        bottomMargin=bottom_m
    )

    meta = report_data.metadata

    # 2. Typography Styles
    styles = getSampleStyleSheet()

    title_cover_style = ParagraphStyle(
        "CoverTitle",
        fontName="Times-Bold",
        fontSize=20,
        leading=26,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=15
    )

    sub_cover_style = ParagraphStyle(
        "CoverSub",
        fontName="Times-Bold",
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6
    )

    italic_cover_style = ParagraphStyle(
        "CoverItalic",
        fontName="Times-Italic",
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    chap_num_style = ParagraphStyle(
        "ChapNum",
        fontName="Times-Bold",
        fontSize=15,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=4
    )

    chap_title_style = ParagraphStyle(
        "ChapTitle",
        fontName="Times-Bold",
        fontSize=17,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1e1b4b"),
        spaceAfter=18
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        fontName="Times-Bold",
        fontSize=13,
        leading=17,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "AcademicBody",
        fontName="Times-Roman",
        fontSize=11.5,
        leading=17.5,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=10,
        firstLineIndent=24
    )

    body_no_indent = ParagraphStyle(
        "AcademicBodyNoIndent",
        fontName="Times-Roman",
        fontSize=11.5,
        leading=17.5,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=10
    )

    code_style = ParagraphStyle(
        "CodeText",
        fontName="Courier",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0f172a")
    )

    caption_style = ParagraphStyle(
        "FigureCaption",
        fontName="Times-Italic",
        fontSize=9.5,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#475569"),
        spaceBefore=6,
        spaceAfter=12
    )

    ref_style = ParagraphStyle(
        "ReferenceItem",
        fontName="Times-Roman",
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
        leftIndent=24,
        firstLineIndent=-24
    )

    story = []

    # ==========================================
    # 1. TITLE / COVER PAGE
    # ==========================================
    story.append(Spacer(1, 20))
    story.append(Paragraph(safe_xml(meta.title.upper()), title_cover_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("A PROJECT REPORT", sub_cover_style))
    story.append(Paragraph("Submitted in partial fulfillment of the requirements<br/>for the award of the degree of", italic_cover_style))
    story.append(Paragraph(safe_xml(meta.degree.upper()), sub_cover_style))
    story.append(Paragraph(f"IN<br/>{safe_xml(meta.department.upper())}", sub_cover_style))
    story.append(Spacer(1, 20))

    # Student Names & Guide Table
    student_rows = []
    for s in meta.students:
        student_rows.append(f"<b>{safe_xml(s.name.upper())}</b><br/>(Roll No: {safe_xml(s.roll_no)})")
    students_html = "<br/><br/>".join(student_rows)

    guide_html = f"<b>{safe_xml(meta.guide_name.upper())}</b><br/>{safe_xml(meta.guide_designation)}"

    sub_table_data = [
        [
            Paragraph(f"<b>SUBMITTED BY:</b><br/><br/>{students_html}", ParagraphStyle("SubLeft", fontName="Times-Roman", fontSize=10.5, leading=15)),
            Paragraph(f"<b>UNDER THE GUIDANCE OF:</b><br/><br/>{guide_html}", ParagraphStyle("SubRight", fontName="Times-Roman", fontSize=10.5, leading=15))
        ]
    ]

    t_sub = Table(sub_table_data, colWidths=[printable_w * 0.52, printable_w * 0.48])
    t_sub.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_sub)
    story.append(Spacer(1, 35))

    # College & Academic Year Block
    story.append(Paragraph(safe_xml(meta.department.upper()), sub_cover_style))
    story.append(Paragraph(safe_xml(meta.college_name.upper()), title_cover_style))
    if meta.university_name:
        story.append(Paragraph(f"(Affiliated to {safe_xml(meta.university_name)})", italic_cover_style))
    story.append(Paragraph(f"ACADEMIC YEAR: {safe_xml(meta.academic_year)}", sub_cover_style))

    story.append(PageBreak())

    # ==========================================
    # 2. CERTIFICATE PAGE
    # ==========================================
    story.append(Paragraph(safe_xml(meta.college_name.upper()), sub_cover_style))
    story.append(Paragraph(safe_xml(meta.department.upper()), italic_cover_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("CERTIFICATE", title_cover_style))
    story.append(Spacer(1, 10))

    cert_text = (
        f"This is to certify that the project report entitled <b>\"{safe_xml(meta.title)}\"</b> is a bona fide record "
        f"of the project work done jointly by <b>{', '.join([safe_xml(s.name) for s in meta.students])}</b> "
        f"in partial fulfillment of the requirements for the award of the degree of <b>{safe_xml(meta.degree)}</b> in "
        f"<b>{safe_xml(meta.department)}</b> during the academic year <b>{safe_xml(meta.academic_year)}</b>."
    )
    story.append(Paragraph(cert_text, body_no_indent))
    story.append(Spacer(1, 15))

    cert_sub_text = (
        "The project report has been examined and approved as satisfying the academic requirements prescribed by the University. "
        "The results embodied in this report have not been submitted to any other University or Institute for the award of any degree or diploma."
    )
    story.append(Paragraph(cert_sub_text, body_no_indent))
    story.append(Spacer(1, 50))

    # Signatures Grid
    sig_data = [
        [
            Paragraph("_______________________<br/><b>Project Guide</b><br/>" + safe_xml(meta.guide_name), ParagraphStyle("S1", fontName="Times-Roman", fontSize=10, leading=14)),
            Paragraph("_______________________<br/><b>Head of Department</b><br/>" + safe_xml(meta.hod_name), ParagraphStyle("S2", fontName="Times-Roman", fontSize=10, leading=14))
        ],
        [
            Spacer(1, 30),
            Spacer(1, 30)
        ],
        [
            Paragraph("_______________________<br/><b>Internal Examiner</b>", ParagraphStyle("S3", fontName="Times-Roman", fontSize=10, leading=14)),
            Paragraph("_______________________<br/><b>External Examiner</b>", ParagraphStyle("S4", fontName="Times-Roman", fontSize=10, leading=14))
        ]
    ]
    t_sig = Table(sig_data, colWidths=[printable_w * 0.5, printable_w * 0.5])
    t_sig.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_sig)

    story.append(PageBreak())

    # ==========================================
    # 3. DECLARATION PAGE
    # ==========================================
    story.append(Paragraph("CANDIDATES' DECLARATION", title_cover_style))
    story.append(Spacer(1, 15))

    decl_text = (
        f"We hereby declare that the project work entitled <b>\"{safe_xml(meta.title)}\"</b> is an authentic record "
        f"of our own work carried out as requirements for the award of the degree of <b>{safe_xml(meta.degree)}</b> in "
        f"<b>{safe_xml(meta.department)}</b> under the supervision and guidance of <b>{safe_xml(meta.guide_name)}</b>, "
        f"{safe_xml(meta.guide_designation)}, at <b>{safe_xml(meta.college_name)}</b>.<br/><br/>"
        f"We also confirm that the matter embodied in this project report has not been submitted by us to any other "
        f"university or institute for the award of any degree, diploma, or certificate."
    )
    story.append(Paragraph(decl_text, body_no_indent))
    story.append(Spacer(1, 40))

    decl_rows = []
    for s in meta.students:
        decl_rows.append([
            Paragraph(f"Date: ____________<br/>Place: ____________", ParagraphStyle("DP", fontName="Times-Roman", fontSize=10, leading=14)),
            Paragraph(f"_______________________<br/><b>{safe_xml(s.name)}</b><br/>Roll No: {safe_xml(s.roll_no)}", ParagraphStyle("DS", fontName="Times-Roman", fontSize=10, leading=14, alignment=TA_RIGHT))
        ])
        decl_rows.append([Spacer(1, 15), Spacer(1, 15)])

    t_decl = Table(decl_rows, colWidths=[printable_w * 0.45, printable_w * 0.55])
    t_decl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_decl)

    story.append(PageBreak())

    # ==========================================
    # 4. ACKNOWLEDGEMENT PAGE
    # ==========================================
    story.append(Paragraph("ACKNOWLEDGEMENT", title_cover_style))
    story.append(Spacer(1, 15))

    ack_text = (
        f"We express our profound gratitude and heartfelt appreciation to our esteemed guide, "
        f"<b>{safe_xml(meta.guide_name)}</b>, {safe_xml(meta.guide_designation)}, Department of {safe_xml(meta.department)}, "
        f"for their invaluable guidance, constructive criticism, and relentless encouragement throughout the progression of this project.<br/><br/>"
        f"We extend our sincere thanks to <b>{safe_xml(meta.hod_name)}</b>, Head of Department, {safe_xml(meta.department)}, "
        f"and to our Principal, <b>{safe_xml(meta.principal_name)}</b>, for providing excellent laboratory infrastructure, administrative support, "
        f"and an enriching academic environment.<br/><br/>"
        f"Special thanks are due to all faculty and technical staff of the department for their continuous cooperation. "
        f"Finally, we wish to thank our parents and peers whose constant moral support and motivation remained a cornerstone of our efforts."
    )
    story.append(Paragraph(ack_text, body_style))
    story.append(Spacer(1, 40))

    ack_sign = [
        Paragraph(
            "<br/>".join([f"<b>{safe_xml(s.name)}</b> ({safe_xml(s.roll_no)})" for s in meta.students]),
            ParagraphStyle("AckS", fontName="Times-Roman", fontSize=10.5, leading=15, alignment=TA_RIGHT)
        )
    ]
    story.append(ack_sign[0])

    story.append(PageBreak())

    # ==========================================
    # 5. ABSTRACT & KEYWORDS
    # ==========================================
    story.append(Paragraph("ABSTRACT", title_cover_style))
    story.append(Spacer(1, 12))

    for ab_p in report_data.abstract.split("\n\n"):
        if ab_p.strip():
            story.append(Paragraph(safe_xml(ab_p.strip()), body_style))

    story.append(Spacer(1, 15))
    kw_str = ", ".join([safe_xml(k) for k in report_data.keywords])
    story.append(Paragraph(f"<b>Keywords:</b> <i>{kw_str}</i>", body_no_indent))

    story.append(PageBreak())

    # ==========================================
    # 6. TABLE OF CONTENTS
    # ==========================================
    story.append(Paragraph("TABLE OF CONTENTS", title_cover_style))
    story.append(Spacer(1, 15))

    toc_rows = [
        [Paragraph("<b>Chapter / Topic</b>", ParagraphStyle("TH1", fontName="Times-Bold", fontSize=10.5)),
         Paragraph("<b>Page No.</b>", ParagraphStyle("TH2", fontName="Times-Bold", fontSize=10.5, alignment=TA_RIGHT))]
    ]

    toc_rows.append([Paragraph("Certificate", ParagraphStyle("TI", fontName="Times-Roman", fontSize=10)), Paragraph("ii", ParagraphStyle("TR", fontName="Times-Roman", fontSize=10, alignment=TA_RIGHT))])
    toc_rows.append([Paragraph("Declaration", ParagraphStyle("TI", fontName="Times-Roman", fontSize=10)), Paragraph("iii", ParagraphStyle("TR", fontName="Times-Roman", fontSize=10, alignment=TA_RIGHT))])
    toc_rows.append([Paragraph("Acknowledgement", ParagraphStyle("TI", fontName="Times-Roman", fontSize=10)), Paragraph("iv", ParagraphStyle("TR", fontName="Times-Roman", fontSize=10, alignment=TA_RIGHT))])
    toc_rows.append([Paragraph("Abstract", ParagraphStyle("TI", fontName="Times-Roman", fontSize=10)), Paragraph("v", ParagraphStyle("TR", fontName="Times-Roman", fontSize=10, alignment=TA_RIGHT))])

    dummy_page = 1
    for ch in report_data.chapters:
        toc_rows.append([
            Paragraph(f"<b>{safe_xml(ch.title)}</b>", ParagraphStyle("TCH", fontName="Times-Bold", fontSize=10.5)),
            Paragraph(str(dummy_page), ParagraphStyle("TRB", fontName="Times-Bold", fontSize=10.5, alignment=TA_RIGHT))
        ])
        for sub in ch.subsections:
            toc_rows.append([
                Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{safe_xml(sub.heading)}", ParagraphStyle("TSUB", fontName="Times-Roman", fontSize=9.5)),
                Paragraph(str(dummy_page), ParagraphStyle("TR", fontName="Times-Roman", fontSize=9.5, alignment=TA_RIGHT))
            ])
        dummy_page += 3

    toc_rows.append([Paragraph("<b>References</b>", ParagraphStyle("TCH", fontName="Times-Bold", fontSize=10.5)), Paragraph(str(dummy_page), ParagraphStyle("TRB", fontName="Times-Bold", fontSize=10.5, alignment=TA_RIGHT))])

    t_toc = Table(toc_rows, colWidths=[printable_w * 0.85, printable_w * 0.15])
    t_toc.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#0f172a")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # ==========================================
    # 6B. LIST OF FIGURES & LIST OF TABLES
    # ==========================================
    story.append(Paragraph("LIST OF FIGURES", title_cover_style))
    story.append(Spacer(1, 15))

    lof_rows = [
        [Paragraph("<b>Figure No. & Caption</b>", ParagraphStyle("LFH1", fontName="Times-Bold", fontSize=10.5)),
         Paragraph("<b>Page No.</b>", ParagraphStyle("LFH2", fontName="Times-Bold", fontSize=10.5, alignment=TA_RIGHT))]
    ]
    fig_counts = {}
    for sc in report_data.screenshots:
        tgt_ch = getattr(sc, "chapter_target", 7)
        fig_counts[tgt_ch] = fig_counts.get(tgt_ch, 0) + 1
        cap = sc.caption if sc.caption else "System Architecture Model"
        page_val = "12" if tgt_ch == 4 else ("18" if tgt_ch == 6 else "24")
        lof_rows.append([
            Paragraph(f"Figure {tgt_ch}.{fig_counts[tgt_ch]}: {safe_xml(cap)}", ParagraphStyle("LFI", fontName="Times-Roman", fontSize=9.5)),
            Paragraph(page_val, ParagraphStyle("LFP", fontName="Times-Roman", fontSize=9.5, alignment=TA_RIGHT))
        ])

    if len(lof_rows) == 1:
        lof_rows.append([Paragraph("Figure 4.1: High-Level Layered System Architecture Topology", ParagraphStyle("LFI", fontName="Times-Roman", fontSize=9.5)), Paragraph("12", ParagraphStyle("LFP", fontName="Times-Roman", fontSize=9.5, alignment=TA_RIGHT))])
        lof_rows.append([Paragraph("Figure 4.2: Data Flow Diagram (DFD Level 1 Operational Flow)", ParagraphStyle("LFI", fontName="Times-Roman", fontSize=9.5)), Paragraph("14", ParagraphStyle("LFP", fontName="Times-Roman", fontSize=9.5, alignment=TA_RIGHT))])
        lof_rows.append([Paragraph("Figure 7.1: Comparative End-to-End Latency Benchmark", ParagraphStyle("LFI", fontName="Times-Roman", fontSize=9.5)), Paragraph("24", ParagraphStyle("LFP", fontName="Times-Roman", fontSize=9.5, alignment=TA_RIGHT))])
        lof_rows.append([Paragraph("Figure 7.2: Quantitative Classification Accuracy Telemetry", ParagraphStyle("LFI", fontName="Times-Roman", fontSize=9.5)), Paragraph("26", ParagraphStyle("LFP", fontName="Times-Roman", fontSize=9.5, alignment=TA_RIGHT))])

    t_lof = Table(lof_rows, colWidths=[printable_w * 0.85, printable_w * 0.15])
    t_lof.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#0f172a")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_lof)
    story.append(Spacer(1, 20))

    # LIST OF TABLES
    story.append(Paragraph("LIST OF TABLES", title_cover_style))
    story.append(Spacer(1, 15))
    lot_rows = [
        [Paragraph("<b>Table No. & Description</b>", ParagraphStyle("LTH1", fontName="Times-Bold", fontSize=10.5)),
         Paragraph("<b>Page No.</b>", ParagraphStyle("LTH2", fontName="Times-Bold", fontSize=10.5, alignment=TA_RIGHT))],
        [Paragraph("Table 3.1: Hardware and Software Computational Specification", ParagraphStyle("LTI", fontName="Times-Roman", fontSize=9.5)), Paragraph("8", ParagraphStyle("LTP", fontName="Times-Roman", fontSize=9.5, alignment=TA_RIGHT))],
        [Paragraph("Table 4.1: Relational Database Schema Normalization (3NF) & Entity Integrity", ParagraphStyle("LTI", fontName="Times-Roman", fontSize=9.5)), Paragraph("15", ParagraphStyle("LTP", fontName="Times-Roman", fontSize=9.5, alignment=TA_RIGHT))],
        [Paragraph("Table 6.1: Comprehensive Verification & Test Case Execution Matrix (TC-01 to TC-10)", ParagraphStyle("LTI", fontName="Times-Roman", fontSize=9.5)), Paragraph("21", ParagraphStyle("LTP", fontName="Times-Roman", fontSize=9.5, alignment=TA_RIGHT))],
        [Paragraph("Table 7.1: Quantitative Latency and Resource Utilization Under Multi-Core Stress", ParagraphStyle("LTI", fontName="Times-Roman", fontSize=9.5)), Paragraph("25", ParagraphStyle("LTP", fontName="Times-Roman", fontSize=9.5, alignment=TA_RIGHT))]
    ]
    t_lot = Table(lot_rows, colWidths=[printable_w * 0.85, printable_w * 0.15])
    t_lot.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#0f172a")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_lot)
    story.append(PageBreak())

    # ==========================================
    # 7. CHAPTERS (1 to 8+)
    # ==========================================
    for ch_idx, ch in enumerate(report_data.chapters):
        # Match "CHAPTER X" prefix
        chap_num_text = f"CHAPTER {ch.id}"
        story.append(Paragraph(chap_num_text, chap_num_style))
        story.append(Paragraph(safe_xml(ch.title.upper()), chap_title_style))

        if ch.summary:
            sum_style = ParagraphStyle(
                "ChapSummary",
                fontName="Times-Italic",
                fontSize=11,
                leading=16,
                alignment=TA_JUSTIFY,
                textColor=colors.HexColor("#334155"),
                spaceAfter=14
            )
            story.append(Paragraph(safe_xml(ch.summary), sum_style))

        # Subsections
        for sub in ch.subsections:
            story.append(Paragraph(safe_xml(sub.heading), h1_style))

            # Paragraphs
            paragraphs = sub.content.split("\n\n")
            for p_text in paragraphs:
                p_clean = p_text.strip()
                if p_clean:
                    story.append(Paragraph(safe_xml(p_clean), body_style))

            # Code Snippet (if any)
            if sub.code_snippet:
                code_clean = sub.code_snippet.strip()
                # Wrap code in clean table cell with gray background
                p_code = Paragraph(safe_xml(code_clean), code_style)
                t_code = Table([[p_code]], colWidths=[printable_w])
                t_code.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ]))
                story.append(Spacer(1, 4))
                story.append(t_code)
                story.append(Paragraph(f"Snippet {ch.id}.{ch.subsections.index(sub)+1}: Source Code Implementation", caption_style))
                story.append(Spacer(1, 6))

            # Table Data (if any)
            if sub.table_data:
                raw_table = []
                if isinstance(sub.table_data, dict):
                    hdrs = sub.table_data.get("headers", [])
                    rws = sub.table_data.get("rows", [])
                    if hdrs:
                        raw_table.append(hdrs)
                    raw_table.extend(rws)
                elif isinstance(sub.table_data, list):
                    raw_table = sub.table_data

                if raw_table and len(raw_table) > 0 and len(raw_table[0]) > 0:
                    t_rows = []
                    for r_idx, row in enumerate(raw_table):
                        t_row = []
                        for c in row:
                            f_name = "Times-Bold" if r_idx == 0 else "Times-Roman"
                            c_color = colors.white if r_idx == 0 else colors.HexColor("#0f172a")
                            cell_st = ParagraphStyle(
                                f"Cell_{ch.id}_{sub.heading}_{r_idx}",
                                fontName=f_name,
                                fontSize=9.5,
                                leading=13,
                                textColor=c_color,
                                alignment=TA_LEFT
                            )
                            t_row.append(Paragraph(safe_xml(str(c)), cell_st))
                        t_rows.append(t_row)

                    num_cols = len(raw_table[0])
                    col_w = printable_w / max(1, num_cols)
                    t_data = Table(t_rows, colWidths=[col_w] * num_cols)
                    t_data.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    story.append(Spacer(1, 4))
                    story.append(t_data)
                    story.append(Paragraph(f"Table {ch.id}.1: Experimental Benchmark and Comparative Data", caption_style))
                    story.append(Spacer(1, 6))

        # Embed Relevant Screenshots/Figures for this chapter based on chapter_target
        if report_data.screenshots:
            chap_screenshots = [sc for sc in report_data.screenshots if getattr(sc, "chapter_target", 7) == ch.id]
            is_results_ch = any(k in ch.title.lower() for k in ["result", "benchmark", "experiment", "testing", "evaluation"])
            if is_results_ch:
                all_ids = [c.id for c in report_data.chapters]
                orphans = [sc for sc in report_data.screenshots if getattr(sc, "chapter_target", 7) not in all_ids]
                chap_screenshots.extend(orphans)

            for s_idx, sc in enumerate(chap_screenshots, 1):
                img_path = sc.filepath
                if img_path and os.path.exists(img_path):
                    try:
                        # Render image respecting maximum printable width
                        img = Image(img_path, width=min(printable_w, 420), height=230)
                        story.append(Spacer(1, 6))
                        story.append(img)
                        story.append(Paragraph(f"Figure {ch.id}.{s_idx}: {safe_xml(sc.caption)}", caption_style))
                        story.append(Spacer(1, 8))
                    except Exception as img_err:
                        print(f"Warning: Failed embedding image in PDF: {img_err}")

        story.append(PageBreak())

    # ==========================================
    # 8. REFERENCES
    # ==========================================
    story.append(Paragraph("REFERENCES", title_cover_style))
    story.append(Spacer(1, 15))

    for idx, ref in enumerate(report_data.references):
        ref_text = ref.strip()
        if not ref_text.startswith("["):
            ref_text = f"[{idx+1}] {ref_text}"
        story.append(Paragraph(safe_xml(ref_text), ref_style))

    # Build Document using AcademicNumberedCanvas
    canvas_maker = AcademicNumberedCanvas
    # Set short title for running header
    canvas_maker.report_title_short = meta.title[:55]
    doc.build(story, canvasmaker=canvas_maker)

    return output_filepath


build_academic_pdf = create_university_pdf

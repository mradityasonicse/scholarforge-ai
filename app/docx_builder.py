import os
from typing import List, Optional, Dict, Any
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

from app.models import ReportData, Chapter, Subsection, ScreenshotItem


def set_cell_background(cell, fill_hex="F2F4F7"):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set cell padding (in twips: 20 twips = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)


def add_page_number_to_section(section):
    """Add standard page numbering in footer."""
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    # Add page number run
    run = footer_para.add_run()
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(120, 120, 120)


def create_university_docx(report_data: ReportData, output_filepath: str) -> str:
    """
    Builds a complete, authentic University Project Report in DOCX format.
    Standardized to 1.25" Left (Binding) margin, Times New Roman 12pt, 1.5 line spacing.
    """
    doc = docx.Document()
    
    # Configure Default Styles
    style_normal = doc.styles['Normal']
    style_normal.font.name = "Times New Roman"
    style_normal.font.size = Pt(12)
    style_normal.font.color.rgb = RGBColor(30, 30, 30)
    style_normal.paragraph_format.line_spacing = 1.5
    style_normal.paragraph_format.space_after = Pt(6)

    # Set Page Margins for first section (Cover Page)
    section = doc.sections[0]
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.25)  # Left gutter for spiral/hardcover binding
    section.right_margin = Inches(1.0)
    section.different_first_page_header_footer = True

    meta = report_data.metadata

    # ==========================================
    # 1. COVER / TITLE PAGE
    # ==========================================
    p_title_top = doc.add_paragraph()
    p_title_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title_top.paragraph_format.space_before = Pt(30)
    p_title_top.paragraph_format.space_after = Pt(10)
    r_title = p_title_top.add_run(meta.title.upper())
    r_title.bold = True
    r_title.font.size = Pt(20)
    r_title.font.name = "Times New Roman"
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    p_report = doc.add_paragraph()
    p_report.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_report.paragraph_format.space_before = Pt(15)
    p_report.paragraph_format.space_after = Pt(6)
    r_rep = p_report.add_run("A PROJECT REPORT")
    r_rep.bold = True
    r_rep.font.size = Pt(13)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(6)
    r_sub = p_sub.add_run("Submitted in partial fulfillment of the requirements\nfor the award of the degree of")
    r_sub.italic = True
    r_sub.font.size = Pt(11)

    p_degree = doc.add_paragraph()
    p_degree.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_degree.paragraph_format.space_before = Pt(4)
    p_degree.paragraph_format.space_after = Pt(20)
    r_deg = p_degree.add_run(meta.degree.upper())
    r_deg.bold = True
    r_deg.font.size = Pt(13)

    # Student Names Block
    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_by.paragraph_format.space_after = Pt(6)
    r_by = p_by.add_run("Submitted by:")
    r_by.bold = True
    r_by.font.size = Pt(12)

    if meta.students:
        table_st = doc.add_table(rows=len(meta.students) + 1, cols=2)
        table_st.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr_cells = table_st.rows[0].cells
        hdr_cells[0].text = "Candidate Name"
        hdr_cells[1].text = "University Roll No. / USN"
        set_cell_background(hdr_cells[0], "E2E8F0")
        set_cell_background(hdr_cells[1], "E2E8F0")
        hdr_cells[0].paragraphs[0].runs[0].bold = True
        hdr_cells[1].paragraphs[0].runs[0].bold = True
        
        for idx, st in enumerate(meta.students):
            row_cells = table_st.rows[idx + 1].cells
            row_cells[0].text = st.name
            row_cells[1].text = st.roll_no
            set_cell_margins(row_cells[0], 60, 60, 100, 100)
            set_cell_margins(row_cells[1], 60, 60, 100, 100)
    else:
        p_std_fallback = doc.add_paragraph("Project Team Candidates")
        p_std_fallback.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Guide Details Block
    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide.paragraph_format.space_before = Pt(24)
    p_guide.paragraph_format.space_after = Pt(2)
    r_gtitle = p_guide.add_run("Under the Guidance of\n")
    r_gtitle.italic = True
    r_gtitle.font.size = Pt(11)
    r_gname = p_guide.add_run(f"{meta.guide_name}\n")
    r_gname.bold = True
    r_gname.font.size = Pt(12)
    r_gdesg = p_guide.add_run(meta.guide_designation)
    r_gdesg.font.size = Pt(11)

    # College Footer Block
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(30)
    p_inst.paragraph_format.space_after = Pt(2)
    r_dept = p_inst.add_run(f"{meta.department.upper()}\n")
    r_dept.bold = True
    r_dept.font.size = Pt(13)
    r_coll = p_inst.add_run(f"{meta.college_name.upper()}\n")
    r_coll.bold = True
    r_coll.font.size = Pt(12)
    if meta.university_name:
        r_univ = p_inst.add_run(f"(Affiliated to {meta.university_name})\n")
        r_univ.italic = True
        r_univ.font.size = Pt(10)
    r_yr = p_inst.add_run(f"Academic Year: {meta.academic_year}")
    r_yr.bold = True
    r_yr.font.size = Pt(11)

    # End of Cover Page
    doc.add_page_break()

    # ==========================================
    # 2. CERTIFICATE OF AUTHENTICITY
    # ==========================================
    p_cert_title = doc.add_paragraph()
    p_cert_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert_title.paragraph_format.space_before = Pt(20)
    p_cert_title.paragraph_format.space_after = Pt(20)
    r_ct = p_cert_title.add_run("CERTIFICATE")
    r_ct.bold = True
    r_ct.font.size = Pt(16)

    student_str = ", ".join([f"{s.name} ({s.roll_no})" for s in meta.students]) if meta.students else "the candidates"
    
    cert_text = report_data.certificate_text or (
        f"This is to certify that the project report entitled \"{meta.title}\", submitted by {student_str} "
        f"in partial fulfillment of the requirements for the award of the degree of {meta.degree} from "
        f"{meta.college_name}, is a bona fide record of work carried out by them under my supervision and guidance.\n\n"
        f"The results embodied in this report have not been submitted to any other University or Institute "
        f"for the award of any degree or diploma."
    )
    p_cert_body = doc.add_paragraph(cert_text)
    p_cert_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Signature Blocks
    p_sig_space = doc.add_paragraph()
    p_sig_space.paragraph_format.space_before = Pt(60)

    sig_table = doc.add_table(rows=2, cols=3)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_table.rows[0].cells[0].paragraphs[0].text = "_______________________\nGuide Signature\n" + meta.guide_name
    sig_table.rows[0].cells[1].paragraphs[0].text = "_______________________\nHead of Department\n" + (meta.hod_name or "HOD")
    sig_table.rows[0].cells[2].paragraphs[0].text = "_______________________\nPrincipal\n" + (meta.principal_name or "Principal")

    sig_table.rows[1].cells[0].paragraphs[0].text = "\n\n_______________________\nExternal Examiner 1"
    sig_table.rows[1].cells[1].paragraphs[0].text = ""
    sig_table.rows[1].cells[2].paragraphs[0].text = "\n\n_______________________\nExternal Examiner 2"

    for row in sig_table.rows:
        for cell in row.cells:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in cell.paragraphs[0].runs:
                r.font.size = Pt(10)

    doc.add_page_break()

    # ==========================================
    # 3. STUDENT DECLARATION
    # ==========================================
    p_decl_title = doc.add_paragraph()
    p_decl_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_decl_title.paragraph_format.space_before = Pt(20)
    p_decl_title.paragraph_format.space_after = Pt(20)
    r_dt = p_decl_title.add_run("DECLARATION")
    r_dt.bold = True
    r_dt.font.size = Pt(16)

    decl_text = report_data.declaration_text or (
        f"We, the undersigned, hereby declare that the project report entitled \"{meta.title}\" "
        f"submitted to {meta.college_name} is our original work and has been carried out by us under the "
        f"guidance of {meta.guide_name}, {meta.guide_designation}, {meta.department}.\n\n"
        f"We further declare that the content of this project report does not infringe on any copyright or "
        f"proprietary right and has not formed the basis for the award of any degree, diploma, associateship, "
        f"fellowship or other similar titles in any other university."
    )
    p_decl_body = doc.add_paragraph(decl_text)
    p_decl_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    p_sig_st = doc.add_paragraph()
    p_sig_st.paragraph_format.space_before = Pt(50)
    p_sig_st.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if meta.students:
        for s in meta.students:
            r = p_sig_st.add_run(f"___________________________\n{s.name} ({s.roll_no})\n\n")
            r.font.size = Pt(11)
    else:
        p_sig_st.add_run("___________________________\n(Signature of Candidate)\n")

    doc.add_page_break()

    # ==========================================
    # 4. ACKNOWLEDGEMENT
    # ==========================================
    p_ack_title = doc.add_paragraph()
    p_ack_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ack_title.paragraph_format.space_before = Pt(20)
    p_ack_title.paragraph_format.space_after = Pt(20)
    r_at = p_ack_title.add_run("ACKNOWLEDGEMENT")
    r_at.bold = True
    r_at.font.size = Pt(16)

    ack_text = report_data.acknowledgement_text or (
        f"We take immense pleasure in expressing our deep sense of gratitude and indebtedness to our project guide, "
        f"{meta.guide_name}, {meta.guide_designation}, for their invaluable guidance, encouragement, and continuous "
        f"support throughout the course of this project.\n\n"
        f"We also express our sincere thanks to {meta.hod_name or 'the Head of Department'}, {meta.department}, for "
        f"providing the necessary laboratory infrastructure and departmental resources.\n\n"
        f"We are deeply thankful to our respected Principal, {meta.principal_name or 'the Principal'}, {meta.college_name}, "
        f"for their visionary encouragement. Finally, we wish to thank our parents and fellow classmates for their moral "
        f"support and constructive feedback during the realization of this system."
    )
    p_ack_body = doc.add_paragraph(ack_text)
    p_ack_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_page_break()

    # ==========================================
    # 5. ABSTRACT
    # ==========================================
    p_abs_title = doc.add_paragraph()
    p_abs_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs_title.paragraph_format.space_before = Pt(20)
    p_abs_title.paragraph_format.space_after = Pt(20)
    r_ab = p_abs_title.add_run("ABSTRACT")
    r_ab.bold = True
    r_ab.font.size = Pt(16)

    p_abs_body = doc.add_paragraph(report_data.abstract)
    p_abs_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    if report_data.keywords:
        p_kw = doc.add_paragraph()
        p_kw.paragraph_format.space_before = Pt(12)
        r_kwh = p_kw.add_run("Keywords: ")
        r_kwh.bold = True
        r_kwb = p_kw.add_run(", ".join(report_data.keywords))
        r_kwb.italic = True

    doc.add_page_break()

    # ==========================================
    # 6. TABLE OF CONTENTS
    # ==========================================
    p_toc_title = doc.add_paragraph()
    p_toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc_title.paragraph_format.space_before = Pt(20)
    p_toc_title.paragraph_format.space_after = Pt(16)
    r_toc = p_toc_title.add_run("TABLE OF CONTENTS")
    r_toc.bold = True
    r_toc.font.size = Pt(16)

    # Standard preliminary entries
    toc_entries = [
        ("Certificate", "ii"),
        ("Declaration", "iii"),
        ("Acknowledgement", "iv"),
        ("Abstract", "v"),
        ("List of Figures", "vii"),
        ("List of Tables", "viii"),
    ]
    
    # Add chapters to TOC
    approx_page = 1
    for ch in report_data.chapters:
        toc_entries.append((ch.title, str(approx_page)))
        approx_page += 3
        for sub in ch.subsections:
            toc_entries.append((f"    {sub.heading}", str(approx_page)))

    toc_entries.append(("References", str(approx_page + 2)))

    toc_table = doc.add_table(rows=len(toc_entries), cols=2)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (title, pnum) in enumerate(toc_entries):
        row = toc_table.rows[idx]
        cell_t = row.cells[0]
        cell_p = row.cells[1]
        cell_t.text = title
        cell_p.text = pnum
        cell_p.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if not title.startswith("    "):
            cell_t.paragraphs[0].runs[0].bold = True
            cell_p.paragraphs[0].runs[0].bold = True
        set_cell_margins(cell_t, 30, 30, 40, 40)
        set_cell_margins(cell_p, 30, 30, 40, 40)

    doc.add_page_break()

    # ==========================================
    # 7. LIST OF FIGURES & TABLES
    # ==========================================
    p_lof_title = doc.add_paragraph()
    p_lof_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof_title.paragraph_format.space_before = Pt(20)
    p_lof_title.paragraph_format.space_after = Pt(16)
    r_lof = p_lof_title.add_run("LIST OF FIGURES")
    r_lof.bold = True
    r_lof.font.size = Pt(16)

    lof_entries = []
    fig_idx = 1
    for s in report_data.screenshots:
        caption = s.caption if s.caption else f"Figure {fig_idx}: System Interface"
        lof_entries.append((caption, "18"))
        fig_idx += 1

    if not lof_entries:
        lof_entries.append(("Figure 4.1: High-Level Architecture Diagram", "12"))
        lof_entries.append(("Figure 4.2: Data Flow Diagram (DFD Level 1)", "14"))
        lof_entries.append(("Figure 6.1: Application User Dashboard", "18"))

    lof_table = doc.add_table(rows=len(lof_entries), cols=2)
    lof_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (caption, page_no) in enumerate(lof_entries):
        row = lof_table.rows[idx]
        row.cells[0].text = caption
        row.cells[1].text = page_no
        row.cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        set_cell_margins(row.cells[0], 30, 30, 40, 40)
        set_cell_margins(row.cells[1], 30, 30, 40, 40)

    doc.add_page_break()

    # ==========================================
    # 8. CHAPTERS
    # ==========================================
    # Setup page numbering in footer for chapter body
    add_page_number_to_section(doc.sections[0])

    screenshot_pool = list(report_data.screenshots)
    used_screenshot_idx = 0

    for ch_idx, chapter in enumerate(report_data.chapters):
        # Chapter Heading
        p_ch = doc.add_paragraph()
        p_ch.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_ch.paragraph_format.space_before = Pt(24)
        p_ch.paragraph_format.space_after = Pt(12)
        r_ch_title = p_ch.add_run(chapter.title.upper())
        r_ch_title.bold = True
        r_ch_title.font.size = Pt(16)
        r_ch_title.font.color.rgb = RGBColor(15, 23, 42)

        if chapter.summary:
            p_sm = doc.add_paragraph(chapter.summary)
            p_sm.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        # Subsections
        for sub in chapter.subsections:
            p_sub_hdr = doc.add_paragraph()
            p_sub_hdr.paragraph_format.space_before = Pt(14)
            p_sub_hdr.paragraph_format.space_after = Pt(6)
            p_sub_hdr.paragraph_format.keep_with_next = True
            r_sh = p_sub_hdr.add_run(sub.heading)
            r_sh.bold = True
            r_sh.font.size = Pt(13)
            r_sh.font.color.rgb = RGBColor(30, 41, 59)

            # Sub-content
            paragraphs = [p.strip() for p in sub.content.split("\n\n") if p.strip()]
            for para_text in paragraphs:
                p_body = doc.add_paragraph(para_text)
                p_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p_body.paragraph_format.line_spacing = 1.5
                p_body.paragraph_format.space_after = Pt(6)

            # Code Snippet Block (if any)
            if sub.code_snippet:
                p_code_hdr = doc.add_paragraph(f"Listing: {sub.heading} Implementation")
                p_code_hdr.runs[0].italic = True
                p_code_hdr.runs[0].font.size = Pt(10)
                
                table_code = doc.add_table(rows=1, cols=1)
                table_code.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell_code = table_code.rows[0].cells[0]
                set_cell_background(cell_code, "F8FAFC")
                set_cell_margins(cell_code, 120, 120, 150, 150)
                p_c = cell_code.paragraphs[0]
                p_c.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p_c.paragraph_format.line_spacing = 1.0
                r_c = p_c.add_run(sub.code_snippet)
                r_c.font.name = "Consolas"
                r_c.font.size = Pt(9.5)
                r_c.font.color.rgb = RGBColor(30, 41, 59)

            # Tabular Data (if any)
            if sub.table_data and "headers" in sub.table_data and "rows" in sub.table_data:
                headers = sub.table_data["headers"]
                rows = sub.table_data["rows"]
                tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                # Header row
                for h_idx, h_text in enumerate(headers):
                    cell = tbl.rows[0].cells[h_idx]
                    cell.text = str(h_text)
                    set_cell_background(cell, "E2E8F0")
                    cell.paragraphs[0].runs[0].bold = True
                    set_cell_margins(cell, 60, 60, 80, 80)
                # Data rows
                for r_idx, row_vals in enumerate(rows):
                    for c_idx, val in enumerate(row_vals):
                        if c_idx < len(tbl.rows[r_idx + 1].cells):
                            cell = tbl.rows[r_idx + 1].cells[c_idx]
                            cell.text = str(val)
                            set_cell_margins(cell, 50, 50, 80, 80)

        # Embed Screenshot into Results Chapter (typically Chapter 6 or if chapter title mentions results/screenshots)
        is_results_chap = any(k in chapter.title.lower() for k in ["result", "screenshot", "output", "experiment", "implementation"])
        if is_results_chap and screenshot_pool:
            while screenshot_pool:
                sc = screenshot_pool.pop(0)
                used_screenshot_idx += 1
                if os.path.exists(sc.filepath):
                    try:
                        p_img = doc.add_paragraph()
                        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_img.paragraph_format.space_before = Pt(14)
                        p_img.paragraph_format.space_after = Pt(4)
                        # Add image with maximum width 5.5 inches to respect margins
                        run_img = p_img.add_run()
                        run_img.add_picture(sc.filepath, width=Inches(5.5))
                        
                        # Add Caption
                        p_cap = doc.add_paragraph()
                        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_cap.paragraph_format.space_after = Pt(14)
                        r_cap = p_cap.add_run(f"Figure {chapter.id}.{used_screenshot_idx}: {sc.caption}")
                        r_cap.italic = True
                        r_cap.bold = True
                        r_cap.font.size = Pt(10.5)
                        r_cap.font.color.rgb = RGBColor(71, 85, 105)
                    except Exception as img_err:
                        print(f"Warning embedding screenshot {sc.filename}: {img_err}")

        # Page break after every chapter except the last one
        if ch_idx < len(report_data.chapters) - 1:
            doc.add_page_break()

    # ==========================================
    # 9. REFERENCES / BIBLIOGRAPHY
    # ==========================================
    doc.add_page_break()
    p_ref_title = doc.add_paragraph()
    p_ref_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ref_title.paragraph_format.space_before = Pt(20)
    p_ref_title.paragraph_format.space_after = Pt(16)
    r_rt = p_ref_title.add_run("REFERENCES")
    r_rt.bold = True
    r_rt.font.size = Pt(16)

    if report_data.references:
        for idx, ref_text in enumerate(report_data.references):
            p_ref = doc.add_paragraph()
            p_ref.paragraph_format.left_indent = Inches(0.4)
            p_ref.paragraph_format.first_line_indent = Inches(-0.4)
            p_ref.paragraph_format.space_after = Pt(6)
            p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            ref_clean = ref_text.strip()
            if not ref_clean.startswith("["):
                ref_clean = f"[{idx+1}] {ref_clean}"
            r_rf = p_ref.add_run(ref_clean)
            r_rf.font.size = Pt(11)
    else:
        # Fallback standard references
        default_refs = [
            "[1] I. Goodfellow, Y. Bengio, and A. Courville, Deep Learning. Cambridge, MA, USA: MIT Press, 2016.",
            "[2] R. S. Pressman and B. R. Maxim, Software Engineering: A Practitioner's Approach, 9th ed. McGraw-Hill Education, 2020.",
            "[3] A. Vaswani et al., \"Attention is all you need,\" in Advances in Neural Information Processing Systems (NeurIPS), 2017, pp. 5998–6008.",
            "[4] M. Fowler, Patterns of Enterprise Application Architecture. Addison-Wesley Professional, 2002.",
            "[5] Official Python Documentation, \"Python 3 Documentation,\" Python Software Foundation, 2024. [Online]. Available: https://docs.python.org/3/."
        ]
        for ref_clean in default_refs:
            p_ref = doc.add_paragraph(ref_clean)
            p_ref.paragraph_format.left_indent = Inches(0.4)
            p_ref.paragraph_format.first_line_indent = Inches(-0.4)
            p_ref.paragraph_format.space_after = Pt(6)

    # Save to file
    os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
    doc.save(output_filepath)
    return output_filepath

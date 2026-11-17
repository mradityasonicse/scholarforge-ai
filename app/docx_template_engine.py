import os
import re
from typing import Dict, Any, Optional
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from app.models import ReportData
from app.docx_builder import set_cell_background, set_cell_margins


def replace_placeholder_in_paragraph(paragraph, placeholder: str, replacement: str):
    """Replaces text placeholders across runs in a paragraph."""
    if placeholder in paragraph.text:
        # Simple replace if whole text has it
        full_text = paragraph.text.replace(placeholder, replacement)
        # Clear runs and set replaced text on first run
        if paragraph.runs:
            first_run = paragraph.runs[0]
            first_run.text = full_text
            for r in paragraph.runs[1:]:
                r.text = ""
        else:
            paragraph.add_run(full_text)


def inject_into_custom_template(template_path: str, report_data: ReportData, output_path: str) -> str:
    """
    Injects project report data into a user-provided custom university .docx template.
    Preserves college's specific headers, margins, borders, and watermarks.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Custom template not found at {template_path}")

    doc = docx.Document(template_path)
    meta = report_data.metadata
    student_str = ", ".join([f"{s.name} ({s.roll_no})" for s in meta.students]) if meta.students else "Student Candidates"

    replacements = {
        "{{PROJECT_TITLE}}": meta.title.upper(),
        "{{TITLE}}": meta.title,
        "{{DOMAIN}}": meta.domain or "Computer Science & Engineering",
        "{{DEGREE}}": meta.degree.upper(),
        "{{DEPARTMENT}}": meta.department,
        "{{COLLEGE_NAME}}": meta.college_name,
        "{{UNIVERSITY_NAME}}": meta.university_name or "",
        "{{ACADEMIC_YEAR}}": meta.academic_year,
        "{{GUIDE_NAME}}": meta.guide_name,
        "{{GUIDE_DESIGNATION}}": meta.guide_designation,
        "{{HOD_NAME}}": meta.hod_name or "Head of Department",
        "{{STUDENT_NAMES}}": student_str,
        "{{ABSTRACT}}": report_data.abstract,
        "{{KEYWORDS}}": ", ".join(report_data.keywords)
    }

    # 1. Scan and replace in all paragraphs
    for p in doc.paragraphs:
        for ph, val in replacements.items():
            if ph in p.text:
                replace_placeholder_in_paragraph(p, ph, val)

    # 2. Scan and replace in all tables
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for ph, val in replacements.items():
                        if ph in p.text:
                            replace_placeholder_in_paragraph(p, ph, val)

    # 3. Append Chapters if template doesn't already have them populated
    # Check if "{{CHAPTERS}}" placeholder was placed, or append to end of template
    chapters_injected = False
    for p in doc.paragraphs:
        if "{{CHAPTERS}}" in p.text:
            p.text = ""  # Clear placeholder
            # Append chapters right after
            append_chapters_to_doc(doc, report_data)
            chapters_injected = True
            break

    if not chapters_injected:
        # Append after page break at the end of the template
        doc.add_page_break()
        append_chapters_to_doc(doc, report_data)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    return output_path


def append_chapters_to_doc(doc: docx.Document, report_data: ReportData):
    """Appends structured chapters, tables, and screenshots conforming to template typography."""
    screenshot_pool = list(report_data.screenshots)
    used_screenshot_idx = 0

    for ch_idx, chapter in enumerate(report_data.chapters):
        p_ch = doc.add_paragraph()
        p_ch.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_ch.paragraph_format.space_before = Pt(20)
        p_ch.paragraph_format.space_after = Pt(10)
        r_ch = p_ch.add_run(chapter.title.upper())
        r_ch.bold = True
        r_ch.font.size = Pt(16)
        r_ch.font.name = "Times New Roman"

        if chapter.summary:
            p_sm = doc.add_paragraph(chapter.summary)
            p_sm.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_sm.paragraph_format.line_spacing = 1.5

        for sub in chapter.subsections:
            p_sh = doc.add_paragraph()
            p_sh.paragraph_format.space_before = Pt(12)
            p_sh.paragraph_format.space_after = Pt(4)
            p_sh.paragraph_format.keep_with_next = True
            r_sh = p_sh.add_run(sub.heading)
            r_sh.bold = True
            r_sh.font.size = Pt(13)
            r_sh.font.name = "Times New Roman"

            for para in [p.strip() for p in sub.content.split("\n\n") if p.strip()]:
                p_b = doc.add_paragraph(para)
                p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p_b.paragraph_format.line_spacing = 1.5
                p_b.paragraph_format.space_after = Pt(6)

            if sub.code_snippet:
                tbl_code = doc.add_table(rows=1, cols=1)
                tbl_code.alignment = WD_TABLE_ALIGNMENT.CENTER
                c = tbl_code.rows[0].cells[0]
                set_cell_background(c, "F8FAFC")
                set_cell_margins(c, 100, 100, 120, 120)
                p_code = c.paragraphs[0]
                r_code = p_code.add_run(sub.code_snippet)
                r_code.font.name = "Consolas"
                r_code.font.size = Pt(9.5)

            if sub.table_data and "headers" in sub.table_data:
                headers = sub.table_data["headers"]
                rows = sub.table_data["rows"]
                tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                for h_idx, h in enumerate(headers):
                    cell = tbl.rows[0].cells[h_idx]
                    cell.text = str(h)
                    cell.paragraphs[0].runs[0].bold = True
                    set_cell_background(cell, "E2E8F0")
                for r_idx, row in enumerate(rows):
                    for c_idx, val in enumerate(row):
                        if c_idx < len(tbl.rows[r_idx + 1].cells):
                            tbl.rows[r_idx + 1].cells[c_idx].text = str(val)

        # Embed Screenshot
        is_results = any(k in chapter.title.lower() for k in ["result", "screenshot", "output", "experiment"])
        if is_results and screenshot_pool:
            while screenshot_pool:
                sc = screenshot_pool.pop(0)
                used_screenshot_idx += 1
                if os.path.exists(sc.filepath):
                    try:
                        p_img = doc.add_paragraph()
                        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_img.paragraph_format.space_before = Pt(12)
                        p_img.paragraph_format.space_after = Pt(4)
                        p_img.add_run().add_picture(sc.filepath, width=Inches(5.5))

                        p_cap = doc.add_paragraph()
                        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_cap.paragraph_format.space_after = Pt(12)
                        r_cap = p_cap.add_run(f"Figure {chapter.id}.{used_screenshot_idx}: {sc.caption}")
                        r_cap.italic = True
                        r_cap.bold = True
                        r_cap.font.size = Pt(10.5)
                    except Exception as e:
                        print(f"Error embedding picture in custom template: {e}")

        if ch_idx < len(report_data.chapters) - 1:
            doc.add_page_break()

    # Append References
    doc.add_page_break()
    p_ref_t = doc.add_paragraph()
    p_ref_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_rt = p_ref_t.add_run("REFERENCES")
    r_rt.bold = True
    r_rt.font.size = Pt(16)

    for idx, ref in enumerate(report_data.references):
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)
        ref_text = ref.strip() if ref.strip().startswith("[") else f"[{idx+1}] {ref.strip()}"
        p_ref.add_run(ref_text)

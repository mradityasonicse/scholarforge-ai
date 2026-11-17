import os
import sys
import json
from app.models import (
    ProjectMetadata,
    StudentDetail,
    CodeSource,
    ScreenshotItem,
    FormatConfig,
    LLMConfig,
    GenerateReportRequest,
    PromptRevisionRequest,
    ReportData
)
from app.report_generator import generate_full_report
from app.prompt_reviser import revise_report_with_prompt
from app.docx_builder import create_university_docx
from app.github_parser import parse_github_url, fetch_github_repo_data

def test_pipeline():
    print("[1/5] Testing GitHub URL Parser...")
    parsed = parse_github_url("https://github.com/psf/requests")
    assert parsed == ("psf", "requests"), f"Expected ('psf', 'requests'), got {parsed}"
    print("  ✓ GitHub URL parser passed!")

    print("[2/5] Testing Full Report Generation (Offline Synthesis Engine)...")
    req = GenerateReportRequest(
        metadata=ProjectMetadata(
            title="Automated Medical Diagnosis via Deep Learning",
            domain="Healthcare & Deep Learning",
            degree="Bachelor of Technology in Computer Science & Engineering",
            college_name="Apex Institute of Technology",
            department="Department of Computer Science & Engineering",
            university_name="State Technical University",
            academic_year="2024 - 2026",
            guide_name="Dr. Amit Sharma",
            guide_designation="Associate Professor",
            hod_name="Dr. R. V. Patel",
            principal_name="Dr. M. K. Nair",
            students=[
                StudentDetail(name="Rahul Verma", roll_no="21BCSE042"),
                StudentDetail(name="Priya Singh", roll_no="21BCSE088")
            ]
        ),
        code_source=CodeSource(
            github_url="https://github.com/apex/medical-diagnosis",
            detected_tech_stack=["Python", "PyTorch", "FastAPI", "React", "PostgreSQL"],
            readme_content="Medical diagnostic system utilizing Convolutional Neural Networks.",
            file_tree_summary="main.py\nmodels/cnn.py\napi/routes.py\nrequirements.txt"
        ),
        screenshots=[],
        format_config=FormatConfig(preset="btech_standard"),
        llm_config=LLMConfig(provider="offline")
    )

    report_data = generate_full_report(req)
    assert report_data is not None, "Report data is None"
    assert len(report_data.chapters) >= 7, f"Expected at least 7 chapters, got {len(report_data.chapters)}"
    assert "Automated Medical Diagnosis" in report_data.metadata.title
    print(f"  ✓ Generated {len(report_data.chapters)} academic chapters successfully!")

    print("[3/5] Testing Prompt Revision Engine...")
    rev_req = PromptRevisionRequest(
        report=report_data,
        prompt="Bhai roll number 21BCSE099 kar do aur Chapter 4 me CNN loss equations add karo",
        target_section="all",
        llm_config=LLMConfig(provider="offline")
    )
    rev_res = revise_report_with_prompt(rev_req)
    assert rev_res.success is True, "Revision failed"
    assert rev_res.updated_report.metadata.students[0].roll_no == "21BCSE099", f"Expected roll 21BCSE099, got {rev_res.updated_report.metadata.students[0].roll_no}"
    print(f"  ✓ Prompt revision applied successfully: {rev_res.revision_summary}")

    print("[4/5] Testing DOCX University Report Builder...")
    output_docx = os.path.join(os.path.dirname(__file__), "uploads", "test_report.docx")
    saved_path = create_university_docx(rev_res.updated_report, output_docx)
    assert os.path.exists(saved_path), f"File {saved_path} does not exist"
    size_kb = os.path.getsize(saved_path) / 1024
    print(f"  ✓ DOCX created successfully at {saved_path} (Size: {size_kb:.2f} KB)")

    print("[5/5] Testing FastAPI App Endpoints...")
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    
    res_formats = client.get("/api/formats")
    assert res_formats.status_code == 200
    assert "btech_standard" in res_formats.json()["formats"]
    
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert "ScholarForge AI" in res_index.text
    print("  ✓ FastAPI Web endpoints tested and responsive!")

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY! (100% OPERATIONAL)")

if __name__ == "__main__":
    test_pipeline()

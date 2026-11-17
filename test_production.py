import os
import sys
import json
import docx
from fastapi.testclient import TestClient

from app.database import init_db, save_project, list_projects, get_project, delete_project
from app.diagram_generator import generate_architecture_diagrams
from app.docx_template_engine import inject_into_custom_template
from app.report_generator import generate_full_report
from app.models import (
    ProjectMetadata,
    StudentDetail,
    CodeSource,
    FormatConfig,
    LLMConfig,
    GenerateReportRequest
)
from app.main import app

def run_production_tests():
    print("=" * 65)
    print("  RUNNING SCHOLARFORGE PRODUCTION VERIFICATION TEST SUITE")
    print("=" * 65)

    # 1. Test SQLite Persistence
    print("\n[1/5] Testing SQLite Database Persistence & CRUD...")
    init_db()
    test_payload = {
        "metadata": {
            "title": "Autonomous Drone Fleet Management",
            "domain": "Robotics & Distributed Computing",
            "degree": "B.Tech in Artificial Intelligence",
            "college_name": "National Institute of Advanced Studies"
        },
        "code_source": {"detected_tech_stack": ["Python", "ROS2", "FastAPI"]},
        "format_config": {"preset": "btech_standard"},
        "screenshots": [],
        "report_data": {},
        "diagrams": {}
    }
    pid = save_project(test_payload)
    assert pid is not None, "Failed to save project draft"
    print(f"  ✓ Saved project draft with ID: {pid}")

    drafts = list_projects()
    assert len(drafts) >= 1, "Failed to list drafts"
    print(f"  ✓ Listed {len(drafts)} drafts from SQLite")

    loaded = get_project(pid)
    assert loaded["title"] == "Autonomous Drone Fleet Management"
    print("  ✓ Retrieved project by ID successfully")

    # 2. Test Diagram Generator
    print("\n[2/5] Testing Mermaid.js Diagram Engine...")
    diagrams = generate_architecture_diagrams("Autonomous Drone Fleet Management", ["Python", "ROS2", "FastAPI", "React", "PostgreSQL"], "Robotics")
    for key in ["architecture", "dfd", "sequence", "erd", "flowchart"]:
        assert key in diagrams, f"Missing diagram {key}"
        assert len(diagrams[key]) > 20, f"Diagram {key} is empty"
    print("  ✓ Generated Architecture, DFD, Sequence, ERD, and Flowchart diagrams!")

    # 3. Test Custom Word (.docx) Template Injection
    print("\n[3/5] Testing Custom College DOCX Template Injection...")
    sample_tpl_path = os.path.join(os.path.dirname(__file__), "uploads", "sample_template.docx")
    sample_doc = docx.Document()
    sample_doc.add_heading("COLLEGE OFFICIAL TEMPLATE", 0)
    p = sample_doc.add_paragraph("Project: {{PROJECT_TITLE}}\nDegree: {{DEGREE}}\nGuide: {{GUIDE_NAME}}\nStudents: {{STUDENT_NAMES}}")
    sample_doc.save(sample_tpl_path)

    # Generate a report to inject
    req = GenerateReportRequest(
        metadata=ProjectMetadata(
            title="Deep Reinforcement Learning in Robotics",
            domain="Robotics & AI",
            degree="Master of Technology in Robotics",
            college_name="Indian Institute of Information Technology",
            department="Dept of Robotics & Automation",
            guide_name="Dr. V. Raman",
            guide_designation="Professor",
            students=[StudentDetail(name="Siddharth Rao", roll_no="24MTROB012")]
        ),
        code_source=CodeSource(detected_tech_stack=["Python", "PyTorch", "ROS2"]),
        format_config=FormatConfig(preset="btech_standard"),
        llm_config=LLMConfig(provider="offline")
    )
    rep_data = generate_full_report(req)

    injected_out = os.path.join(os.path.dirname(__file__), "uploads", "custom_injected_report.docx")
    inject_into_custom_template(sample_tpl_path, rep_data, injected_out)
    assert os.path.exists(injected_out), "Injected report not found"
    
    # Verify injected content
    check_doc = docx.Document(injected_out)
    full_text = " ".join([p.text for p in check_doc.paragraphs])
    assert "DEEP REINFORCEMENT LEARNING IN ROBOTICS" in full_text
    assert "Siddharth Rao (24MTROB012)" in full_text
    print(f"  ✓ Injected placeholders and chapters into custom template successfully! ({os.path.getsize(injected_out) / 1024:.2f} KB)")

    # 4. Test Production Endpoints
    print("\n[4/5] Testing Production FastAPI Endpoints & Health Checks...")
    client = TestClient(app)
    
    h_res = client.get("/health")
    assert h_res.status_code == 200
    assert h_res.json()["status"] == "healthy"
    print("  ✓ /health endpoint verified (200 OK)")

    diag_res = client.post("/api/generate-diagrams", json={
        "title": "Quantum Key Distribution Simulator",
        "tech_stack": ["Python", "Qiskit", "FastAPI"],
        "domain": "Quantum Cryptography"
    })
    assert diag_res.status_code == 200
    assert diag_res.json()["success"] is True
    print("  ✓ /api/generate-diagrams verified (200 OK)")

    proj_res = client.get("/api/projects")
    assert proj_res.status_code == 200
    print("  ✓ /api/projects verified (200 OK)")

    # 5. Clean up test artifacts
    print("\n[5/5] Cleaning and Final Assertion...")
    delete_project(pid)
    print("  ✓ Test draft cleaned from SQLite database")

    print("\n" + "=" * 65)
    print("  ALL PRODUCTION LEVEL TEST GATES PASSED (100% OPERATIONAL)!")
    print("=" * 65)

if __name__ == "__main__":
    run_production_tests()

import os
import uuid
import shutil
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.models import (
    GenerateReportRequest,
    PromptRevisionRequest,
    ReportData,
    ScreenshotItem,
    CodeSource,
    RevisionResponse,
    LLMConfig
)
from app.academic_templates import UNIVERSITY_FORMATS
from app.github_parser import fetch_github_repo_data, scan_local_directory
from app.report_generator import generate_full_report, call_llm_api
from app.prompt_reviser import revise_report_with_prompt
from app.docx_builder import create_university_docx
from app.docx_template_engine import inject_into_custom_template
from app.diagram_generator import generate_architecture_diagrams
from app.database import (
    init_db,
    save_project,
    list_projects,
    get_project,
    delete_project
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.environ.get("VERCEL"):
    UPLOAD_DIR = "/tmp/uploads"
    TEMPLATES_DIR = "/tmp/templates"
else:
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
    TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
if not os.environ.get("VERCEL"):
    os.makedirs(STATIC_DIR, exist_ok=True)

# Initialize SQLite database
init_db()

app = FastAPI(
    title="ScholarForge AI - University Project Report Generator",
    description="Production-Grade Automated University Project Report Generator with GitHub analysis, Screenshots, Diagrams, Prompts & Custom DOCX Templates",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/health")
async def health_check():
    """Production health check endpoint for Cloud deployments (Render, Railway, Docker)."""
    return {
        "status": "healthy",
        "service": "ScholarForge AI",
        "version": "2.0.0",
        "environment": "production"
    }


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>ScholarForge AI Server Running</h1><p>Frontend loading...</p>")


@app.get("/api/formats")
async def get_formats():
    """Returns available university format templates."""
    return {"formats": UNIVERSITY_FORMATS}


# ==========================================
# REPOSITORY & CODE ANALYSIS
# ==========================================
class AnalyzeRepoRequest(BaseModel):
    github_url: Optional[str] = None
    local_path: Optional[str] = None
    code_text: Optional[str] = None


@app.post("/api/analyze-repo")
async def analyze_repo(req: AnalyzeRepoRequest):
    """
    Parses a GitHub repo URL or local directory to extract tech stack, README, and files.
    """
    if req.github_url and req.github_url.strip():
        data = fetch_github_repo_data(req.github_url.strip())
        return data
    elif req.local_path and req.local_path.strip():
        data = scan_local_directory(req.local_path.strip())
        return data
    elif req.code_text and req.code_text.strip():
        techs = []
        code_lower = req.code_text.lower()
        if "def " in code_lower or "import " in code_lower:
            techs.append("Python")
        if "fastapi" in code_lower:
            techs.append("FastAPI")
        if "react" in code_lower or "usestate" in code_lower:
            techs.append("React")
        if "torch" in code_lower:
            techs.append("PyTorch")
        if "tensorflow" in code_lower or "keras" in code_lower:
            techs.append("TensorFlow")
        if "select " in code_lower or "table" in code_lower:
            techs.append("SQL/Database")

        return {
            "repo_name": "Pasted Code Source",
            "description": "User supplied source code",
            "detected_tech_stack": techs or ["Python"],
            "readme_content": "Pasted code provided directly in prompt.",
            "file_tree_summary": "main_script.py",
            "sample_code": req.code_text[:3000]
        }
    else:
        raise HTTPException(status_code=400, detail="Please provide a GitHub URL, local path, or code text.")


# ==========================================
# DIAGRAM GENERATOR (Mermaid Architecture/DFD/ERD)
# ==========================================
class GenerateDiagramsRequest(BaseModel):
    title: str
    tech_stack: List[str]
    domain: Optional[str] = "Computer Science & Engineering"


@app.post("/api/generate-diagrams")
async def generate_diagrams_api(req: GenerateDiagramsRequest):
    """
    Auto-generates visual Architecture, DFD Level 1, Sequence, and ER diagrams.
    """
    try:
        diagrams = generate_architecture_diagrams(req.title, req.tech_stack, req.domain or "")
        return {"success": True, "diagrams": diagrams}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# SCREENSHOT & TEMPLATE UPLOADS
# ==========================================
@app.post("/api/upload-screenshots")
async def upload_screenshots(files: List[UploadFile] = File(...)):
    """
    Uploads screenshot images and prepares them for report embedding.
    """
    results: List[ScreenshotItem] = []
    for f in files:
        file_ext = os.path.splitext(f.filename)[1].lower()
        if file_ext not in [".png", ".jpg", ".jpeg", ".webp"]:
            continue

        uid = str(uuid.uuid4())[:8]
        clean_name = f"{uid}_{f.filename}"
        dest_path = os.path.join(UPLOAD_DIR, clean_name)

        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)

        base_name = os.path.splitext(f.filename)[0].replace("_", " ").replace("-", " ").title()
        caption = f"Application Screen: {base_name}"

        results.append(ScreenshotItem(
            id=uid,
            filename=clean_name,
            filepath=dest_path,
            caption=caption,
            chapter_target=6
        ))

    return {"screenshots": [s.model_dump() for s in results]}


@app.post("/api/upload-template-docx")
async def upload_custom_template_docx(file: UploadFile = File(...)):
    """
    Uploads a student's official university .docx template file.
    """
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext != ".docx":
        raise HTTPException(status_code=400, detail="Only Microsoft Word .docx templates are supported.")

    uid = str(uuid.uuid4())[:8]
    clean_name = f"template_{uid}_{file.filename}"
    dest_path = os.path.join(TEMPLATES_DIR, clean_name)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "success": True,
        "template_id": uid,
        "template_filename": clean_name,
        "original_filename": file.filename,
        "message": "Custom college template uploaded successfully."
    }


# ==========================================
# REPORT GENERATION & PROMPT REVISION
# ==========================================
@app.post("/api/generate-report")
async def generate_report(request: GenerateReportRequest):
    """
    Generates a full humanized academic project report.
    """
    try:
        report_data = generate_full_report(request)
        return {"success": True, "report": report_data.model_dump()}
    except Exception as e:
        print(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/revise-report")
async def revise_report(request: PromptRevisionRequest):
    """
    Revises the report based on natural language prompt instructions (English or Hinglish).
    """
    try:
        revision_res = revise_report_with_prompt(request)
        return revision_res.model_dump()
    except Exception as e:
        print(f"Error revising report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# DOCUMENT EXPORT (.DOCX)
# ==========================================
class DownloadDocxRequest(BaseModel):
    report: ReportData
    custom_template_filename: Optional[str] = None


@app.post("/api/download-docx")
async def download_docx_api(req: DownloadDocxRequest):
    """
    Generates academic .docx file. Uses custom uploaded template if provided,
    otherwise uses standardized university layout.
    """
    try:
        report = req.report
        safe_title = "".join(c for c in report.metadata.title if c.isalnum() or c in (" ", "_", "-")).strip()
        safe_title = safe_title[:40].replace(" ", "_") or "Project_Report"
        filename = f"{safe_title}_Report.docx"
        output_path = os.path.join(UPLOAD_DIR, filename)

        if req.custom_template_filename:
            custom_tpl_path = os.path.join(TEMPLATES_DIR, req.custom_template_filename)
            if os.path.exists(custom_tpl_path):
                inject_into_custom_template(custom_tpl_path, report, output_path)
            else:
                create_university_docx(report, output_path)
        else:
            create_university_docx(report, output_path)

        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Failed to create DOCX document.")

        return FileResponse(
            path=output_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        print(f"Error creating DOCX: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# PERSISTENT PROJECT DATABASE (SQLite CRUD)
# ==========================================
@app.get("/api/projects")
async def get_projects_list():
    """Returns list of saved drafts in SQLite."""
    return {"projects": list_projects()}


@app.post("/api/projects")
async def save_project_draft(payload: Dict[str, Any]):
    """Saves or updates a project draft."""
    try:
        project_id = save_project(payload)
        return {"success": True, "project_id": project_id, "message": "Draft saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}")
async def get_single_project(project_id: str):
    """Loads a single project draft state."""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@app.delete("/api/projects/{project_id}")
async def delete_single_project(project_id: str):
    """Deletes a saved project draft."""
    ok = delete_project(project_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Project not found.")
    return {"success": True, "message": "Project deleted."}


# ==========================================
# API KEY VALIDATOR
# ==========================================
class TestKeyRequest(BaseModel):
    provider: str
    api_key: str
    model_name: Optional[str] = None


@app.post("/api/test-api-key")
async def test_api_key(req: TestKeyRequest):
    """
    Validates API key connectivity with LLM provider.
    """
    if req.provider.lower() == "offline":
        return {
            "valid": True,
            "message": "Offline Academic Synthesizer is active! 100% free with no API key required."
        }

    llm_conf = LLMConfig(provider=req.provider, api_key=req.api_key, model_name=req.model_name)
    sys_p = "Respond with JSON only: {\"status\": \"ok\"}"
    usr_p = "Ping test"
    res = call_llm_api(sys_p, usr_p, llm_conf)
    if res and "status" in res:
        return {"valid": True, "message": f"Successfully connected to {req.provider.title()} API!"}
    return {"valid": False, "message": f"Connection to {req.provider.title()} failed. Check your key or use Offline Mode."}

import os
from app.code_analyzer import extract_python_symbols, analyze_source_file
from app.github_parser import scan_local_directory, prioritize_source_files
from app.models import RepoFileItem, CodeSource, ProjectMetadata, GenerateReportRequest, FormatConfig, LLMConfig
from app.report_generator import generate_full_report

def test_deep_code_access():
    print("Testing Code Analyzer on sample Python source...")
    sample_code = """
import os
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

app = FastAPI()
router = APIRouter()

class UserQuery(BaseModel):
    query_text: str
    max_tokens: int = 100

class DiagnosisModel:
    def __init__(self, weights_path: str):
        self.weights = weights_path

    def predict(self, features: list):
        return [0.95, 0.05]

@app.get("/api/health")
def health():
    return {"status": "ok"}

@router.post("/api/predict")
async def handle_prediction(payload: UserQuery):
    model = DiagnosisModel("weights.pt")
    return model.predict([payload.query_text])
"""
    analysis = analyze_source_file("api/routes.py", sample_code)
    assert "DiagnosisModel" in analysis["classes"], "Failed to extract DiagnosisModel class"
    assert "UserQuery" in analysis["classes"], "Failed to extract UserQuery class"
    assert any("health" in f for f in analysis["functions"]), "Failed to extract health function"
    assert any("predict" in f for f in analysis["functions"]), "Failed to extract predict function"
    assert any("GET /api/health" in ep for ep in analysis["endpoints"]), "Failed to extract GET endpoint"
    assert any("POST /api/predict" in ep for ep in analysis["endpoints"]), "Failed to extract POST endpoint"
    print(f"  ✓ Code analysis extracted: {len(analysis['classes'])} classes, {len(analysis['functions'])} functions, {len(analysis['endpoints'])} endpoints")

    print("Testing Local Repository Scanning with Deep Code Access...")
    local_data = scan_local_directory(os.path.dirname(__file__))
    assert "files" in local_data, "No files list in local scan data"
    assert len(local_data["files"]) > 0, "Files array is empty"
    print(f"  ✓ Local directory scanned: {len(local_data['files'])} source files analyzed with symbols")

    print("Testing Report Generator with Deep Code Injection...")
    req = GenerateReportRequest(
        metadata=ProjectMetadata(
            title="Real-Time Medical Prediction Platform",
            domain="Health Informatics",
            degree="Bachelor of Technology in Computer Science",
            college_name="College of Engineering",
            guide_name="Dr. S. K. Roy"
        ),
        code_source=CodeSource(
            files=[
                RepoFileItem(
                    path="api/routes.py",
                    name="routes.py",
                    language="python",
                    content=sample_code,
                    classes=analysis["classes"],
                    functions=analysis["functions"],
                    endpoints=analysis["endpoints"],
                    selected=True
                )
            ]
        ),
        format_config=FormatConfig(preset="btech_standard"),
        llm_config=LLMConfig(provider="offline")
    )
    rep = generate_full_report(req)
    chap5 = [c for c in rep.chapters if any(k in c.title.lower() for k in ["implementation", "module"])][0]
    sub1 = chap5.subsections[0]
    assert "api/routes.py" in str(sub1.code_snippet) or "routes.py" in sub1.content, "Real code was not injected into Chapter 5"
    assert "DiagnosisModel" in sub1.content or "DiagnosisModel" in str(sub1.code_snippet), "Class DiagnosisModel was not referenced in Chapter 5"
    print("  ✓ Real code, classes, and endpoints successfully injected into Chapter 5!")
    print("\nALL REPOSITORY CODE ACCESS TESTS PASSED!")

if __name__ == "__main__":
    test_deep_code_access()

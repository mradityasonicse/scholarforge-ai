from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StudentDetail(BaseModel):
    name: str = Field(..., description="Student Name")
    roll_no: str = Field(..., description="Roll Number / USN / Registration Number")
    email: Optional[str] = None


class ProjectMetadata(BaseModel):
    title: str = Field(..., description="Title of the Project")
    domain: Optional[str] = "Computer Science & Engineering"
    degree: str = "Bachelor of Technology in Computer Science & Engineering"
    college_name: str = "Department of Computer Science & Engineering, Institute of Technology"
    department: str = "Department of Computer Science & Engineering"
    university_name: Optional[str] = "State Technological University"
    academic_year: str = "2024 - 2026"
    guide_name: str = "Dr. S. K. Sharma"
    guide_designation: str = "Associate Professor"
    hod_name: Optional[str] = "Dr. R. V. Patel"
    principal_name: Optional[str] = "Dr. M. K. Nair"
    students: List[StudentDetail] = []


class ScreenshotItem(BaseModel):
    id: str
    filename: str
    filepath: str
    caption: str = "System Interface"
    chapter_target: int = 6


class CodeSource(BaseModel):
    github_url: Optional[str] = None
    local_path: Optional[str] = None
    code_text: Optional[str] = None
    detected_tech_stack: List[str] = []
    file_tree_summary: Optional[str] = None
    readme_content: Optional[str] = None


class FormatConfig(BaseModel):
    preset: str = "btech_standard"  # btech_standard, vtu, aktu, mca_bca, ieee_condensed, custom
    custom_guidelines: Optional[str] = None
    font_family: str = "Times New Roman"
    line_spacing: float = 1.5


class LLMConfig(BaseModel):
    provider: str = "gemini"  # gemini, groq, openai, ollama, offline
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    custom_prompt: Optional[str] = None


class GenerateReportRequest(BaseModel):
    metadata: ProjectMetadata
    code_source: CodeSource
    screenshots: List[ScreenshotItem] = []
    format_config: FormatConfig = Field(default_factory=FormatConfig)
    llm_config: LLMConfig = Field(default_factory=LLMConfig)


class Subsection(BaseModel):
    heading: str
    content: str
    code_snippet: Optional[str] = None
    code_language: Optional[str] = None
    table_data: Optional[Dict[str, Any]] = None  # {"headers": [...], "rows": [[...]]}
    figures: List[str] = []  # Image filenames or IDs


class Chapter(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    subsections: List[Subsection] = []


class ReportData(BaseModel):
    metadata: ProjectMetadata
    abstract: str
    keywords: List[str] = []
    certificate_text: Optional[str] = None
    declaration_text: Optional[str] = None
    acknowledgement_text: Optional[str] = None
    chapters: List[Chapter] = []
    references: List[str] = []
    screenshots: List[ScreenshotItem] = []
    format_config: FormatConfig = Field(default_factory=FormatConfig)


class PromptRevisionRequest(BaseModel):
    report: ReportData
    prompt: str = Field(..., description="User's change prompt in English or Hinglish")
    target_section: Optional[str] = "all"  # 'all', 'abstract', or 'chapter_X'
    llm_config: LLMConfig = Field(default_factory=LLMConfig)


class RevisionResponse(BaseModel):
    success: bool
    message: str
    updated_report: ReportData
    revision_summary: str

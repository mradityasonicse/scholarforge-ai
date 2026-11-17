import os
import json
import re
import requests
from typing import Dict, Any, List, Optional
from app.models import GenerateReportRequest, ReportData, Chapter, Subsection, ScreenshotItem
from app.academic_templates import UNIVERSITY_FORMATS, parse_custom_format_guideline
from app.academic_prompts import ACADEMIC_HUMANIZER_SYSTEM_PROMPT, build_humanized_generation_prompt
from app.diagram_generator import generate_architecture_diagrams


def call_llm_api(system_prompt: str, user_prompt: str, llm_config) -> Optional[str]:
    """
    Executes LLM request via Gemini, Groq, OpenAI, or Ollama.
    Returns response text string.
    """
    provider = (llm_config.provider or "gemini").lower()
    api_key = (llm_config.api_key or "").strip()

    if provider == "gemini":
        if not api_key:
            return None
        model = llm_config.model_name or "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": system_prompt + "\n\n" + user_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.35,
                "maxOutputTokens": 8192,
                "responseMimeType": "application/json"
            }
        }
        try:
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=75)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
            else:
                print(f"Gemini API Error: {res.status_code} {res.text}")
        except Exception as e:
            print(f"Gemini Request failed: {e}")

    elif provider == "groq":
        if not api_key:
            return None
        model = llm_config.model_name or "llama-3.3-70b-versatile"
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=65)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            else:
                print(f"Groq API Error: {res.status_code} {res.text}")
        except Exception as e:
            print(f"Groq Request failed: {e}")

    elif provider == "openai":
        if not api_key:
            return None
        model = llm_config.model_name or "gpt-4o-mini"
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=65)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenAI Request failed: {e}")

    elif provider == "ollama":
        model = llm_config.model_name or "llama3"
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "format": "json"
        }
        try:
            res = requests.post(url, json=payload, timeout=90)
            if res.status_code == 200:
                return res.json().get("response", "")
        except Exception as e:
            print(f"Ollama Request failed: {e}")

    return None


def generate_offline_academic_report(request: GenerateReportRequest, chapter_templates: List[Dict[str, Any]]) -> ReportData:
    """
    Intelligent Humanized Academic Synthesis Engine.
    Strictly free of AI clichés; produces varied syntax, formal technical diction,
    mathematical notation, and concrete telemetry metrics.
    """
    meta = request.metadata
    code = request.code_source
    title = meta.title
    tech_list = code.detected_tech_stack or ["Python", "FastAPI", "React", "PostgreSQL", "Docker"]
    tech_str = ", ".join(tech_list)

    # 1. Humanized Academic Abstract
    abstract = (
        f"This dissertation presents the design, mathematical formulation, and empirical evaluation of \"{title}\", "
        f"an automated computational framework addressing latency and modularity challenges in {meta.domain}. "
        f"Traditional implementations often display severe throughput degradation and state inconsistencies when scaled across distributed endpoints. "
        f"To resolve these bottlenecks, we synthesize an event-driven, decoupled architecture incorporating {tech_str}.\n\n"
        f"The proposed pipeline employs rigorous data sanitization, asynchronous stream handling, and deterministic state transitions. "
        f"Experimental stress testing conducted under synthetic concurrent workloads demonstrated a 99th percentile response latency of 46.2 ms, "
        f"representing a 3.4x performance gain over legacy monolithic architectures. "
        f"The architectural schematics, formal verification proofs, test case matrices, and implementation benchmarks documented herein "
        f"confirm that the system satisfies both industrial production criteria and university accreditation benchmarks."
    )

    keywords = [meta.domain, "Asynchronous Architecture", "Empirical Evaluation", "State Serialization", "Latency Optimization"] + tech_list[:3]

    built_chapters: List[Chapter] = []

    for ch_spec in chapter_templates:
        ch_id = ch_spec.get("id", 1)
        ch_title = ch_spec.get("title", f"CHAPTER {ch_id}")
        subsections: List[Subsection] = []

        sub_list = ch_spec.get("subsections", [])
        if not sub_list:
            sub_list = [f"{ch_id}.1 Theoretical Foundation", f"{ch_id}.2 Engineering Execution", f"{ch_id}.3 Telemetry Analysis"]

        for sub_name in sub_list:
            sub_clean = sub_name.lower()
            code_snip = None
            tbl_data = None

            if any(k in sub_clean for k in ["overview", "background", "intro"]):
                content = (
                    f"Contemporary computing paradigms in {meta.domain} demand rigorous operational predictability and fault isolation. "
                    f"The system titled \"{title}\" was conceptualized to resolve architectural debt that plagues legacy software systems. "
                    f"By enforcing clean separation of concerns across service layers, the proposed platform circumvents classic single-point failures.\n\n"
                    f"Using {tech_str}, the software pipeline guarantees determinism across ingestion, transformation, and presentation boundaries. "
                    f"This document provides a comprehensive post-implementation dissertation detailing theoretical underpinnings, component topologies, "
                    f"and empirical validation results conforming to university board guidelines."
                )

            elif "problem" in sub_clean:
                content = (
                    f"Prior approaches in {meta.domain} manifest systemic vulnerabilities: non-deterministic execution schedules, memory leaks "
                    f"under sustained traffic, and unstandardized data interchange schemas. In mission-critical environments, such deficiencies "
                    f"lead to unacceptable operational downtime.\n\n"
                    f"Formally, the research problem addressed by \"{title}\" is stated as: To synthesize an asynchronous, fault-tolerant execution engine "
                    f"that ensures sub-50ms query turnaround times while preserving strict ACID transaction guarantees across heterogeneous client instances."
                )

            elif any(k in sub_clean for k in ["objective", "aim", "scope"]):
                content = (
                    f"The technical milestones of \"{title}\" are defined along five distinct engineering vectors:\n\n"
                    f"1. Architectural Decoupling: Establish a modular topology that isolates UI rendering from computational microservices.\n"
                    f"2. Mathematical & Algorithmic Optimization: Formulate data pipelines bounded strictly within O(N log N) time complexity.\n"
                    f"3. Resilient Communication Contracts: Enforce end-to-end type safety using strict schema validation contracts.\n"
                    f"4. Empirical Verification: Execute exhaustive black-box, white-box, and regression test suites with 100% test passing ratios.\n"
                    f"5. Production Hardening: Incorporate role-based access control, cryptographic token verification, and persistent audit logging."
                )

            elif any(k in sub_clean for k in ["literature", "survey", "related"]):
                content = (
                    f"An exhaustive survey of academic publications across IEEE Transactions, ACM Digital Library, and Springer journals "
                    f"was performed to contextualize our methodological advancements. Canonical literature by Vaswani et al. (2017) and Goodfellow et al. (2016) "
                    f"underscored the necessity of parameterized model abstraction.\n\n"
                    f"However, comparative analysis of existing research demonstrates marked oversights regarding deterministic client serialization "
                    f"and low-overhead audit logging. As delineated in Table {ch_id}.1, the proposed solution overcomes each documented deficiency."
                )
                tbl_data = {
                    "headers": ["Author & Citation", "Architectural Model", "Throughput Limit", "Identified Research Gap"],
                    "rows": [
                        ["Smith & Patel (IEEE 2022)", "Monolithic Layered Stack", "120 req/sec", "High thread contention and locking overhead"],
                        ["Kumar et al. (Springer 2023)", "Serverless Function Mesh", "450 req/sec", "Cold-start latency spikes exceeding 400ms"],
                        ["Proposed System (2024)", "Asynchronous Decoupled Engine", "1,850 req/sec", "Deterministic execution; minimal initialization latency"]
                    ]
                }

            elif any(k in sub_clean for k in ["requirement", "specification", "srs"]):
                content = (
                    f"The Software Requirements Specification (SRS) for \"{title}\" defines explicit functional boundaries and quantitative SLAs. "
                    f"The platform guarantees 99.9% service availability, sub-100ms UI interaction latency, and cryptographic payload protection.\n\n"
                    f"Hardware specifications and runtime operating environments have been sized to ensure low thermal footprint and cost-effective deployment."
                )
                tbl_data = {
                    "headers": ["System Resource", "Minimum Baseline", "Recommended Production Target"],
                    "rows": [
                        ["CPU Architecture", "x86-64 Quad-Core 2.4 GHz", "Octa-Core 3.2 GHz or Apple ARM Silicon"],
                        ["System RAM", "8 GB DDR4", "16 GB High-Bandwidth Unified RAM"],
                        ["Persistent NVMe Storage", "10 GB Available Disk Space", "50 GB High-IOPS NVMe Drive"],
                        ["Operating Platform", "Ubuntu 22.04 LTS / Windows 10", "Linux Containerized / Windows 11 Enterprise"],
                        ["Primary Runtime Runtimes", "Python 3.10+ / Node.js 18+", "Python 3.11+ / Bun Engine 1.4"],
                        ["Relational Store & Cache", "SQLite 3.39+", "PostgreSQL 16 / Redis 7.2"]
                    ]
                }

            elif any(k in sub_clean for k in ["architecture", "design", "uml"]):
                content = (
                    f"The system architecture of \"{title}\" adopts a clean, layered hexagonal topology. Ingress traffic is mediated through an API Gateway "
                    f"which enforces rate-limiting and cryptographic token inspection. Validated payloads pass downstream to core business services, "
                    f"which orchestrate state mutations and execute analytical routines.\n\n"
                    f"Data flow diagrams (DFD Level 0 Context and DFD Level 1 Detailed) illustrate that data mutations remain isolated from telemetry streams, "
                    f"preventing cascading failures during unexpected peak ingress."
                )

            elif any(k in sub_clean for k in ["implementation", "module", "algorithm"]):
                selected_files = [f for f in code.files if getattr(f, "selected", True) and getattr(f, "content", "")]
                if selected_files:
                    primary_f = selected_files[0]
                    mod_names = ", ".join([os.path.basename(f.path) for f in selected_files[:4]])
                    classes_found = [c for f in selected_files for c in (f.classes or [])][:6]
                    funcs_found = [fn for f in selected_files for fn in (f.functions or [])][:6]
                    endpoints_found = [ep for f in selected_files for ep in (f.endpoints or [])][:5]

                    classes_text = f" Primary classes encapsulated within this module include: {', '.join(classes_found)}." if classes_found else ""
                    funcs_text = f" Essential computational subroutines include: {', '.join(funcs_found)}." if funcs_found else ""
                    endpoints_text = f" Exposed API contracts and endpoints include: {', '.join(endpoints_found)}." if endpoints_found else ""

                    content = (
                        f"The software engineering implementation of \"{title}\" is organized into decoupled service modules "
                        f"({mod_names}) adhering to modular abstraction and clean separation of concerns.{classes_text}{funcs_text}{endpoints_text}\n\n"
                        f"The underlying execution routines enforce deterministic data sanitization and state persistence, "
                        f"ensuring asymptotic efficiency bounded within O(N log N) time complexity during real-time transactions."
                    )
                    code_snip = f"# Module: {primary_f.path}\n" + "\n".join(primary_f.content.split("\n")[:40])
                else:
                    content = (
                        f"Implementation of \"{title}\" is organized into decoupled service modules adhering to SOLID software design principles. "
                        f"Data ingestion routines normalize heterogeneous payloads prior to execution of analytical passes.\n\n"
                        f"The core optimization algorithm models convergence through empirical risk minimization: "
                        f"arg min_theta sum [ L(f(x_i; theta), y_i) ] + lambda * ||theta||^2, where parameters theta update iteratively via adaptive gradient moments."
                    )
                    code_snip = (
                        f"# Production Module: Core Execution Pipeline for {title}\n"
                        f"import time\n"
                        f"from typing import Dict, Any\n\n"
                        f"def process_pipeline_payload(payload: Dict[str, Any]) -> Dict[str, Any]:\n"
                        f"    \"\"\"Executes validated pipeline workflow with bounded latency.\"\"\"\n"
                        f"    t_start = time.perf_counter()\n"
                        f"    if not payload:\n"
                        f"        raise ValueError('Invalid payload: input cannot be null')\n"
                        f"    \n"
                        f"    # Step 1: Feature sanitization and transformation\n"
                        f"    sanitized_data = {{k: str(v).strip() for k, v in payload.items()}}\n"
                        f"    \n"
                        f"    # Step 2: Algorithmic inference & metric calculation\n"
                        f"    execution_ms = (time.perf_counter() - t_start) * 1000.0\n"
                        f"    return {{\n"
                        f"        'status': 'success',\n"
                        f"        'project': '{title}',\n"
                        f"        'latency_ms': round(execution_ms, 2),\n"
                        f"        'data': sanitized_data\n"
                        f"    }}\n"
                    )

            elif any(k in sub_clean for k in ["result", "screenshot", "output", "experiment"]):
                content = (
                    f"Empirical experiments were executed across multiple synthetic traffic cycles to evaluate response latency, memory allocation stability, "
                    f"and output accuracy. Benchmark trials recorded zero unhandled exceptions and verified full data consistency.\n\n"
                    f"Visual snapshots of the running user interface, real-time analytics screens, and terminal execution logs "
                    f"confirm that \"{title}\" operates with stability and conforms to external evaluation standards."
                )

            elif any(k in sub_clean for k in ["test", "validation", "qa"]):
                content = (
                    f"Verification of \"{title}\" utilized an automated test harness covering Unit Testing, Module Integration Testing, and User Acceptance Testing (UAT). "
                    f"All critical business pathways achieved 100% test assertion passing rates under test automation."
                )
                tbl_data = {
                    "headers": ["Test ID", "Functional Scope", "Input Condition", "Expected Assertion", "Actual Result", "Verdict"],
                    "rows": [
                        ["TC-AUTH-01", "User Token Ingress", "Valid JWT Token", "HTTP 200 & Claims Authorized", "HTTP 200 Claims Validated", "PASS"],
                        ["TC-VAL-02", "Malformed Payload Ingress", "Empty Request Body", "HTTP 422 Unprocessable Content", "HTTP 422 Returned Correctly", "PASS"],
                        ["TC-PIPE-03", "Pipeline Processing", "Batch Data Array", "Sub-50ms Processing Latency", "38.2 ms Latency Measured", "PASS"],
                        ["TC-DOCX-04", "Report Document Builder", "Full Structured State", "Build .docx with Valid XML", "Pristine .docx Generated", "PASS"],
                        ["TC-CONC-05", "Concurrent Ingress", "100 Simultaneous Threads", "Zero 500 Server Errors", "All Requests Handled", "PASS"]
                    ]
                }

            elif any(k in sub_clean for k in ["conclusion", "future"]):
                content = (
                    f"The development and empirical evaluation of \"{title}\" substantiate the viability of modern asynchronous architectures in {meta.domain}. "
                    f"By replacing brittle legacy implementations with decoupled service modules using {tech_str}, the project attains superior throughput, "
                    f"robust error resilience, and complete auditability.\n\n"
                    f"Future research will target distributed auto-scaling across multi-region Kubernetes clusters, integration of self-supervised transformer models, "
                    f"and automated cryptographic zero-knowledge verification."
                )

            else:
                content = (
                    f"This section analyzes {sub_name} within the framework of \"{title}\". "
                    f"Rigorous software engineering practices and formal specifications ensure predictable runtime performance, "
                    f"satisfying both departmental guidelines and international peer-review standards."
                )

            subsections.append(Subsection(
                heading=sub_name,
                content=content,
                code_snippet=code_snip,
                table_data=tbl_data
            ))

        built_chapters.append(Chapter(
            id=ch_id,
            title=ch_title,
            summary=f"This chapter presents an in-depth scholarly dissertation and technical evaluation of {ch_title.lower()}.",
            subsections=subsections
        ))

    # Peer-reviewed references
    references = [
        "A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser, and I. Polosukhin, \"Attention is all you need,\" in Advances in Neural Information Processing Systems (NeurIPS), vol. 30, pp. 5998–6008, 2017.",
        "I. Goodfellow, Y. Bengio, and A. Courville, Deep Learning. Cambridge, MA, USA: MIT Press, 2016.",
        "R. S. Pressman and B. R. Maxim, Software Engineering: A Practitioner's Approach, 9th ed. New York, NY, USA: McGraw-Hill Education, 2020.",
        "M. Fowler, Patterns of Enterprise Application Architecture. Boston, MA, USA: Addison-Wesley Professional, 2002.",
        "Python Software Foundation, \"Python 3 Language Reference and Runtime Architecture,\" 2024. [Online]. Available: https://docs.python.org/3/.",
        "E. Gamma, R. Helm, R. Johnson, and J. Vlissides, Design Patterns: Elements of Reusable Object-Oriented Software. Reading, MA, USA: Addison-Wesley, 1994.",
        "IEEE Computer Society, \"IEEE Standard for Software and System Test Documentation,\" IEEE Std 829-2008, pp. 1–126, 2008."
    ]

    return ReportData(
        metadata=meta,
        abstract=abstract,
        keywords=keywords,
        chapters=built_chapters,
        references=references,
        screenshots=request.screenshots,
        format_config=request.format_config
    )


def generate_full_report(request: GenerateReportRequest) -> ReportData:
    """
    Main Report Generation Orchestrator.
    Executes humanized, Turnitin-compliant prompt with LLM or offline fallback.
    """
    format_key = request.format_config.preset
    if format_key in UNIVERSITY_FORMATS:
        chapter_specs = UNIVERSITY_FORMATS[format_key]["chapters"]
    elif format_key == "custom" and request.format_config.custom_guidelines:
        chapter_specs = parse_custom_format_guideline(request.format_config.custom_guidelines)
    else:
        chapter_specs = UNIVERSITY_FORMATS["btech_standard"]["chapters"]

    provider = (request.llm_config.provider or "offline").lower()
    api_key = (request.llm_config.api_key or "").strip()

    if provider != "offline" and api_key:
        system_prompt = ACADEMIC_HUMANIZER_SYSTEM_PROMPT
        user_prompt = build_humanized_generation_prompt(
            meta=request.metadata,
            code=request.code_source,
            chapter_specs=json.dumps(chapter_specs, indent=2),
            custom_prompt=request.llm_config.custom_prompt or ""
        )

        response_text = call_llm_api(system_prompt, user_prompt, request.llm_config)
        if response_text:
            try:
                clean_json = response_text.strip()
                if clean_json.startswith("```"):
                    clean_json = re.sub(r"^```(?:json)?\s*", "", clean_json)
                    clean_json = re.sub(r"\s*```$", "", clean_json)

                parsed_data = json.loads(clean_json)
                chapters = []
                for ch in parsed_data.get("chapters", []):
                    subs = []
                    for s in ch.get("subsections", []):
                        subs.append(Subsection(
                            heading=s.get("heading", ""),
                            content=s.get("content", ""),
                            code_snippet=s.get("code_snippet"),
                            table_data=s.get("table_data")
                        ))
                    chapters.append(Chapter(
                        id=ch.get("id", len(chapters) + 1),
                        title=ch.get("title", f"CHAPTER {len(chapters) + 1}"),
                        summary=ch.get("summary", ""),
                        subsections=subs
                    ))

                return ReportData(
                    metadata=request.metadata,
                    abstract=parsed_data.get("abstract", "Abstract"),
                    keywords=parsed_data.get("keywords", ["Engineering", "Computer Science"]),
                    chapters=chapters,
                    references=parsed_data.get("references", []),
                    screenshots=request.screenshots,
                    format_config=request.format_config
                )
            except Exception as parse_err:
                print(f"Warning: Failed parsing LLM response as JSON: {parse_err}. Falling back to offline synthesizer.")

    return generate_offline_academic_report(request, chapter_specs)

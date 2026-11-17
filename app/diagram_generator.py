import re
from typing import Dict, Any, List


def generate_architecture_diagrams(title: str, tech_stack: List[str], domain: str) -> Dict[str, str]:
    """
    Generates academic Mermaid.js diagrams:
    1. System Architecture
    2. Data Flow Diagram (DFD Level 1)
    3. UML Sequence Diagram
    4. Database ER Diagram
    5. Operational Process Flowchart
    """
    techs_lower = [t.lower() for t in tech_stack]
    frontend_tech = "React / Web UI"
    if any("flutter" in t for t in techs_lower):
        frontend_tech = "Flutter Mobile Client"
    elif any("react" in t for t in techs_lower):
        frontend_tech = "React Single Page Application"
    elif any("next" in t for t in techs_lower):
        frontend_tech = "Next.js Frontend Client"

    backend_tech = "FastAPI / Python Service"
    if any("django" in t for t in techs_lower):
        backend_tech = "Django REST Framework"
    elif any("express" in t or "node" in t for t in techs_lower):
        backend_tech = "Node.js / Express Server"
    elif any("fastapi" in t for t in techs_lower):
        backend_tech = "FastAPI Async Engine"

    db_tech = "PostgreSQL Database"
    if any("mongo" in t for t in techs_lower):
        db_tech = "MongoDB NoSQL Store"
    elif any("mysql" in t for t in techs_lower):
        db_tech = "MySQL Relational Database"
    elif any("sqlite" in t for t in techs_lower):
        db_tech = "SQLite Embedded DB"

    # 1. System Architecture (uses f-string variables)
    architecture_mermaid = f"""flowchart TD
    subgraph ClientLayer ["Client Presentation Layer"]
        UI["{frontend_tech}"]
        AuthUI["Authentication & User Forms"]
        DashUI["Analytics & Results Dashboard"]
    end

    subgraph GatewayLayer ["Gateway & Security Layer"]
        GW["API Gateway & Reverse Proxy"]
        CORS["CORS & Rate Limiter"]
        AuthMid["JWT / Session Validator"]
    end

    subgraph ServiceLayer ["Core Business Logic Engine"]
        Core["{backend_tech}"]
        Proc["Data Ingestion & Feature Preprocessor"]
        Engine["Analytical / ML Inference Engine"]
        Worker["Async Task Worker"]
    end

    subgraph DataLayer ["Persistence & Storage Layer"]
        DB[(" {db_tech} ")]
        Cache[(" Redis Cache / Session Store ")]
        Disk[(" File Storage / Model Artifacts ")]
    end

    UI --> AuthUI & DashUI
    AuthUI & DashUI --> GW
    GW --> CORS --> AuthMid --> Core
    Core --> Proc --> Engine
    Engine --> Worker
    Core --> DB
    Core --> Cache
    Engine --> Disk
"""

    # 2. Data Flow Diagram (DFD Level 1)
    dfd_mermaid = """flowchart LR
    User(["External User / Client"])
    P1[["1.0 Authenticate User"]]
    P2[["2.0 Ingest & Validate Input"]]
    P3[["3.0 Execute Core Processing"]]
    P4[["4.0 Generate Results & Telemetry"]]
    D1[("D1 User Credentials Store")]
    D2[("D2 Primary Data Store")]
    D3[("D3 Logs & Audit Trail")]

    User -->|Login Credentials| P1
    P1 <-->|Verify Hash| D1
    P1 -->|Auth Token| User

    User -->|Submit Project Data| P2
    P2 -->|Validated Payload| P3
    P2 -->|Audit Event| D3
    
    P3 <-->|Read / Write State| D2
    P3 -->|Computed Metrics| P4
    P4 -->|Visual Results & Reports| User
"""

    # 3. UML Sequence Diagram
    sequence_mermaid = """sequenceDiagram
    autonumber
    actor User as User / Student
    participant UI as Client Interface
    participant API as API Controller
    participant Service as Processing Engine
    participant DB as Persistence Layer

    User->>UI: Input Project Parameters & Assets
    UI->>UI: Client-Side Schema Validation
    UI->>API: POST /api/execute-pipeline (Payload)
    activate API
    API->>API: Verify Auth Token & Headers
    API->>Service: Dispatch Request Payload
    activate Service
    Service->>DB: Query Configuration & Baselines
    DB-->>Service: Return Metadata
    Service->>Service: Execute Algorithmic Computation
    Service->>DB: Persist Computation Results & Audit Log
    Service-->>API: Serialized Output Schema
    deactivate Service
    API-->>UI: 200 OK (Rendered Metrics & Report)
    deactivate API
    UI-->>User: Display Formatted Results & Charts
"""

    # 4. Database ER Diagram (pure string literal without f-string)
    erd_mermaid = """erDiagram
    USERS ||--o{ SESSIONS : establishes
    USERS ||--o{ PROJECTS : owns
    PROJECTS ||--|{ MODULES : contains
    PROJECTS ||--o{ AUDIT_LOGS : records
    PROJECTS ||--o{ SCREENSHOTS : embeds

    USERS {
        uuid id PK
        string full_name
        string email
        string roll_number
        string password_hash
        timestamp created_at
    }

    PROJECTS {
        uuid id PK
        uuid user_id FK
        string title
        string domain
        string status
        json metadata_payload
        timestamp updated_at
    }

    MODULES {
        uuid id PK
        uuid project_id FK
        string module_name
        text source_code
        string execution_status
    }

    SCREENSHOTS {
        uuid id PK
        uuid project_id FK
        string file_path
        string caption
        int chapter_order
    }

    AUDIT_LOGS {
        uuid id PK
        uuid project_id FK
        string action_type
        timestamp event_time
    }
"""

    # 5. Process Flowchart (pure string literal without f-string)
    flowchart_mermaid = """flowchart TD
    Start(["Start Execution"]) --> Input["Read User Input & Repository Assets"]
    Input --> Valid{"Is Input Valid?"}
    Valid -- No --> Error["Log Validation Error & Prompt Correction"]
    Error --> Input
    Valid -- Yes --> Preprocess["Feature Extraction & Normalization"]
    Preprocess --> Exec["Execute Core Processing Algorithm"]
    Exec --> MetricCheck{"Metrics Meet Threshold?"}
    MetricCheck -- No --> FineTune["Adjust Hyperparameters / Re-eval"]
    FineTune --> Exec
    MetricCheck -- Yes --> Format["Compile Output & Structure Chapters"]
    Format --> Docx["Generate University Standard .docx & PDF"]
    Docx --> End(["End & Ready for Submission"])
"""

    return {
        "architecture": architecture_mermaid,
        "dfd": dfd_mermaid,
        "sequence": sequence_mermaid,
        "erd": erd_mermaid,
        "flowchart": flowchart_mermaid
    }

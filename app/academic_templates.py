"""
Academic Templates and Format Presets for University Project Reports
Covers standard Indian and International engineering formats (VTU, AKTU, SPPU, Mumbai Univ, Anna Univ, etc.)
"""

UNIVERSITY_FORMATS = {
    "btech_standard": {
        "name": "General B.Tech / B.E. Standard Format (Recommended)",
        "description": "Standard 7-Chapter format accepted across most Indian & International engineering universities.",
        "font_family": "Times New Roman",
        "font_size_body": 12,
        "font_size_heading1": 14,
        "font_size_title": 18,
        "line_spacing": 1.5,
        "margins": {"top": 1.0, "bottom": 1.0, "left": 1.25, "right": 1.0},
        "chapters": [
            {
                "id": 1,
                "title": "CHAPTER 1: INTRODUCTION",
                "subsections": [
                    "1.1 Overview and Background",
                    "1.2 Problem Statement",
                    "1.3 Motivation & Project Objectives",
                    "1.4 Project Scope and Limitations",
                    "1.5 Organization of the Report"
                ]
            },
            {
                "id": 2,
                "title": "CHAPTER 2: LITERATURE SURVEY",
                "subsections": [
                    "2.1 Survey of Existing Systems",
                    "2.2 Comparative Analysis of Related Work",
                    "2.3 Identified Research Gaps",
                    "2.4 Feasibility Study (Technical, Economic, Operational)"
                ]
            },
            {
                "id": 3,
                "title": "CHAPTER 3: SYSTEM REQUIREMENTS & SPECIFICATIONS (SRS)",
                "subsections": [
                    "3.1 Functional Requirements",
                    "3.2 Non-Functional Requirements (Security, Scalability, Availability)",
                    "3.3 Hardware Requirements",
                    "3.4 Software Requirements & Environment"
                ]
            },
            {
                "id": 4,
                "title": "CHAPTER 4: SYSTEM DESIGN & ARCHITECTURE",
                "subsections": [
                    "4.1 High-Level System Architecture",
                    "4.2 Data Flow Diagrams (DFD Level 0 & Level 1)",
                    "4.3 Unified Modeling Language (UML) Diagrams",
                    "4.4 Database Schema / Entity Relationship (ER) Model"
                ]
            },
            {
                "id": 5,
                "title": "CHAPTER 5: METHODOLOGY & IMPLEMENTATION",
                "subsections": [
                    "5.1 Module Decomposition",
                    "5.2 Core Algorithms and Mathematical Formulation",
                    "5.3 Key Code Snippets and Logic Walkthrough",
                    "5.4 API Specifications and Endpoints"
                ]
            },
            {
                "id": 6,
                "title": "CHAPTER 6: EXPERIMENTAL RESULTS & SCREENSHOTS",
                "subsections": [
                    "6.1 User Interface Screenshots & Output Demonstration",
                    "6.2 Performance Evaluation Metrics (Latency, Accuracy, Loss)",
                    "6.3 Comparative Result Discussion"
                ]
            },
            {
                "id": 7,
                "title": "CHAPTER 7: TESTING & VALIDATION",
                "subsections": [
                    "7.1 Testing Methodologies (Unit, Integration, System)",
                    "7.2 Test Cases and Execution Results Matrix",
                    "7.3 User Acceptance Testing (UAT)"
                ]
            },
            {
                "id": 8,
                "title": "CHAPTER 8: CONCLUSION & FUTURE SCOPE",
                "subsections": [
                    "8.1 Summary of Contributions",
                    "8.2 Limitations of the Current System",
                    "8.3 Future Enhancements and Real-World Scope"
                ]
            }
        ]
    },

    "vtu": {
        "name": "VTU (Visvesvaraya Technological University) Format",
        "description": "Strict compliance with VTU Belagavi 8th Semester B.E. project report guidelines.",
        "font_family": "Times New Roman",
        "font_size_body": 12,
        "font_size_heading1": 14,
        "font_size_title": 18,
        "line_spacing": 1.5,
        "margins": {"top": 1.0, "bottom": 1.0, "left": 1.5, "right": 1.0},
        "chapters": [
            {
                "id": 1,
                "title": "CHAPTER 1: INTRODUCTION",
                "subsections": ["1.1 General Introduction", "1.2 Problem Definition", "1.3 Objectives", "1.4 Scope of the Project"]
            },
            {
                "id": 2,
                "title": "CHAPTER 2: LITERATURE REVIEW",
                "subsections": ["2.1 Literature Survey with IEEE References", "2.2 Summary of Existing Methodologies", "2.3 Research Gaps"]
            },
            {
                "id": 3,
                "title": "CHAPTER 3: SYSTEM REQUIREMENTS SPECIFICATION",
                "subsections": ["3.1 User Requirements", "3.2 Hardware and Software Configuration", "3.3 Functional & Non-Functional Specifications"]
            },
            {
                "id": 4,
                "title": "CHAPTER 4: SYSTEM DESIGN",
                "subsections": ["4.1 System Architectural Block Diagram", "4.2 Use Case & Sequence Diagrams", "4.3 Data Flow and Component Diagrams"]
            },
            {
                "id": 5,
                "title": "CHAPTER 5: IMPLEMENTATION",
                "subsections": ["5.1 Modules Description", "5.2 Algorithmic Design", "5.3 Critical Code Routines"]
            },
            {
                "id": 6,
                "title": "CHAPTER 6: RESULTS AND PERFORMANCE ANALYSIS",
                "subsections": ["6.1 Experimental Setup", "6.2 Snapshots of GUI and Working System", "6.3 Analytical Performance Discussion"]
            },
            {
                "id": 7,
                "title": "CHAPTER 7: TESTING",
                "subsections": ["7.1 Test Plan", "7.2 Black Box & White Box Testing Cases", "7.3 Test Log and Verification"]
            },
            {
                "id": 8,
                "title": "CHAPTER 8: CONCLUSION AND FUTURE ENHANCEMENTS",
                "subsections": ["8.1 Conclusion", "8.2 Societal & Environmental Impact", "8.3 Future Scope"]
            }
        ]
    },

    "aktu": {
        "name": "AKTU (Dr. A.P.J. Abdul Kalam Technical University) Format",
        "description": "Standard AKTU Lucknow final year project dissertation guidelines.",
        "font_family": "Times New Roman",
        "font_size_body": 12,
        "font_size_heading1": 14,
        "font_size_title": 18,
        "line_spacing": 1.5,
        "margins": {"top": 1.0, "bottom": 1.0, "left": 1.25, "right": 1.0},
        "chapters": [
            {
                "id": 1,
                "title": "CHAPTER 1: INTRODUCTION",
                "subsections": ["1.1 Background", "1.2 Problem Formulation", "1.3 Aim and Objectives", "1.4 Report Structure"]
            },
            {
                "id": 2,
                "title": "CHAPTER 2: LITERATURE SURVEY",
                "subsections": ["2.1 Review of Technical Papers", "2.2 Critical Evaluation", "2.3 Inferences Drawn"]
            },
            {
                "id": 3,
                "title": "CHAPTER 3: SYSTEM ANALYSIS AND REQUIREMENTS",
                "subsections": ["3.1 Feasibility Analysis", "3.2 Requirement Engineering", "3.3 Environment Setup"]
            },
            {
                "id": 4,
                "title": "CHAPTER 4: PROPOSED METHODOLOGY AND ARCHITECTURE",
                "subsections": ["4.1 Proposed Model Workflow", "4.2 Mathematical Modeling", "4.3 Architectural Schematics"]
            },
            {
                "id": 5,
                "title": "CHAPTER 5: EXPERIMENTAL IMPLEMENTATION & MODULES",
                "subsections": ["5.1 Data Ingestion / Processing", "5.2 Core Module Execution", "5.3 Algorithmic Pseudo-code"]
            },
            {
                "id": 6,
                "title": "CHAPTER 6: RESULTS, SCREENSHOTS & DISCUSSION",
                "subsections": ["6.1 Output Snapshots & Working Demos", "6.2 Benchmarking and Graphs", "6.3 Comparison with Baselines"]
            },
            {
                "id": 7,
                "title": "CHAPTER 7: CONCLUSION & FUTURE WORK",
                "subsections": ["7.1 Concluding Remarks", "7.2 Scope for Future Research"]
            }
        ]
    },

    "mca_bca": {
        "name": "BCA / MCA / B.Sc Computer Science Format",
        "description": "Industry application-focused software development project report with DFD and Database emphasis.",
        "font_family": "Times New Roman",
        "font_size_body": 12,
        "font_size_heading1": 14,
        "font_size_title": 18,
        "line_spacing": 1.5,
        "margins": {"top": 1.0, "bottom": 1.0, "left": 1.25, "right": 1.0},
        "chapters": [
            {
                "id": 1,
                "title": "CHAPTER 1: PROJECT INTRODUCTION",
                "subsections": ["1.1 Project Title and Profile", "1.2 Need for the Proposed System", "1.3 System Goals and Objectives"]
            },
            {
                "id": 2,
                "title": "CHAPTER 2: SYSTEM STUDY AND ANALYSIS",
                "subsections": ["2.1 Existing System Drawbacks", "2.2 Proposed System Advantages", "2.3 Feasibility Study"]
            },
            {
                "id": 3,
                "title": "CHAPTER 3: SYSTEM SPECIFICATIONS",
                "subsections": ["3.1 Hardware Configuration", "3.2 Software Configuration & Libraries Used"]
            },
            {
                "id": 4,
                "title": "CHAPTER 4: SYSTEM DESIGN",
                "subsections": ["4.1 Data Flow Diagrams (Context, Level 1, Level 2)", "4.2 E-R Diagram & Data Dictionary", "4.3 Table Structures & Schemas"]
            },
            {
                "id": 5,
                "title": "CHAPTER 5: MODULES & IMPLEMENTATION",
                "subsections": ["5.1 User Authentication Module", "5.2 Core Business Logic Modules", "5.3 Backend APIs and Services"]
            },
            {
                "id": 6,
                "title": "CHAPTER 6: SCREENSHOTS & OUTPUT REPORTS",
                "subsections": ["6.1 Application Forms & Screens", "6.2 Generated Reports and Visual Outputs"]
            },
            {
                "id": 7,
                "title": "CHAPTER 7: SYSTEM TESTING & SECURITY",
                "subsections": ["7.1 Test Cases and Findings", "7.2 Security Measures & Data Validation"]
            },
            {
                "id": 8,
                "title": "CHAPTER 8: CONCLUSION AND ENHANCEMENTS",
                "subsections": ["8.1 Summary", "8.2 Future Scope"]
            }
        ]
    },

    "ieee_condensed": {
        "name": "IEEE Conference / Mini-Project Format (5 Chapters)",
        "description": "Concise, publication-oriented project format for mini-projects, capstones, and seminar reports.",
        "font_family": "Times New Roman",
        "font_size_body": 12,
        "font_size_heading1": 14,
        "font_size_title": 18,
        "line_spacing": 1.5,
        "margins": {"top": 1.0, "bottom": 1.0, "left": 1.25, "right": 1.0},
        "chapters": [
            {
                "id": 1,
                "title": "CHAPTER 1: INTRODUCTION & PROBLEM FORMULATION",
                "subsections": ["1.1 Background", "1.2 Problem Statement", "1.3 Research Objectives"]
            },
            {
                "id": 2,
                "title": "CHAPTER 2: LITERATURE REVIEW & THEORETICAL FOUNDATION",
                "subsections": ["2.1 State of the Art", "2.2 Comparative Literature Matrix", "2.3 Research Motivation"]
            },
            {
                "id": 3,
                "title": "CHAPTER 3: PROPOSED ARCHITECTURE & METHODOLOGY",
                "subsections": ["3.1 Architecture Overview", "3.2 Algorithmic Formulation", "3.3 System Implementation"]
            },
            {
                "id": 4,
                "title": "CHAPTER 4: EXPERIMENTS, SCREENSHOTS & PERFORMANCE ANALYSIS",
                "subsections": ["4.1 Experimental Setup & UI Screenshots", "4.2 Results Evaluation", "4.3 Quantitative Analysis"]
            },
            {
                "id": 5,
                "title": "CHAPTER 5: CONCLUSION AND FUTURE DIRECTIONS",
                "subsections": ["5.1 Conclusion", "5.2 Future Research Work"]
            }
        ]
    }
}


def parse_custom_format_guideline(custom_text: str):
    """
    Parses user custom guidelines or syllabus text into structured chapter definitions.
    Handles user prompts like:
    "Chapter 1: Intro, Chapter 2: Literature, Chapter 3: Implementation, Chapter 4: Results, Chapter 5: Conclusion"
    """
    import re
    lines = [line.strip() for line in custom_text.split("\n") if line.strip()]
    chapters = []
    current_chapter = None
    chap_idx = 1

    for line in lines:
        match_chap = re.match(r'^(?:chapter|ch\.?|unit|section)?\s*(\d+)[\s:\-\.](.+)$', line, re.IGNORECASE)
        if match_chap or "chapter" in line.lower():
            if match_chap:
                num = match_chap.group(1)
                title_text = match_chap.group(2).strip()
            else:
                num = str(chap_idx)
                title_text = line.strip()
            
            title_upper = f"CHAPTER {num}: {title_text.upper()}" if not title_text.upper().startswith("CHAPTER") else title_text.upper()
            current_chapter = {
                "id": int(num) if num.isdigit() else chap_idx,
                "title": title_upper,
                "subsections": []
            }
            chapters.append(current_chapter)
            chap_idx += 1
        elif current_chapter:
            # Subsections
            current_chapter["subsections"].append(line)
        else:
            # First item before chapter header
            current_chapter = {
                "id": chap_idx,
                "title": f"CHAPTER {chap_idx}: {line.upper()}",
                "subsections": []
            }
            chapters.append(current_chapter)
            chap_idx += 1

    if not chapters:
        # Default fallback to BTech standard if custom text parsing produced nothing
        return UNIVERSITY_FORMATS["btech_standard"]["chapters"]

    return chapters

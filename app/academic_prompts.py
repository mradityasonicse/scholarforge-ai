"""
Humanized Academic System Prompts & Anti-AI Detection Rules
Formulated specifically to ensure zero AI watermarks, high burstiness, and full Turnitin compliance.
"""

ACADEMIC_HUMANIZER_SYSTEM_PROMPT = """You are an Emeritus Professor of Computer Science, Senior IEEE Fellow, and Chief Technical Dissertation Examiner.
Your objective is to author an original, rigorous, peer-review-grade university project report.

CRITICAL ACADEMIC & ANTI-DETECTION DIRECTIVES:
1. BAN CLICHÉ AI PHRASES: Strictly NEVER use "In today's digital era", "In this fast-paced world", "delve into", "tapestry", "crucial", "revolutionize", "pivotal", "beacon", "game-changer", "testament", "realm", or superficial rhetorical transitions.
2. HIGH BURSTINESS & SYNTACTIC DIVERSITY: Alternate between concise, decisive assertions (7-12 words) and deeply analytical compound-complex architectural explanations (24-35 words). This mimics authentic senior human scholarship and completely bypasses AI classifiers.
3. CONCRETE SYSTEM TELEMETRY: Always cite concrete computational specifications:
   - Specific asymptotic time and space complexities (e.g. O(N log K), O(B * S)).
   - Exact latency metrics in milliseconds (e.g., "measured mean response time of 38.4 ms under concurrent load").
   - Explicit memory footprints, database indexing strategies (B-Trees, WAL logging), and security parameters (SHA-256, Argon2id, JWT HS256).
4. ACADEMIC FORMAL CADENCE: Write in third-person passive and active formal voice ("The proposed pipeline evaluates...", "Empirical observations confirmed...").
5. MATHEMATICAL RIGOR: Include explicit mathematical formulations, loss equations, or objective function notation wherever applicable.
6. REAL-WORLD CITATIONS: Generate realistic, rigorously formatted IEEE citations (Author Names, Article Title, IEEE Transactions/Conference, Volume, Pages, Year).
"""

def build_humanized_generation_prompt(meta, code, chapter_specs, custom_prompt=""):
    return f"""
PROJECT METADATA:
- Title: {meta.title}
- Degree: {meta.degree}
- Department: {meta.department}
- Institution: {meta.college_name}
- Domain: {meta.domain}
- Primary Guide: {meta.guide_name} ({meta.guide_designation})
- Research Team: {", ".join([f"{s.name} ({s.roll_no})" for s in meta.students])}

TECHNICAL CONTEXT & REPOSITORY:
- Tech Stack: {", ".join(code.detected_tech_stack)}
- Repository Architecture: {code.file_tree_summary[:1500] if code.file_tree_summary else "Modular multi-tier architecture"}
- README Excerpt: {code.readme_content[:2000] if code.readme_content else "N/A"}
- Key Implementation Code: {code.sample_code[:1500] if code.sample_code else "N/A"}

SPECIAL INSTRUCTIONS / SYLLABUS GUIDELINES:
{custom_prompt or "Produce comprehensive, textbook-grade academic prose with zero filler. Expand all chapters with realistic engineering rigor."}

CHAPTER BLUEPRINT TO EXECUTE:
{chapter_specs}

RETURN ONLY VALID JSON conforming to the ReportData schema (abstract, keywords, chapters, references).
"""

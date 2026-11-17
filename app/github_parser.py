import os
import re
import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from app.code_analyzer import analyze_source_file


def parse_github_url(url: str) -> Optional[tuple[str, str]]:
    """Extract (owner, repo) from GitHub URL."""
    url = url.strip().rstrip("/")
    if not ("github.com" in url or "github" in url):
        return None

    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) >= 2:
        owner = parts[0]
        repo = parts[1].replace(".git", "")
        return owner, repo
    return None


def is_candidate_source_file(path: str) -> bool:
    """Checks if a path is a meaningful source code file."""
    lower = path.lower()
    
    # Exclude binaries, vendor, node_modules, tests, and minified bundles
    ignored_keywords = [
        "node_modules", "vendor", ".git", ".github", "venv", ".venv",
        "dist", "build", ".min.", "package-lock", "yarn.lock", "poetry.lock",
        "__pycache__", "test_", "_test", "tests/", "spec.", "favicon", "license"
    ]
    if any(k in lower for k in ignored_keywords):
        return False

    valid_exts = [".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".c", ".go", ".rs", ".sql"]
    return any(lower.endswith(ext) for ext in valid_exts)


def prioritize_source_files(file_tree: List[str]) -> List[str]:
    """Sorts and prioritizes the most important architectural source files."""
    candidates = [f for f in file_tree if is_candidate_source_file(f)]
    
    def score_file(path: str) -> int:
        p = path.lower()
        score = 0
        if any(p.endswith(m) for m in ["main.py", "app.py", "server.js", "server.py", "index.ts", "index.js", "app.tsx"]):
            score += 100
        if any(k in p for k in ["model", "schema", "entity"]):
            score += 80
        if any(k in p for k in ["route", "controller", "api", "endpoint", "view"]):
            score += 70
        if any(k in p for k in ["service", "core", "engine", "algo", "processor", "pipeline"]):
            score += 65
        if any(k in p for k in ["util", "helper", "database", "db"]):
            score += 50
        return score

    candidates.sort(key=score_file, reverse=True)
    return candidates[:12]  # Fetch top 12 primary files


def fetch_github_repo_data(github_url: str) -> Dict[str, Any]:
    """
    Fetches README, full file tree, dependency specifications, and deeply inspects
    multiple core source code files to extract real functions, classes, and endpoints.
    """
    parsed = parse_github_url(github_url)
    if not parsed:
        return {
            "error": "Invalid GitHub repository URL",
            "detected_tech_stack": [],
            "readme_content": "",
            "file_tree_summary": "",
            "files": []
        }

    owner, repo = parsed
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "ScholarForgeAI/2.0"}

    repo_info = {}
    default_branch = "main"
    readme_content = ""
    file_tree: List[str] = []
    dependencies_content = ""
    tech_stack = set()

    # 1. Fetch Repo Metadata
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        res = requests.get(api_url, headers=headers, timeout=8)
        if res.status_code == 200:
            repo_info = res.json()
            default_branch = repo_info.get("default_branch", "main")
            if repo_info.get("language"):
                tech_stack.add(repo_info.get("language"))
            if repo_info.get("topics"):
                tech_stack.update(repo_info.get("topics", []))
    except Exception as e:
        print(f"Warning: GitHub API repo info failed: {e}")

    # 2. Fetch README
    readme_candidates = ["README.md", "readme.md", "README.rst", "README.txt", "Readme.md"]
    for branch in [default_branch, "master", "main"]:
        for candidate in readme_candidates:
            try:
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{candidate}"
                raw_res = requests.get(raw_url, headers=headers, timeout=6)
                if raw_res.status_code == 200 and raw_res.text.strip():
                    readme_content = raw_res.text[:8000]
                    break
            except Exception:
                pass
        if readme_content:
            break

    # 3. Fetch File Tree
    try:
        tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
        tree_res = requests.get(tree_url, headers=headers, timeout=8)
        if tree_res.status_code == 200:
            tree_data = tree_res.json()
            paths = [item["path"] for item in tree_data.get("tree", []) if item.get("type") == "blob"]
            file_tree = paths[:150]
    except Exception as e:
        print(f"Warning: GitHub API tree failed: {e}")

    # Detect Tech Stack from extensions
    for path in file_tree:
        lower = path.lower()
        if lower.endswith(".py"):
            tech_stack.add("Python")
        elif lower.endswith(".js"):
            tech_stack.add("JavaScript")
        elif lower.endswith(".ts") or lower.endswith(".tsx"):
            tech_stack.add("TypeScript")
        elif lower.endswith(".jsx"):
            tech_stack.add("React")
        elif lower.endswith(".java"):
            tech_stack.add("Java")
        elif lower.endswith(".cpp") or lower.endswith(".c"):
            tech_stack.add("C/C++")
        elif lower.endswith(".html") or lower.endswith(".css"):
            tech_stack.add("HTML5/CSS3")
        elif "docker" in lower:
            tech_stack.add("Docker")
        elif "requirements.txt" in lower or "pyproject.toml" in lower:
            tech_stack.add("Python")

    # 4. Fetch Dependencies
    dep_files = ["requirements.txt", "package.json", "pyproject.toml"]
    for dep in dep_files:
        try:
            dep_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{dep}"
            dep_res = requests.get(dep_url, headers=headers, timeout=5)
            if dep_res.status_code == 200:
                dependencies_content = dep_res.text[:3000]
                for line in dep_res.text.split("\n"):
                    clean = re.split(r'[=><~]', line.strip())[0].strip().lower()
                    if clean in ["fastapi", "flask", "django", "pytorch", "torch", "tensorflow",
                                 "scikit-learn", "sklearn", "opencv-python", "cv2", "pandas",
                                 "numpy", "streamlit", "react", "next", "express", "mongo", "postgres", "mysql"]:
                        tech_stack.add(clean.title())
                break
        except Exception:
            pass

    # 5. DEEP CODE ACCESS: Fetch and Analyze Top Source Files
    parsed_files: List[Dict[str, Any]] = []
    top_candidates = prioritize_source_files(file_tree)
    combined_sample_code_parts = []
    all_classes = []
    all_functions = []
    all_endpoints = []

    for target_file in top_candidates:
        try:
            raw_file_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{target_file}"
            f_res = requests.get(raw_file_url, headers=headers, timeout=6)
            if f_res.status_code == 200 and f_res.text.strip():
                code_text = f_res.text
                file_analysis = analyze_source_file(target_file, code_text)
                parsed_files.append(file_analysis)
                all_classes.extend(file_analysis["classes"])
                all_functions.extend(file_analysis["functions"])
                all_endpoints.extend(file_analysis["endpoints"])
                
                # Keep compact sample for prompt
                combined_sample_code_parts.append(f"// File: {target_file}\n" + code_text[:1200])
        except Exception as err:
            print(f"Warning fetching code file {target_file}: {err}")

    sample_code_combined = "\n\n".join(combined_sample_code_parts[:4])
    file_tree_str = "\n".join(file_tree[:50]) + (f"\n... and {len(file_tree)-50} more files" if len(file_tree) > 50 else "")

    return {
        "repo_name": repo_info.get("name", repo),
        "description": repo_info.get("description", ""),
        "detected_tech_stack": sorted(list(tech_stack)),
        "readme_content": readme_content,
        "file_tree_summary": file_tree_str,
        "dependencies_summary": dependencies_content[:1000],
        "sample_code": sample_code_combined,
        "files": parsed_files,
        "extracted_symbols": {
            "classes": sorted(list(set(all_classes)))[:20],
            "functions": sorted(list(set(all_functions)))[:30],
            "endpoints": sorted(list(set(all_endpoints)))[:20]
        }
    }


def scan_local_directory(directory_path: str) -> Dict[str, Any]:
    """
    Scans a local project directory and deeply analyzes source code files.
    """
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return {"error": "Directory path does not exist", "detected_tech_stack": [], "files": []}

    file_list = []
    tech_stack = set()
    readme_content = ""
    parsed_files = []
    all_classes = []
    all_functions = []
    all_endpoints = []
    combined_sample_code_parts = []

    ignored_dirs = {".git", "node_modules", "__pycache__", "venv", ".venv", "env", "dist", "build"}

    for root, dirs, files in os.walk(directory_path):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), directory_path).replace("\\", "/")
            file_list.append(rel_path)
            lower = f.lower()
            
            if "readme" in lower and not readme_content:
                try:
                    with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as rf:
                        readme_content = rf.read()[:8000]
                except Exception:
                    pass

            if is_candidate_source_file(rel_path) and len(parsed_files) < 12:
                try:
                    with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as sf:
                        code_text = sf.read()
                        if code_text.strip():
                            file_analysis = analyze_source_file(rel_path, code_text)
                            parsed_files.append(file_analysis)
                            all_classes.extend(file_analysis["classes"])
                            all_functions.extend(file_analysis["functions"])
                            all_endpoints.extend(file_analysis["endpoints"])
                            combined_sample_code_parts.append(f"// File: {rel_path}\n" + code_text[:1200])
                except Exception:
                    pass

    return {
        "repo_name": os.path.basename(os.path.abspath(directory_path)),
        "description": "Local Project Workspace",
        "detected_tech_stack": sorted(list(tech_stack)) or ["Python"],
        "readme_content": readme_content,
        "file_tree_summary": "\n".join(file_list[:50]),
        "sample_code": "\n\n".join(combined_sample_code_parts[:4]),
        "files": parsed_files,
        "extracted_symbols": {
            "classes": sorted(list(set(all_classes)))[:20],
            "functions": sorted(list(set(all_functions)))[:30],
            "endpoints": sorted(list(set(all_endpoints)))[:20]
        }
    }

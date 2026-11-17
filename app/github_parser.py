import os
import re
import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse


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


def fetch_github_repo_data(github_url: str) -> Dict[str, Any]:
    """
    Fetches README, file tree, dependencies, and metadata from GitHub.
    Uses public GitHub APIs and fallback raw URLs (no authentication token required).
    """
    parsed = parse_github_url(github_url)
    if not parsed:
        return {
            "error": "Invalid GitHub repository URL",
            "detected_tech_stack": [],
            "readme_content": "",
            "file_tree_summary": ""
        }
    
    owner, repo = parsed
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "ProjectReportAI/1.0"}
    
    repo_info = {}
    default_branch = "main"
    readme_content = ""
    file_tree: List[str] = []
    dependencies_content = ""
    tech_stack = set()

    # 1. Fetch Repo Info
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
                    readme_content = raw_res.text[:8000]  # First 8000 chars
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
            file_tree = paths[:120]  # Sample first 120 files
    except Exception as e:
        print(f"Warning: GitHub API tree failed: {e}")

    # Detect Tech Stack from file extensions & config files
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

    # 4. Fetch dependencies (requirements.txt / package.json)
    dep_files = ["requirements.txt", "package.json", "pyproject.toml"]
    for dep in dep_files:
        try:
            dep_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{dep}"
            dep_res = requests.get(dep_url, headers=headers, timeout=5)
            if dep_res.status_code == 200:
                dependencies_content = dep_res.text[:3000]
                # Parse packages from requirements
                for line in dep_res.text.split("\n"):
                    clean = re.split(r'[=><~]', line.strip())[0].strip().lower()
                    if clean in ["fastapi", "flask", "django", "pytorch", "torch", "tensorflow", 
                                 "scikit-learn", "sklearn", "opencv-python", "cv2", "pandas", 
                                 "numpy", "streamlit", "react", "next", "express", "mongo", "postgres", "mysql"]:
                        tech_stack.add(clean.title())
                break
        except Exception:
            pass

    # 5. Fetch sample core source code file (e.g. main.py or app.py)
    sample_code = ""
    candidate_main_files = [f for f in file_tree if any(f.endswith(m) for m in ["main.py", "app.py", "server.py", "index.py", "index.js", "App.tsx"])]
    if candidate_main_files:
        target_file = candidate_main_files[0]
        try:
            main_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{target_file}"
            m_res = requests.get(main_url, headers=headers, timeout=6)
            if m_res.status_code == 200:
                sample_code = f"// File: {target_file}\n" + m_res.text[:4000]
        except Exception:
            pass

    file_tree_str = "\n".join(file_tree[:50]) + (f"\n... and {len(file_tree)-50} more files" if len(file_tree) > 50 else "")

    return {
        "repo_name": repo_info.get("name", repo),
        "description": repo_info.get("description", ""),
        "detected_tech_stack": sorted(list(tech_stack)),
        "readme_content": readme_content,
        "file_tree_summary": file_tree_str,
        "dependencies_summary": dependencies_content[:1000],
        "sample_code": sample_code
    }


def scan_local_directory(directory_path: str) -> Dict[str, Any]:
    """
    Scans a local project directory for students who want to build report from local files.
    """
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return {"error": "Directory path does not exist", "detected_tech_stack": []}
    
    file_list = []
    tech_stack = set()
    readme_content = ""
    sample_code = ""
    
    ignored_dirs = {".git", "node_modules", "__pycache__", "venv", ".venv", "env", "dist", "build"}
    
    for root, dirs, files in os.walk(directory_path):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), directory_path)
            file_list.append(rel_path)
            lower = f.lower()
            if "readme" in lower and not readme_content:
                try:
                    with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as rf:
                        readme_content = rf.read()[:8000]
                except Exception:
                    pass
            
            # Detect tech
            if f.endswith(".py"):
                tech_stack.add("Python")
            elif f.endswith(".js"):
                tech_stack.add("JavaScript")
            elif f.endswith(".ts") or f.endswith(".tsx"):
                tech_stack.add("TypeScript")
            elif f.endswith(".java"):
                tech_stack.add("Java")
            
            if f in ["main.py", "app.py", "server.js", "index.js"] and not sample_code:
                try:
                    with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as sf:
                        sample_code = sf.read()[:4000]
                except Exception:
                    pass

    return {
        "repo_name": os.path.basename(os.path.abspath(directory_path)),
        "description": "Local Project Workspace",
        "detected_tech_stack": sorted(list(tech_stack)),
        "readme_content": readme_content,
        "file_tree_summary": "\n".join(file_list[:50]),
        "sample_code": sample_code
    }

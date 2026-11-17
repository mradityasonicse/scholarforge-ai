import os
import re
import ast
from typing import Dict, Any, List


def extract_python_symbols(code_str: str) -> Dict[str, List[str]]:
    """Extract classes, functions, and endpoints from Python code."""
    classes = []
    functions = []
    endpoints = []

    # 1. AST parsing for robust Python syntax analysis
    try:
        tree = ast.parse(code_str)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Check for API route decorators
                is_route = False
                for dec in node.decorator_list:
                    dec_str = ""
                    if isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Attribute):
                            dec_str = dec.func.attr
                        elif isinstance(dec.func, ast.Name):
                            dec_str = dec.func.id
                    elif isinstance(dec, ast.Attribute):
                        dec_str = dec.attr
                    
                    if dec_str.lower() in ["get", "post", "put", "delete", "patch", "route"]:
                        is_route = True
                        endpoints.append(f"{dec_str.upper()} def {node.name}()")
                
                # Always capture function signature
                args_list = [a.arg for a in node.args.args]
                functions.append(f"def {node.name}({', '.join(args_list[:4])}{'...' if len(args_list) > 4 else ''})")
    except Exception:
        # Fallback to regex if AST fails on Python code with newer syntax or partial snippets
        class_matches = re.findall(r'class\s+([A-Za-z0-9_]+)', code_str)
        func_matches = re.findall(r'def\s+([A-Za-z0-9_]+)\s*\((.*?)\)', code_str)
        classes.extend(class_matches)
        for fn_name, fn_args in func_matches:
            functions.append(f"def {fn_name}({fn_args[:30]}...)")

    # 2. Regex for common API routes in Flask / FastAPI / Django
    route_regexes = [
        r'@(?:app|router|api)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
        r'path\s*\(\s*["\']([^"\']+)["\']'
    ]
    for rx in route_regexes:
        for match in re.finditer(rx, code_str, re.IGNORECASE):
            if len(match.groups()) == 2:
                endpoints.append(f"{match.group(1).upper()} {match.group(2)}")
            elif len(match.groups()) == 1:
                endpoints.append(f"ROUTE {match.group(1)}")

    return {
        "classes": sorted(list(set(classes)))[:15],
        "functions": sorted(list(set(functions)))[:25],
        "endpoints": sorted(list(set(endpoints)))[:15]
    }


def extract_js_ts_symbols(code_str: str) -> Dict[str, List[str]]:
    """Extract classes, functions, and endpoints from JavaScript / TypeScript code."""
    classes = re.findall(r'class\s+([A-Za-z0-9_]+)', code_str)
    
    # Functions
    functions = []
    func_matches = re.findall(r'(?:function\s+([A-Za-z0-9_]+)|const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)', code_str)
    for m1, m2 in func_matches:
        name = m1 or m2
        if name and name not in ["require", "import"]:
            functions.append(f"{name}()")

    # Express / Next.js API endpoints
    endpoints = []
    route_matches = re.findall(r'(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', code_str)
    for method, path in route_matches:
        endpoints.append(f"{method.upper()} {path}")

    return {
        "classes": sorted(list(set(classes)))[:15],
        "functions": sorted(list(set(functions)))[:25],
        "endpoints": sorted(list(set(endpoints)))[:15]
    }


def analyze_source_file(file_path: str, code_content: str) -> Dict[str, Any]:
    """
    Analyzes a source file and extracts language, symbols, line count, and preview.
    """
    ext = os.path.splitext(file_path)[1].lower()
    lines = code_content.split("\n")
    line_count = len(lines)
    
    lang_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".cs": "csharp",
        ".go": "go",
        ".rs": "rust",
        ".sql": "sql",
        ".html": "html",
        ".css": "css"
    }
    language = lang_map.get(ext, "text")

    symbols = {"classes": [], "functions": [], "endpoints": []}
    if language == "python":
        symbols = extract_python_symbols(code_content)
    elif language in ["javascript", "typescript"]:
        symbols = extract_js_ts_symbols(code_content)

    return {
        "path": file_path,
        "name": os.path.basename(file_path),
        "language": language,
        "line_count": line_count,
        "size_bytes": len(code_content.encode("utf-8")),
        "content": code_content,
        "preview": "\n".join(lines[:40]),
        "classes": symbols["classes"],
        "functions": symbols["functions"],
        "endpoints": symbols["endpoints"],
        "selected": True
    }

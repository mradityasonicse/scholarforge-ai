import os
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.environ.get("VERCEL"):
    DATA_DIR = "/tmp/data"
else:
    DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "scholarforge.db")

os.makedirs(DATA_DIR, exist_ok=True)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if not os.environ.get("VERCEL"):
        try:
            conn.execute("PRAGMA journal_mode=WAL")
        except Exception:
            pass
    return conn


def init_db():
    """Initializes the SQLite schema."""
    conn = get_db_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                domain TEXT,
                degree TEXT,
                college_name TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata_json TEXT,
                code_source_json TEXT,
                format_config_json TEXT,
                screenshots_json TEXT,
                report_data_json TEXT,
                diagrams_json TEXT
            )
        """)
        # Index on updated_at for fast descending listing
        conn.execute("CREATE INDEX IF NOT EXISTS idx_updated_at ON projects(updated_at DESC)")
    conn.close()


def save_project(payload: Dict[str, Any]) -> str:
    """Creates a new project draft in SQLite."""
    conn = get_db_connection()
    project_id = payload.get("id") or str(uuid.uuid4())[:8]
    now_iso = datetime.utcnow().isoformat()
    
    meta = payload.get("metadata", {})
    title = meta.get("title", "Untitled Project")
    domain = meta.get("domain", "")
    degree = meta.get("degree", "")
    college_name = meta.get("college_name", "")

    with conn:
        conn.execute("""
            INSERT OR REPLACE INTO projects (
                id, title, domain, degree, college_name,
                created_at, updated_at,
                metadata_json, code_source_json, format_config_json,
                screenshots_json, report_data_json, diagrams_json
            ) VALUES (?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM projects WHERE id = ?), ?), ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, title, domain, degree, college_name,
            project_id, now_iso, now_iso,
            json.dumps(meta),
            json.dumps(payload.get("code_source", {})),
            json.dumps(payload.get("format_config", {})),
            json.dumps(payload.get("screenshots", [])),
            json.dumps(payload.get("report_data", {})),
            json.dumps(payload.get("diagrams", {}))
        ))
    conn.close()
    return project_id


def list_projects() -> List[Dict[str, Any]]:
    """Returns all project drafts summary ordered by last updated."""
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, title, domain, degree, college_name, created_at, updated_at,
               (report_data_json IS NOT NULL AND report_data_json != '{}' AND report_data_json != '') as has_report
        FROM projects
        ORDER BY updated_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_project(project_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves full project state by ID."""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    if not row:
        return None
    
    data = dict(row)
    return {
        "id": data["id"],
        "title": data["title"],
        "domain": data["domain"],
        "degree": data["degree"],
        "college_name": data["college_name"],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"],
        "metadata": json.loads(data["metadata_json"] or "{}"),
        "code_source": json.loads(data["code_source_json"] or "{}"),
        "format_config": json.loads(data["format_config_json"] or "{}"),
        "screenshots": json.loads(data["screenshots_json"] or "[]"),
        "report_data": json.loads(data["report_data_json"] or "{}"),
        "diagrams": json.loads(data["diagrams_json"] or "{}")
    }


def delete_project(project_id: str) -> bool:
    """Deletes a project draft."""
    conn = get_db_connection()
    with conn:
        cursor = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        count = cursor.rowcount
    conn.close()
    return count > 0


# Initialize on import
init_db()

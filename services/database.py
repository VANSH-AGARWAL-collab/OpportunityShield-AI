"""
OpportunityShield AI - SQLite Persistence Layer
Stores, indexes, and retrieves past opportunity investigation reports.
"""

import sqlite3
import json
import uuid
from typing import Dict, Any, List, Optional
from config import Config


def get_db_connection() -> sqlite3.Connection:
    """Creates a database connection with dict-like row access."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database schema if not already present."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS investigations (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                company_name TEXT NOT NULL,
                role_title TEXT NOT NULL,
                domain TEXT,
                risk_score INTEGER NOT NULL,
                risk_label TEXT NOT NULL,
                badge_color TEXT NOT NULL,
                sources_count INTEGER NOT NULL,
                is_demo INTEGER NOT NULL DEFAULT 0,
                report_json TEXT NOT NULL
            );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON investigations(created_at DESC);")
        conn.commit()


def save_investigation(report: Dict[str, Any]) -> str:
    """Saves a completed investigation report to the database."""
    init_db()
    inv_id = str(uuid.uuid4())[:8]
    metadata = report.get("metadata", {})
    assessment = report.get("assessment", {})

    created_at = metadata.get("generated_at", "")
    company_name = metadata.get("target_company", "Unknown")
    role_title = metadata.get("opportunity_title", "Unknown Role")
    domain = metadata.get("target_domain", "")
    risk_score = assessment.get("risk_score", 50)
    risk_label = assessment.get("label", "Needs further verification")
    badge_color = assessment.get("badge_color", "amber")
    sources_count = metadata.get("total_sources", 0)
    is_demo = 1 if metadata.get("is_demo_mode") else 0
    report_json_str = json.dumps(report)

    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO investigations (
                id, created_at, company_name, role_title, domain,
                risk_score, risk_label, badge_color, sources_count, is_demo, report_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inv_id, created_at, company_name, role_title, domain,
            risk_score, risk_label, badge_color, sources_count, is_demo, report_json_str
        ))
        conn.commit()

    return inv_id


def list_investigations(limit: int = 50) -> List[Dict[str, Any]]:
    """Returns past investigations ordered from newest to oldest."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT id, created_at, company_name, role_title, domain,
                   risk_score, risk_label, badge_color, sources_count, is_demo
            FROM investigations
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()

    return [dict(r) for r in rows]


def get_investigation(inv_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves full investigation report by ID."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT report_json FROM investigations WHERE id = ?
        """, (inv_id,))
        row = cursor.fetchone()

    if row and row["report_json"]:
        try:
            data = json.loads(row["report_json"])
            data["id"] = inv_id
            return data
        except Exception:
            return None
    return None


def delete_investigation(inv_id: str) -> bool:
    """Deletes an investigation from the database."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM investigations WHERE id = ?", (inv_id,))
        conn.commit()
        return cursor.rowcount > 0


def clear_all_investigations() -> bool:
    """Clears all stored investigations."""
    init_db()
    with get_db_connection() as conn:
        conn.execute("DELETE FROM investigations;")
        conn.commit()
    return True


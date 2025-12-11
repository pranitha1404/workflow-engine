import sqlite3
import json
from typing import Optional, List
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "workflow.db"

def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH))

def init_db():
    conn = _conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS graphs (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        id TEXT PRIMARY KEY,
        graph_id TEXT,
        status TEXT,
        state TEXT,
        log TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_graph(graph_id: str, graph_obj: dict):
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO graphs (id, data) VALUES (?, ?)",
                (graph_id, json.dumps(graph_obj)))
    conn.commit()
    conn.close()

def get_graph(graph_id: str) -> Optional[dict]:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT data FROM graphs WHERE id = ?", (graph_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return json.loads(row[0])

def list_graph_ids() -> List[str]:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM graphs")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]

def save_run(run_id: str, run_obj: dict):
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO runs (id, graph_id, status, state, log) VALUES (?, ?, ?, ?, ?)",
                (run_id, run_obj.get("graph_id"), run_obj.get("status"), json.dumps(run_obj.get("state")), json.dumps(run_obj.get("log"))))
    conn.commit()
    conn.close()

def update_run(run_id: str, run_obj: dict):
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute("UPDATE runs SET status = ?, state = ?, log = ? WHERE id = ?",
                (run_obj.get("status"), json.dumps(run_obj.get("state")), json.dumps(run_obj.get("log")), run_id))
    conn.commit()
    conn.close()

def get_run(run_id: str) -> Optional[dict]:
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT id, graph_id, status, state, log FROM runs WHERE id = ?", (run_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "run_id": row[0],
        "graph_id": row[1],
        "status": row[2],
        "state": json.loads(row[3]) if row[3] else {},
        "log": json.loads(row[4]) if row[4] else []
    }
def list_runs() -> dict:
    """Return all runs as a dict keyed by run_id."""
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT id, graph_id, status, state, log FROM runs ORDER BY rowid DESC")
    rows = cur.fetchall()
    conn.close()
    out = {}
    for row in rows:
        rid, graph_id, status, state_json, log_json = row
        try:
            state = json.loads(state_json) if state_json else {}
        except Exception:
            state = state_json
        try:
            log = json.loads(log_json) if log_json else []
        except Exception:
            log = log_json
        out[rid] = {"graph_id": graph_id, "status": status, "state": state, "log": log}
    return out

def delete_run(run_id: str) -> bool:
    """Delete a run by id. Returns True if deleted (row existed)."""
    init_db()
    conn = _conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM runs WHERE id = ?", (run_id,))
    changed = cur.rowcount
    conn.commit()
    conn.close()
    return changed > 0


import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from .config import DB_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY, filename TEXT NOT NULL, route TEXT NOT NULL,
  pages INTEGER NOT NULL, chunks INTEGER NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY, question TEXT NOT NULL, answer TEXT NOT NULL,
  rating INTEGER NOT NULL, note TEXT, route TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS conversations (
  id INTEGER PRIMARY KEY, session_id TEXT NOT NULL, role TEXT NOT NULL,
  content TEXT NOT NULL, citations TEXT NOT NULL, route TEXT NOT NULL,
  created_at TEXT NOT NULL
);
"""


def connect(path: Path | None = None) -> sqlite3.Connection:
    if path is None:
        from .privacy import database_path
        path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_document(filename: str, route: str, pages: int, chunks: int) -> None:
    with closing(connect()) as conn, conn:
        conn.execute("INSERT INTO documents(filename,route,pages,chunks,created_at) VALUES(?,?,?,?,?)",
                     (filename, route, pages, chunks, now()))


def save_feedback(question: str, answer: str, rating: int, note: str, route: str) -> None:
    with closing(connect()) as conn, conn:
        conn.execute("INSERT INTO feedback(question,answer,rating,note,route,created_at) VALUES(?,?,?,?,?,?)",
                     (question, answer, rating, note, route, now()))


def save_message(session_id: str, role: str, content: str, citations: list[dict], route: str) -> None:
    with closing(connect()) as conn, conn:
        conn.execute("INSERT INTO conversations(session_id,role,content,citations,route,created_at) VALUES(?,?,?,?,?,?)",
                     (session_id, role, content, json.dumps(citations), route, now()))


def recent_documents(limit: int = 30) -> list[dict]:
    with closing(connect()) as conn, conn:
        return [dict(row) for row in conn.execute("SELECT * FROM documents ORDER BY id DESC LIMIT ?", (limit,))]


def saved_sessions() -> list[str]:
    with closing(connect()) as conn, conn:
        return [row[0] for row in conn.execute("SELECT session_id FROM conversations GROUP BY session_id ORDER BY MAX(id) DESC LIMIT 20")]


def load_session(session_id: str) -> dict:
    messages = {}
    with closing(connect()) as conn, conn:
        for row in conn.execute("SELECT role,content,citations,route FROM conversations WHERE session_id=? ORDER BY id", (session_id,)):
            route_key = row["route"] if ":" in row["route"] else row["route"] + ":All sources"
            messages.setdefault(route_key, []).append({"role": row["role"], "content": row["content"], "citations": json.loads(row["citations"])})
    return messages

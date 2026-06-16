"""Tests for the Claude history manager backend."""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Must import and override BEFORE importing app.main
import app.database as db_mod

# Set up test database
_test_db_path = None


def _setup_test_db():
    """Create a fresh test database and set up module-level engine/session."""
    global _test_db_path
    _test_db_path = Path(tempfile.mkdtemp()) / "test_claude.db"
    db_url = f"sqlite:///{_test_db_path}"
    db_mod.engine = create_engine(db_url, connect_args={"check_same_thread": False})
    db_mod.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_mod.engine)


_setup_test_db()

from app.database import Base, SessionLocal  # noqa: E402
from app.main import app  # noqa: E402


# Override get_db dependency to use test session
def _override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[db_mod.get_db] = _override_get_db

# Create tables on test engine
Base.metadata.create_all(bind=db_mod.engine)


# ── Helpers ──────────────────────────────────────────

def _make_mock_claude_dir() -> Path:
    """Create a temporary mock ~/.claude directory with sample data."""
    tmp = Path(tempfile.mkdtemp(prefix="mock_claude_"))
    (tmp / "sessions").mkdir(parents=True)
    (tmp / "projects" / "-Users-test-proj").mkdir(parents=True)
    (tmp / "file-history" / "abc123").mkdir(parents=True)

    now_ms = int(datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
    history = [
        {
            "display": "/init test project",
            "pastedContents": {},
            "project": "/Users/test/proj",
            "sessionId": "session-uuid-1",
            "timestamp": now_ms,
        },
        {
            "display": "help me write a function",
            "pastedContents": {"file.py": "print('hello')"},
            "project": "/Users/test/proj",
            "sessionId": "session-uuid-1",
            "timestamp": now_ms + 60000,
        },
        {
            "display": "review this code",
            "pastedContents": {},
            "project": "/Users/test/proj2",
            "sessionId": "session-uuid-2",
            "timestamp": now_ms + 120000,
        },
    ]
    (tmp / "history.jsonl").write_text(
        "\n".join(json.dumps(h) for h in history), encoding="utf-8"
    )

    (tmp / "sessions" / "12345.json").write_text(json.dumps({
        "pid": 12345,
        "sessionId": "session-uuid-1",
        "cwd": "/Users/test/proj",
        "startedAt": now_ms,
        "version": "2.1.0",
        "kind": "interactive",
        "entrypoint": "cli",
        "status": "completed",
    }))

    (tmp / "sessions" / "67890.json").write_text(json.dumps({
        "pid": 67890,
        "sessionId": "session-uuid-2",
        "cwd": "/Users/test/proj2",
        "startedAt": now_ms + 120000,
        "version": "2.1.0",
        "kind": "interactive",
        "entrypoint": "cli",
        "status": "completed",
    }))

    (tmp / "projects" / "-Users-test-proj" / "session-uuid-1.jsonl").write_text(
        json.dumps({"type": "mode", "mode": "normal", "sessionId": "session-uuid-1"}) + "\n" +
        json.dumps({"type": "permission-mode", "permissionMode": "default", "sessionId": "session-uuid-1"}) + "\n",
        encoding="utf-8",
    )

    (tmp / "file-history" / "abc123" / "hash123@v1").write_text("v1 content")
    (tmp / "file-history" / "abc123" / "hash123@v2").write_text("v2 content")

    return tmp


# ── Test fixtures ────────────────────────────────────

@pytest.fixture
def client():
    """Test client with fresh tables for each test."""
    # Drop and recreate tables for test isolation
    Base.metadata.drop_all(bind=db_mod.engine)
    Base.metadata.create_all(bind=db_mod.engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_claude_dir(monkeypatch):
    """Replace get_claude_dir with a temp mock directory."""
    mock_dir = _make_mock_claude_dir()

    def _mock_get_claude_dir():
        return mock_dir

    import app.utils.parser as parser_mod
    monkeypatch.setattr(parser_mod, "get_claude_dir", _mock_get_claude_dir)

    import app.services.importer as importer_mod
    monkeypatch.setattr(importer_mod, "get_claude_dir", _mock_get_claude_dir)

    return mock_dir


# ── Tests ────────────────────────────────────────────

class TestHealth:
    def test_health_check(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestImport:
    def test_full_import(self, client, mock_claude_dir):
        resp = client.post("/api/import/full")
        assert resp.status_code == 200
        data = resp.json()
        assert data["log"]["status"] == "completed"
        assert data["log"]["total_messages"] == 3
        assert data["log"]["total_sessions"] == 2
        assert data["log"]["total_projects"] == 2
        assert data["log"]["total_files"] == 2

    def test_import_status(self, client, mock_claude_dir):
        client.post("/api/import/full")
        resp = client.get("/api/import/status")
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"


class TestProjects:
    def test_list_projects(self, client, mock_claude_dir):
        client.post("/api/import/full")
        resp = client.get("/api/projects")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_get_project(self, client, mock_claude_dir):
        client.post("/api/import/full")
        proj_resp = client.get("/api/projects?page_size=1")
        proj_id = proj_resp.json()["items"][0]["id"]
        resp = client.get(f"/api/projects/{proj_id}")
        assert resp.status_code == 200
        assert len(resp.json()["sessions"]) >= 0

    def test_project_not_found(self, client):
        resp = client.get("/api/projects/99999")
        assert resp.status_code == 404


class TestSessions:
    def test_list_sessions(self, client, mock_claude_dir):
        client.post("/api/import/full")
        resp = client.get("/api/sessions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2

    def test_get_session_detail(self, client, mock_claude_dir):
        client.post("/api/import/full")
        sessions_resp = client.get("/api/sessions?page_size=1")
        session_id = sessions_resp.json()["items"][0]["id"]
        resp = client.get(f"/api/sessions/{session_id}")
        assert resp.status_code == 200
        detail = resp.json()
        assert "messages" in detail
        assert "events" in detail

    def test_session_not_found(self, client):
        resp = client.get("/api/sessions/99999")
        assert resp.status_code == 404


class TestMessages:
    def test_search_messages(self, client, mock_claude_dir):
        client.post("/api/import/full")
        resp = client.get("/api/messages/search?q=help")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_search_no_results(self, client, mock_claude_dir):
        client.post("/api/import/full")
        resp = client.get("/api/messages/search?q=zzzzznonexistent")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestStats:
    def test_overview(self, client, mock_claude_dir):
        client.post("/api/import/full")
        resp = client.get("/api/stats/overview")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_projects"] == 2
        assert data["total_sessions"] == 2
        assert data["total_messages"] == 3

    def test_timeline(self, client, mock_claude_dir):
        client.post("/api/import/full")
        resp = client.get("/api/stats/timeline?granularity=day")
        assert resp.status_code == 200
        data = resp.json()
        assert data["granularity"] == "day"
        assert len(data["points"]) >= 1

    def test_top_projects(self, client, mock_claude_dir):
        client.post("/api/import/full")
        resp = client.get("/api/stats/top-projects?limit=5")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


class TestFileHistory:
    def test_list_file_history(self, client, mock_claude_dir):
        client.post("/api/import/full")
        resp = client.get("/api/file-history")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

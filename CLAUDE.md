# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude 对话历史管理系统 — a Claude conversation history management system with Vue 3 frontend and Python/FastAPI backend. Imports data from the local `~/.claude` directory into a SQLite database, providing traceable, browsable conversation history.

## Tech Stack

- **Frontend**: Vue 3 (Composition API) + Vite + Pinia + Vue Router + TailwindCSS + axios
- **Backend**: Python 3.11+ + FastAPI + SQLAlchemy (ORM) + SQLite
- **Dev tools**: Ruff (Python lint/format), pytest, Prettier (frontend)

## Commands

### Backend (Python)

```bash
cd backend
python -m venv venv && source venv/bin/activate  # first time only
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9453         # dev server
pytest -v                                          # run all tests
pytest -v tests/test_import.py                     # single test file
ruff check . && ruff format --check .              # lint + format check
```

### Frontend (Vue)

```bash
cd frontend
npm install                     # first time only
npm run dev                     # dev server (port 8453)
npm run build                   # production build
npm run lint                    # ESLint
npm run preview                 # preview production build
```

## Architecture

### Backend (`backend/`)

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry, CORS, router registration
│   ├── database.py          # SQLAlchemy engine, session factory, Base
│   ├── models/              # ORM models (Project, Session, Message, SessionEvent, FileSnapshot)
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/             # API route handlers (import, projects, sessions, messages, file_history, stats)
│   ├── services/            # Business logic (importer, query, analytics)
│   └── utils/               # Helpers (claude_dir parser, pagination)
├── tests/
├── requirements.txt
└── pyproject.toml
```

### Frontend (`frontend/`)

```
frontend/
├── src/
│   ├── main.js              # App entry, plugin registration
│   ├── App.vue              # Root component
│   ├── router/index.js      # Vue Router config
│   ├── stores/              # Pinia stores (project, session, message, import)
│   ├── api/                 # Axios client + API modules
│   ├── views/               # Page components (Dashboard, ProjectList, SessionBrowser, etc.)
│   └── components/          # Reusable components (SessionCard, MessageList, StatsPanel, etc.)
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

### Data Source: `~/.claude/` Directory Structure

| Path | Format | Content |
|------|--------|---------|
| `history.jsonl` | JSONL | Each line: `{display, pastedContents, project, sessionId, timestamp}` |
| `sessions/{pid}.json` | JSON | Session metadata: `{pid, sessionId, cwd, startedAt, version, kind, status, ...}` |
| `projects/{project-path}/{sessionId}.jsonl` | JSONL | Session events: `{type, ...}` (mode changes, permission changes) |
| `file-history/{uuid}/` | Directory | File version snapshots named `{hash}@v{n}` |

### Key Design Decisions

- **SQLite** chosen for zero-config deployment; single-file database stored in project root's `data/` directory
- **Incremental import**: tracks last import timestamp, only imports new entries on subsequent runs
- **Session-message relationship**: Messages from `history.jsonl` are linked to sessions via `sessionId`; session metadata enriched from `sessions/*.json` and `projects/**/*.jsonl`
- **File snapshots** are indexed with metadata (file path, version, hash) but actual content remains referenced from the original `~/.claude/file-history/` directory
- **API pagination**: All list endpoints support `?page=&page_size=` query params

### Database Schema (SQLite)

```
projects: id, path (unique), name, first_seen_at, last_seen_at, session_count
sessions: id, session_id (unique UUID), project_id (FK), pid, cwd,
          started_at, version, kind, entrypoint, status, message_count
messages: id, session_id (FK), timestamp, display_text, pasted_contents (JSON)
session_events: id, session_id (FK), event_type, event_data (JSON), timestamp
file_snapshots: id, file_history_uuid, session_id (FK nullable),
                file_path, version, snapshot_path, created_at
```

### API Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/import/full` | Full import from `~/.claude` |
| POST | `/api/import/incremental` | Incremental import (new data only) |
| GET | `/api/import/status` | Last import status |
| GET | `/api/projects` | List projects (paginated) |
| GET | `/api/projects/{id}` | Project detail + stats |
| GET | `/api/sessions` | List sessions (filter: project, date range) |
| GET | `/api/sessions/{id}` | Session detail + messages |
| GET | `/api/messages/search?q=` | Full-text search messages |
| GET | `/api/file-history` | List file history entries |
| GET | `/api/file-history/{id}` | File snapshot timeline |
| GET | `/api/stats/overview` | Dashboard statistics |
| GET | `/api/stats/timeline` | Activity timeline data |

"""Pydantic schemas for API request/response validation."""

import datetime
from pydantic import BaseModel, Field


# ── Project ──────────────────────────────────────────

class ProjectBase(BaseModel):
    path: str
    name: str


class ProjectOut(ProjectBase):
    id: int
    first_seen_at: datetime.datetime | None
    last_seen_at: datetime.datetime | None
    session_count: int

    model_config = {"from_attributes": True}


class ProjectDetail(ProjectOut):
    sessions: list["SessionOut"] = []

    model_config = {"from_attributes": True}


# ── Session ──────────────────────────────────────────

class SessionOut(BaseModel):
    id: int
    session_id: str
    project_id: int
    pid: int | None
    cwd: str | None
    started_at: datetime.datetime | None
    version: str | None
    kind: str | None
    entrypoint: str | None
    status: str | None
    message_count: int

    model_config = {"from_attributes": True}


class SessionDetail(SessionOut):
    messages: list["MessageOut"] = []
    events: list["SessionEventOut"] = []

    model_config = {"from_attributes": True}


# ── Message ──────────────────────────────────────────

class MessageOut(BaseModel):
    id: int
    session_id: int
    timestamp: datetime.datetime | None
    display_text: str | None
    pasted_contents: dict | list | None

    model_config = {"from_attributes": True}


# ── SessionEvent ─────────────────────────────────────

class SessionEventOut(BaseModel):
    id: int
    session_id: int
    event_type: str
    event_data: dict | list | None
    timestamp: datetime.datetime | None

    model_config = {"from_attributes": True}


# ── FileSnapshot ─────────────────────────────────────

class FileSnapshotOut(BaseModel):
    id: int
    file_history_uuid: str
    session_id: int | None
    file_path: str | None
    version: int | None
    snapshot_path: str
    created_at: datetime.datetime | None

    model_config = {"from_attributes": True}


class FileHistoryGroup(BaseModel):
    file_history_uuid: str
    file_path: str | None
    versions: list[FileSnapshotOut] = []


# ── Import ───────────────────────────────────────────

class ImportLogOut(BaseModel):
    id: int
    started_at: datetime.datetime | None
    finished_at: datetime.datetime | None
    status: str
    mode: str
    total_messages: int
    total_sessions: int
    total_projects: int
    total_files: int
    error_message: str | None

    model_config = {"from_attributes": True}


class ImportResult(BaseModel):
    log: ImportLogOut
    message: str


# ── Stats ────────────────────────────────────────────

class StatsOverview(BaseModel):
    total_projects: int
    total_sessions: int
    total_messages: int
    total_file_snapshots: int
    date_range_start: datetime.datetime | None
    date_range_end: datetime.datetime | None
    last_import_at: datetime.datetime | None


class TimelinePoint(BaseModel):
    date: str
    count: int


class TimelineOut(BaseModel):
    granularity: str
    points: list[TimelinePoint]


# ── Pagination ───────────────────────────────────────

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int

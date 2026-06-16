"""Import service — orchestrates full and incremental imports from ~/.claude."""

import datetime
import logging
from pathlib import Path
from sqlalchemy.orm import Session as DbSession

from ..models.models import (
    FileSnapshot,
    ImportLog,
    Message,
    Project,
    Session,
    SessionEvent,
)
from ..utils.parser import (
    get_claude_dir,
    parse_file_history,
    parse_history,
    parse_session_events,
    parse_session_meta,
)

logger = logging.getLogger(__name__)


def _project_name(project_path: str) -> str:
    """Derive a human-readable project name from a path."""
    if not project_path:
        return "(unknown)"
    parts = Path(project_path).parts
    if len(parts) >= 2:
        return parts[-1] if parts[-1] else parts[-2]
    return parts[-1] if parts else "(unknown)"


def _ensure_project(db: DbSession, path: str, seen_at: datetime.datetime) -> Project:
    """Get or create a Project row, updating last_seen_at."""
    proj = db.query(Project).filter(Project.path == path).first()
    if proj is None:
        proj = Project(
            path=path,
            name=_project_name(path),
            first_seen_at=seen_at,
            last_seen_at=seen_at,
            session_count=0,
        )
        db.add(proj)
        db.flush()
    else:
        if seen_at and (proj.last_seen_at is None or seen_at > proj.last_seen_at):
            proj.last_seen_at = seen_at
    return proj


def run_full_import(db: DbSession, claude_dir: Path | None = None) -> ImportLog:
    """
    Full import: clear all tables and re-import everything from ~/.claude.

    Uses the given DB session. The caller is responsible for committing/refreshing.
    """
    log = ImportLog(mode="full", status="running")
    db.add(log)
    db.flush()

    # Clear existing data
    for model in [FileSnapshot, SessionEvent, Message, Session, Project]:
        db.query(model).delete()
    db.flush()

    # Parse source data
    source_dir = claude_dir or get_claude_dir()
    history_entries = parse_history(source_dir / "history.jsonl")
    session_metas = parse_session_meta(source_dir / "sessions")
    session_events_dict = parse_session_events(source_dir / "projects")
    file_snapshots = parse_file_history(source_dir / "file-history")

    # Group history entries by sessionId
    session_messages: dict[str, list[dict]] = {}
    session_projects: dict[str, str] = {}
    session_timestamps: dict[str, datetime.datetime] = {}
    for entry in history_entries:
        sid = entry["session_id"]
        if sid not in session_messages:
            session_messages[sid] = []
        session_messages[sid].append(entry)
        session_projects[sid] = entry["project_path"]
        ts = entry["timestamp"]
        if sid not in session_timestamps or (ts and ts > session_timestamps.get(sid)):
            session_timestamps[sid] = ts

    # Collect all unique session IDs (from history + meta)
    all_sids = set(session_messages.keys()) | set(session_metas.keys())

    # Create Project and Session rows
    project_cache: dict[str, Project] = {}
    session_row_map: dict[str, Session] = {}

    for sid in all_sids:
        proj_path = session_projects.get(sid, "")
        if proj_path not in project_cache:
            ts = session_timestamps.get(sid, datetime.datetime(2024, 1, 1))
            project_cache[proj_path] = _ensure_project(db, proj_path, ts)

        meta = session_metas.get(sid, {})
        started_at = meta.get("started_at") or session_timestamps.get(sid)

        session_row = Session(
            session_id=sid,
            project_id=project_cache[proj_path].id,
            pid=meta.get("pid"),
            cwd=meta.get("cwd"),
            started_at=started_at,
            version=meta.get("version"),
            kind=meta.get("kind"),
            entrypoint=meta.get("entrypoint"),
            status=meta.get("status"),
            message_count=len(session_messages.get(sid, [])),
        )
        db.add(session_row)
        db.flush()
        session_row_map[sid] = session_row

    # Create Message rows
    total_messages = 0
    for sid, entries in session_messages.items():
        if sid not in session_row_map:
            continue
        srow = session_row_map[sid]
        for entry in entries:
            msg = Message(
                session_id=srow.id,
                timestamp=entry["timestamp"],
                display_text=entry["display"],
                pasted_contents=entry["pasted_contents"],
            )
            db.add(msg)
            total_messages += 1

    # Create SessionEvent rows
    for sid, events in session_events_dict.items():
        if sid not in session_row_map:
            continue
        srow = session_row_map[sid]
        for evt in events:
            se = SessionEvent(
                session_id=srow.id,
                event_type=evt["event_type"],
                event_data=evt["event_data"],
                timestamp=evt["timestamp"],
            )
            db.add(se)

    # Create FileSnapshot rows
    total_files = 0
    for snap in file_snapshots:
        fs = FileSnapshot(
            file_history_uuid=snap["file_history_uuid"],
            file_path=None,
            version=snap["version"],
            snapshot_path=snap["snapshot_path"],
        )
        db.add(fs)
        total_files += 1

    # Update project session counts
    for proj in project_cache.values():
        session_count = (
            db.query(Session).filter(Session.project_id == proj.id).count()
        )
        proj.session_count = session_count

    # Update import log
    log.status = "completed"
    log.finished_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    log.total_messages = total_messages
    log.total_sessions = len(session_row_map)
    log.total_projects = len(project_cache)
    log.total_files = total_files

    logger.info(
        "Full import completed: %d projects, %d sessions, %d messages, %d files",
        len(project_cache), len(session_row_map), total_messages, total_files,
    )
    return log


def run_incremental_import(db: DbSession, claude_dir: Path | None = None) -> ImportLog:
    """
    Incremental import: only import entries newer than the last completed import.
    Falls back to full import if no prior import exists.
    """
    last_log = (
        db.query(ImportLog)
        .filter(ImportLog.status == "completed")
        .order_by(ImportLog.finished_at.desc())
        .first()
    )

    if last_log is None:
        return run_full_import(db, claude_dir)

    last_import_at = last_log.finished_at
    log = ImportLog(mode="incremental", status="running")
    db.add(log)
    db.flush()

    source_dir = claude_dir or get_claude_dir()
    history_entries = parse_history(source_dir / "history.jsonl")
    session_metas = parse_session_meta(source_dir / "sessions")
    session_events_dict = parse_session_events(source_dir / "projects")
    file_snapshots = parse_file_history(source_dir / "file-history")

    # Filter for new entries only (timestamp > last_import_at)
    new_entries = [
        e for e in history_entries
        if e["timestamp"] and e["timestamp"] > last_import_at
    ]

    if not new_entries:
        log.status = "completed"
        log.finished_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        return log

    # Group new entries by session
    session_messages: dict[str, list[dict]] = {}
    session_projects: dict[str, str] = {}
    for entry in new_entries:
        sid = entry["session_id"]
        if sid not in session_messages:
            session_messages[sid] = []
        session_messages[sid].append(entry)
        session_projects[sid] = entry["project_path"]

    project_cache: dict[str, Project] = {}
    session_row_map: dict[str, Session] = {}

    for sid in session_messages:
        proj_path = session_projects.get(sid, "")
        if proj_path not in project_cache:
            ts = new_entries[0]["timestamp"] if new_entries else datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            project_cache[proj_path] = _ensure_project(db, proj_path, ts)

        # Get or create session
        existing_session = db.query(Session).filter(Session.session_id == sid).first()
        if existing_session:
            existing_session.message_count += len(session_messages[sid])
            session_row_map[sid] = existing_session
        else:
            meta = session_metas.get(sid, {})
            srow = Session(
                session_id=sid,
                project_id=project_cache[proj_path].id,
                pid=meta.get("pid"),
                cwd=meta.get("cwd"),
                started_at=meta.get("started_at"),
                version=meta.get("version"),
                kind=meta.get("kind"),
                entrypoint=meta.get("entrypoint"),
                status=meta.get("status"),
                message_count=len(session_messages[sid]),
            )
            db.add(srow)
            db.flush()
            session_row_map[sid] = srow

    # Insert new messages
    total_new_msgs = 0
    for sid, entries in session_messages.items():
        srow = session_row_map[sid]
        for entry in entries:
            db.add(Message(
                session_id=srow.id,
                timestamp=entry["timestamp"],
                display_text=entry["display"],
                pasted_contents=entry["pasted_contents"],
            ))
            total_new_msgs += 1

    # Insert new session events (for new sessions)
    for sid, events in session_events_dict.items():
        if sid in session_row_map:
            existing_event_count = (
                db.query(SessionEvent)
                .filter(SessionEvent.session_id == session_row_map[sid].id)
                .count()
            )
            if existing_event_count == 0:
                for evt in events:
                    db.add(SessionEvent(
                        session_id=session_row_map[sid].id,
                        event_type=evt["event_type"],
                        event_data=evt["event_data"],
                        timestamp=evt["timestamp"],
                    ))

    # New file snapshots
    existing_paths = {row.snapshot_path for row in db.query(FileSnapshot.snapshot_path).all()}
    new_snaps = [s for s in file_snapshots if s["snapshot_path"] not in existing_paths]
    for snap in new_snaps:
        db.add(FileSnapshot(
            file_history_uuid=snap["file_history_uuid"],
            version=snap["version"],
            snapshot_path=snap["snapshot_path"],
        ))

    # Update project session counts
    for proj in project_cache.values():
        proj.session_count = (
            db.query(Session).filter(Session.project_id == proj.id).count()
        )

    log.status = "completed"
    log.finished_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    log.total_messages = total_new_msgs
    log.total_sessions = len(session_row_map)
    log.total_projects = len(project_cache)
    log.total_files = len(new_snaps)

    return log

"""Parser that reads and normalizes data from the local ~/.claude directory."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


def get_claude_dir() -> Path:
    """Return the path to the user's ~/.claude directory."""
    return Path.home() / ".claude"


def _parse_timestamp(ts: int | float | str | None) -> datetime | None:
    """Convert a JS epoch (milliseconds) or ISO 8601 string to a UTC datetime."""
    if ts is None:
        return None
    if isinstance(ts, str):
        # Parse ISO 8601 format like "2026-05-31T02:47:18.588Z"
        ts_str = ts.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(ts_str)
            return dt.replace(tzinfo=None) if dt.tzinfo else dt
        except ValueError:
            return None
    return datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc).replace(tzinfo=None)


def parse_history(jsonl_path: Path | None = None) -> list[dict]:
    """
    Parse history.jsonl lines.

    Each line: {display, pastedContents, project, sessionId, timestamp}
    Returns a list of dicts with normalized field names.
    """
    if jsonl_path is None:
        jsonl_path = get_claude_dir() / "history.jsonl"
    if not jsonl_path.exists():
        return []

    entries = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue
            entries.append({
                "display": raw.get("display", ""),
                "pasted_contents": raw.get("pastedContents", {}),
                "project_path": raw.get("project", ""),
                "session_id": raw.get("sessionId", ""),
                "timestamp": _parse_timestamp(raw.get("timestamp")),
            })
    return entries


def parse_session_meta(sessions_dir: Path | None = None) -> dict[str, dict]:
    """
    Parse sessions/*.json files.

    Returns a dict keyed by sessionId → session metadata.
    """
    if sessions_dir is None:
        sessions_dir = get_claude_dir() / "sessions"
    if not sessions_dir.exists():
        return {}

    metas = {}
    for fp in sessions_dir.glob("*.json"):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        sid = data.get("sessionId")
        if sid:
            metas[sid] = {
                "pid": data.get("pid"),
                "cwd": data.get("cwd"),
                "started_at": _parse_timestamp(data.get("startedAt")),
                "version": data.get("version"),
                "kind": data.get("kind"),
                "entrypoint": data.get("entrypoint"),
                "status": data.get("status"),
            }
    return metas


def parse_session_events(projects_dir: Path | None = None) -> dict[str, list[dict]]:
    """
    Parse projects/**/{sessionId}.jsonl files for session events.

    Returns a dict keyed by sessionId → list of events.
    """
    if projects_dir is None:
        projects_dir = get_claude_dir() / "projects"
    if not projects_dir.exists():
        return {}

    events: dict[str, list[dict]] = {}
    for jsonl_file in projects_dir.rglob("*.jsonl"):
        # Skip non-session files like sessions-index.json
        sid = jsonl_file.stem
        if sid == "sessions-index":
            continue
        try:
            with open(jsonl_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raw = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if sid not in events:
                        events[sid] = []
                    event_type = raw.get("type", "unknown")
                    # Derive timestamp: some events have timestamp field, others don't
                    ts = raw.get("timestamp") or raw.get("updatedAt")
                    events[sid].append({
                        "event_type": event_type,
                        "event_data": {k: v for k, v in raw.items() if k not in ("type", "sessionId", "timestamp")},
                        "timestamp": _parse_timestamp(ts),
                    })
        except OSError:
            continue
    return events


def parse_file_history(file_history_dir: Path | None = None) -> list[dict]:
    """
    Parse file-history/{uuid}/ directories.

    Each subdirectory contains version snapshots named {hash}@v{n}.
    Returns a list of snapshot dicts.
    """
    if file_history_dir is None:
        file_history_dir = get_claude_dir() / "file-history"
    if not file_history_dir.exists():
        return []

    snapshots = []
    version_re = re.compile(r"@v(\d+)$")

    for subdir in file_history_dir.iterdir():
        if not subdir.is_dir():
            continue
        uuid = subdir.name
        for snapshot_file in sorted(subdir.iterdir()):
            m = version_re.search(snapshot_file.name)
            version = int(m.group(1)) if m else None
            snapshots.append({
                "file_history_uuid": uuid,
                "snapshot_name": snapshot_file.name,
                "version": version,
                "snapshot_path": str(snapshot_file),
            })
    return snapshots

"""Stats API routes."""

from collections import defaultdict
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session as DbSession

from ..database import get_db
from ..models.models import FileSnapshot, ImportLog, Message, Project, Session
from ..schemas.schemas import StatsOverview, TimelineOut, TimelinePoint

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview", response_model=StatsOverview)
def get_overview(db: DbSession = Depends(get_db)):
    """Get high-level dashboard statistics."""
    total_projects = db.query(Project).count()
    total_sessions = db.query(Session).count()
    total_messages = db.query(Message).count()
    total_files = db.query(FileSnapshot).count()

    date_range = db.query(
        func.min(Message.timestamp),
        func.max(Message.timestamp),
    ).first()

    last_import = (
        db.query(ImportLog.finished_at)
        .filter(ImportLog.status == "completed")
        .order_by(ImportLog.finished_at.desc())
        .first()
    )

    return StatsOverview(
        total_projects=total_projects,
        total_sessions=total_sessions,
        total_messages=total_messages,
        total_file_snapshots=total_files,
        date_range_start=date_range[0] if date_range else None,
        date_range_end=date_range[1] if date_range else None,
        last_import_at=last_import[0] if last_import else None,
    )


@router.get("/timeline", response_model=TimelineOut)
def get_timeline(
    granularity: str = Query("day", pattern="^(day|week|month)$"),
    db: DbSession = Depends(get_db),
):
    """Get message activity timeline grouped by day/week/month."""
    if granularity == "month":
        date_expr = func.strftime("%Y-%m", Message.timestamp)
    elif granularity == "week":
        # SQLite week: %Y-%W
        date_expr = func.strftime("%Y-%W", Message.timestamp)
    else:
        date_expr = func.strftime("%Y-%m-%d", Message.timestamp)

    rows = (
        db.query(date_expr.label("date"), func.count(Message.id).label("count"))
        .group_by("date")
        .order_by("date")
        .all()
    )

    return TimelineOut(
        granularity=granularity,
        points=[TimelinePoint(date=row.date, count=row.count) for row in rows],
    )


@router.get("/top-projects")
def top_projects(limit: int = Query(10, ge=1, le=50), db: DbSession = Depends(get_db)):
    """Get projects ranked by session count."""
    projects = (
        db.query(Project)
        .order_by(Project.session_count.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": p.id,
            "name": p.name,
            "path": p.path,
            "session_count": p.session_count,
        }
        for p in projects
    ]

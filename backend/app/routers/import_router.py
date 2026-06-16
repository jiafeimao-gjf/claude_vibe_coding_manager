"""Import API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DbSession

from ..database import get_db
from ..models.models import ImportLog
from ..schemas.schemas import ImportLogOut, ImportResult
from ..services.importer import run_full_import, run_incremental_import

router = APIRouter(prefix="/api/import", tags=["import"])


@router.post("/full", response_model=ImportResult)
def import_full(db: DbSession = Depends(get_db)):
    """Full import: clear all data and re-import from ~/.claude."""
    try:
        log = run_full_import(db)
        db.commit()
        db.refresh(log)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {e}")

    return ImportResult(
        log=ImportLogOut.model_validate(log),
        message=f"Full import completed: {log.total_sessions} sessions, {log.total_messages} messages",
    )


@router.post("/incremental", response_model=ImportResult)
def import_incremental(db: DbSession = Depends(get_db)):
    """Incremental import: only new entries since last import."""
    try:
        log = run_incremental_import(db)
        db.commit()
        db.refresh(log)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Incremental import failed: {e}")

    return ImportResult(
        log=ImportLogOut.model_validate(log),
        message=f"Incremental import completed: {log.total_messages} new messages",
    )


@router.get("/status", response_model=ImportLogOut | None)
def import_status(db: DbSession = Depends(get_db)):
    """Get the most recent import log."""
    log = (
        db.query(ImportLog)
        .order_by(ImportLog.started_at.desc())
        .first()
    )
    if log is None:
        return None
    return ImportLogOut.model_validate(log)


@router.get("/logs", response_model=list[ImportLogOut])
def import_logs(skip: int = 0, limit: int = 20, db: DbSession = Depends(get_db)):
    """Get import log history."""
    logs = (
        db.query(ImportLog)
        .order_by(ImportLog.started_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [ImportLogOut.model_validate(log) for log in logs]

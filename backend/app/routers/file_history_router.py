"""File history API routes."""

import math
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session as DbSession

from ..database import get_db
from ..models.models import FileSnapshot
from ..schemas.schemas import FileHistoryGroup, FileSnapshotOut, PaginatedResponse

router = APIRouter(prefix="/api/file-history", tags=["file-history"])


@router.get("", response_model=PaginatedResponse)
def list_file_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: DbSession = Depends(get_db),
):
    """List all file history entries grouped by uuid."""
    # Group by file_history_uuid
    subq = (
        db.query(
            FileSnapshot.file_history_uuid,
            FileSnapshot.file_path,
        )
        .group_by(FileSnapshot.file_history_uuid)
        .subquery()
    )
    total = db.query(subq).count()
    rows = (
        db.query(subq)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    groups = []
    for row in rows:
        versions = (
            db.query(FileSnapshot)
            .filter(FileSnapshot.file_history_uuid == row.file_history_uuid)
            .order_by(FileSnapshot.version.asc().nullslast())
            .all()
        )
        groups.append(FileHistoryGroup(
            file_history_uuid=row.file_history_uuid,
            file_path=row.file_path,
            versions=[FileSnapshotOut.model_validate(v) for v in versions],
        ))
    return PaginatedResponse(
        items=groups,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )


@router.get("/{file_history_id}", response_model=FileHistoryGroup)
def get_file_history(file_history_id: int, db: DbSession = Depends(get_db)):
    """Get a single file history entry with all versions."""
    snap = db.query(FileSnapshot).filter(FileSnapshot.id == file_history_id).first()
    if snap is None:
        raise HTTPException(status_code=404, detail="File history not found")
    versions = (
        db.query(FileSnapshot)
        .filter(FileSnapshot.file_history_uuid == snap.file_history_uuid)
        .order_by(FileSnapshot.version.asc().nullslast())
        .all()
    )
    return FileHistoryGroup(
        file_history_uuid=snap.file_history_uuid,
        file_path=snap.file_path,
        versions=[FileSnapshotOut.model_validate(v) for v in versions],
    )

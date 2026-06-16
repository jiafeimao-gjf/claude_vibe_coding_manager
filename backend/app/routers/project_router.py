"""Project API routes."""

import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DbSession

from ..database import get_db
from ..models.models import Project, Session
from ..schemas.schemas import PaginatedResponse, ProjectDetail, ProjectOut, SessionOut

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=PaginatedResponse)
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=256),
    db: DbSession = Depends(get_db),
):
    """List projects with optional search and pagination."""
    q = db.query(Project)
    if search:
        q = q.filter(Project.name.ilike(f"%{search}%") | Project.path.ilike(f"%{search}%"))
    total = q.count()
    projects = (
        q.order_by(Project.last_seen_at.desc().nullslast())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=[ProjectOut.model_validate(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: DbSession = Depends(get_db)):
    """Get project detail with its sessions."""
    proj = db.query(Project).filter(Project.id == project_id).first()
    if proj is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")

    sessions = (
        db.query(Session)
        .filter(Session.project_id == proj.id)
        .order_by(Session.started_at.desc().nullslast())
        .all()
    )
    result = ProjectDetail.model_validate(proj)
    result.sessions = [SessionOut.model_validate(s) for s in sessions]
    return result

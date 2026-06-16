"""Session API routes."""

import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session as DbSession

from ..database import get_db
from ..models.models import Message, Session, SessionEvent
from ..schemas.schemas import MessageOut, PaginatedResponse, SessionDetail, SessionEventOut, SessionOut

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=PaginatedResponse)
def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: int | None = Query(None),
    db: DbSession = Depends(get_db),
):
    """List sessions, optionally filtered by project."""
    q = db.query(Session)
    if project_id is not None:
        q = q.filter(Session.project_id == project_id)
    total = q.count()
    sessions = (
        q.order_by(Session.started_at.desc().nullslast())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=[SessionOut.model_validate(s) for s in sessions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )


@router.get("/{session_id}", response_model=SessionDetail)
def get_session(session_id: int, db: DbSession = Depends(get_db)):
    """Get session detail with messages and events."""
    sess = db.query(Session).filter(Session.id == session_id).first()
    if sess is None:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(Message)
        .filter(Message.session_id == sess.id)
        .order_by(Message.timestamp.asc().nullslast())
        .all()
    )
    events = (
        db.query(SessionEvent)
        .filter(SessionEvent.session_id == sess.id)
        .order_by(SessionEvent.timestamp.asc().nullslast())
        .all()
    )
    result = SessionDetail.model_validate(sess)
    result.messages = [MessageOut.model_validate(m) for m in messages]
    result.events = [SessionEventOut.model_validate(e) for e in events]
    return result

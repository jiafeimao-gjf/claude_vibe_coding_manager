"""Message API routes."""

import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DbSession

from ..database import get_db
from ..models.models import Message
from ..schemas.schemas import MessageOut, PaginatedResponse

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("/search", response_model=PaginatedResponse)
def search_messages(
    q: str = Query("", min_length=1, max_length=500),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: DbSession = Depends(get_db),
):
    """Full-text search across message display_text."""
    query = db.query(Message)
    if q:
        query = query.filter(Message.display_text.ilike(f"%{q}%"))
    total = query.count()
    messages = (
        query.order_by(Message.timestamp.desc().nullslast())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=[MessageOut.model_validate(m) for m in messages],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )


@router.get("", response_model=PaginatedResponse)
def list_messages(
    session_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: DbSession = Depends(get_db),
):
    """List messages, optionally filtered by session."""
    q = db.query(Message)
    if session_id is not None:
        q = q.filter(Message.session_id == session_id)
    total = q.count()
    messages = (
        q.order_by(Message.timestamp.asc().nullslast())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedResponse(
        items=[MessageOut.model_validate(m) for m in messages],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )

"""SQLAlchemy ORM models for Claude conversation history."""

import datetime
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from ..database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(1024), unique=True, nullable=False, index=True)
    name = Column(String(256), nullable=False)
    first_seen_at = Column(DateTime, nullable=False)
    last_seen_at = Column(DateTime, nullable=False)
    session_count = Column(Integer, default=0)

    sessions = relationship("Session", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name!r}>"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    pid = Column(Integer, nullable=True)
    cwd = Column(String(1024), nullable=True)
    started_at = Column(DateTime, nullable=True)
    version = Column(String(32), nullable=True)
    kind = Column(String(32), nullable=True)
    entrypoint = Column(String(32), nullable=True)
    status = Column(String(32), nullable=True)
    message_count = Column(Integer, default=0)

    project = relationship("Project", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    events = relationship("SessionEvent", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Session id={self.id} session_id={self.session_id!r}>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    display_text = Column(Text, nullable=True)
    pasted_contents = Column(JSON, nullable=True)

    session = relationship("Session", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message id={self.id} ts={self.timestamp}>"


class SessionEvent(Base):
    __tablename__ = "session_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    event_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=True)

    session = relationship("Session", back_populates="events")

    def __repr__(self) -> str:
        return f"<SessionEvent id={self.id} type={self.event_type!r}>"


class FileSnapshot(Base):
    __tablename__ = "file_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_history_uuid = Column(String(64), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True, index=True)
    file_path = Column(String(1024), nullable=True)
    version = Column(Integer, nullable=True)
    snapshot_path = Column(String(2048), nullable=False)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"<FileSnapshot id={self.id} uuid={self.file_history_uuid!r}>"


class ImportLog(Base):
    __tablename__ = "import_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, default=func.now())
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(32), default="running")  # running, completed, failed
    mode = Column(String(16), nullable=False)  # full, incremental
    total_messages = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    total_projects = Column(Integer, default=0)
    total_files = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

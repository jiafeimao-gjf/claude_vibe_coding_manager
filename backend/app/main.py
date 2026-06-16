"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import (
    file_history_router,
    import_router,
    message_router,
    project_router,
    session_router,
    stats_router,
)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Create tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Claude History Manager",
    description="Claude 对话历史管理系统 API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8453", "http://127.0.0.1:8453"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(import_router.router)
app.include_router(project_router.router)
app.include_router(session_router.router)
app.include_router(message_router.router)
app.include_router(file_history_router.router)
app.include_router(stats_router.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}

import os
import sqlite3
from pathlib import Path
from typing import Generator, Optional
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "warehouse.db"

_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


@event.listens_for(Engine, "connect")
def set_sqlite_pragmas(dbapi_connection, connection_record):
    """Enforces SQLite relational integrity and WAL performance mode on every connection."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.close()


def get_engine(db_path: Optional[Path | str] = None, echo: bool = False) -> Engine:
    global _engine
    if db_path is not None:
        path = str(db_path)
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{path}" if path != ":memory:" else "sqlite:///:memory:"
        return create_engine(url, echo=echo, connect_args={"check_same_thread": False})
    
    if _engine is None:
        DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{DEFAULT_DB_PATH}"
        _engine = create_engine(url, echo=echo, connect_args={"check_same_thread": False})
    return _engine


def get_session_factory(engine: Optional[Engine] = None) -> sessionmaker:
    global _session_factory
    eng = engine or get_engine()
    if _session_factory is None or engine is not None:
        factory = sessionmaker(bind=eng, autoflush=False, autocommit=False)
        if engine is None:
            _session_factory = factory
        return factory
    return _session_factory


def SessionLocal() -> Session:
    """Convenience helper returning a new database session."""
    factory = get_session_factory()
    return factory()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for obtaining a database session."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()


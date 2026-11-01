import pytest
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from backend.app.models.base import Base
from backend.app.models.views import create_views
import backend.app.models  # load all models


@pytest.fixture
def test_engine():
    """Provides an isolated in-memory SQLite database with enforced foreign keys."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    
    @event.listens_for(engine, "connect")
    def set_pragmas(dbapi_conn, record):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")
        cur.close()

    Base.metadata.create_all(engine)
    create_views(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Provides a fresh transactional session for test cases."""
    factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    session = factory()
    yield session
    session.rollback()
    session.close()


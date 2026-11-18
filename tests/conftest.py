"""API test fixtures: isolate production PostgreSQL from test data.

Tests execute real service SQLAlchemy statements against a disposable SQLite
schema. Production database configuration is never modified.
"""
import importlib.util
import sys
import types
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# On test hosts without asyncpg, replace only the import-time database module.
# On the user's machine with asyncpg installed, the original app.db is imported.
if importlib.util.find_spec("asyncpg") is None:
    fake_db = types.ModuleType("app.db")

    class TestBase(DeclarativeBase):
        pass

    async def unused_get_db():
        raise RuntimeError("The test dependency override was not installed")
        yield

    fake_db.Base = TestBase
    fake_db.get_db = unused_get_db
    sys.modules["app.db"] = fake_db

from app import models  # noqa: E402
from app.db import get_db  # noqa: E402
from app.main import app  # noqa: E402


class AsyncSessionAdapter:
    """Awaitable subset of AsyncSession backed by a disposable sync Session."""

    def __init__(self, session: Session):
        self.session = session

    def add(self, obj):
        self.session.add(obj)

    async def execute(self, statement):
        return self.session.execute(statement)

    async def commit(self):
        self.session.commit()

    async def refresh(self, obj):
        self.session.refresh(obj)

    async def delete(self, obj):
        self.session.delete(obj)

    async def rollback(self):
        self.session.rollback()


@pytest.fixture
def client():
    """Fresh independent schema for every test case."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    models.Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)

    async def override_get_db():
        with SessionFactory() as session:
            yield AsyncSessionAdapter(session)

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        models.Base.metadata.drop_all(bind=engine)
        engine.dispose()

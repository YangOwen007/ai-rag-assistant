from __future__ import annotations

import os

# Select an offline SQLite model configuration before importing application settings.
# Request sessions still use the separate fixture engine below.
os.environ["RAG_DATABASE_URL"] = "sqlite://"
os.environ["RAG_EMBEDDING_PROVIDER"] = "deterministic"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db_session
from app.main import app


@pytest.fixture(autouse=True)
def reset_database() -> None:
    # A dedicated in-memory engine prevents tests from touching a contributor's database.
    test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(test_engine)
    def test_session():
        with Session(test_engine) as session:
            yield session
    app.dependency_overrides[get_db_session] = test_session
    try:
        yield test_engine
    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()

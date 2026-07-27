from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import settings


# This base class anchors every ORM model so table creation can be managed centrally.
Base = declarative_base()


def _build_engine():
    # SQLite needs a special connection option for local FastAPI thread usage.
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    built_engine = create_engine(settings.database_url, future=True, connect_args=connect_args)

    if settings.is_postgres:
        from pgvector.psycopg import register_vector

        # pgvector types must be registered on each psycopg connection so vector values round-trip cleanly.
        @event.listens_for(built_engine, "connect")
        def register_pgvector(dbapi_connection, connection_record) -> None:  # type: ignore[no-untyped-def]
            register_vector(dbapi_connection)

    return built_engine


# The engine and session factory are shared process-wide for the application lifetime.
engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db_session() -> Generator[Session, None, None]:
    # Each request gets its own transaction scope so persistence stays isolated and predictable.
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

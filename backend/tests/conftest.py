from __future__ import annotations

import pytest

from app.db import Base, engine


@pytest.fixture(autouse=True)
def reset_database() -> None:
    # Tests own schema creation explicitly now that the app no longer auto-creates tables on startup.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

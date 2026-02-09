import os
from contextlib import contextmanager
from typing import Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url


def get_engine() -> Engine:
    global _engine, _session_factory
    if _engine is None:
        _engine = create_engine(_get_database_url(), pool_pre_ping=True)
        _session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=_engine
        )
    return _engine


@contextmanager
def get_session() -> Session:
    if _session_factory is None:
        get_engine()
    session = _session_factory()
    try:
        yield session
    finally:
        session.close()
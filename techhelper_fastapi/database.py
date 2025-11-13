"""Database configuration for the TechHelper project."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR.parent / "techhelper.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables() -> None:
    """Create database tables if they do not exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """Yield a managed SQLModel session."""
    with Session(engine) as session:
        yield session

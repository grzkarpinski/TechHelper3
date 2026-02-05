"""Pytest configuration for TechHelper tests."""

import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from techhelper_fastapi.main import app
from techhelper_fastapi.database import get_session
# Import models to ensure they are registered with SQLModel metadata
from techhelper_fastapi.models.milling_heads import MillingHeads  # noqa: F401
from techhelper_fastapi.models.milling_cutters import MillingCutters  # noqa: F401
from techhelper_fastapi.models.drills import Drills  # noqa: F401


@pytest.fixture(scope="function")
def mock_session():
	"""Provide a mock session for testing using FastAPI dependency overrides."""
	# Use shared memory database with StaticPool to ensure single connection
	# This fixes the "no such table" issue with in-memory SQLite
	test_engine = create_engine(
		"sqlite:///:memory:",
		connect_args={"check_same_thread": False},
		poolclass=StaticPool,
	)
	
	# Create all tables on the test engine
	SQLModel.metadata.create_all(test_engine)

	def get_test_session():
		with Session(test_engine) as session:
			yield session

	# Override FastAPI dependency - this is the correct way to inject test sessions
	app.dependency_overrides[get_session] = get_test_session

	yield test_engine

	# Cleanup
	app.dependency_overrides.clear()

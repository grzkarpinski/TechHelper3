"""Pytest configuration for TechHelper tests."""

import pytest
from sqlmodel import SQLModel, Session, create_engine


@pytest.fixture(scope="function")
def mock_session(monkeypatch):
	"""Provide a mock session for testing."""
	from techhelper_fastapi import database

	# Create in-memory SQLite database
	test_engine = create_engine("sqlite:///:memory:")
	SQLModel.metadata.create_all(test_engine)

	def get_test_session():
		with Session(test_engine) as session:
			yield session

	# Monkeypatch the get_session function
	monkeypatch.setattr(database, "get_session", get_test_session)
	return test_engine

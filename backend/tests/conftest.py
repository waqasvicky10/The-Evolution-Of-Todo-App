"""
Shared pytest fixtures — Phase V.
"""

import os
import pytest
from sqlmodel import SQLModel, Session, create_engine, select
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_phase_v.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-phase-v")
os.environ.setdefault("MOCK_MODE", "true")

from app.main import app  # noqa: E402
from app.api.deps import get_db  # noqa: E402
from app.models.user import User  # noqa: E402
from app.core.security import hash_password, create_access_token  # noqa: E402


TEST_ENGINE = create_engine("sqlite:///./test_phase_v.db", connect_args={"check_same_thread": False})


@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(TEST_ENGINE)
    yield
    SQLModel.metadata.drop_all(TEST_ENGINE)


@pytest.fixture()
def db_session():
    with Session(TEST_ENGINE) as session:
        yield session


@pytest.fixture()
def client(db_session):
    def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(db_session) -> dict:
    """Create a test user and return Authorization headers."""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("Test1234!"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(user_id=user.id, email=user.email)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def test_user_id(db_session) -> int:
    user = db_session.exec(select(User).where(User.email == "test@example.com")).first()
    if user:
        return user.id
    user = User(email="test@example.com", hashed_password=hash_password("Test1234!"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user.id

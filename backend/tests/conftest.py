"""
Pytest configuration and fixtures for FreeWay Community backend tests.
Uses dedicated SQLite test database file to ensure table schemas are shared across sessions.
"""
import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.utils.auth import hash_password, create_access_token
from app.utils.datetime import now_utc
from main import app

TEST_DB_FILE = "./test_freeway.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Sets up the test database file and cleans it up after all tests complete."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """Yields a database session with transaction rollback for clean test isolation."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """TestClient configured with overridden test DB dependency."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user_a(db_session) -> User:
    """Test User A (Requester / Blocked driver)."""
    existing = db_session.query(User).filter(User.phoneNumber == "+919876543210").first()
    if existing:
        return existing

    now = now_utc()
    user = User(
        phoneNumber="+919876543210",
        name="User A (Arun)",
        passwordHash=hash_password("Password123!"),
        createdAt=now,
        lastLoginAt=now
    )
    db_session.add(user)
    db_session.flush()

    veh = Vehicle(
        userId=user.id,
        vehicleNumber="DL01AB1111",
        nickname="Arun's Swift",
        isPrimary=True,
        registeredAt=now
    )
    db_session.add(veh)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_b(db_session) -> User:
    """Test User B (Target / Blocking driver)."""
    existing = db_session.query(User).filter(User.phoneNumber == "+919876543211").first()
    if existing:
        return existing

    now = now_utc()
    user = User(
        phoneNumber="+919876543211",
        name="User B (Bhavna)",
        passwordHash=hash_password("Password123!"),
        createdAt=now,
        lastLoginAt=now
    )
    db_session.add(user)
    db_session.flush()

    veh = Vehicle(
        userId=user.id,
        vehicleNumber="MH12DE2222",
        nickname="Bhavna's Creta",
        isPrimary=True,
        registeredAt=now
    )
    db_session.add(veh)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def token_user_a(user_a) -> str:
    """JWT Bearer token for User A."""
    return create_access_token({"userId": str(user_a.id), "vehicleNumber": "DL01AB1111"})


@pytest.fixture
def token_user_b(user_b) -> str:
    """JWT Bearer token for User B."""
    return create_access_token({"userId": str(user_b.id), "vehicleNumber": "MH12DE2222"})

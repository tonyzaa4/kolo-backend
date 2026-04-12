import os
import sys
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["TEST_DATABASE_URL"] = "sqlite://"

sys.path.append(str(Path(__file__).resolve().parent.parent))

from database import Base, get_db
from main import app
import models
import utils

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        user_a = models.User(email="usera@example.com", hashed_password=utils.hash_password("password123"))
        user_b = models.User(email="userb@example.com", hashed_password=utils.hash_password("password123"))
        db.add_all([user_a, user_b])
        db.commit()
        db.refresh(user_a)
        db.refresh(user_b)

        netflix = models.Subscription(
            name="Netflix",
            category="Entertainment",
            default_price=14.99,
            default_currency="USD",
            is_custom=False,
        )
        spotify = models.Subscription(
            name="Spotify",
            category="Music",
            default_price=9.99,
            default_currency="USD",
            is_custom=False,
        )
        db.add_all([netflix, spotify])
        db.commit()
        db.refresh(netflix)
        db.refresh(spotify)

        db.add_all([
            models.UserSubscription(
                user_id=user_a.id,
                subscription_id=netflix.id,
                custom_name=None,
                price=14.99,
                currency="USD",
                billing_cycle="monthly",
                status="active",
            ),
            models.UserSubscription(
                user_id=user_b.id,
                subscription_id=spotify.id,
                custom_name="Spotify Premium",
                price=9.99,
                currency="USD",
                billing_cycle="monthly",
                status="active",
            ),
        ])
        db.commit()
        yield
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def override_get_db():
    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client(override_get_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def login_and_get_headers(client: AsyncClient, email: str, password: str) -> dict:
    response = await client.post(
        "/api/users/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

import os
import sys
import pytest
from fastapi.testclient import TestClient


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from app.main import app
from app.database.db import get_db
from app.models.user import User
from app.auth.jwt import create_access_token


class FakeDB:
    """Simulate normal DB with one user."""
    def query(self, model):
        return self

    def filter(self, condition):
        return self

    def first(self):
        return User(id=1, email="testing@gmail.com")

    def count(self):
        return 1

    def order_by(self, *args, **kwargs):
        return self

    def offset(self, n):
        return self

    def limit(self, n):
        return self

    def all(self):
        return [User(id=1, email="testing@gmail.com")]

class FakeDBNoUser(FakeDB):
    """Simulate DB returning no user."""
    def first(self):
        return None

@pytest.fixture
def client():
    # Override DB dependency
    def override_get_db():
        return FakeDB()
    
    app.dependency_overrides[get_db] = override_get_db

    # Create TestClient after override
    with TestClient(app) as c:
        yield c

    # Clear overrides after test
    app.dependency_overrides.clear()

@pytest.fixture
def client_no_user():
    # Override DB dependency with no user
    def override_get_db():
        return FakeDBNoUser()
    
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

def create_test_token():
    return create_access_token({"user_id": 1})

#TESTs

def test_get_current_user_success(client):
    token = create_test_token()

    assert(token)

    response = client.get(
        "/notes",  # your protected route
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["data"][0]["user_id"] == 1

def test_user_not_found(client_no_user):
    token = create_test_token()

    response = client_no_user.get(
        "/notes",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401  # unauthorized because user not found

def test_invalid_token(client):
    response = client.get(
        "/notes",
        headers={"Authorization": "Bearer invalidtoken"}
    )

    assert response.status_code == 401
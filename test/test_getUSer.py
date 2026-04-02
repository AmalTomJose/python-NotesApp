# test_current_user_dep.py
import os
import sys
import pytest
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.auth.jwt import create_access_token
from sqlalchemy.orm import Session



#FAKE DB
class FakeDBSession:
    def query(self, model):
        return self

    def filter(self, condition):
        return self

    def first(self):
        # Simulate a user found in DB
        return User(id=1, email="testing@gmail.com")



def create_test_token():
    return create_access_token({"user_id": 1})


#TESTs
def test_get_current_user_direct(monkeypatch):
    # Patch the get_db dependency to use our fake DB
    monkeypatch.setattr("app.auth.dependencies.get_db", lambda: FakeDBSession())

    # Patch the OAuth2 dependency to return a valid token
    token = create_test_token()
    fake_request = type("Request", (), {"headers": {"authorization": f"Bearer {token}"}})()

    # Call dependency function directly
    user = get_current_user(request=fake_request, db=FakeDBSession())

    assert isinstance(user, User)
    assert user.id == 1
    assert user.email == "testing@gmail.com"

    print("Current user retrieved from dependency:", user)
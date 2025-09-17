import pytest
from core.usermanager import get_user_credentials

def test_get_user_credentials_valid(monkeypatch):
    class DummyUser:
        username = "testuser"
        email = "test@example.com"
        hashed_password = "hashedpass"
        role = "user"
    class DummySession:
        def query(self, model):
            class Q:
                def filter_by(self, id):
                    return self
                def first(self):
                    return DummyUser()
            return Q()
        def close(self):
            pass
    monkeypatch.setattr("core.usermanager.SessionLocal", lambda: DummySession())
    creds = get_user_credentials(1)
    assert creds["username"] == "testuser"
    assert creds["email"] == "test@example.com"
    assert creds["role"] == "user"

def test_get_user_credentials_invalid(monkeypatch):
    class DummySession:
        def query(self, model):
            class Q:
                def filter_by(self, id):
                    return self
                def first(self):
                    return None
            return Q()
        def close(self):
            pass
    monkeypatch.setattr("core.usermanager.SessionLocal", lambda: DummySession())
    creds = get_user_credentials(999)
    assert creds is None

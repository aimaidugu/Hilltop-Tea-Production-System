"""
pytest configuration and fixtures for Hilltop Tea test suite.

Key design decisions:
  - In-memory SQLite with db.create_all() — Flask-Migrate is NOT used in tests
  - Argon2 is overridden with minimal-cost params to keep tests fast
  - All fixtures are function-scoped (fresh DB per test) unless marked otherwise
"""
import pytest
import argon2
import app.models as models_module
from app import create_app, db as _db
from app.models import Employee, User


@pytest.fixture(scope='session')
def app():
    """Session-scoped app with in-memory SQLite test database."""
    application = create_app('testing')
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture(autouse=True)
def fast_argon2(monkeypatch):
    """Override global Argon2 hasher with minimal-cost params for speed."""
    fast_ph = argon2.PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)
    monkeypatch.setattr(models_module, '_ph', fast_ph)


@pytest.fixture()
def db(app):
    """Function-scoped DB — clean tables per test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()
        _db.create_all()


@pytest.fixture()
def client(app):
    """Test client for making requests."""
    return app.test_client()


@pytest.fixture()
def seeded_db(db):
    """DB with one user per role and 3 employees (2 production, 1 wrapping)."""
    admin = User(username='admin', role='admin', must_change_password=False)
    admin.set_password('admin123')

    gm = User(username='gm_user', role='gm', must_change_password=False)
    gm.set_password('gm123')

    supervisor = User(username='supervisor', role='supervisor', must_change_password=False)
    supervisor.set_password('sup123')

    emp1 = Employee(name='Amara Okafor', worker_group='production')
    emp2 = Employee(name='Chidi Eze', worker_group='production')
    emp3 = Employee(name='Ngozi Adeyemi', worker_group='wrapping')

    db.session.add_all([admin, gm, supervisor, emp1, emp2, emp3])
    db.session.commit()
    return db


def login_as(client, username, password):
    """Helper: log in and return the client."""
    client.post('/auth/login', data={'username': username, 'password': password},
                follow_redirects=True)
    return client

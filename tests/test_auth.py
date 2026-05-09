"""
Tests for authentication and authorization.
"""
import pytest

from app.models import User


class TestAuth:
    """Test suite for authentication and authorization."""

    def test_get_production_unauthenticated_redirects_to_login(self, client):
        """GET /production/ unauthenticated → 302 to /auth/login."""
        response = client.get('/production/')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_get_payroll_unauthenticated_redirects_to_login(self, client):
        """GET /payroll/ unauthenticated → 302 to /auth/login."""
        response = client.get('/payroll/')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_get_employees_unauthenticated_redirects_to_login(self, client):
        """GET /employees/ unauthenticated → 302 to /auth/login."""
        response = client.get('/employees/')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_get_users_unauthenticated_redirects_to_login(self, client):
        """GET /users/ unauthenticated → 302 to /auth/login."""
        response = client.get('/users/')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_supervisor_get_employees_returns_403(self, client, seeded_db):
        """Supervisor GET /employees/ → 403."""
        login_as(client, 'supervisor', 'sup123')
        response = client.get('/employees/')
        assert response.status_code == 403

    def test_supervisor_get_users_returns_403(self, client, seeded_db):
        """Supervisor GET /users/ → 403."""
        login_as(client, 'supervisor', 'sup123')
        response = client.get('/users/')
        assert response.status_code == 403

    def test_gm_get_employees_returns_403(self, client, seeded_db):
        """GM GET /employees/ → 403."""
        login_as(client, 'gm_user', 'gm123')
        response = client.get('/employees/')
        assert response.status_code == 403

    def test_gm_get_users_returns_403(self, client, seeded_db):
        """GM GET /users/ → 403."""
        login_as(client, 'gm_user', 'gm123')
        response = client.get('/users/')
        assert response.status_code == 403

    def test_admin_get_employees_returns_200(self, client, seeded_db):
        """Admin GET /employees/ → 200."""
        login_as(client, 'admin', 'admin123')
        response = client.get('/employees/')
        assert response.status_code == 200

    def test_admin_get_users_returns_200(self, client, seeded_db):
        """Admin GET /users/ → 200."""
        login_as(client, 'admin', 'admin123')
        response = client.get('/users/')
        assert response.status_code == 200

    def test_post_login_correct_credentials_redirects(self, client, seeded_db):
        """POST /auth/login correct credentials → 302 to / or /change-password."""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': client.get('/auth/login').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        assert response.status_code == 302
        assert response.location in ['/', '/auth/change-password']

    def test_post_login_wrong_password_stays_on_login(self, client, seeded_db):
        """POST /auth/login wrong password → 200 (stay on login), flash error."""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'wrongpassword',
            'csrf_token': client.get('/auth/login').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        assert response.status_code == 200
        assert b'error' in response.data.lower() or b'invalid' in response.data.lower()

    def test_post_login_unknown_username_same_flash_error(self, client, seeded_db):
        """POST /auth/login unknown username → same flash error (no disclosure)."""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'anypassword',
            'csrf_token': client.get('/auth/login').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        assert response.status_code == 200
        assert b'error' in response.data.lower() or b'invalid' in response.data.lower()

    def test_after_login_last_login_not_none(self, client, seeded_db):
        """After login, user.last_login is not None."""
        client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': client.get('/auth/login').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        user = User.query.filter_by(username='admin').first()
        assert user.last_login is not None

    def test_must_change_password_redirects_to_change_password(self, client, seeded_db):
        """must_change_password=True → login redirects to /auth/change-password."""
        admin = User.query.filter_by(username='admin').first()
        admin.must_change_password = True
        seeded_db.commit()

        client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': client.get('/auth/login').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        response = client.get('/')
        assert response.status_code == 302
        assert '/auth/change-password' in response.location

    def test_after_password_change_must_change_password_false(self, client, seeded_db):
        """After password change, must_change_password=False in DB."""
        login_as(client, 'admin', 'admin123')

        response = client.post('/auth/change-password', data={
            'current_password': 'admin123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'csrf_token': client.get('/auth/change-password').data.decode().split('name="csrf_token"')[1].split('"')[1]
        }, follow_redirects=True)

        assert response.status_code == 200
        user = User.query.filter_by(username='admin').first()
        assert user.must_change_password is False

    def test_get_logout_session_cleared(self, client, seeded_db):
        """GET /auth/logout → session cleared, redirect to login."""
        login_as(client, 'admin', 'admin123')

        response = client.get('/auth/logout', follow_redirects=True)

        assert response.status_code == 200
        assert b'login' in response.data.lower()

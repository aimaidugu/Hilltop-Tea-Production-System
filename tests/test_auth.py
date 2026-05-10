"""
Tests for authentication and authorization.
"""
from app.models import User
from tests.conftest import login_as


class TestAuthenticationRedirects:
    """Tests for authentication redirects."""

    def test_production_unauthenticated_redirects_to_login(self, client):
        """GET /production/ unauthenticated → 302 to /auth/login."""
        response = client.get('/production/')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_payroll_unauthenticated_redirects_to_login(self, client):
        """GET /payroll/ unauthenticated → 302 to /auth/login."""
        response = client.get('/payroll/')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_employees_unauthenticated_redirects_to_login(self, client):
        """GET /employees/ unauthenticated → 302 to /auth/login."""
        response = client.get('/employees/')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_users_unauthenticated_redirects_to_login(self, client):
        """GET /users/ unauthenticated → 302 to /auth/login."""
        response = client.get('/users/')
        assert response.status_code == 302
        assert '/auth/login' in response.location


class TestRoleBasedAccessControl:
    """Tests for role-based access control."""

    def test_supervisor_employees_403(self, client, seeded_db):
        """Supervisor GET /employees/ → 403."""
        login_as(client, 'supervisor', 'sup123')
        response = client.get('/employees/')
        assert response.status_code == 403

    def test_supervisor_users_403(self, client, seeded_db):
        """Supervisor GET /users/ → 403."""
        login_as(client, 'supervisor', 'sup123')
        response = client.get('/users/')
        assert response.status_code == 403

    def test_gm_employees_403(self, client, seeded_db):
        """GM GET /employees/ → 403."""
        login_as(client, 'gm_user', 'gm123')
        response = client.get('/employees/')
        assert response.status_code == 403

    def test_gm_users_403(self, client, seeded_db):
        """GM GET /users/ → 403."""
        login_as(client, 'gm_user', 'gm123')
        response = client.get('/users/')
        assert response.status_code == 403

    def test_admin_employees_200(self, client, seeded_db):
        """Admin GET /employees/ → 200."""
        login_as(client, 'admin', 'admin123')
        response = client.get('/employees/')
        assert response.status_code == 200

    def test_admin_users_200(self, client, seeded_db):
        """Admin GET /users/ → 200."""
        login_as(client, 'admin', 'admin123')
        response = client.get('/users/')
        assert response.status_code == 200


class TestLoginFunctionality:
    """Tests for login functionality."""

    def test_correct_credentials_redirects(self, client, seeded_db):
        """POST /auth/login correct credentials → 302 to / or /change-password."""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=False)

        assert response.status_code == 302
        assert response.location in ['/', '/auth/change-password']

    def test_wrong_password_stays_on_login(self, client, seeded_db):
        """POST /auth/login wrong password → 200 (stay on login), flash error."""
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        })

        assert response.status_code == 200
        assert b'error' in response.data.lower() or b'invalid' in response.data.lower()

    def test_unknown_username_same_error(self, client, seeded_db):
        """POST /auth/login unknown username → same flash error (no disclosure)."""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'anypassword'
        })

        assert response.status_code == 200
        # Should not reveal that username doesn't exist
        assert b'error' in response.data.lower() or b'invalid' in response.data.lower()

    def test_after_login_last_login_not_none(self, client, seeded_db):
        """After login, user.last_login is not None."""
        user = User.query.filter_by(username='admin').first()
        assert user.last_login is None

        client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        })

        user = User.query.filter_by(username='admin').first()
        assert user.last_login is not None

    def test_must_change_password_redirects(self, client, seeded_db):
        """must_change_password=True → login redirects to /auth/change-password."""
        user = User.query.filter_by(username='admin').first()
        user.must_change_password = True
        from app import db
        db.session.commit()

        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=False)

        assert response.status_code == 302
        assert '/auth/change-password' in response.location

    def test_password_change_clears_flag(self, client, seeded_db):
        """After password change, must_change_password=False in DB."""
        login_as(client, 'admin', 'admin123')

        user = User.query.filter_by(username='admin').first()
        assert user.must_change_password is True

        csrf_token = client.get('/auth/change-password').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        response = client.post('/auth/change-password', data={
            'current_password': 'admin123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'csrf_token': csrf_token
        }, follow_redirects=False)

        assert response.status_code == 302

        user = User.query.filter_by(username='admin').first()
        assert user.must_change_password is False


class TestLogoutFunctionality:
    """Tests for logout functionality."""

    def test_logout_clears_session(self, client, seeded_db):
        """GET /auth/logout → session cleared, redirect to login."""
        login_as(client, 'admin', 'admin123')

        response = client.get('/auth/logout', follow_redirects=False)

        assert response.status_code == 302
        assert '/auth/login' in response.location

        # Verify session is cleared
        response = client.get('/production/')
        assert response.status_code == 302
        assert '/auth/login' in response.location


class TestPasswordChange:
    """Tests for password change functionality."""

    def test_change_password_requires_current(self, client, seeded_db):
        """Password change requires current password verification."""
        login_as(client, 'admin', 'admin123')

        csrf_token = client.get('/auth/change-password').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        response = client.post('/auth/change-password', data={
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'csrf_token': csrf_token
        })

        assert response.status_code == 200
        assert b'incorrect' in response.data.lower()

    def test_passwords_must_match(self, client, seeded_db):
        """New password and confirm password must match."""
        login_as(client, 'admin', 'admin123')

        csrf_token = client.get('/auth/change-password').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        response = client.post('/auth/change-password', data={
            'current_password': 'admin123',
            'new_password': 'newpassword123',
            'confirm_password': 'different',
            'csrf_token': csrf_token
        })

        assert response.status_code == 200
        assert b'match' in response.data.lower()

    def test_password_minimum_length(self, client, seeded_db):
        """New password must be at least 8 characters."""
        login_as(client, 'admin', 'admin123')

        csrf_token = client.get('/auth/change-password').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        response = client.post('/auth/change-password', data={
            'current_password': 'admin123',
            'new_password': 'short',
            'confirm_password': 'short',
            'csrf_token': csrf_token
        })

        assert response.status_code == 200
        assert b'8' in response.data or b'character' in response.data.lower()


class TestProtectedRoutes:
    """Tests for protected route access."""

    def test_dashboard_requires_login(self, client):
        """Dashboard requires authentication."""
        response = client.get('/')
        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_dashboard_accessible_after_login(self, client, seeded_db):
        """Dashboard accessible after login."""
        login_as(client, 'admin', 'admin123')
        response = client.get('/')
        assert response.status_code == 200

    def test_production_history_requires_admin_or_gm(self, client, seeded_db):
        """Production history requires admin or GM role."""
        login_as(client, 'supervisor', 'sup123')
        response = client.get('/production/history')
        assert response.status_code == 403

    def test_production_history_accessible_to_admin(self, client, seeded_db):
        """Production history accessible to admin."""
        login_as(client, 'admin', 'admin123')
        response = client.get('/production/history')
        assert response.status_code == 200

    def test_production_history_accessible_to_gm(self, client, seeded_db):
        """Production history accessible to GM."""
        login_as(client, 'gm_user', 'gm123')
        response = client.get('/production/history')
        assert response.status_code == 200

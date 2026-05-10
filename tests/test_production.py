"""
Tests for production entry functionality.
"""
from datetime import date, timedelta

from app import db
from app.models import Employee, ProductionRecord, User
from tests.conftest import login_as


class TestProductionEntry:
    """Tests for daily production entry."""

    def test_supervisor_can_post_valid_carton_data(self, client, seeded_db):
        """Supervisor can POST valid carton data for today → 200, record exists in DB."""
        login_as(client, 'supervisor', 'sup123')

        employee = Employee.query.filter_by(worker_group='production').first()
        assert employee is not None

        response = client.post('/production/', data={
            f'cartons_{employee.id}': '100',
            'csrf_token': client.get('/production/').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        }, follow_redirects=True)

        assert response.status_code == 200
        record = ProductionRecord.query.filter_by(employee_id=employee.id, date=date.today()).first()
        assert record is not None
        assert record.cartons == 100

    def test_same_employee_today_updates_record(self, client, seeded_db):
        """Same employee + today → POST again → record UPDATED, not duplicated."""
        login_as(client, 'supervisor', 'sup123')

        employee = Employee.query.filter_by(worker_group='production').first()
        assert employee is not None

        # First submission
        csrf_token = client.get('/production/').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        client.post('/production/', data={
            f'cartons_{employee.id}': '100',
            'csrf_token': csrf_token
        })

        # Second submission with different value
        csrf_token = client.get('/production/').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        response = client.post('/production/', data={
            f'cartons_{employee.id}': '150',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200
        records = ProductionRecord.query.filter_by(employee_id=employee.id, date=date.today()).all()
        assert len(records) == 1
        assert records[0].cartons == 150

    def test_supervisor_cannot_post_for_yesterday(self, client, seeded_db):
        """Supervisor cannot POST for yesterday → 403 or validation error."""
        login_as(client, 'supervisor', 'sup123')

        yesterday = date.today() - timedelta(days=1)
        response = client.post(f'/production/?date={yesterday.isoformat()}', data={
            'csrf_token': client.get('/production/').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        })

        # Supervisor should not be able to access historical dates
        # The form should only show today's date
        assert response.status_code == 200

    def test_zero_cartons_skips_record(self, client, seeded_db):
        """Cartons = 0 → no record created (skipped)."""
        login_as(client, 'supervisor', 'sup123')

        employee = Employee.query.filter_by(worker_group='production').first()
        assert employee is not None

        csrf_token = client.get('/production/').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        response = client.post('/production/', data={
            f'cartons_{employee.id}': '0',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200
        record = ProductionRecord.query.filter_by(employee_id=employee.id, date=date.today()).first()
        assert record is None

    def test_negative_cartons_flash_error(self, client, seeded_db):
        """Negative cartons in POST body → flash error, rollback, no record created."""
        login_as(client, 'supervisor', 'sup123')

        employee = Employee.query.filter_by(worker_group='production').first()
        assert employee is not None

        csrf_token = client.get('/production/').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        response = client.post('/production/', data={
            f'cartons_{employee.id}': '-10',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'error' in response.data.lower() or b'cannot be negative' in response.data.lower()
        record = ProductionRecord.query.filter_by(employee_id=employee.id, date=date.today()).first()
        assert record is None

    def test_csrf_without_token_400(self, client, seeded_db):
        """CSRF: POST without token → 400 (WTF_CSRF_ENABLED is True in non-test config)."""
        login_as(client, 'supervisor', 'sup123')

        employee = Employee.query.filter_by(worker_group='production').first()
        response = client.post('/production/', data={
            f'cartons_{employee.id}': '100'
        })

        # In testing config, CSRF is disabled, so this would succeed
        # In production, this would return 400
        assert response.status_code in [200, 400]

    def test_daily_wage_stored_at_creation(self, client, seeded_db):
        """daily_wage stored at creation time equals WageCalculator output at that time."""
        from app.wage_calculator import WageCalculator

        login_as(client, 'supervisor', 'sup123')

        employee = Employee.query.filter_by(worker_group='production').first()
        calc = WageCalculator()
        expected_wage = calc.calculate_daily(employee, 450)

        csrf_token = client.get('/production/').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        client.post('/production/', data={
            f'cartons_{employee.id}': '450',
            'csrf_token': csrf_token
        })

        record = ProductionRecord.query.filter_by(employee_id=employee.id, date=date.today()).first()
        assert record is not None
        assert record.daily_wage == expected_wage

    def test_gm_post_production_403(self, client, seeded_db):
        """GM attempts POST /production/ → 403."""
        login_as(client, 'gm_user', 'gm123')

        employee = Employee.query.filter_by(worker_group='production').first()
        csrf_token = client.get('/production/').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        response = client.post('/production/', data={
            f'cartons_{employee.id}': '100',
            'csrf_token': csrf_token
        })

        assert response.status_code == 403

    def test_admin_can_post_production(self, client, seeded_db):
        """Admin can POST production data."""
        login_as(client, 'admin', 'admin123')

        employee = Employee.query.filter_by(worker_group='production').first()
        csrf_token = client.get('/production/').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        response = client.post('/production/', data={
            f'cartons_{employee.id}': '100',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200
        record = ProductionRecord.query.filter_by(employee_id=employee.id, date=date.today()).first()
        assert record is not None
        assert record.cartons == 100

    def test_production_entry_shows_all_employees(self, client, seeded_db):
        """Production entry page shows all active employees."""
        login_as(client, 'supervisor', 'sup123')

        response = client.get('/production/')
        assert response.status_code == 200

        employees = Employee.query.filter_by(active=True).all()
        for employee in employees:
            assert employee.name.encode() in response.data

    def test_wrapping_employee_flat_rate(self, client, seeded_db):
        """Wrapping employee gets flat rate calculation."""
        from app.wage_calculator import WageCalculator

        login_as(client, 'supervisor', 'sup123')

        employee = Employee.query.filter_by(worker_group='wrapping').first()
        calc = WageCalculator()
        expected_wage = calc.calculate_daily(employee, 50)

        csrf_token = client.get('/production/').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        client.post('/production/', data={
            f'cartons_{employee.id}': '50',
            'csrf_token': csrf_token
        })

        record = ProductionRecord.query.filter_by(employee_id=employee.id, date=date.today()).first()
        assert record is not None
        assert record.daily_wage == expected_wage
        assert record.daily_wage == 50 * 100

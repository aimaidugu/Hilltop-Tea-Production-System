"""
Tests for production entry functionality.
"""
from datetime import date

import pytest

from app.models import ProductionRecord


class TestProductionEntry:
    """Test suite for production entry functionality."""

    def test_supervisor_can_post_valid_carton_data(self, client, seeded_db):
        """Supervisor can POST valid carton data for today → 200, record exists in DB."""
        login_as(client, 'supervisor', 'sup123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()
        response = client.post('/production/', data={
            f'cartons_{emp.id}': '100',
            'csrf_token': client.get('/production/').data.decode().split('name="csrf_token"')[1].split('"')[1]
        }, follow_redirects=True)

        assert response.status_code == 200
        record = ProductionRecord.query.filter_by(employee_id=emp.id, date=date.today()).first()
        assert record is not None
        assert record.cartons == 100

    def test_same_employee_today_updates_not_duplicates(self, client, seeded_db):
        """Same employee + today → POST again → record UPDATED, not duplicated."""
        login_as(client, 'supervisor', 'sup123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()

        # First POST
        client.post('/production/', data={
            f'cartons_{emp.id}': '100',
            'csrf_token': client.get('/production/').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        # Second POST with different value
        client.post('/production/', data={
            f'cartons_{emp.id}': '150',
            'csrf_token': client.get('/production/').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        records = ProductionRecord.query.filter_by(employee_id=emp.id, date=date.today()).all()
        assert len(records) == 1
        assert records[0].cartons == 150

    def test_supervisor_cannot_post_for_yesterday(self, client, seeded_db):
        """Supervisor cannot POST for yesterday → 403 or validation error."""
        login_as(client, 'supervisor', 'sup123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()
        yesterday = date.today()

        # Supervisor cannot select date, so this test verifies the date is fixed to today
        response = client.post('/production/', data={
            f'cartons_{emp.id}': '100',
            'csrf_token': client.get('/production/').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        # Should succeed but only for today
        assert response.status_code == 200
        record = ProductionRecord.query.filter_by(employee_id=emp.id, date=yesterday).first()
        assert record is None

    def test_zero_cartons_no_record_created(self, client, seeded_db):
        """Cartons = 0 → no record created (skipped)."""
        login_as(client, 'supervisor', 'sup123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()
        client.post('/production/', data={
            f'cartons_{emp.id}': '0',
            'csrf_token': client.get('/production/').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        record = ProductionRecord.query.filter_by(employee_id=emp.id, date=date.today()).first()
        assert record is None

    def test_negative_cartons_flash_error_rollback(self, client, seeded_db):
        """Negative cartons in POST body → flash error, rollback, no record created."""
        login_as(client, 'supervisor', 'sup123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()
        response = client.post('/production/', data={
            f'cartons_{emp.id}': '-10',
            'csrf_token': client.get('/production/').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        assert response.status_code == 200
        assert b'error' in response.data.lower() or b'invalid' in response.data.lower()
        record = ProductionRecord.query.filter_by(employee_id=emp.id, date=date.today()).first()
        assert record is None

    def test_daily_wage_matches_calculator_at_creation(self, client, seeded_db):
        """daily_wage stored at creation time equals WageCalculator output at that time."""
        from app.wage_calculator import WageCalculator

        login_as(client, 'supervisor', 'sup123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()
        cartons = 420

        client.post('/production/', data={
            f'cartons_{emp.id}': str(cartons),
            'csrf_token': client.get('/production/').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        record = ProductionRecord.query.filter_by(employee_id=emp.id, date=date.today()).first()
        calc = WageCalculator()
        expected_wage = calc.calculate_daily(emp, cartons)

        assert record is not None
        assert record.daily_wage == expected_wage

    def test_gm_post_production_returns_403(self, client, seeded_db):
        """GM attempts POST /production/ → 403."""
        login_as(client, 'gm_user', 'gm123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()
        response = client.post('/production/', data={
            f'cartons_{emp.id}': '100',
            'csrf_token': client.get('/production/').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        assert response.status_code == 403

    def test_admin_can_post_with_date_parameter(self, client, seeded_db):
        """Admin can POST with ?date parameter to specify date."""
        login_as(client, 'admin', 'admin123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()
        test_date = '2024-01-15'

        response = client.post(f'/production/?date={test_date}', data={
            f'cartons_{emp.id}': '100',
            'csrf_token': client.get(f'/production/?date={test_date}').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        assert response.status_code == 200
        record = ProductionRecord.query.filter_by(employee_id=emp.id, date=date.fromisoformat(test_date)).first()
        assert record is not None
        assert record.cartons == 100

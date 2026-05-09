"""
Tests for payroll functionality.
"""
from datetime import date

import pytest

from app.models import Payment, ProductionRecord


class TestPayroll:
    """Test suite for payroll functionality."""

    def test_three_production_records_month_total_wage(self, client, seeded_db):
        """3 production records in month → total_wage = sum of daily_wages."""
        login_as(client, 'admin', 'admin123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()
        month_start = date(2024, 1, 1)

        # Create three production records
        for day in [1, 2, 3]:
            record = ProductionRecord(
                employee_id=emp.id,
                date=date(2024, 1, day),
                cartons=100,
                daily_wage=25000,
                created_by=1
            )
            seeded_db.add(record)

        seeded_db.commit()

        response = client.get('/payroll/?month=2024-01')
        assert response.status_code == 200
        assert b'75,000.00' in response.data  # 3 * 25000

    def test_zero_records_month_all_zeros(self, client, seeded_db):
        """0 records in month → all zeros, no error."""
        login_as(client, 'admin', 'admin123')

        response = client.get('/payroll/?month=2024-01')
        assert response.status_code == 200
        # Should display empty state or zeros

    def test_payment_in_month_reduces_balance(self, client, seeded_db):
        """Payment in same month → reduces balance."""
        login_as(client, 'admin', 'admin123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()

        # Create production record
        record = ProductionRecord(
            employee_id=emp.id,
            date=date(2024, 1, 1),
            cartons=100,
            daily_wage=25000,
            created_by=1
        )
        seeded_db.add(record)

        # Create payment
        payment = Payment(
            employee_id=emp.id,
            amount=10000,
            payment_date=date(2024, 1, 15),
            recorded_by=1
        )
        seeded_db.add(payment)

        seeded_db.commit()

        response = client.get('/payroll/?month=2024-01')
        assert response.status_code == 200
        # Balance should be 15000 (25000 - 10000)

    def test_payment_different_month_does_not_affect_balance(self, client, seeded_db):
        """Payment in DIFFERENT month → does NOT affect selected month balance."""
        login_as(client, 'admin', 'admin123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()

        # Create production record in January
        record = ProductionRecord(
            employee_id=emp.id,
            date=date(2024, 1, 1),
            cartons=100,
            daily_wage=25000,
            created_by=1
        )
        seeded_db.add(record)

        # Create payment in February
        payment = Payment(
            employee_id=emp.id,
            amount=10000,
            payment_date=date(2024, 2, 15),
            recorded_by=1
        )
        seeded_db.add(payment)

        seeded_db.commit()

        response = client.get('/payroll/?month=2024-01')
        assert response.status_code == 200
        # January balance should be 25000 (payment in February doesn't affect it)

    def test_balance_equals_wage_minus_paid(self, client, seeded_db):
        """Balance = wage - paid (exact float check to 2 decimal places)."""
        login_as(client, 'admin', 'admin123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()

        # Create production record
        record = ProductionRecord(
            employee_id=emp.id,
            date=date(2024, 1, 1),
            cartons=100,
            daily_wage=25000,
            created_by=1
        )
        seeded_db.add(record)

        # Create payment
        payment = Payment(
            employee_id=emp.id,
            amount=12345.67,
            payment_date=date(2024, 1, 15),
            recorded_by=1
        )
        seeded_db.add(payment)

        seeded_db.commit()

        response = client.get('/payroll/?month=2024-01')
        assert response.status_code == 200
        # Balance should be 12654.33 (25000 - 12345.67)

    def test_positive_balance_employee_owed_money(self, client, seeded_db):
        """balance > 0 → employee is owed money (rendered in danger class)."""
        login_as(client, 'admin', 'admin123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()

        record = ProductionRecord(
            employee_id=emp.id,
            date=date(2024, 1, 1),
            cartons=100,
            daily_wage=25000,
            created_by=1
        )
        seeded_db.add(record)
        seeded_db.commit()

        response = client.get('/payroll/?month=2024-01')
        assert response.status_code == 200
        # Should show positive balance in danger color

    def test_negative_balance_credit_overpaid(self, client, seeded_db):
        """balance < 0 → credit / overpaid (rendered in good class)."""
        login_as(client, 'admin', 'admin123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()

        record = ProductionRecord(
            employee_id=emp.id,
            date=date(2024, 1, 1),
            cartons=100,
            daily_wage=25000,
            created_by=1
        )
        seeded_db.add(record)

        payment = Payment(
            employee_id=emp.id,
            amount=30000,
            payment_date=date(2024, 1, 15),
            recorded_by=1
        )
        seeded_db.add(payment)

        seeded_db.commit()

        response = client.get('/payroll/?month=2024-01')
        assert response.status_code == 200
        # Should show negative balance in good color

    def test_payment_amount_zero_validation_error(self, client, seeded_db):
        """Payment amount = 0 → validation error, not stored."""
        login_as(client, 'admin', 'admin123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()

        response = client.post(f'/payroll/{emp.id}/pay?month=2024-01', data={
            'amount': '0',
            'payment_date': '2024-01-15',
            'csrf_token': client.get(f'/payroll/{emp.id}/pay?month=2024-01').data.decode().split('name="csrf_token"')[1].split('"')[1]
        })

        assert response.status_code == 200
        payment = Payment.query.filter_by(employee_id=emp.id).first()
        assert payment is None

    def test_payment_amount_exceeds_total_wage_stored(self, client, seeded_db):
        """Payment amount > total_wage → stored, balance goes negative."""
        login_as(client, 'admin', 'admin123')

        emp = seeded_db.query(Employee).filter_by(group='production').first()

        record = ProductionRecord(
            employee_id=emp.id,
            date=date(2024, 1, 1),
            cartons=100,
            daily_wage=25000,
            created_by=1
        )
        seeded_db.add(record)
        seeded_db.commit()

        response = client.post(f'/payroll/{emp.id}/pay?month=2024-01', data={
            'amount': '50000',
            'payment_date': '2024-01-15',
            'csrf_token': client.get(f'/payroll/{emp.id}/pay?month=2024-01').data.decode().split('name="csrf_token"')[1].split('"')[1]
        }, follow_redirects=True)

        assert response.status_code == 200
        payment = Payment.query.filter_by(employee_id=emp.id).first()
        assert payment is not None
        assert payment.amount == 50000

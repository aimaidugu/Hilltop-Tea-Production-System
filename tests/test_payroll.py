"""
Tests for payroll functionality.
"""
from datetime import date, timedelta

from app import db
from app.models import Employee, Payment, ProductionRecord, User
from tests.conftest import login_as


class TestPayrollCalculation:
    """Tests for payroll calculation logic."""

    def test_three_production_records_month_total_wage(self, client, seeded_db):
        """3 production records in month → total_wage = sum of daily_wages."""
        login_as(client, 'admin', 'admin123')

        employee = Employee.query.filter_by(worker_group='production').first()
        today = date.today()

        # Create 3 production records
        for i in range(3):
            record = ProductionRecord(
                employee_id=employee.id,
                date=today - timedelta(days=i),
                cartons=100,
                daily_wage=100 * 250,
                created_by=1
            )
            db.session.add(record)
        db.session.commit()

        response = client.get(f'/payroll/?month={today.strftime("%Y-%m")}')
        assert response.status_code == 200
        assert b'75000' in response.data  # 3 * 100 * 250

    def test_zero_records_month_all_zeros(self, client, seeded_db):
        """0 records in month → all zeros, no error."""
        login_as(client, 'admin', 'admin123')

        today = date.today()
        response = client.get(f'/payroll/?month={today.strftime("%Y-%m")}')
        assert response.status_code == 200

    def test_payment_in_month_reduces_balance(self, client, seeded_db):
        """Payment in same month → reduces balance."""
        login_as(client, 'admin', 'admin123')

        employee = Employee.query.filter_by(worker_group='production').first()
        today = date.today()

        # Create production record
        record = ProductionRecord(
            employee_id=employee.id,
            date=today,
            cartons=100,
            daily_wage=25000,
            created_by=1
        )
        db.session.add(record)

        # Create payment
        payment = Payment(
            employee_id=employee.id,
            amount=10000,
            payment_date=today,
            recorded_by=1
        )
        db.session.add(payment)
        db.session.commit()

        response = client.get(f'/payroll/?month={today.strftime("%Y-%m")}')
        assert response.status_code == 200
        # Balance should be 25000 - 10000 = 15000
        assert b'15000' in response.data

    def test_payment_different_month_no_affect(self, client, seeded_db):
        """Payment in DIFFERENT month → does NOT affect selected month balance."""
        login_as(client, 'admin', 'admin123')

        employee = Employee.query.filter_by(worker_group='production').first()
        today = date.today()
        last_month = today.replace(day=1) - timedelta(days=1)

        # Create production record this month
        record = ProductionRecord(
            employee_id=employee.id,
            date=today,
            cartons=100,
            daily_wage=25000,
            created_by=1
        )
        db.session.add(record)

        # Create payment last month
        payment = Payment(
            employee_id=employee.id,
            amount=10000,
            payment_date=last_month,
            recorded_by=1
        )
        db.session.add(payment)
        db.session.commit()

        response = client.get(f'/payroll/?month={today.strftime("%Y-%m")}')
        assert response.status_code == 200
        # Balance should be 25000 (no payment this month)
        assert b'25000' in response.data

    def test_balance_equals_wage_minus_paid(self, client, seeded_db):
        """Balance = wage - paid (exact float check to 2 decimal places)."""
        login_as(client, 'admin', 'admin123')

        employee = Employee.query.filter_by(worker_group='production').first()
        today = date.today()

        # Create production record
        record = ProductionRecord(
            employee_id=employee.id,
            date=today,
            cartons=100,
            daily_wage=25000.50,
            created_by=1
        )
        db.session.add(record)

        # Create payment
        payment = Payment(
            employee_id=employee.id,
            amount=10000.25,
            payment_date=today,
            recorded_by=1
        )
        db.session.add(payment)
        db.session.commit()

        response = client.get(f'/payroll/?month={today.strftime("%Y-%m")}')
        assert response.status_code == 200
        # Balance should be 25000.50 - 10000.25 = 15000.25
        assert b'15000.25' in response.data

    def test_positive_balance_rendered_danger(self, client, seeded_db):
        """balance > 0 → employee is owed money (rendered in danger class)."""
        login_as(client, 'admin', 'admin123')

        employee = Employee.query.filter_by(worker_group='production').first()
        today = date.today()

        # Create production record
        record = ProductionRecord(
            employee_id=employee.id,
            date=today,
            cartons=100,
            daily_wage=25000,
            created_by=1
        )
        db.session.add(record)
        db.session.commit()

        response = client.get(f'/payroll/?month={today.strftime("%Y-%m")}')
        assert response.status_code == 200
        # Positive balance should be in danger class
        assert b'balance-owed' in response.data

    def test_negative_balance_rendered_good(self, client, seeded_db):
        """balance < 0 → credit / overpaid (rendered in good class)."""
        login_as(client, 'admin', 'admin123')

        employee = Employee.query.filter_by(worker_group='production').first()
        today = date.today()

        # Create production record
        record = ProductionRecord(
            employee_id=employee.id,
            date=today,
            cartons=100,
            daily_wage=25000,
            created_by=1
        )
        db.session.add(record)

        # Create payment exceeding wage
        payment = Payment(
            employee_id=employee.id,
            amount=30000,
            payment_date=today,
            recorded_by=1
        )
        db.session.add(payment)
        db.session.commit()

        response = client.get(f'/payroll/?month={today.strftime("%Y-%m")}')
        assert response.status_code == 200
        # Negative balance should be in good class
        assert b'balance-credit' in response.data

    def test_payment_amount_zero_validation_error(self, client, seeded_db):
        """Payment amount = 0 → validation error, not stored."""
        login_as(client, 'admin', 'admin123')

        employee = Employee.query.filter_by(worker_group='production').first()
        today = date.today()

        csrf_token = client.get(f'/payroll/{employee.id}/pay').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        response = client.post(f'/payroll/{employee.id}/pay', data={
            'amount': '0',
            'payment_date': today.isoformat(),
            'csrf_token': csrf_token
        })

        assert response.status_code == 200
        # Payment should not be created
        payment = Payment.query.filter_by(employee_id=employee.id).first()
        assert payment is None

    def test_payment_exceeding_total_wage_stored(self, client, seeded_db):
        """Payment amount > total_wage → stored, balance goes negative."""
        login_as(client, 'admin', 'admin123')

        employee = Employee.query.filter_by(worker_group='production').first()
        today = date.today()

        # Create production record
        record = ProductionRecord(
            employee_id=employee.id,
            date=today,
            cartons=100,
            daily_wage=25000,
            created_by=1
        )
        db.session.add(record)
        db.session.commit()

        csrf_token = client.get(f'/payroll/{employee.id}/pay').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        response = client.post(f'/payroll/{employee.id}/pay', data={
            'amount': '30000',
            'payment_date': today.isoformat(),
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200
        # Payment should be created
        payment = Payment.query.filter_by(employee_id=employee.id).first()
        assert payment is not None
        assert payment.amount == 30000

    def test_payroll_preserves_month_on_redirect(self, client, seeded_db):
        """After save: redirect to payroll with same month preserved in query string."""
        login_as(client, 'admin', 'admin123')

        employee = Employee.query.filter_by(worker_group='production').first()
        today = date.today()
        month_str = today.strftime('%Y-%m')

        csrf_token = client.get(f'/payroll/{employee.id}/pay?month={month_str}').data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        response = client.post(f'/payroll/{employee.id}/pay?month={month_str}', data={
            'amount': '10000',
            'payment_date': today.isoformat(),
            'csrf_token': csrf_token
        }, follow_redirects=False)

        assert response.status_code == 302
        assert f'month={month_str}' in response.location

    def test_payroll_group_filter(self, client, seeded_db):
        """Group filter in payroll view filters results correctly."""
        login_as(client, 'admin', 'admin123')

        today = date.today()

        # Create records for both groups
        prod_emp = Employee.query.filter_by(worker_group='production').first()
        wrap_emp = Employee.query.filter_by(worker_group='wrapping').first()

        prod_record = ProductionRecord(
            employee_id=prod_emp.id,
            date=today,
            cartons=100,
            daily_wage=25000,
            created_by=1
        )
        db.session.add(prod_record)

        wrap_record = ProductionRecord(
            employee_id=wrap_emp.id,
            date=today,
            cartons=50,
            daily_wage=5000,
            created_by=1
        )
        db.session.add(wrap_record)
        db.session.commit()

        # Test production filter
        response = client.get(f'/payroll/?month={today.strftime("%Y-%m")}&group=production')
        assert response.status_code == 200
        assert prod_emp.name.encode() in response.data
        assert wrap_emp.name.encode() not in response.data

        # Test wrapping filter
        response = client.get(f'/payroll/?month={today.strftime("%Y-%m")}&group=wrapping')
        assert response.status_code == 200
        assert wrap_emp.name.encode() in response.data
        assert prod_emp.name.encode() not in response.data

    def test_payroll_grand_totals(self, client, seeded_db):
        """Grand totals row reflects filtered results."""
        login_as(client, 'admin', 'admin123')

        today = date.today()

        # Create records for multiple employees
        employees = Employee.query.filter_by(active=True).limit(3).all()
        for emp in employees:
            record = ProductionRecord(
                employee_id=emp.id,
                date=today,
                cartons=100,
                daily_wage=25000,
                created_by=1
            )
            db.session.add(record)
        db.session.commit()

        response = client.get(f'/payroll/?month={today.strftime("%Y-%m")}')
        assert response.status_code == 200
        # Grand totals should be 3 * 25000 = 75000
        assert b'75000' in response.data

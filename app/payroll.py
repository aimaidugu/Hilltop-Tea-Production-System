"""
Hilltop Tea — Payroll Blueprint.

Monthly payroll view and payment recording.
"""
from datetime import date, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.forms import PaymentForm
from app.models import Employee, Payment, ProductionRecord
from app.utils import flash_error, flash_success, get_adjacent_months, month_range, paginate

payroll_bp = Blueprint('payroll', __name__)


@payroll_bp.route('/')
@login_required
def index():
    """
    Monthly payroll view.

    GET: Render payroll table with month picker and filters.
    """
    # Get month from query string, default to previous month
    month_str = request.args.get('month')
    if month_str:
        try:
            first_day, last_day = month_range(month_str)
        except ValueError:
            # Invalid format, default to previous month
            today = date.today()
            if today.month == 1:
                first_day = date(today.year - 1, 12, 1)
            else:
                first_day = date(today.year, today.month - 1, 1)
            last_day = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            month_str = first_day.strftime('%Y-%m')
            flash_error('Invalid month format. Using previous month.')
    else:
        today = date.today()
        if today.month == 1:
            first_day = date(today.year - 1, 12, 1)
        else:
            first_day = date(today.year, today.month - 1, 1)
        last_day = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        month_str = first_day.strftime('%Y-%m')

    # ═══════════════════════════════════════════════════════════════
    # PPP: payroll_view
    # ═══════════════════════════════════════════════════════════════
    # PRE-CONDITIONS:
    #   - User is authenticated (any role)
    #   - ?month=YYYY-MM query param (default: previous calendar month)
    #
    # ALGORITHM:
    #   1. Parse month string → first_day (date), last_day (date)
    #   2. IF parse fails: default to previous month; flash warning
    #   3. Build base query: all employees (active OR has records this month)
    #   4. FOR EACH employee:
    #      a. wage_total = SUM(ProductionRecord.daily_wage)
    #              WHERE employee_id=id AND date BETWEEN first_day AND last_day
    #      b. carton_total = SUM(ProductionRecord.cartons)
    #              WHERE employee_id=id AND date BETWEEN first_day AND last_day
    #      c. paid_total = SUM(Payment.amount)
    #              WHERE employee_id=id AND payment_date BETWEEN first_day AND last_day
    #      d. balance = wage_total - paid_total
    #      e. Append row dict to results
    #   5. Apply group filter if ?group= param present
    #   6. Sort by employee name ASC
    #   7. Compute grand_totals = sum of all columns
    #   8. Render payroll.html with results, grand_totals, month, adjacent months
    #
    # PERFORMANCE NOTE:
    #   Use a single SQL query with LEFT JOINs and GROUP BY employee_id,
    #   NOT N+1 queries. On Vercel (10s timeout), N+1 across 100+ employees
    #   will exceed the limit.
    #
    # POST-CONDITIONS:
    #   - Each row has correct wage, paid, balance for the selected month only
    #   - Grand totals row reflects filtered results
    # ═══════════════════════════════════════════════════════════════

    # Single query with LEFT JOINs and GROUP BY for performance
    from sqlalchemy import func, case

    query = db.session.query(
        Employee.id,
        Employee.name,
        Employee.worker_group,
        func.coalesce(func.sum(ProductionRecord.cartons), 0).label('carton_total'),
        func.coalesce(func.sum(ProductionRecord.daily_wage), 0).label('wage_total'),
        func.coalesce(func.sum(Payment.amount), 0).label('paid_total'),
    ).outerjoin(
        ProductionRecord,
        (ProductionRecord.employee_id == Employee.id) &
        (ProductionRecord.date >= first_day) &
        (ProductionRecord.date <= last_day)
    ).outerjoin(
        Payment,
        (Payment.employee_id == Employee.id) &
        (Payment.payment_date >= first_day) &
        (Payment.payment_date <= last_day)
    ).group_by(Employee.id).order_by(Employee.name)

    # Apply group filter
    group_filter = request.args.get('group')
    if group_filter and group_filter in ('production', 'wrapping'):
        query = query.filter(Employee.worker_group == group_filter)

    results = query.all()

    # Build result list with calculated balance
    payroll_data = []
    grand_wage = 0
    grand_paid = 0
    grand_cartons = 0

    for emp_id, emp_name, emp_group, carton_total, wage_total, paid_total in results:
        balance = wage_total - paid_total
        payroll_data.append({
            'id': emp_id,
            'name': emp_name,
            'group': emp_group.value if emp_group else 'unknown',
            'cartons': int(carton_total),
            'wage': float(wage_total),
            'paid': float(paid_total),
            'balance': balance,
        })
        grand_wage += wage_total
        grand_paid += paid_total
        grand_cartons += carton_total

    grand_balance = grand_wage - grand_paid

    # Get adjacent months for navigation
    prev_month, next_month = get_adjacent_months(month_str)

    return render_template(
        'payroll.html',
        month_str=month_str,
        payroll_data=payroll_data,
        grand_cartons=grand_cartons,
        grand_wage=grand_wage,
        grand_paid=grand_paid,
        grand_balance=grand_balance,
        prev_month=prev_month,
        next_month=next_month,
        group_filter=group_filter,
    )


@payroll_bp.route('/<int:employee_id>/pay', methods=['GET', 'POST'])
@login_required
def record_payment(employee_id):
    """
    Record a payment for an employee.

    GET: Render payment form.
    POST: Save payment and redirect to payroll view.
    """
    employee = Employee.query.get_or_404(employee_id)
    form = PaymentForm()

    # Pre-fill date with today
    if not form.payment_date.data:
        form.payment_date.data = date.today()

    if form.validate_on_submit():
        payment = Payment(
            employee_id=employee.id,
            amount=form.amount.data,
            payment_date=form.payment_date.data,
            notes=form.notes.data,
            recorded_by=current_user.id
        )
        db.session.add(payment)
        db.session.commit()

        flash_success(f'Payment of ₦{form.amount.data:,.2f} recorded for {employee.name}.')

        # Redirect back to payroll with the same month
        month_str = request.args.get('month')
        if month_str:
            return redirect(url_for('payroll.index', month=month_str))
        return redirect(url_for('payroll.index'))

    return render_template(
        'record_payment.html',
        form=form,
        employee=employee,
        month_str=request.args.get('month'),
    )

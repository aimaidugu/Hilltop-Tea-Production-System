"""
Hilltop Tea — Payroll Management Blueprint.

Handles monthly payroll view and payment recording.
All authenticated users can access.
"""
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.forms import PaymentForm
from app.models import Employee, Payment, ProductionRecord
from app.utils import get_adjacent_months, get_previous_month, month_range, paginate

payroll_bp = Blueprint('payroll', __name__)


@payroll_bp.route('/')
@login_required
def payroll_view():
    """
    Display monthly payroll summary with wage, paid, and balance per employee.

    Query parameter ?month=YYYY-MM selects the month (default: previous month).
    Query parameter ?group=production|wrapping filters by employee group.
    """
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

    month_str = request.args.get('month', get_previous_month())
    group_filter = request.args.get('group')

    try:
        first_day, last_day = month_range(month_str)
    except ValueError:
        flash(f'Invalid month format: {month_str}. Using previous month.', 'warning')
        month_str = get_previous_month()
        first_day, last_day = month_range(month_str)

    # Single query with LEFT JOINs and GROUP BY for performance
    query = db.session.query(
        Employee.id,
        Employee.name,
        Employee.group,
        Employee.active,
        db.func.coalesce(db.func.sum(ProductionRecord.cartons), 0).label('carton_total'),
        db.func.coalesce(db.func.sum(ProductionRecord.daily_wage), 0).label('wage_total'),
        db.func.coalesce(db.func.sum(Payment.amount), 0).label('paid_total')
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
    if group_filter and group_filter in ('production', 'wrapping'):
        query = query.filter(Employee.group == group_filter)

    results = query.all()

    # Build result list with calculated balance
    payroll_data = []
    grand_totals = {'cartons': 0, 'wage': 0, 'paid': 0, 'balance': 0}

    for row in results:
        wage_total = float(row.wage_total)
        paid_total = float(row.paid_total)
        balance = wage_total - paid_total

        payroll_data.append({
            'id': row.id,
            'name': row.name,
            'group': row.group,
            'active': row.active,
            'cartons': int(row.carton_total),
            'wage': wage_total,
            'paid': paid_total,
            'balance': balance
        })

        grand_totals['cartons'] += int(row.carton_total)
        grand_totals['wage'] += wage_total
        grand_totals['paid'] += paid_total
        grand_totals['balance'] += balance

    # Get adjacent months for navigation
    prev_month, next_month = get_adjacent_months(month_str)

    return render_template('payroll.html',
                          payroll_data=payroll_data,
                          grand_totals=grand_totals,
                          month_str=month_str,
                          prev_month=prev_month,
                          next_month=next_month,
                          group_filter=group_filter)


@payroll_bp.route('/<int:employee_id>/pay', methods=['GET', 'POST'])
@login_required
def record_payment(employee_id):
    """
    Record a payment for an employee.

    GET: Render payment form.
    POST: Save payment and redirect to payroll with month preserved.
    """
    employee = Employee.query.get_or_404(employee_id)
    month_str = request.args.get('month', get_previous_month())

    form = PaymentForm()
    if form.validate_on_submit():
        payment = Payment(
            employee_id=employee_id,
            amount=form.amount.data,
            payment_date=form.payment_date.data,
            notes=form.notes.data,
            recorded_by=current_user.id
        )
        db.session.add(payment)
        db.session.commit()
        flash(f'Payment of ₦{form.amount.data:,.2f} recorded for {employee.name}.', 'success')
        return redirect(url_for('payroll.payroll_view', month=month_str))

    return render_template('record_payment.html',
                          form=form,
                          employee=employee,
                          month_str=month_str)

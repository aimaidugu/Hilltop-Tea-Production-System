"""
Hilltop Tea — Main Blueprint.

Dashboard and analytics views.
"""
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required

from app import db
from app.models import Employee, Payment, ProductionRecord
from app.utils import month_range

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    """
    Main dashboard view.

    Displays:
    - Today's production summary
    - Current month payroll overview
    - Charts for analytics
    - Recent activity
    """
    today = date.today()
    current_month = today.strftime('%Y-%m')

    # Today's production
    today_records = ProductionRecord.query.filter_by(date=today).all()
    today_cartons = sum(r.cartons for r in today_records)
    today_employees = len(set(r.employee_id for r in today_records))

    # Current month payroll
    first_day, last_day = month_range(current_month)
    month_wages = db.session.query(
        db.func.sum(ProductionRecord.daily_wage)
    ).filter(
        ProductionRecord.date >= first_day,
        ProductionRecord.date <= last_day
    ).scalar() or 0

    month_paid = db.session.query(
        db.func.sum(Payment.amount)
    ).filter(
        Payment.payment_date >= first_day,
        Payment.payment_date <= last_day
    ).scalar() or 0

    month_balance = month_wages - month_paid

    # Last 14 days daily cartons (for bar chart)
    fourteen_days_ago = today - timedelta(days=13)
    daily_cartons = db.session.query(
        ProductionRecord.date,
        db.func.sum(ProductionRecord.cartons)
    ).filter(
        ProductionRecord.date >= fourteen_days_ago,
        ProductionRecord.date <= today
    ).group_by(ProductionRecord.date).order_by(ProductionRecord.date).all()

    daily_chart_labels = [d.strftime('%b %d') for d, _ in daily_cartons]
    daily_chart_data = [float(c) for _, c in daily_cartons]

    # Last 6 months wage totals (for line chart)
    monthly_wages = []
    monthly_labels = []
    for i in range(5, -1, -1):
        month_date = (today.replace(day=1) - timedelta(days=32*i)).replace(day=1)
        month_str = month_date.strftime('%Y-%m')
        fd, ld = month_range(month_str)

        total = db.session.query(
            db.func.sum(ProductionRecord.daily_wage)
        ).filter(
            ProductionRecord.date >= fd,
            ProductionRecord.date <= ld
        ).scalar() or 0

        monthly_wages.append(float(total))
        monthly_labels.append(month_date.strftime('%b %Y'))

    # Current month wage split by group (for donut chart)
    production_wages = db.session.query(
        db.func.sum(ProductionRecord.daily_wage)
    ).join(Employee).filter(
        Employee.worker_group == 'production',
        ProductionRecord.date >= first_day,
        ProductionRecord.date <= last_day
    ).scalar() or 0

    wrapping_wages = db.session.query(
        db.func.sum(ProductionRecord.daily_wage)
    ).join(Employee).filter(
        Employee.worker_group == 'wrapping',
        ProductionRecord.date >= first_day,
        ProductionRecord.date <= last_day
    ).scalar() or 0

    wage_split_labels = ['Production', 'Wrapping']
    wage_split_data = [float(production_wages), float(wrapping_wages)]

    # Recent payments
    recent_payments = Payment.query.order_by(
        Payment.timestamp.desc()
    ).limit(5).all()

    return render_template(
        'index.html',
        today=today,
        current_month=current_month,
        today_cartons=today_cartons,
        today_employees=today_employees,
        month_wages=month_wages,
        month_paid=month_paid,
        month_balance=month_balance,
        daily_chart_labels=daily_chart_labels,
        daily_chart_data=daily_chart_data,
        monthly_labels=monthly_labels,
        monthly_wages=monthly_wages,
        wage_split_labels=wage_split_labels,
        wage_split_data=wage_split_data,
        recent_payments=recent_payments,
    )


@main_bp.route('/api/chart-data')
@login_required
def chart_data():
    """
    API endpoint for chart data.

    Returns JSON data for dashboard charts.
    """
    today = date.today()

    # Last 14 days daily cartons
    fourteen_days_ago = today - timedelta(days=13)
    daily_cartons = db.session.query(
        ProductionRecord.date,
        db.func.sum(ProductionRecord.cartons)
    ).filter(
        ProductionRecord.date >= fourteen_days_ago,
        ProductionRecord.date <= today
    ).group_by(ProductionRecord.date).order_by(ProductionRecord.date).all()

    return jsonify({
        'daily_cartons': [
            {'date': d.strftime('%Y-%m-%d'), 'cartons': int(c)}
            for d, c in daily_cartons
        ]
    })

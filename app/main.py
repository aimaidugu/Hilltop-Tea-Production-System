"""
Hilltop Tea — Main Dashboard Blueprint.

Provides the main dashboard view with analytics and summary statistics.
"""
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, render_template
from flask_login import login_required

from app import db
from app.models import Employee, Payment, ProductionRecord

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    """
    Main dashboard with production and payroll analytics.

    Displays:
    - Today's production summary
    - Current month payroll overview
    - Charts for daily cartons, monthly trends, and wage split
    - Recent payment activity
    """
    today = datetime.utcnow().date()
    first_of_month = today.replace(day=1)

    # Today's production
    today_records = ProductionRecord.query.filter_by(date=today).all()
    today_cartons = sum(r.cartons for r in today_records)
    today_employees = len(today_records)

    # Current month payroll
    month_records = ProductionRecord.query.filter(
        ProductionRecord.date >= first_of_month,
        ProductionRecord.date <= today
    ).all()
    month_wages = sum(r.daily_wage for r in month_records)

    month_payments = Payment.query.filter(
        Payment.payment_date >= first_of_month,
        Payment.payment_date <= today
    ).all()
    month_paid = sum(p.amount for p in month_payments)

    month_balance = month_wages - month_paid

    # Last 14 days daily cartons
    fourteen_days_ago = today - timedelta(days=14)
    daily_cartons = db.session.query(
        ProductionRecord.date,
        db.func.sum(ProductionRecord.cartons).label('total')
    ).filter(
        ProductionRecord.date >= fourteen_days_ago
    ).group_by(ProductionRecord.date).order_by(ProductionRecord.date).all()

    daily_chart_labels = [d[0].strftime('%b %d') for d in daily_cartons]
    daily_chart_data = [int(d[1]) if d[1] else 0 for d in daily_cartons]

    # Last 6 months wage totals
    monthly_wages = []
    monthly_labels = []
    for i in range(6):
        month_start = (first_of_month - timedelta(days=32 * i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        total = db.session.query(db.func.sum(ProductionRecord.daily_wage)).filter(
            ProductionRecord.date >= month_start,
            ProductionRecord.date <= month_end
        ).scalar() or 0
        monthly_wages.insert(0, float(total))
        monthly_labels.insert(0, month_start.strftime('%b %Y'))

    # Current month wage split by group
    production_wage = db.session.query(db.func.sum(ProductionRecord.daily_wage)).join(
        Employee, Employee.id == ProductionRecord.employee_id
    ).filter(
        Employee.group == 'production',
        ProductionRecord.date >= first_of_month,
        ProductionRecord.date <= today
    ).scalar() or 0

    wrapping_wage = db.session.query(db.func.sum(ProductionRecord.daily_wage)).join(
        Employee, Employee.id == ProductionRecord.employee_id
    ).filter(
        Employee.group == 'wrapping',
        ProductionRecord.date >= first_of_month,
        ProductionRecord.date <= today
    ).scalar() or 0

    wage_split_labels = ['Production', 'Wrapping']
    wage_split_data = [float(production_wage), float(wrapping_wage)]

    # Recent payments (last 5)
    recent_payments = Payment.query.order_by(
        Payment.timestamp.desc()
    ).limit(5).all()

    return render_template('index.html',
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
                          recent_payments=recent_payments)


@main_bp.route('/api/daily-cartons')
@login_required
def api_daily_cartons():
    """API endpoint for daily carton chart data."""
    today = datetime.utcnow().date()
    fourteen_days_ago = today - timedelta(days=14)

    daily_cartons = db.session.query(
        ProductionRecord.date,
        db.func.sum(ProductionRecord.cartons).label('total')
    ).filter(
        ProductionRecord.date >= fourteen_days_ago
    ).group_by(ProductionRecord.date).order_by(ProductionRecord.date).all()

    return jsonify({
        'labels': [d[0].strftime('%b %d') for d in daily_cartons],
        'data': [int(d[1]) if d[1] else 0 for d in daily_cartons]
    })


@main_bp.route('/api/monthly-wages')
@login_required
def api_monthly_wages():
    """API endpoint for monthly wage trend chart data."""
    today = datetime.utcnow().date()
    first_of_month = today.replace(day=1)

    monthly_wages = []
    monthly_labels = []
    for i in range(6):
        month_start = (first_of_month - timedelta(days=32 * i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        total = db.session.query(db.func.sum(ProductionRecord.daily_wage)).filter(
            ProductionRecord.date >= month_start,
            ProductionRecord.date <= month_end
        ).scalar() or 0
        monthly_wages.insert(0, float(total))
        monthly_labels.insert(0, month_start.strftime('%b %Y'))

    return jsonify({
        'labels': monthly_labels,
        'data': monthly_wages
    })


@main_bp.route('/api/wage-split')
@login_required
def api_wage_split():
    """API endpoint for wage split by group chart data."""
    today = datetime.utcnow().date()
    first_of_month = today.replace(day=1)

    production_wage = db.session.query(db.func.sum(ProductionRecord.daily_wage)).join(
        Employee, Employee.id == ProductionRecord.employee_id
    ).filter(
        Employee.group == 'production',
        ProductionRecord.date >= first_of_month,
        ProductionRecord.date <= today
    ).scalar() or 0

    wrapping_wage = db.session.query(db.func.sum(ProductionRecord.daily_wage)).join(
        Employee, Employee.id == ProductionRecord.employee_id
    ).filter(
        Employee.group == 'wrapping',
        ProductionRecord.date >= first_of_month,
        ProductionRecord.date <= today
    ).scalar() or 0

    return jsonify({
        'labels': ['Production', 'Wrapping'],
        'data': [float(production_wage), float(wrapping_wage)]
    })

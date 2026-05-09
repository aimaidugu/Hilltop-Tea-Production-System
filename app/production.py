"""
Hilltop Tea — Production Entry Blueprint.

Handles daily production record entry and history viewing.
Supervisor and Admin access.
"""
from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.forms import ProductionEntryForm
from app.models import Employee, ProductionRecord
from app.utils import month_range, paginate, require_role
from app.wage_calculator import WageCalculator

production_bp = Blueprint('production', __name__)


@production_bp.route('/', methods=['GET', 'POST'])
@login_required
@require_role('supervisor', 'admin')
def daily_production():
    """
    Handle daily production entry.

    GET: Render form with today's records pre-filled.
    POST: Save or update production records for today.

    Supervisors can only submit for today. Admins can select date.
    """
    form = ProductionEntryForm()

    # Determine date to use
    if current_user.role == 'admin':
        date_str = request.args.get('date')
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Using today.', 'warning')
                selected_date = datetime.utcnow().date()
        else:
            selected_date = datetime.utcnow().date()
    else:
        selected_date = datetime.utcnow().date()

    # Get all active employees
    employees = Employee.query.filter_by(active=True).order_by(Employee.name).all()

    # Get existing records for this date
    existing_records = {
        r.employee_id: r
        for r in ProductionRecord.query.filter_by(date=selected_date).all()
    }

    # Pre-fill form data
    if request.method == 'GET':
        for emp in employees:
            if emp.id in existing_records:
                setattr(form, f'cartons_{emp.id}', existing_records[emp.id].cartons)
            else:
                setattr(form, f'cartons_{emp.id}', 0)

    if form.validate_on_submit() and request.method == 'POST':
        # ═══════════════════════════════════════════════════════════════
        # PPP: save_daily_production
        # ═══════════════════════════════════════════════════════════════
        # PRE-CONDITIONS:
        #   - User is authenticated with role 'supervisor' or 'admin'
        #   - Today's date is used; Supervisor cannot submit for past dates
        #
        # ALGORITHM:
        #   1. Initialise: calc = WageCalculator(); saved = 0; errors = []
        #   2. Begin DB transaction
        #   3. FOR EACH active employee (employee_id from form fields):
        #      a. Read cartons_<id> from form; convert to int
        #      b. IF conversion fails OR cartons < 0:
        #            Append to errors; continue to next employee
        #      c. IF cartons == 0: skip (no record for zero cartons)
        #      d. wage = calc.calculate_daily(employee, cartons)
        #      e. QUERY existing = ProductionRecord WHERE
        #            employee_id=id AND date=today
        #      f. IF existing: UPDATE existing.cartons and existing.daily_wage
        #         ELSE: INSERT new ProductionRecord
        #      g. Increment saved counter
        #   4. IF errors: rollback; flash each error; re-render form
        #   5. ELSE: commit; flash "Production saved for {saved} employees"; redirect GET
        #
        # POST-CONDITIONS:
        #   - All valid entries have exactly one ProductionRecord for today
        #   - daily_wage reflects rate at time of save (immutable after)
        #   - PRG pattern prevents double-submit on browser refresh
        # ═══════════════════════════════════════════════════════════════

        calc = WageCalculator()
        saved = 0
        errors = []

        try:
            for emp in employees:
                cartons_field = f'cartons_{emp.id}'
                cartons_str = request.form.get(cartons_field, '0')

                try:
                    cartons = int(cartons_str)
                except (ValueError, TypeError):
                    errors.append(f'Invalid carton count for {emp.name}')
                    continue

                if cartons < 0:
                    errors.append(f'Negative cartons for {emp.name}')
                    continue

                if cartons == 0:
                    existing = existing_records.get(emp.id)
                    if existing:
                        db.session.delete(existing)
                    continue

                wage = calc.calculate_daily(emp, cartons)

                existing = existing_records.get(emp.id)
                if existing:
                    existing.cartons = cartons
                    existing.daily_wage = wage
                    existing.created_by = current_user.id
                else:
                    record = ProductionRecord(
                        employee_id=emp.id,
                        date=selected_date,
                        cartons=cartons,
                        daily_wage=wage,
                        created_by=current_user.id
                    )
                    db.session.add(record)

                saved += 1

            if errors:
                db.session.rollback()
                for error in errors:
                    flash(error, 'danger')
                return render_template('production_entry.html',
                                      form=form,
                                      employees=employees,
                                      selected_date=selected_date,
                                      existing_records=existing_records)

            db.session.commit()
            flash(f'Production saved for {saved} employees.', 'success')
            return redirect(url_for('production.daily_production',
                                    date=selected_date.strftime('%Y-%m-%d')))

        except Exception as e:
            db.session.rollback()
            flash(f'Error saving production: {str(e)}', 'danger')
            return render_template('production_entry.html',
                                  form=form,
                                  employees=employees,
                                  selected_date=selected_date,
                                  existing_records=existing_records)

    return render_template('production_entry.html',
                          form=form,
                          employees=employees,
                          selected_date=selected_date,
                          existing_records=existing_records)


@production_bp.route('/history')
@login_required
@require_role('admin', 'gm')
def production_history():
    """
    Display paginated production history with date and employee filters.

    Admin and GM only.
    """
    page = request.args.get('page', 1, type=int)
    date_filter = request.args.get('date')
    employee_filter = request.args.get('employee', type=int)

    query = ProductionRecord.query.join(Employee)

    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(ProductionRecord.date == filter_date)
        except ValueError:
            pass

    if employee_filter:
        query = query.filter(ProductionRecord.employee_id == employee_filter)

    query = query.order_by(ProductionRecord.date.desc(), Employee.name)
    pagination = paginate(query, page)

    # Get all employees for filter dropdown
    all_employees = Employee.query.filter_by(active=True).order_by(Employee.name).all()

    return render_template('production_history.html',
                          records=pagination.items,
                          pagination=pagination,
                          date_filter=date_filter,
                          employee_filter=employee_filter,
                          all_employees=all_employees)

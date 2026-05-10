"""
Hilltop Tea — Production Entry Blueprint.

Handles daily production record entry and history.
"""
from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.forms import ProductionEntryForm
from app.models import Employee, ProductionRecord
from app.utils import flash_error, flash_success, paginate, require_role
from app.wage_calculator import WageCalculator

production_bp = Blueprint('production', __name__)


@production_bp.route('/', methods=['GET', 'POST'])
@login_required
@require_role('supervisor', 'admin')
def index():
    """
    Daily production entry form.

    GET: Render form with today's records pre-filled.
    POST: Save production data for all active employees.
    """
    form = ProductionEntryForm()

    # Determine date (supervisors only see today, admins can select)
    if current_user.role == 'admin':
        date_str = request.args.get('date')
        if date_str:
            try:
                entry_date = date.fromisoformat(date_str)
            except ValueError:
                entry_date = date.today()
                flash_error('Invalid date format. Using today.')
        else:
            entry_date = date.today()
    else:
        entry_date = date.today()

    # Get all active employees
    employees = Employee.query.filter_by(active=True).order_by(Employee.name).all()

    # Get existing records for this date
    existing_records = {
        r.employee_id: r
        for r in ProductionRecord.query.filter_by(date=entry_date).all()
    }

    if form.validate_on_submit():
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
            for employee in employees:
                field_name = f'cartons_{employee.id}'
                cartons_str = request.form.get(field_name, '0')

                try:
                    cartons = int(cartons_str)
                except ValueError:
                    errors.append(f'Invalid carton count for {employee.name}')
                    continue

                if cartons < 0:
                    errors.append(f'Cartons cannot be negative for {employee.name}')
                    continue

                if cartons == 0:
                    # Skip zero carton entries
                    existing = existing_records.get(employee.id)
                    if existing:
                        db.session.delete(existing)
                    continue

                wage = calc.calculate_daily(employee, cartons)

                existing = existing_records.get(employee.id)
                if existing:
                    existing.cartons = cartons
                    existing.daily_wage = wage
                    existing.created_by = current_user.id
                else:
                    record = ProductionRecord(
                        employee_id=employee.id,
                        date=entry_date,
                        cartons=cartons,
                        daily_wage=wage,
                        created_by=current_user.id
                    )
                    db.session.add(record)

                saved += 1

            if errors:
                db.session.rollback()
                for error in errors:
                    flash_error(error)
                return render_template(
                    'production_entry.html',
                    form=form,
                    employees=employees,
                    entry_date=entry_date,
                    existing_records=existing_records,
                )

            db.session.commit()
            flash_success(f'Production saved for {saved} employees.')
            return redirect(url_for('production.index', date=entry_date.isoformat()))

        except Exception as e:
            db.session.rollback()
            flash_error(f'Error saving production: {str(e)}')
            return render_template(
                'production_entry.html',
                form=form,
                employees=employees,
                entry_date=entry_date,
                existing_records=existing_records,
            )

    return render_template(
        'production_entry.html',
        form=form,
        employees=employees,
        entry_date=entry_date,
        existing_records=existing_records,
    )


@production_bp.route('/history')
@login_required
@require_role('admin', 'gm')
def history():
    """
    Production history view.

    GET: Render paginated table of all production records with filters.
    """
    page = request.args.get('page', 1, type=int)
    date_filter = request.args.get('date')
    employee_filter = request.args.get('employee')

    query = ProductionRecord.query.join(Employee)

    if date_filter:
        try:
            filter_date = date.fromisoformat(date_filter)
            query = query.filter(ProductionRecord.date == filter_date)
        except ValueError:
            pass

    if employee_filter:
        query = query.filter(Employee.id == employee_filter)

    query = query.order_by(ProductionRecord.date.desc(), Employee.name)
    pagination = paginate(query, page)

    # Get all employees for filter dropdown
    all_employees = Employee.query.filter_by(active=True).order_by(Employee.name).all()

    return render_template(
        'production_history.html',
        pagination=pagination,
        all_employees=all_employees,
        date_filter=date_filter,
        employee_filter=employee_filter,
    )

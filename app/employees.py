"""
Hilltop Tea — Employee Management Blueprint.

CRUD operations for employee records. Admin only.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.forms import EmployeeForm
from app.models import Employee, Payment, ProductionRecord
from app.utils import flash_error, flash_success, paginate, require_role

employees_bp = Blueprint('employees', __name__)


@employees_bp.route('/')
@login_required
@require_role('admin')
def index():
    """
    List all active employees with pagination.

    GET: Render paginated list of active employees.
    """
    page = request.args.get('page', 1, type=int)
    query = Employee.query.filter_by(active=True).order_by(Employee.name)
    pagination = paginate(query, page)
    return render_template('employee_list.html', pagination=pagination, active_only=True)


@employees_bp.route('/inactive')
@login_required
@require_role('admin')
def inactive():
    """
    List all inactive employees.

    GET: Render list of inactive employees with reactivate option.
    """
    page = request.args.get('page', 1, type=int)
    query = Employee.query.filter_by(active=False).order_by(Employee.name)
    pagination = paginate(query, page)
    return render_template('employee_list.html', pagination=pagination, active_only=False)


@employees_bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def add():
    """
    Add a new employee.

    GET: Render employee creation form.
    POST: Create new employee and redirect to list.
    """
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee(
            name=form.name.data,
            worker_group=form.group.data
        )
        db.session.add(employee)
        db.session.commit()
        flash_success(f'Employee {employee.name} added successfully.')
        return redirect(url_for('employees.index'))

    return render_template('employee_form.html', form=form, title='Add Employee')


@employees_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def edit(id):
    """
    Edit an existing employee.

    GET: Render employee edit form.
    POST: Update employee and redirect to list.
    """
    employee = Employee.query.get_or_404(id)
    form = EmployeeForm(obj=employee)

    if form.validate_on_submit():
        employee.name = form.name.data
        employee.worker_group = form.group.data
        db.session.commit()
        flash_success(f'Employee {employee.name} updated successfully.')
        return redirect(url_for('employees.index'))

    return render_template('employee_form.html', form=form, title='Edit Employee', employee=employee)


@employees_bp.route('/<int:id>/deactivate', methods=['POST'])
@login_required
@require_role('admin')
def deactivate(id):
    """
    Soft delete an employee (set active=False).

    POST: Deactivate employee and redirect to list.
    """
    employee = Employee.query.get_or_404(id)
    employee.active = False
    db.session.commit()
    flash_success(f'Employee {employee.name} deactivated. Historical records are preserved.')
    return redirect(url_for('employees.index'))


@employees_bp.route('/<int:id>/reactivate', methods=['POST'])
@login_required
@require_role('admin')
def reactivate(id):
    """
    Reactivate a deactivated employee.

    POST: Set active=True and redirect to inactive list.
    """
    employee = Employee.query.get_or_404(id)
    employee.active = True
    db.session.commit()
    flash_success(f'Employee {employee.name} reactivated successfully.')
    return redirect(url_for('employees.inactive'))


@employees_bp.route('/<int:id>/hard-delete', methods=['POST'])
@login_required
@require_role('admin')
def hard_delete(id):
    """
    Permanently delete an employee.

    POST: Delete employee if no records exist, otherwise show error.
    """
    employee = Employee.query.get_or_404(id)

    # Check for existing records
    has_production = ProductionRecord.query.filter_by(employee_id=id).first() is not None
    has_payments = Payment.query.filter_by(employee_id=id).first() is not None

    if has_production or has_payments:
        flash_error(
            f'Cannot delete {employee.name}. '
            'Employee has historical records. Use deactivate instead.'
        )
        return redirect(url_for('employees.index'))

    db.session.delete(employee)
    db.session.commit()
    flash_success(f'Employee {employee.name} permanently deleted.')
    return redirect(url_for('employees.index'))

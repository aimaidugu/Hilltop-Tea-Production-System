"""
Hilltop Tea — Employee Management Blueprint.

Handles CRUD operations for employee records.
Admin-only access.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app import db
from app.forms import EmployeeForm
from app.models import Employee, Payment, ProductionRecord
from app.utils import paginate, require_role

employees_bp = Blueprint('employees', __name__)


@employees_bp.route('/')
@login_required
@require_role('admin')
def list_employees():
    """
    Display paginated list of active employees.

    Admin only.
    """
    page = request.args.get('page', 1, type=int)
    query = Employee.query.filter_by(active=True).order_by(Employee.name)
    pagination = paginate(query, page)
    return render_template('employee_list.html',
                          employees=pagination.items,
                          pagination=pagination,
                          active_only=True)


@employees_bp.route('/inactive')
@login_required
@require_role('admin')
def list_inactive():
    """
    Display paginated list of inactive employees.

    Admin only.
    """
    page = request.args.get('page', 1, type=int)
    query = Employee.query.filter_by(active=False).order_by(Employee.name)
    pagination = paginate(query, page)
    return render_template('employee_list.html',
                          employees=pagination.items,
                          pagination=pagination,
                          active_only=False)


@employees_bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def add_employee():
    """
    Add a new employee.

    GET: Render form.
    POST: Create employee and redirect to list.
    """
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee(
            name=form.name.data,
            group=form.group.data
        )
        db.session.add(employee)
        db.session.commit()
        flash(f'Employee {employee.name} added successfully.', 'success')
        return redirect(url_for('employees.list_employees'))

    return render_template('employee_form.html', form=form, title='Add Employee')


@employees_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def edit_employee(id):
    """
    Edit an existing employee.

    GET: Render form with existing data.
    POST: Update employee and redirect to list.
    """
    employee = Employee.query.get_or_404(id)
    form = EmployeeForm(obj=employee)

    if form.validate_on_submit():
        employee.name = form.name.data
        employee.group = form.group.data
        db.session.commit()
        flash(f'Employee {employee.name} updated successfully.', 'success')
        return redirect(url_for('employees.list_employees'))

    return render_template('employee_form.html',
                          form=form,
                          title='Edit Employee',
                          employee=employee)


@employees_bp.route('/<int:id>/deactivate', methods=['POST'])
@login_required
@require_role('admin')
def deactivate_employee(id):
    """
    Soft delete an employee by setting active=False.

    Historical records are preserved.
    """
    employee = Employee.query.get_or_404(id)
    employee.active = False
    db.session.commit()
    flash(f'Employee {employee.name} deactivated. Historical records are preserved.', 'info')
    return redirect(url_for('employees.list_employees'))


@employees_bp.route('/<int:id>/reactivate', methods=['POST'])
@login_required
@require_role('admin')
def reactivate_employee(id):
    """
    Reactivate an inactive employee by setting active=True.
    """
    employee = Employee.query.get_or_404(id)
    employee.active = True
    db.session.commit()
    flash(f'Employee {employee.name} reactivated successfully.', 'success')
    return redirect(url_for('employees.list_inactive'))


@employees_bp.route('/<int:id>/hard-delete', methods=['POST'])
@login_required
@require_role('admin')
def hard_delete_employee(id):
    """
    Permanently delete an employee and all associated records.

    Blocked if any production records or payments exist.
    """
    employee = Employee.query.get_or_404(id)

    # Check for existing records
    has_production = ProductionRecord.query.filter_by(employee_id=id).first() is not None
    has_payments = Payment.query.filter_by(employee_id=id).first() is not None

    if has_production or has_payments:
        flash(
            f'Cannot delete {employee.name}. '
            'Employee has associated production records or payments. '
            'Deactivate instead to preserve history.',
            'danger'
        )
        return redirect(url_for('employees.list_employees'))

    db.session.delete(employee)
    db.session.commit()
    flash(f'Employee {employee.name} permanently deleted.', 'success')
    return redirect(url_for('employees.list_employees'))

"""
Hilltop Tea — User Management Blueprint.

CRUD operations for user accounts. Admin only.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.forms import UserForm
from app.models import User
from app.utils import flash_error, flash_success, paginate, require_role

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
@login_required
@require_role('admin')
def index():
    """
    List all users.

    GET: Render table of all users with actions.
    """
    page = request.args.get('page', 1, type=int)
    query = User.query.order_by(User.username)
    pagination = paginate(query, page)
    return render_template('user_list.html', pagination=pagination)


@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def add():
    """
    Add a new user.

    GET: Render user creation form.
    POST: Create new user and redirect to list.
    """
    form = UserForm()

    if form.validate_on_submit():
        if not form.password.data:
            flash_error('Password is required for new users.')
            return render_template('user_form.html', form=form, title='Add User')

        user = User(
            username=form.username.data,
            role=form.role.data,
            must_change_password=form.must_change_password.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash_success(f'User {user.username} created successfully.')
        return redirect(url_for('users.index'))

    return render_template('user_form.html', form=form, title='Add User')


@users_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def edit(id):
    """
    Edit an existing user.

    GET: Render user edit form.
    POST: Update user and redirect to list.
    """
    user = User.query.get_or_404(id)
    form = UserForm(obj=user, original_username=user.username)

    if form.validate_on_submit():
        user.username = form.username.data
        user.role = form.role.data
        user.must_change_password = form.must_change_password.data

        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()
        flash_success(f'User {user.username} updated successfully.')
        return redirect(url_for('users.index'))

    return render_template('user_form.html', form=form, title='Edit User', user=user)


@users_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@require_role('admin')
def delete(id):
    """
    Delete a user.

    POST: Delete user if allowed, otherwise show error.
    """
    user = User.query.get_or_404(id)

    # Cannot delete own account
    if user.id == current_user.id:
        flash_error('You cannot delete your own account.')
        return redirect(url_for('users.index'))

    # Cannot delete if it's the last admin
    admin_count = User.query.filter_by(role='admin').count()
    if user.role == 'admin' and admin_count <= 1:
        flash_error('Cannot delete the last admin account.')
        return redirect(url_for('users.index'))

    db.session.delete(user)
    db.session.commit()
    flash_success(f'User {user.username} deleted successfully.')
    return redirect(url_for('users.index'))

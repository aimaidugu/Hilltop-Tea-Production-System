"""
Hilltop Tea — User Management Blueprint.

Handles CRUD operations for user accounts.
Admin-only access.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.forms import UserForm
from app.models import User
from app.utils import paginate, require_role

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
@login_required
@require_role('admin')
def list_users():
    """
    Display paginated list of all users.

    Admin only.
    """
    page = request.args.get('page', 1, type=int)
    query = User.query.order_by(User.username)
    pagination = paginate(query, page)
    return render_template('user_list.html',
                          users=pagination.items,
                          pagination=pagination)


@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def add_user():
    """
    Add a new user.

    GET: Render form.
    POST: Create user and redirect to list.
    """
    form = UserForm(is_edit=False)

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            role=form.role.data,
            must_change_password=True
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User {user.username} created successfully.', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('user_form.html', form=form, title='Add User')


@users_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@require_role('admin')
def edit_user(id):
    """
    Edit an existing user.

    GET: Render form with existing data.
    POST: Update user and redirect to list.
    """
    user = User.query.get_or_404(id)
    form = UserForm(obj=user, is_edit=True)

    if form.validate_on_submit():
        user.username = form.username.data
        user.role = form.role.data

        if form.password.data:
            user.set_password(form.password.data)
            user.must_change_password = True

        db.session.commit()
        flash(f'User {user.username} updated successfully.', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('user_form.html',
                          form=form,
                          title='Edit User',
                          user=user)


@users_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@require_role('admin')
def delete_user(id):
    """
    Delete a user account.

    Cannot delete own account or the last admin account.
    """
    user = User.query.get_or_404(id)

    # Prevent deleting own account
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('users.list_users'))

    # Prevent deleting the last admin
    admin_count = User.query.filter_by(role='admin').count()
    if user.role == 'admin' and admin_count <= 1:
        flash('Cannot delete the last admin account.', 'danger')
        return redirect(url_for('users.list_users'))

    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted successfully.', 'success')
    return redirect(url_for('users.list_users'))

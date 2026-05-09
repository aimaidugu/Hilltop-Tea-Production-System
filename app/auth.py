"""
Hilltop Tea — Authentication Blueprint.

Handles login, logout, and password change functionality.
"""
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from app import db
from app.forms import ChangePasswordForm, LoginForm
from app.models import User
from app.utils import require_role

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user authentication.

    GET: Render login form.
    POST: Validate credentials and establish session.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'danger')
            return render_template('login.html', form=form)

        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()

        if user.must_change_password:
            flash('Please change your password before continuing.', 'warning')
            return redirect(url_for('auth.change_password'))

        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Log out the current user and redirect to login page.
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Handle password change for authenticated users.

    GET: Render password change form.
    POST: Validate current password and update to new password.
    """
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('change_password.html', form=form)

        current_user.set_password(form.new_password.data)
        current_user.must_change_password = False
        db.session.commit()

        flash('Password changed successfully.', 'success')
        return redirect(url_for('main.index'))

    return render_template('change_password.html', form=form)

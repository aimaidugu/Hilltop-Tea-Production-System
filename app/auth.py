"""
Hilltop Tea — Authentication Blueprint.

Handles user login, logout, and password management.
"""
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.forms import ChangePasswordForm, LoginForm
from app.models import User
from app.utils import flash_error, flash_success

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.

    GET: Render login form.
    POST: Validate credentials and log user in.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()

            # Redirect to change password if required
            if user.must_change_password:
                flash_success('Please change your password to continue.')
                return redirect(url_for('auth.change_password'))

            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))

        flash_error('Invalid username or password.')

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Handle user logout.

    Clears the session and redirects to login page.
    """
    logout_user()
    flash_success('You have been logged out.')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Handle password change for authenticated users.

    GET: Render password change form.
    POST: Validate and update password.
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash_error('Current password is incorrect.')
            return render_template('change_password.html', form=form)

        current_user.set_password(form.new_password.data)
        current_user.must_change_password = False
        db.session.commit()

        flash_success('Password changed successfully.')
        return redirect(url_for('main.index'))

    return render_template('change_password.html', form=form)

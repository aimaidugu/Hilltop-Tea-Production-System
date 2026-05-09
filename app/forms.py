"""
Hilltop Tea — WTForms for user input validation.

All forms include CSRF protection and field-level validation.
"""
from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, IntegerField,
    TextAreaField, DateField, FloatField, SubmitField
)
from wtforms.validators import (
    DataRequired, Length, EqualTo, NumberRange, Optional, ValidationError
)

from app.models import User


class LoginForm(FlaskForm):
    """Form for user authentication."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class ChangePasswordForm(FlaskForm):
    """Form for password change after first login or password reset."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(),
            Length(min=8, message='Password must be at least 8 characters.')
        ]
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(),
            EqualTo('new_password', message='Passwords must match.')
        ]
    )
    submit = SubmitField('Change Password')


class EmployeeForm(FlaskForm):
    """Form for creating and editing employees."""
    name = StringField(
        'Full Name',
        validators=[DataRequired(), Length(min=2, max=120)]
    )
    group = SelectField(
        'Worker Group',
        choices=[
            ('production', 'Production (Maisa Machine Operators)'),
            ('wrapping', 'Wrapping (Tea Capsule Team)')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Save Employee')


class ProductionEntryForm(FlaskForm):
    """Dynamic form for daily production entry. Fields are generated per employee."""
    submit = SubmitField('Save Production')


class PaymentForm(FlaskForm):
    """Form for recording employee payments."""
    amount = FloatField(
        'Payment Amount (₦)',
        validators=[
            DataRequired(),
            NumberRange(min=0.01, message='Amount must be greater than zero.')
        ]
    )
    payment_date = DateField(
        'Payment Date',
        validators=[DataRequired()],
        default=date.today
    )
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Record Payment')


class UserForm(FlaskForm):
    """Form for creating and editing users."""
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=80)]
    )
    role = SelectField(
        'Role',
        choices=[
            ('admin', 'Administrator'),
            ('gm', 'General Manager'),
            ('supervisor', 'Supervisor')
        ],
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[
            Optional(),
            Length(min=8, message='Password must be at least 8 characters.')
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            Optional(),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    submit = SubmitField('Save User')

    def __init__(self, *args, is_edit: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_edit = is_edit
        if is_edit:
            self.password.validators = [Optional()]
            self.confirm_password.validators = [Optional()]
        else:
            self.password.validators = [
                DataRequired(),
                Length(min=8, message='Password must be at least 8 characters.')
            ]
            self.confirm_password.validators = [
                DataRequired(),
                EqualTo('password', message='Passwords must match.')
            ]

    def validate_username(self, field):
        """Ensure username is unique (except when editing same user)."""
        if self.is_edit:
            user = User.query.filter(
                User.username == field.data,
                User.id != self.id
            ).first()
        else:
            user = User.query.filter_by(username=field.data).first()
        if user is not None:
            raise ValidationError('Username already exists.')

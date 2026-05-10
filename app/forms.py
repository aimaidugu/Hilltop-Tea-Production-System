"""
Hilltop Tea — WTForms.

All form classes for input validation and CSRF protection.
"""
from datetime import date
from typing import Optional

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    FloatField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    Optional as OptionalValidator,
    ValidationError,
)

from app.models import User


class LoginForm(FlaskForm):
    """Form for user login."""

    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')


class ChangePasswordForm(FlaskForm):
    """Form for changing user password."""

    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(),
            Length(min=8, message='Password must be at least 8 characters long'),
        ]
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(),
            EqualTo('new_password', message='Passwords must match'),
        ]
    )
    submit = SubmitField('Change Password')


class EmployeeForm(FlaskForm):
    """Form for creating/editing employees."""

    name = StringField(
        'Full Name',
        validators=[
            DataRequired(),
            Length(min=2, max=120, message='Name must be between 2 and 120 characters'),
        ]
    )
    group = SelectField(
        'Worker Group',
        choices=[
            ('production', 'Production (Maisa Machine)'),
            ('wrapping', 'Wrapping (Tea Capsules)'),
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Save Employee')


class ProductionEntryForm(FlaskForm):
    """Form for daily production entry."""

    submit = SubmitField('Save Production')


class PaymentForm(FlaskForm):
    """Form for recording employee payments."""

    amount = FloatField(
        'Payment Amount (₦)',
        validators=[
            DataRequired(),
            NumberRange(min=0.01, message='Amount must be greater than 0'),
        ]
    )
    payment_date = DateField('Payment Date', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[OptionalValidator()])
    submit = SubmitField('Record Payment')


class UserForm(FlaskForm):
    """Form for creating/editing users."""

    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=3, max=80, message='Username must be between 3 and 80 characters'),
        ]
    )
    role = SelectField(
        'Role',
        choices=[
            ('admin', 'Administrator'),
            ('gm', 'General Manager'),
            ('supervisor', 'Supervisor'),
        ],
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[
            OptionalValidator(),
            Length(min=8, message='Password must be at least 8 characters long'),
        ]
    )
    confirm_password = PasswordField('Confirm Password')
    must_change_password = BooleanField('Require password change on next login', default=True)
    submit = SubmitField('Save User')

    def __init__(self, *args, original_username: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, field):
        """Validate username uniqueness."""
        if field.data != self.original_username:
            existing = User.query.filter_by(username=field.data).first()
            if existing:
                raise ValidationError('Username already exists. Please choose a different one.')

    def validate_confirm_password(self, field):
        """Validate password confirmation."""
        if self.password.data and field.data != self.password.data:
            raise ValidationError('Passwords must match.')

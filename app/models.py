"""
Hilltop Tea — Database Models.

All SQLAlchemy models with Google-style docstrings.
Password hashing uses Argon2 via argon2-cffi.
"""
from datetime import datetime
from enum import Enum

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from app import db, login

# Global Argon2 hasher instance
_ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)


class UserRole(Enum):
    """User role enumeration for access control."""
    ADMIN = 'admin'
    GM = 'gm'
    SUPERVISOR = 'supervisor'


class EmployeeGroup(Enum):
    """Employee group enumeration for wage calculation."""
    PRODUCTION = 'production'
    WRAPPING = 'wrapping'


class User(UserMixin, db.Model):
    """
    Application user with role-based access control.

    Attributes:
        id: Primary key.
        username: Unique login identifier.
        password_hash: Argon2-hashed password.
        role: User role (admin, gm, supervisor).
        must_change_password: Flag for forced password change on first login.
        last_login: Timestamp of last successful login.
        created_at: Account creation timestamp.
    """

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(
        db.Enum(UserRole.ADMIN.value, UserRole.GM.value, UserRole.SUPERVISOR.value,
                name='user_role_enum'),
        nullable=False
    )
    must_change_password = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    created_production = db.relationship(
        'ProductionRecord',
        foreign_keys='ProductionRecord.created_by',
        back_populates='creator',
        lazy='dynamic'
    )
    recorded_payments = db.relationship(
        'Payment',
        foreign_keys='Payment.recorded_by',
        back_populates='recorder',
        lazy='dynamic'
    )

    __table_args__ = (
        db.CheckConstraint('username IS NOT NULL'),
        db.CheckConstraint('password_hash IS NOT NULL'),
    )

    def __repr__(self) -> str:
        return f'<User {self.username} ({self.role})>'

    def to_dict(self) -> dict:
        """Return model as plain dict."""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'must_change_password': self.must_change_password,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def set_password(self, raw_password: str) -> None:
        """Hash and store password using Argon2id."""
        self.password_hash = _ph.hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verify password. Returns False on any mismatch or invalid hash."""
        try:
            return _ph.verify(self.password_hash, raw_password)
        except (VerifyMismatchError, InvalidHashError):
            return False

    def needs_rehash(self) -> bool:
        """True if stored hash should be upgraded to current Argon2 params."""
        return _ph.check_needs_rehash(self.password_hash)


class Employee(db.Model):
    """
    Factory worker with production/wrapping group assignment.

    Attributes:
        id: Primary key.
        name: Full name of the employee.
        group: Worker group (production or wrapping).
        active: Soft delete flag. False employees are preserved in history.
        created_at: Record creation timestamp.
    """

    __tablename__ = 'employee'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    group = db.Column(
        db.Enum(EmployeeGroup.PRODUCTION.value, EmployeeGroup.WRAPPING.value,
                name='employee_group_enum'),
        nullable=False
    )
    active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    production_records = db.relationship(
        'ProductionRecord',
        back_populates='employee',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    payments = db.relationship(
        'Payment',
        back_populates='employee',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    __table_args__ = (
        db.CheckConstraint('name IS NOT NULL'),
        db.CheckConstraint('group IS NOT NULL'),
        db.Index('idx_employee_active', 'active'),
    )

    def __repr__(self) -> str:
        status = 'active' if self.active else 'inactive'
        return f'<Employee {self.name} ({self.group}, {status})>'

    def to_dict(self) -> dict:
        """Return model as plain dict."""
        return {
            'id': self.id,
            'name': self.name,
            'group': self.group,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ProductionRecord(db.Model):
    """
    Daily production record with immutable wage calculation.

    The daily_wage is calculated once at insertion time and never updated,
    preserving payroll accuracy across rate changes.

    Attributes:
        id: Primary key.
        employee_id: Foreign key to employee.
        date: Production date.
        cartons: Number of cartons produced.
        daily_wage: Calculated wage at time of record creation.
        created_by: Foreign key to user who created the record.
        timestamp: Record creation timestamp.
    """

    __tablename__ = 'production_record'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(
        db.Integer,
        db.ForeignKey('employee.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    date = db.Column(db.Date, nullable=False, index=True)
    cartons = db.Column(db.Integer, nullable=False)
    daily_wage = db.Column(db.Float, nullable=False)
    created_by = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='SET NULL'),
        nullable=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employee = db.relationship('Employee', back_populates='production_records')
    creator = db.relationship('User', foreign_keys=[created_by], back_populates='created_production')

    __table_args__ = (
        db.CheckConstraint('cartons >= 0'),
        db.UniqueConstraint('employee_id', 'date', name='uq_employee_date'),
        db.Index('idx_production_employee_date', 'employee_id', 'date'),
    )

    def __repr__(self) -> str:
        return f'<ProductionRecord {self.employee_id} on {self.date}: {self.cartons} cartons>'

    def to_dict(self) -> dict:
        """Return model as plain dict."""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'date': self.date.isoformat() if self.date else None,
            'cartons': self.cartons,
            'daily_wage': self.daily_wage,
            'created_by': self.created_by,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


class Payment(db.Model):
    """
    Payment record for payroll tracking.

    Payments are not linked to specific production records, only to
    an employee and a payment date.

    Attributes:
        id: Primary key.
        employee_id: Foreign key to employee.
        amount: Payment amount in Naira.
        payment_date: Date payment was made.
        notes: Optional notes about the payment.
        recorded_by: Foreign key to user who recorded the payment.
        timestamp: Record creation timestamp.
    """

    __tablename__ = 'payment'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(
        db.Integer,
        db.ForeignKey('employee.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)
    recorded_by = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='SET NULL'),
        nullable=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employee = db.relationship('Employee', back_populates='payments')
    recorder = db.relationship('User', foreign_keys=[recorded_by], back_populates='recorded_payments')

    __table_args__ = (
        db.CheckConstraint('amount > 0'),
        db.Index('idx_payment_employee_date', 'employee_id', 'payment_date'),
    )

    def __repr__(self) -> str:
        return f'<Payment ₦{self.amount} to employee {self.employee_id} on {self.payment_date}>'

    def to_dict(self) -> dict:
        """Return model as plain dict."""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'amount': self.amount,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'notes': self.notes,
            'recorded_by': self.recorded_by,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


# Flask-Login user loader
@login.user_loader
def load_user(user_id: int) -> User | None:
    """Load user by ID for Flask-Login session management."""
    return User.query.get(int(user_id))

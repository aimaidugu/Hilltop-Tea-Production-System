"""
Hilltop Tea — Utility Functions.

Helper functions for the application.
"""
from datetime import date, datetime, timedelta
from functools import wraps
from typing import Optional, Tuple

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def require_role(*roles: str):
    """
    Route decorator enforcing role-based access control.

    Usage:
        @require_role('admin', 'gm')
        def my_route(): ...

    Returns:
        HTTP 403 if authenticated user's role is not in `roles`.
        HTTP 401/redirect handled by Flask-Login's @login_required.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator


def month_range(month_str: str) -> Tuple[date, date]:
    """
    Get first and last day of a month from 'YYYY-MM' string.

    Args:
        month_str: Month string in 'YYYY-MM' format.

    Returns:
        Tuple of (first_day, last_day) as date objects.

    Raises:
        ValueError: If month_str is not in valid format.
    """
    try:
        year, month = map(int, month_str.split('-'))
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        return first_day, last_day
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Invalid month format: {month_str}. Expected 'YYYY-MM'.") from e


def format_naira(amount: float) -> str:
    """
    Format a number as Nigerian Naira currency.

    Args:
        amount: Numeric value to format.

    Returns:
        Formatted currency string (e.g., '₦1,234.56').
    """
    return f'₦{amount:,.2f}'


def paginate(query, page: int, per_page: int = 25):
    """
    Paginate a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object.
        page: Current page number (1-indexed).
        per_page: Number of items per page.

    Returns:
        Pagination object with items, total, pages, etc.
    """
    return query.paginate(page=page, per_page=per_page, error_out=False)


def get_adjacent_months(month_str: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Get previous and next month strings for navigation.

    Args:
        month_str: Current month in 'YYYY-MM' format.

    Returns:
        Tuple of (previous_month, next_month) as 'YYYY-MM' strings.
        None if month is out of reasonable range.
    """
    try:
        year, month = map(int, month_str.split('-'))
        current = date(year, month, 1)

        # Previous month
        if month == 1:
            prev_month = date(year - 1, 12, 1)
        else:
            prev_month = date(year, month - 1, 1)

        # Next month
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)

        return (
            prev_month.strftime('%Y-%m'),
            next_month.strftime('%Y-%m'),
        )
    except (ValueError, AttributeError):
        return None, None


def flash_success(message: str) -> None:
    """Flash a success message."""
    flash(message, 'success')


def flash_error(message: str) -> None:
    """Flash an error message."""
    flash(message, 'danger')


def flash_warning(message: str) -> None:
    """Flash a warning message."""
    flash(message, 'warning')


def flash_info(message: str) -> None:
    """Flash an info message."""
    flash(message, 'info')

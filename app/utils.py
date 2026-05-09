"""
Hilltop Tea — Utility functions and decorators.

Contains role-based access control, date helpers, and formatting utilities.
"""
from functools import wraps
from datetime import datetime, timedelta
from typing import Optional

from flask import abort, request, url_for
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


def month_range(month_str: str) -> tuple[datetime, datetime]:
    """
    Parse a month string and return first and last day of that month.

    Args:
        month_str: String in format 'YYYY-MM'.

    Returns:
        Tuple of (first_day, last_day) as datetime objects at midnight.

    Raises:
        ValueError: If month_str is not in valid format.
    """
    try:
        year, month = map(int, month_str.split('-'))
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12.")
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        return first_day, last_day
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Invalid month format: {month_str}. Expected 'YYYY-MM'.") from e


def format_naira(amount: float) -> str:
    """
    Format a number as Nigerian Naira currency.

    Args:
        amount: Numeric value to format.

    Returns:
        String formatted as '₦X,XXX.XX'.
    """
    return f'₦{amount:,.2f}'


def paginate(query, page: int, per_page: int = 25):
    """
    Paginate a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object.
        page: Page number (1-indexed).
        per_page: Number of items per page.

    Returns:
        Pagination object with items, total, pages, etc.
    """
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )


def get_previous_month() -> str:
    """
    Get the previous month as 'YYYY-MM' string.

    Returns:
        Previous month in 'YYYY-MM' format.
    """
    today = datetime.utcnow()
    first_of_this_month = today.replace(day=1)
    previous_month = first_of_this_month - timedelta(days=1)
    return previous_month.strftime('%Y-%m')


def get_adjacent_months(current_month: str) -> tuple[Optional[str], Optional[str]]:
    """
    Get previous and next month strings relative to current_month.

    Args:
        current_month: String in 'YYYY-MM' format.

    Returns:
        Tuple of (previous_month, next_month) as 'YYYY-MM' strings.
        None for boundaries (no month before Jan of current year, etc.).
    """
    try:
        year, month = map(int, current_month.split('-'))
        prev_month = None
        next_month = None

        if month == 1:
            prev_month = f'{year - 1}-12'
        else:
            prev_month = f'{year}-{month - 1:02d}'

        if month == 12:
            next_month = f'{year + 1}-01'
        else:
            next_month = f'{year}-{month + 1:02d}'

        return prev_month, next_month
    except (ValueError, AttributeError):
        return None, None

"""
Hilltop Tea — Application Configuration.

All environment-dependent values come from environment variables.
Never hardcode secrets. DATABASE_URL controls which DB engine is used.
"""
import os
from datetime import timedelta


def _resolve_db_url() -> str:
    """
    Resolve DATABASE_URL from environment.

    Handles Railway/Heroku's legacy postgres:// prefix.
    Falls back to SQLite for local development.

    Returns:
        SQLAlchemy-compatible database URI string.
    """
    url = os.environ.get('DATABASE_URL', '').strip()
    if url.startswith('postgres://'):
        url = 'postgresql+psycopg2://' + url[len('postgres://'):]
    elif url.startswith('postgresql://') and '+psycopg2' not in url:
        url = url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    return url or 'sqlite:///hilltop_dev.db'


class Config:
    """Base configuration. All values overridable via environment variables."""
    SECRET_KEY                    = os.environ.get('SECRET_KEY', 'dev-insecure-key-change-me')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED               = True
    RECORDS_PER_PAGE               = 25
    MAX_CONTENT_LENGTH             = 2 * 1024 * 1024  # 2 MB upload limit


class DevelopmentConfig(Config):
    """Local development. SQLite, debug mode on."""
    DEBUG                    = True
    SQLALCHEMY_DATABASE_URI  = 'sqlite:///hilltop_dev.db'


class TestingConfig(Config):
    """pytest test suite. In-memory SQLite, CSRF off, fast Argon2."""
    TESTING                  = True
    SQLALCHEMY_DATABASE_URI  = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED         = False
    SECRET_KEY               = 'test-secret-not-used-in-production'
    SERVER_NAME              = 'localhost'


class ProductionConfig(Config):
    """Production. PostgreSQL required via DATABASE_URL."""
    DEBUG                    = False
    SQLALCHEMY_DATABASE_URI  = _resolve_db_url()
    SESSION_COOKIE_SECURE    = True
    SESSION_COOKIE_HTTPONLY  = True
    SESSION_COOKIE_SAMESITE  = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)


config = {
    'development' : DevelopmentConfig,
    'testing'     : TestingConfig,
    'production'  : ProductionConfig,
    'default'     : DevelopmentConfig,
}

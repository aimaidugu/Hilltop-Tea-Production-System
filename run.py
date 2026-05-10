"""
Hilltop Tea — Application entry point.

For local development: python run.py
For production: gunicorn (Railway/Oracle) or Vercel (api/index.py)

Database initialisation:
  SQLite (dev):  db.create_all() runs automatically on startup.
  PostgreSQL:    Run `flask db upgrade` manually after first deploy.
                 Do NOT call db.create_all() against PostgreSQL in production.
"""
import os
import sys

from app import create_app, db
from app.models import User

ENV        = os.environ.get('FLASK_ENV', 'development')
IS_SQLITE  = 'sqlite' in os.environ.get('DATABASE_URL', 'sqlite')
app        = create_app(ENV)


def _seed_admin() -> None:
    """Create the default admin account if no users exist. Idempotent."""
    if User.query.count() > 0:
        return
    admin = User(username='admin', role='admin', must_change_password=True)
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print('✓ Default admin created. Login: admin / admin123')
    print('⚠  Change this password immediately after first login.')


with app.app_context():
    if IS_SQLITE:
        db.create_all()
        _seed_admin()
    else:
        # PostgreSQL: schema is managed by Flask-Migrate.
        # Run: flask db upgrade
        # Then: flask shell -c "from run import _seed_admin; _seed_admin()"
        print('ℹ  PostgreSQL detected. Run `flask db upgrade` if first deploy.')
        try:
            _seed_admin()
        except Exception as exc:
            print(f'ℹ  Seed skipped: {exc}')

# `app` is importable at module level for gunicorn and Vercel
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'✓ Hilltop Tea starting on http://0.0.0.0:{port}')
    if IS_SQLITE:
        from waitress import serve
        serve(app, host='0.0.0.0', port=port)
    else:
        print('ℹ  Use gunicorn for PostgreSQL deployments.')
        sys.exit(1)

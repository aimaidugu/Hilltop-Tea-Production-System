"""
Hilltop Tea — Application Factory.

Create and configure the Flask application.
All extensions are initialised here. All blueprints are registered here.
No business logic lives in this file.
"""
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

from config import config

db      = SQLAlchemy()
login   = LoginManager()
csrf    = CSRFProtect()
migrate = Migrate()

login.login_view     = 'auth.login'
login.login_message  = 'Please log in to access this page.'
login.login_message_category = 'warning'


def create_app(config_name: str = 'default') -> Flask:
    """
    Flask application factory.

    Args:
        config_name: Key into the `config` dict from config.py.
                     One of: 'development', 'testing', 'production', 'default'.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialise extensions
    db.init_app(app)
    login.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.auth       import auth_bp
    from app.main       import main_bp
    from app.employees  import employees_bp
    from app.production import production_bp
    from app.payroll    import payroll_bp
    from app.reports    import reports_bp
    from app.users      import users_bp

    app.register_blueprint(auth_bp,       url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(employees_bp,  url_prefix='/employees')
    app.register_blueprint(production_bp, url_prefix='/production')
    app.register_blueprint(payroll_bp,    url_prefix='/payroll')
    app.register_blueprint(reports_bp,    url_prefix='/reports')
    app.register_blueprint(users_bp,      url_prefix='/users')

    # Context processor for static URL handling (Vercel compatibility)
    @app.context_processor
    def inject_static():
        import os
        is_vercel = os.environ.get('VERCEL') == '1'
        def static_url(path):
            if is_vercel:
                return f'/public/{path}'
            return url_for('static', filename=path)
        return dict(static_url=static_url)

    # Register error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app

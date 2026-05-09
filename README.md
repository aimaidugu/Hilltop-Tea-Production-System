# HILLTOP TEA — Wage Tracking & Payroll System

A production-grade web application for managing daily production records, wage calculations, and monthly payroll for Hilltop Tea factory workers.

## Features

- Role-based access control (Admin, GM, Supervisor)
- Table-driven tiered wage calculation (no if-else chains)
- Live real-time wage preview as carton counts are entered
- Monthly payroll with payment tracking and balance calculation
- PDF wage sheet export
- Dashboard with Chart.js analytics
- Deploy to Vercel, Railway, or Oracle Cloud Free Tier

## Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
git clone https://github.com/yourusername/hilltop_tea.git
cd hilltop_tea
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # Edit SECRET_KEY at minimum
python run.py
```

Open http://localhost:5000

Default login: **admin / admin123** (forced password change on first login)

## Running Tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
# Target: >80% coverage
```

## Database Migrations (PostgreSQL only)

```bash
flask db init        # First time only
flask db migrate -m "initial schema"
flask db upgrade
```

## Generating Documentation PDFs

```bash
cd docs/
python generate_pdfs.py
# Output: docs/pdf/*.pdf
```

## Environment Variables

| Variable | Required | Description | Example |
|-----------|----------|-------------|---------|
| SECRET_KEY | Yes | Flask session secret | openssl rand -hex 32 |
| DATABASE_URL | Prod only | PostgreSQL connection URI | postgresql://user:pass@host/db |
| FLASK_ENV | No | Environment name | production |
| PORT | No | Server port (Railway injects) | 5000 |
| VERCEL | No | Set to '1' by Vercel automatically | 1 |

## Default Credentials

⚠️ **Change immediately after first login.**

- Username: `admin`
- Password: `admin123`

## Deployment

- [Vercel](docs/deployment_vercel.md)
- [Railway](docs/deployment_railway.md)
- [Oracle Cloud Free Tier](docs/deployment_oracle.md)

## Project Structure

```
hilltop_tea/
├── api/
│   └── index.py                  # Vercel WSGI entry
├── app/
│   ├── __init__.py               # App factory
│   ├── models.py                 # User, Employee, ProductionRecord, Payment
│   ├── forms.py                  # WTForms for all forms
│   ├── auth.py                   # Authentication blueprint
│   ├── main.py                   # Dashboard blueprint
│   ├── employees.py              # Employee management (Admin only)
│   ├── production.py             # Production entry (Supervisor + Admin)
│   ├── payroll.py                # Payroll view (all authenticated)
│   ├── reports.py                # PDF export via reportlab
│   ├── users.py                  # User management (Admin only)
│   ├── wage_calculator.py        # WageCalculator ADT
│   ├── utils.py                  # Decorators and helpers
│   ├── static/
│   │   ├── css/style.css         # Brand CSS (350+ lines)
│   │   └── js/hilltop.js         # Alpine.js components
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── change_password.html
│       ├── employee_list.html
│       ├── employee_form.html
│       ├── production_entry.html
│       ├── payroll.html
│       ├── record_payment.html
│       ├── user_list.html
│       ├── user_form.html
│       └── errors/
│           ├── 403.html
│           ├── 404.html
│           └── 500.html
├── docs/
│   ├── system_specification.md
│   ├── system_architecture.md
│   ├── system_flowchart.md
│   ├── system_documentation.md
│   ├── methodology.md
│   ├── tech_stack.md
│   ├── construction_decisions.md
│   ├── deployment_vercel.md
│   ├── deployment_railway.md
│   ├── deployment_oracle.md
│   └── generate_pdfs.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_wage_calculator.py
│   ├── test_production.py
│   ├── test_payroll.py
│   └── test_auth.py
├── public/                       # Vercel static files
├── instance/                     # SQLite DB location
├── migrations/                   # Flask-Migrate migrations
├── run.py                        # Dev/prod launcher
├── run.bat                       # Windows launcher
├── vercel.json                   # Vercel config
├── Procfile                      # Railway/Heroku config
├── railway.json                  # Railway config
├── nixpacks.toml                 # Railway build config
├── config.py                     # Configuration
├── requirements.txt             # Python dependencies
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## License

MIT

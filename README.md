# HILLTOP TEA — Wage Tracking & Payroll System

A production-grade web application for managing daily production records, wage calculations, and monthly payroll for Hilltop Tea factory workers.

## Features

- Role-based access control (Admin, GM, Supervisor)
- Table-driven tiered wage calculation
- Real-time wage preview as carton counts are entered
- Monthly payroll with payment tracking and balance calculation
- PDF wage sheet export
- Dashboard with Chart.js analytics
- Deployable to Vercel, Railway, or Oracle Cloud

## Environment Variables

| Variable | Required | Description |
|-----------|----------|-------------|
| SECRET_KEY | Yes | Flask session secret |
| DATABASE_URL | Yes | PostgreSQL connection URI |
| FLASK_ENV | No | Environment name (default: production) |
| PORT | No | Server port (default: 5000) |
| VERCEL | No | Set to '1' by Vercel automatically |

## Default Credentials

⚠️ **Change immediately after first login.**

- Username: `admin`
- Password: `admin123`

## Deployment

### Vercel

1. Import repository to Vercel
2. Set environment variables
3. Deploy

### Railway

1. Import repository to Railway
2. Add PostgreSQL database
3. Set environment variables
4. Deploy

### Oracle Cloud

1. Clone repository to compute instance
2. Install dependencies
3. Configure environment variables
4. Run with gunicorn

## Project Structure

```
hilltop_tea/
├── api/
│   └── index.py                  # Vercel WSGI entry
├── app/
│   ├── __init__.py               # App factory
│   ├── models.py                 # Database models
│   ├── forms.py                  # Form definitions
│   ├── auth.py                   # Authentication
│   ├── main.py                   # Dashboard
│   ├── employees.py              # Employee management
│   ├── production.py             # Production entry
│   ├── payroll.py                # Payroll view
│   ├── reports.py                # PDF export
│   ├── users.py                  # User management
│   ├── wage_calculator.py        # Wage calculation
│   ├── utils.py                  # Utilities
│   ├── static/                   # Static assets
│   └── templates/                # HTML templates
├── public/                       # Vercel static files
├── vercel.json                   # Vercel config
├── Procfile                      # Railway config
├── railway.json                  # Railway config
├── nixpacks.toml                 # Railway build config
├── config.py                     # Configuration
├── requirements.txt             # Dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## License

MIT

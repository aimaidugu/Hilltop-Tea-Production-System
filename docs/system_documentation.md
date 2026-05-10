# System Documentation

## User Manual

### Installation Guide

#### Windows Installation

1. **Prerequisites**
   - Windows 10 or later
   - Python 3.11 or higher
   - pip package manager

2. **Setup Steps**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/hilltop_tea.git
   cd hilltop_tea

   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Copy environment file
   copy .env.example .env

   # Edit .env and set SECRET_KEY
   notepad .env

   # Run the application
   python run.py
   ```

3. **Access the Application**
   - Open browser to http://localhost:5000
   - Default credentials: admin / admin123

#### macOS Installation

1. **Prerequisites**
   - macOS 10.15 or later
   - Python 3.11 or higher
   - Homebrew (recommended)

2. **Setup Steps**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/hilltop_tea.git
   cd hilltop_tea

   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Copy environment file
   cp .env.example .env

   # Edit .env and set SECRET_KEY
   nano .env

   # Run the application
   python run.py
   ```

3. **Access the Application**
   - Open browser to http://localhost:5000
   - Default credentials: admin / admin123

#### Linux Installation

1. **Prerequisites**
   - Linux distribution with Python 3.11+
   - pip package manager
   - build-essential (for some packages)

2. **Setup Steps**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/hilltop_tea.git
   cd hilltop_tea

   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Copy environment file
   cp .env.example .env

   # Edit .env and set SECRET_KEY
   nano .env

   # Run the application
   python run.py
   ```

3. **Access the Application**
   - Open browser to http://localhost:5000
   - Default credentials: admin / admin123

### First-Time Setup

#### Database Initialization

For local development with SQLite, the database is automatically created on first run. For production with PostgreSQL:

```bash
# Initialize migrations
flask db init

# Create initial migration
flask db migrate -m "Initial schema"

# Apply migration
flask db upgrade

# Seed admin user
flask shell
>>> from run import _seed_admin
>>> _seed_admin()
>>> exit()
```

#### Changing Default Password

1. Log in with default credentials (admin / admin123)
2. You will be redirected to the change password page
3. Enter your current password (admin123)
4. Enter your new password (minimum 8 characters)
5. Confirm your new password
6. Click "Change Password"
7. You will be redirected to the dashboard

### Admin Guide

#### User Management

**Adding a New User**
1. Navigate to Users → Add User
2. Enter username (3-80 characters)
3. Select role (Administrator, General Manager, or Supervisor)
4. Enter password (minimum 8 characters)
5. Optionally require password change on first login
6. Click "Save User"

**Editing a User**
1. Navigate to Users
2. Click "Edit" next to the user
3. Modify username or role as needed
4. Optionally enter new password to reset
5. Click "Save User"

**Deleting a User**
1. Navigate to Users
2. Click "Delete" next to the user
3. Confirm deletion
4. Note: You cannot delete your own account or the last admin

#### Employee Management

**Adding an Employee**
1. Navigate to Employees → Add Employee
2. Enter full name (2-120 characters)
3. Select worker group (Production or Wrapping)
4. Click "Save Employee"

**Editing an Employee**
1. Navigate to Employees
2. Click "Edit" next to the employee
3. Modify name or group as needed
4. Click "Save Employee"

**Deactivating an Employee**
1. Navigate to Employees
2. Click "Deactivate" next to the employee
3. Confirm deactivation
4. Historical records are preserved
5. Employee no longer appears in production entry

**Viewing Inactive Employees**
1. Navigate to Employees
2. Click "View inactive employees" link
3. Click "Reactivate" to restore an employee

#### Production History

**Viewing Historical Records**
1. Navigate to Production → History
2. Use date filter to select specific date
3. Use employee filter to select specific employee
4. View paginated results

**Entering Historical Data**
1. Navigate to Production
2. As admin, add ?date=YYYY-MM-DD to URL
3. Enter carton counts for desired date
4. Click "Save Production"

### General Manager Guide

#### Dashboard Overview

The dashboard provides:
- Today's total cartons and active workers
- Current month wages, payments, and balance
- Daily carton chart (last 14 days)
- Wage split by group (donut chart)
- Monthly wage trend (line chart)
- Recent payments list

#### Production History

GMs have full access to production history:
1. Navigate to Production → History
2. Filter by date and/or employee
3. Review historical production data

#### Payroll Management

GMs can view and manage payroll:
1. Navigate to Payroll
2. Select month using month picker
3. Filter by worker group if needed
4. Review wages, payments, and balances
5. Record payments as needed
6. Export PDF wage sheets

### Supervisor Guide

#### Daily Production Entry

**Entering Production Data**
1. Navigate to Production
2. View list of all active employees
3. Enter carton count for each employee
4. Observe real-time wage calculation
5. Click "Save Production"
6. Success message confirms saved records

**Understanding Wage Calculation**

**Production Workers (Maisa Machine)**
- 0-349 cartons: ₦250 per carton
- 350-399 cartons: ₦270 per carton
- 400-499 cartons: ₦300 per carton
- 500+ cartons: ₦320 per carton

**Wrapping Workers (Tea Capsules)**
- Flat rate: ₦100 per carton

**Important Notes**
- Rate applies to ALL cartons for the day (not marginal)
- Zero cartons means no record is created
- Negative values are not allowed
- You can only enter data for today's date

#### Payroll View

Supervisors can view payroll:
1. Navigate to Payroll
2. Select month using month picker
3. Review employee wages and balances
4. Record payments as needed
5. Export PDF reports

#### Recording Payments

1. Navigate to Payroll
2. Click "Record Payment" for desired employee
3. Enter payment amount
4. Select payment date
5. Add optional notes
6. Click "Record Payment"
7. System redirects back to payroll view

### Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid username or password" | Wrong credentials | Check username and password, ensure caps lock is off |
| "Database connection failed" | PostgreSQL not running | Start PostgreSQL service or check connection string |
| "Module not found" | Missing dependencies | Run `pip install -r requirements.txt` |
| "CSRF token missing" | Session expired | Refresh page and try again |
| "403 Forbidden" | Insufficient permissions | Contact administrator for access |
| "Cannot delete employee" | Has existing records | Use deactivate instead of hard delete |
| "PDF generation failed" | Missing reportlab | Install with `pip install reportlab` |
| "Port already in use" | Another process using port 5000 | Stop other process or change PORT variable |
| "Migration failed" | Database schema mismatch | Run `flask db upgrade` |
| "Seed skipped" | Admin already exists | This is normal, admin account already created |

### Common Tasks

#### Resetting a User's Password

1. Navigate to Users
2. Click "Edit" next to the user
3. Enter new password
4. Optionally check "Require password change"
5. Click "Save User"

#### Exporting Monthly Payroll

1. Navigate to Payroll
2. Select desired month
3. Optionally filter by worker group
4. Click "Export PDF"
5. PDF downloads automatically

#### Viewing Employee Production History

1. Navigate to Production → History
2. Select employee from dropdown
3. View all production records for that employee

#### Checking Outstanding Balances

1. Navigate to Payroll
2. Select current month
3. Review Balance column
4. Red text = amount owed
5. Green text = overpaid (credit)

### Security Best Practices

1. **Change default password immediately** after first login
2. **Use strong passwords** with minimum 8 characters
3. **Require password changes** for new users
4. **Review user access** regularly and remove inactive accounts
5. **Keep software updated** with security patches
6. **Use HTTPS** in production environments
7. **Set appropriate session timeouts** for your security needs
8. **Monitor login activity** for suspicious behavior

### Data Backup

For SQLite (development):
```bash
# Backup database
cp instance/hilltop_dev.db instance/hilltop_dev_backup_$(date +%Y%m%d).db
```

For PostgreSQL (production):
```bash
# Backup database
pg_dump -h localhost -U username -d hilltop_tea > backup_$(date +%Y%m%d).sql

# Restore database
psql -h localhost -U username -d hilltop_tea < backup_20260509.sql
```

### Support

For issues or questions:
1. Check this documentation first
2. Review error messages carefully
3. Check system logs for additional details
4. Contact system administrator if issue persists

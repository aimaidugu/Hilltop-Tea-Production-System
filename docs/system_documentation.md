# HILLTOP TEA — System Documentation

## Installation Guide

### Windows Installation

1. **Prerequisites**
   - Download and install Python 3.11 or higher from python.org
   - During installation, check "Add Python to PATH"
   - Open Command Prompt or PowerShell

2. **Clone Repository**
   ```cmd
   git clone https://github.com/yourusername/hilltop_tea.git
   cd hilltop_tea
   ```

3. **Create Virtual Environment**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

5. **Configure Environment**
   ```cmd
   copy .env.example .env
   notepad .env
   ```
   Edit the `.env` file and set a secure `SECRET_KEY`.

6. **Run Application**
   ```cmd
   python run.py
   ```
   Or double-click `run.bat`

7. **Access Application**
   Open http://localhost:5000 in your browser

### macOS Installation

1. **Prerequisites**
   - Install Homebrew if not already installed
   - Install Python 3.11 or higher:
     ```bash
     brew install python@3.11
     ```

2. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/hilltop_tea.git
   cd hilltop_tea
   ```

3. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Edit the `.env` file and set a secure `SECRET_KEY`.

6. **Run Application**
   ```bash
   python run.py
   ```

7. **Access Application**
   Open http://localhost:5000 in your browser

### Linux Installation

1. **Prerequisites**
   - Update package manager:
     ```bash
     sudo apt update
     sudo apt install python3.11 python3.11-venv python3-pip
     ```

2. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/hilltop_tea.git
   cd hilltop_tea
   ```

3. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Edit the `.env` file and set a secure `SECRET_KEY`.

6. **Run Application**
   ```bash
   python run.py
   ```

7. **Access Application**
   Open http://localhost:5000 in your browser

## First-Time Setup

### Database Initialization

For local development using SQLite, the database is automatically created on first run. The system also seeds a default administrator account.

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

### Changing Default Password

1. Log in with the default credentials
2. You will be redirected to the change password page
3. Enter your current password (`admin123`)
4. Enter and confirm your new password (minimum 8 characters)
5. Click "Change Password"

### Creating Additional Users

1. Log in as an administrator
2. Navigate to Users → Add User
3. Enter the username, select the role, and set a password
4. Click "Save User"

### Adding Employees

1. Log in as an administrator
2. Navigate to Employees → Add Employee
3. Enter the employee's full name
4. Select the worker group (Production or Wrapping)
5. Click "Save Employee"

## Admin Guide

### User Management

**Viewing Users**
- Navigate to Users from the main menu
- View all users with their roles, last login, and password status

**Adding a User**
- Click "Add User"
- Enter username (3-80 characters)
- Select role (Administrator, General Manager, or Supervisor)
- Set password (minimum 8 characters)
- Click "Save User"

**Editing a User**
- Click "Edit" next to a user
- Modify username or role as needed
- Optionally set a new password (leave blank to keep current)
- Click "Save User"

**Deleting a User**
- Click "Delete" next to a user
- Confirm the deletion
- Note: You cannot delete your own account or the last admin account

### Employee Management

**Viewing Employees**
- Navigate to Employees from the main menu
- View all active employees with their group and status
- Click "View Inactive" to see deactivated employees

**Adding an Employee**
- Click "Add Employee"
- Enter full name (2-120 characters)
- Select worker group (Production or Wrapping)
- Click "Save Employee"

**Editing an Employee**
- Click "Edit" next to an employee
- Modify name or group as needed
- Click "Save Employee"

**Deactivating an Employee**
- Click "Deactivate" next to an employee
- Confirm the deactivation
- Historical records are preserved

**Reactivating an Employee**
- Navigate to "View Inactive"
- Click "Reactivate" next to an employee

**Hard Deleting an Employee**
- Navigate to "View Inactive"
- Click "Delete" next to an employee
- This is only possible if no production or payment records exist

### Production History

**Viewing All Records**
- Navigate to Production → History
- View all production records with date and employee filters

**Filtering by Date**
- Select a date from the date picker
- Click "Apply" or press Enter

**Filtering by Employee**
- Select an employee from the dropdown
- Click "Apply" or press Enter

## General Manager Guide

### Dashboard Overview

The dashboard provides a comprehensive view of system activity:

- **Today's Cartons**: Total cartons produced today
- **Active Workers Today**: Number of employees with production records today
- **Month Wages**: Total wages for the current month
- **Outstanding Balance**: Net amount owed to employees this month

### Production History

GMs have full access to production history:

1. Navigate to Production → History
2. Use date and employee filters as needed
3. Review production trends and patterns

### Payroll Management

**Viewing Monthly Payroll**
- Navigate to Payroll
- Select the desired month
- Optionally filter by employee group
- Review wages, payments, and balances

**Recording Payments**
- Click "Record Payment" next to an employee
- Enter the payment amount
- Select the payment date
- Optionally add notes
- Click "Record Payment"

**Exporting PDF Reports**
- Click "Export PDF" on the payroll page
- The PDF will download automatically
- Includes all payroll data for the selected month

## Supervisor Guide

### Daily Production Entry

**Accessing Production Entry**
- Navigate to Production from the main menu
- The form displays all active employees

**Entering Carton Counts**
- For each employee, enter the number of cartons produced
- The daily wage is calculated automatically in real-time
- Zero carton entries are skipped (no record created)

**Wage Preview**
- As you enter carton counts, the wage column updates instantly
- Production workers: rate depends on total daily cartons
- Wrapping workers: flat rate of ₦100 per carton

**Saving Production**
- Click "Save Production" when all entries are complete
- A success message confirms the number of employees saved
- Existing records for today are updated automatically

**Wage Tiers Reference**
- 0 – 349 cartons: ₦250 per carton
- 350 – 399 cartons: ₦270 per carton
- 400 – 499 cartons: ₦300 per carton
- 500+ cartons: ₦320 per carton
- Wrapping: ₦100 per carton (flat rate)

### Payroll View

Supervisors can view payroll and record payments:

1. Navigate to Payroll
2. Select the desired month
3. Review employee balances
4. Click "Record Payment" to make payments

### Recording Payments

1. Click "Record Payment" next to an employee
2. Enter the payment amount
3. Select the payment date
4. Optionally add notes
5. Click "Record Payment"

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid username or password" | Incorrect credentials | Verify username and password. Check for typos. |
| "Database locked" | SQLite file in use | Close other instances of the application. |
| "Module not found" | Missing dependencies | Run `pip install -r requirements.txt` |
| "Port 5000 already in use" | Port conflict | Set `PORT=5001` in environment or close conflicting app. |
| "CSRF token missing" | Form submission issue | Refresh the page and try again. |
| "403 Forbidden" | Insufficient permissions | Log in with appropriate role account. |
| "500 Internal Server Error" | Server error | Check logs for details. Contact administrator. |
| "PDF generation failed" | ReportLab error | Ensure all dependencies are installed. |
| "Session expired" | Inactivity timeout | Log in again. Sessions expire after 1 hour. |
| "Cannot delete last admin" | Protection rule | Create another admin account first. |

## Backup and Recovery

### Database Backup (SQLite)

```bash
# Backup
cp instance/hilltop_dev.db instance/hilltop_dev_backup_$(date +%Y%m%d).db

# Restore
cp instance/hilltop_dev_backup_YYYYMMDD.db instance/hilltop_dev.db
```

### Database Backup (PostgreSQL)

```bash
# Backup
pg_dump -h host -U user dbname > backup_$(date +%Y%m%d).sql

# Restore
psql -h host -U user dbname < backup_YYYYMMDD.sql
```

## Security Best Practices

1. **Change Default Password**: Immediately change the default admin password
2. **Use Strong Passwords**: Minimum 8 characters, mix of letters, numbers, symbols
3. **Secure SECRET_KEY**: Use a cryptographically random secret key in production
4. **Enable HTTPS**: Use SSL/TLS in production environments
5. **Regular Backups**: Schedule regular database backups
6. **Review Access**: Periodically review user accounts and permissions
7. **Update Dependencies**: Keep Python packages updated with security patches

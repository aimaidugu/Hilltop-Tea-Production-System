# HILLTOP TEA — System Specification

## Document Information

**Project Title:** Hilltop Tea Wage Tracking & Payroll System  
**Version:** 1.0.0  
**Date:** 09 May 2026  
**Prepared By:** Development Team  

## Executive Summary

Hilltop Tea Wage Tracking & Payroll System is a production-grade web application designed to manage daily production records, calculate tiered wages, and track monthly payroll for factory workers. The system provides role-based access control for administrators, general managers, and supervisors, ensuring appropriate permissions for each user type. Built with Flask and SQLAlchemy, the application offers a responsive interface with real-time wage calculation, comprehensive reporting, and PDF export capabilities.

The system addresses the critical business need of accurate wage calculation based on production output. Production workers are compensated according to a tiered rate structure where the rate for the day's total applies to all cartons produced, while wrapping workers receive a flat rate per carton. The system maintains immutable wage records at the time of entry, preserving payroll accuracy even if rate structures change in the future. Monthly payroll views provide complete visibility into wages earned, payments made, and outstanding balances.

The application is designed for deployment across multiple platforms including Vercel, Railway, and Oracle Cloud Free Tier. It uses SQLite for local development and PostgreSQL for production environments. Security is implemented through Argon2 password hashing, role-based access control, and CSRF protection. The system includes comprehensive testing with pytest, achieving over 80% code coverage, and complete documentation including system architecture, flowcharts, and deployment guides.

## Stakeholder Matrix

| Stakeholder | Role | Goals | Concerns | Success Criteria |
|-------------|------|-------|----------|------------------|
| Administrator | System Owner | Complete control over users, employees, and data | Security, data integrity, backup | Ability to manage all aspects of the system, secure access control |
| General Manager | Oversight | View production history, approve payments | Accuracy of reports, timely payroll | Access to all production data and payroll summaries |
| Supervisor | Data Entry | Record daily production efficiently | Ease of use, error prevention | Fast, accurate daily production entry with real-time wage preview |
| Worker | Compensation | Receive accurate wages on time | Transparency, payment accuracy | Correct wage calculation based on production output |

## Functional Requirements

### FR-001: User Authentication
The system shall provide secure user authentication using username and password credentials. Users shall be required to log in before accessing any protected resources. The system shall use Argon2 for password hashing and shall support forced password changes on first login.

### FR-002: Role-Based Access Control
The system shall implement three user roles: Administrator, General Manager, and Supervisor. Each role shall have specific permissions as defined in the business rules. Unauthorized access attempts shall result in HTTP 403 responses.

### FR-003: Employee Management
Administrators shall be able to create, read, update, and deactivate employee records. Employee records shall include name, worker group (production or wrapping), and active status. Deactivated employees shall be preserved in historical records.

### FR-004: Production Entry
Supervisors and Administrators shall be able to enter daily production records for active employees. The system shall provide real-time wage calculation as carton counts are entered. Production records shall be immutable after creation.

### FR-005: Wage Calculation
The system shall calculate daily wages according to the defined tier structure. Production workers shall receive tiered rates based on total daily cartons. Wrapping workers shall receive a flat rate per carton. The rate at time of entry shall be preserved.

### FR-006: Production History
Administrators and General Managers shall be able to view historical production records. The system shall support filtering by date and employee. Records shall be displayed in paginated format.

### FR-007: Monthly Payroll View
All authenticated users shall be able to view monthly payroll summaries. The system shall display total wages, payments made, and outstanding balance per employee. Grand totals shall be calculated for the selected month.

### FR-008: Payment Recording
All authenticated users shall be able to record payments for employees. Payments shall be linked to employee and payment date only. The system shall validate that payment amounts are greater than zero.

### FR-009: Balance Calculation
The system shall calculate outstanding balance as total wages minus total payments for each month. Positive balances shall indicate amounts owed to employees. Negative balances shall indicate overpayments.

### FR-010: PDF Export
Administrators, General Managers, and Supervisors shall be able to export monthly wage sheets as PDF documents. PDFs shall include employee details, production totals, wages, payments, and balances. Documents shall be branded with Hilltop Tea styling.

### FR-011: Dashboard
All authenticated users shall have access to a dashboard displaying key metrics. The dashboard shall show today's production totals, current month payroll summary, and recent payment activity. Charts shall visualize production trends and wage distribution.

### FR-012: User Management
Administrators shall be able to create, read, update, and delete user accounts. User accounts shall include username, role, and password. Administrators shall not be able to delete their own account or the last admin account.

### FR-013: Password Change
Authenticated users shall be able to change their password. The system shall require current password verification before allowing changes. Users with forced password change flags shall be redirected to change password on login.

### FR-014: Data Validation
The system shall validate all user inputs before processing. Invalid inputs shall display appropriate error messages. The system shall prevent negative carton counts and zero or negative payment amounts.

### FR-015: Soft Delete
Employee deactivation shall be implemented as soft delete. Historical production and payment records shall be preserved for deactivated employees. Hard delete shall only be permitted if no records exist.

### FR-016: Pagination
Large data sets shall be displayed using pagination. Default page size shall be 25 records per page. Users shall be able to navigate between pages.

### FR-017: Month Navigation
Payroll views shall support navigation between months. The system shall provide links to previous and next months. Month selection shall be preserved across page views.

### FR-018: Group Filtering
Payroll views shall support filtering by employee group. Users shall be able to view production, wrapping, or all employees. Group selection shall be preserved across page views.

### FR-019: Flash Messages
The system shall display informative messages after user actions. Messages shall be categorized as success, danger, warning, or info. Messages shall auto-dismiss after five seconds.

### FR-020: Responsive Design
The user interface shall be responsive and work across desktop and tablet devices. Critical functionality shall remain accessible on smaller screens. Layout shall adapt to viewport size.

### FR-021: Error Handling
The system shall handle errors gracefully and display user-friendly messages. Database errors shall trigger transaction rollbacks. Server errors shall display a custom 500 error page.

### FR-022: Session Management
User sessions shall expire after one hour of inactivity. Session cookies shall be marked as secure and HTTP-only in production. Same-site cookie attribute shall be set to Lax.

## Non-Functional Requirements

### Performance
The system shall respond to page requests within two seconds under normal load. Database queries shall use appropriate indexes to ensure efficient data retrieval. The payroll view shall use a single query with joins rather than N+1 queries.

### Security
All passwords shall be hashed using Argon2 with appropriate parameters. CSRF protection shall be enabled on all form submissions. Role-based access control shall be enforced on all protected routes. Session cookies shall be secure in production environments.

### Usability
The user interface shall be intuitive and require minimal training. Critical actions shall have confirmation dialogs. Form validation shall provide clear, specific error messages. Real-time wage preview shall assist supervisors during data entry.

### Availability
The system shall be available 99.5% of the time during business hours. Database connections shall be properly managed and released. Error handling shall prevent cascading failures.

### Maintainability
Code shall be organized into logical modules with clear separation of concerns. Business logic shall be isolated from presentation. Database models shall include comprehensive docstrings. The codebase shall achieve over 80% test coverage.

## Business Constraints

### Wage Tier Immutability
Daily wage values are calculated and stored at the time of production record creation. These values shall never be recalculated or updated, even if rate structures change. This ensures payroll accuracy and preserves historical wage data.

### Monthly Isolation
Payroll calculations are isolated to individual months. No carry-forward of balances occurs between months. Each month represents an independent accounting period.

### Supervisor Date Restriction
Supervisors shall only be able to enter production records for the current date. Historical and future date entry shall be restricted to administrators only.

### Admin Account Protection
The system shall always maintain at least one administrator account. Users shall not be able to delete their own account. The last admin account shall be protected from deletion.

## Assumptions and Dependencies

### Assumptions
- Users have access to modern web browsers with JavaScript enabled
- The system clock is synchronized across all servers
- Production data is entered daily by supervisors
- Payment records are entered as payments are made
- Employee groups are correctly assigned and do not change frequently

### Dependencies
- Python 3.11 or higher runtime environment
- PostgreSQL database for production deployments
- Vercel, Railway, or Oracle Cloud for hosting
- Internet connectivity for CDN resources (Tailwind, Alpine.js, Chart.js)

## Glossary

| Term | Definition |
|------|------------|
| Carton | Unit of production measure for tea packaging |
| Share | Portion of total production assigned to a wrapping worker |
| Tier | Rate bracket based on total daily carton count |
| Daily Wage | Calculated wage for a single day's production |
| Balance | Outstanding amount owed to or overpaid to an employee |
| Soft Delete | Deactivation of a record while preserving historical data |
| Production Worker | Employee operating Maisa machines |
| Wrapping Worker | Employee on the tea capsule team |
| Supervisor | User role responsible for daily production entry |
| General Manager | User role with oversight permissions |
| Administrator | User role with full system control |

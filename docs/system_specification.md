# System Specification

## Hilltop Tea Wage Tracking & Payroll System

**Version:** 1.0
**Date:** May 9, 2026
**Prepared by:** Development Team

## Executive Summary

The Hilltop Tea Wage Tracking & Payroll System is a comprehensive web application designed to manage daily production records, calculate tiered wages, and track monthly payroll for factory workers. The system provides role-based access control for administrators, general managers, and supervisors, ensuring appropriate permissions for different user types.

The application implements a table-driven wage calculation system that eliminates conditional logic in business rules, making wage calculations transparent and maintainable. Production workers are compensated based on daily carton output with four distinct rate tiers, while wrapping workers receive a flat rate per carton. All wage calculations are immutable at the time of record creation, preserving historical accuracy even if rates change in the future.

The system includes real-time wage preview during data entry, comprehensive payroll reporting with PDF export capabilities, and a dashboard with visual analytics. Built on Flask with SQLAlchemy for database management, the application is designed for deployment on multiple platforms including Vercel, Railway, and Oracle Cloud Free Tier, providing flexibility for different hosting requirements.

## Stakeholder Matrix

| Stakeholder | Goals | Concerns | Success Criteria |
|-------------|-------|----------|------------------|
| Administrator | Complete system control, user management, data integrity | Security, audit trail, backup | All CRUD operations functional, role enforcement working |
| General Manager | Oversight of production and payroll, reporting | Data accuracy, timely reports | Dashboard shows accurate metrics, PDF exports work |
| Supervisor | Daily production entry, wage preview | Ease of use, error prevention | Production entry saves correctly, wage calculations accurate |
| Worker | Fair compensation, payment tracking | Transparency, payment accuracy | Wages calculated correctly, payments recorded accurately |

## Functional Requirements

### FR-001: User Authentication
The system shall provide secure user authentication using username and password credentials with Argon2 password hashing.

### FR-002: Role-Based Access Control
The system shall enforce role-based access control with three roles: Administrator, General Manager, and Supervisor.

### FR-003: Employee Management
Administrators shall be able to create, read, update, and deactivate employee records with name and worker group attributes.

### FR-004: Production Entry
Supervisors and Administrators shall be able to enter daily carton counts for all active employees.

### FR-005: Wage Calculation
The system shall calculate daily wages based on predefined rate tiers for production workers and flat rate for wrapping workers.

### FR-006: Real-Time Wage Preview
The system shall display calculated wages in real-time as carton counts are entered.

### FR-007: Production History
Administrators and General Managers shall be able to view historical production records with date and employee filters.

### FR-008: Monthly Payroll View
All authenticated users shall be able to view monthly payroll summaries including total wages, payments, and balances.

### FR-009: Payment Recording
All authenticated users shall be able to record payments for employees with amount, date, and optional notes.

### FR-010: Balance Calculation
The system shall calculate outstanding balances as the difference between total wages and total payments for each month.

### FR-011: PDF Export
The system shall generate branded PDF wage sheets for any selected month with group filtering.

### FR-012: Dashboard Analytics
The system shall display dashboard charts showing daily carton output, wage trends, and group splits.

### FR-013: Password Change
Authenticated users shall be able to change their password with current password verification.

### FR-014: Forced Password Change
The system shall require password change on first login for new users and users with password reset.

### FR-015: User Management
Administrators shall be able to create, edit, and delete user accounts with role assignment.

### FR-016: Soft Delete
Employee deactivation shall preserve historical records while preventing new entries.

### FR-017: Hard Delete Protection
The system shall prevent permanent deletion of employees with existing production or payment records.

### FR-018: Last Login Tracking
The system shall record the timestamp of each successful user login.

### FR-019: Session Management
The system shall implement secure session management with configurable timeout.

### FR-020: CSRF Protection
All form submissions shall be protected against Cross-Site Request Forgery attacks.

### FR-021: Input Validation
All user inputs shall be validated with appropriate constraints and error messages.

### FR-022: Error Handling
The system shall provide user-friendly error pages for 403, 404, and 500 errors.

## Non-Functional Requirements

### Performance
- Dashboard page load time under 2 seconds with 100 employees
- Payroll query for 50 employees completes under 1 second
- PDF generation completes under 5 seconds

### Security
- All passwords hashed with Argon2id
- Session cookies marked HTTPOnly and Secure in production
- CSRF tokens on all form submissions
- SQL injection protection via parameterized queries

### Usability
- Responsive design supporting desktop, tablet, and mobile devices
- Clear visual feedback for all user actions
- Consistent navigation and layout across all pages

### Availability
- Application uptime target of 99.5%
- Graceful degradation during database maintenance
- Automatic session timeout after 1 hour of inactivity

### Maintainability
- Modular blueprint architecture for easy feature addition
- Comprehensive test coverage exceeding 80%
- Clear separation of concerns between models, views, and controllers

## Business Constraints

### Wage Tier Immutability
Daily wage values are calculated and stored at the time of production record creation. These values never change, even if rate tiers are modified later. This ensures payroll accuracy and auditability.

### Monthly Isolation
Each month's payroll is calculated independently. Balances do not carry forward between months. A negative balance indicates overpayment for that specific month only.

### Supervisor Date Restriction
Supervisors can only enter production data for the current date. Only Administrators have the ability to enter or modify historical production records.

### Production vs Wrapping Groups
Production workers (Maisa machine operators) have tiered wage rates based on total daily output. Wrapping workers (tea capsule team) receive a flat rate per carton regardless of volume.

## Assumptions and Dependencies

### Assumptions
- All employees work full shifts when production is recorded
- Carton counts are entered accurately by supervisors
- Payment dates reflect actual payment transaction dates
- Nigerian Naira (₦) is the sole currency for all transactions

### Dependencies
- Python 3.11 or higher runtime environment
- PostgreSQL database for production deployments
- SQLite database for development and testing
- Internet connectivity for CDN-hosted JavaScript libraries

## Glossary

| Term | Definition |
|------|------------|
| Carton | Unit of production measure for tea packaging |
| Share | Portion of total production assigned to a wrapping worker |
| Tier | Rate bracket for production wage calculation |
| Daily Wage | Calculated wage for a single day's production |
| Balance | Outstanding amount owed to employee (wages minus payments) |
| Soft Delete | Deactivation that preserves historical records |
| Hard Delete | Permanent removal of records (blocked when references exist) |
| PRG Pattern | Post-Redirect-Get pattern to prevent duplicate form submissions |

# HILLTOP TEA — Technology Stack

## Overview

Hilltop Tea is built using a modern Python web stack optimized for security, performance, and maintainability. The technology choices prioritize simplicity, reliability, and ease of deployment across multiple platforms. This document provides a comprehensive overview of all technologies used in the project.

## Backend Technologies

### Python 3.11+
Python serves as the primary programming language for the application. Version 3.11 or higher is required to take advantage of improved performance, better error messages, and enhanced type hinting capabilities. Python's extensive ecosystem and clear syntax make it ideal for rapid development and maintenance.

### Flask 3.0.3
Flask is the web framework that provides the foundation for the application. Its lightweight nature and flexibility allow for custom architecture while providing essential features like routing, templating, and request handling. Flask's Blueprint system enables modular organization of the codebase.

### SQLAlchemy 2.0.30
SQLAlchemy serves as the ORM (Object-Relational Mapper) for database operations. Version 2.0 introduces significant improvements including better type support, more intuitive query syntax, and enhanced performance. SQLAlchemy's database abstraction allows the application to work with both SQLite and PostgreSQL seamlessly.

### Flask-Login 0.6.3
Flask-Login handles user authentication and session management. It provides secure session handling, remember me functionality, and user loading from the session. The integration with Flask's request context makes authentication straightforward and secure.

### Flask-WTF 1.2.1
Flask-WTF provides form handling and CSRF protection. It integrates WTForms for form validation and rendering, while automatically adding CSRF tokens to all forms. This protection prevents cross-site request forgery attacks.

### Flask-Migrate 4.0.7
Flask-Migrate handles database schema migrations using Alembic. It provides a command-line interface for creating, applying, and rolling back database migrations. This is essential for managing schema changes in production PostgreSQL databases.

### Argon2-cffi 23.1.0
Argon2 is the password hashing algorithm used for secure password storage. It is a memory-hard algorithm designed to resist GPU and ASIC attacks. The cffi implementation provides Python bindings for the reference Argon2 implementation.

### psycopg2-binary 2.9.9
psycopg2-binary is the PostgreSQL adapter for Python. It provides a robust, feature-rich interface for PostgreSQL databases. The binary distribution includes the necessary C libraries, simplifying installation.

## Frontend Technologies

### Tailwind CSS
Tailwind CSS is a utility-first CSS framework that enables rapid UI development. Instead of writing custom CSS, developers compose designs using pre-defined utility classes. This approach results in smaller CSS bundles and consistent styling across the application.

### Alpine.js 3.14.1
Alpine.js is a lightweight JavaScript framework for adding reactivity to the frontend. It provides a similar developer experience to Vue.js but with a much smaller footprint. Alpine.js is used for form interactions, modal dialogs, and real-time wage calculation.

### Chart.js 4.4.1
Chart.js is a JavaScript library for data visualization. It creates responsive, accessible charts using HTML5 canvas. The dashboard uses Chart.js for bar charts, line charts, and donut charts to display production trends and payroll distribution.

### Google Fonts
The application uses Google Fonts for typography. Cormorant Garamond provides an elegant display font for headings, while DM Sans serves as the body font. DM Mono is used for monetary values and tabular data.

## PDF Generation

### ReportLab 4.2.2
ReportLab is a Python library for PDF generation. It provides comprehensive control over PDF layout, typography, and graphics. The application uses ReportLab to generate branded wage sheet PDFs with tables, headers, footers, and signature blocks.

### Markdown 3.6
Markdown is used for parsing documentation files into HTML for PDF generation. This allows documentation to be maintained in simple Markdown format while producing professional PDF outputs.

### BeautifulSoup4 4.12.3
BeautifulSoup4 is used for HTML parsing in the documentation PDF generator. It extracts headings and paragraphs from converted Markdown for proper formatting in the PDF output.

## Server Technologies

### Gunicorn 22.0.0
Gunicorn (Green Unicorn) is the WSGI HTTP Server used in production. It is a pre-fork worker model that provides excellent performance and stability. Gunicorn is recommended for Railway and Oracle Cloud deployments.

### Waitress 3.0.0
Waitress is a pure Python WSGI server used for local development. It provides a production-quality server without requiring external C dependencies. Waitress is used when running the application directly with Python.

## Development Tools

### pytest 8.2.2
pytest is the testing framework used for the project. It provides a powerful and flexible testing interface with fixtures, parameterized tests, and detailed output. pytest's discovery mechanism makes it easy to organize and run tests.

### pytest-cov 5.0.0
pytest-cov generates code coverage reports for pytest. It integrates seamlessly with pytest and provides multiple output formats including terminal and HTML reports. The project targets over 80% code coverage.

### Coverage 7.5.3
Coverage is the underlying library for code coverage measurement. It tracks which lines of code are executed during test runs and generates comprehensive reports.

### Ruff 0.4.8
Ruff is a fast Python linter and formatter. It replaces multiple tools including Flake8, isort, and Black. Ruff provides consistent code style and catches potential errors before they reach production.

## Environment Management

### python-dotenv 1.0.1
python-dotenv loads environment variables from .env files. This allows configuration to be managed outside of the codebase, keeping secrets and environment-specific settings separate from version control.

## Version Table

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.3 | Web Framework |
| Flask-SQLAlchemy | 3.1.1 | ORM Integration |
| Flask-Login | 0.6.3 | Authentication |
| Flask-WTF | 1.2.1 | Form Handling |
| Flask-Migrate | 4.0.7 | Database Migrations |
| WTForms | 3.1.2 | Form Validation |
| email-validator | 2.2.0 | Email Validation |
| argon2-cffi | 23.1.0 | Password Hashing |
| SQLAlchemy | 2.0.30 | Database ORM |
| psycopg2-binary | 2.9.9 | PostgreSQL Adapter |
| reportlab | 4.2.2 | PDF Generation |
| Markdown | 3.6 | Documentation Parsing |
| beautifulsoup4 | 4.12.3 | HTML Parsing |
| waitress | 3.0.0 | Development Server |
| gunicorn | 22.0.0 | Production Server |
| python-dotenv | 1.0.1 | Environment Variables |
| pytest | 8.2.2 | Testing Framework |
| pytest-cov | 5.0.0 | Coverage Reporting |
| coverage | 7.5.3 | Code Coverage |
| ruff | 0.4.8 | Linting and Formatting |

## Deployment Platforms

### Vercel
Vercel is a serverless platform optimized for frontend and serverless functions. The application uses Vercel's Python runtime to serve the Flask application. Static files are served from Vercel's CDN for optimal performance.

### Railway
Railway is a container-based platform that provides PostgreSQL databases and application hosting. The application uses Railway's Nixpacks build system for Python 3.11 and PostgreSQL support.

### Oracle Cloud Free Tier
Oracle Cloud Free Tier provides always-free compute and database resources. The application can be deployed using similar configuration to Railway, with gunicorn serving the application.

## Browser Requirements

The application requires a modern web browser with JavaScript enabled. Supported browsers include:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

The application uses modern JavaScript features including ES6 modules, async/await, and template literals. These features are supported in all modern browsers.

## Security Considerations

All third-party packages are maintained and regularly updated for security patches. The requirements.txt file pins specific versions to ensure reproducible builds. Security vulnerabilities are monitored through dependency scanning tools.

The application uses HTTPS in production environments, with secure cookie attributes configured appropriately. CSRF protection is enabled on all form submissions, and password hashing uses Argon2 with appropriate parameters.

## Performance Considerations

The technology stack is optimized for performance. SQLAlchemy uses connection pooling for efficient database access. Static files are served from CDN on Vercel. Chart.js uses canvas rendering for efficient chart updates. Alpine.js provides reactive updates without the overhead of larger frameworks.

Database queries are optimized to avoid N+1 query problems. The payroll view uses a single aggregation query with joins rather than multiple queries. Indexes are defined on frequently queried columns to improve query performance.

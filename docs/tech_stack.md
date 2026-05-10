# Technology Stack

## Overview

The Hilltop Tea Wage Tracking & Payroll System is built on a modern Python web stack with carefully selected components for security, performance, and maintainability. This document details all technologies used, their versions, and the rationale for their selection.

## Core Framework

### Flask 3.0.3

Flask serves as the foundational web framework for the application. Its lightweight nature and extensibility make it ideal for this project. Flask provides:
- WSGI compliance for deployment flexibility
- Built-in development server and debugger
- Extensive middleware ecosystem
- Simple routing and view functions
- Jinja2 templating integration

The choice of Flask over heavier frameworks like Django allows for greater architectural flexibility while maintaining simplicity for the application's specific needs.

### Flask-SQLAlchemy 3.1.1

SQLAlchemy integration provides ORM capabilities with:
- Declarative model definitions
- Automatic table creation
- Relationship management
- Query building and optimization
- Database abstraction layer

This ORM layer abstracts database operations, making the code more maintainable and allowing easy switching between SQLite for development and PostgreSQL for production.

### Flask-Login 0.6.3

Flask-Login handles user session management:
- User authentication and session handling
- Remember me functionality
- Login required decorators
- Current user context
- Secure cookie management

This extension simplifies authentication flows while maintaining security best practices.

### Flask-WTF 1.2.1

Form handling and CSRF protection:
- WTForms integration
- CSRF token generation and validation
- Form validation
- File upload handling
- Recaptcha support (optional)

CSRF protection is critical for preventing cross-site request forgery attacks on form submissions.

### Flask-Migrate 4.0.7

Database migration management:
- Alembic integration for Flask
- Automatic migration generation
- Version control for schema changes
- Upgrade and downgrade commands
- Migration history tracking

This ensures database schema changes are managed systematically across development, testing, and production environments.

## Forms and Validation

### WTForms 3.1.2

Core form validation library:
- Field types and validators
- Custom validator support
- Internationalization
- CSRF protection integration
- HTML rendering

WTForms provides robust input validation with minimal code, reducing the risk of injection attacks and data corruption.

### email-validator 2.2.0

Email address validation:
- RFC-compliant email validation
- Domain checking
- Internationalized email support
- Deliverability checking (optional)

While not heavily used in this application, it's included for future email-related features.

## Security

### argon2-cffi 23.1.0

Password hashing with Argon2:
- Argon2id algorithm (winner of Password Hashing Competition)
- Configurable time, memory, and parallelism parameters
- Resistance to GPU/ASIC attacks
- Automatic rehashing detection

Argon2 provides state-of-the-art password security, significantly stronger than older algorithms like bcrypt or PBKDF2.

## Database

### SQLAlchemy 2.0.30

Core ORM library:
- Python SQL toolkit
- Object-relational mapping
- Database abstraction
- Connection pooling
- Transaction management

SQLAlchemy 2.0 provides modern Python features and improved performance over previous versions.

### psycopg2-binary 2.9.9

PostgreSQL adapter for Python:
- Binary distribution for easy installation
- Full PostgreSQL feature support
- Asynchronous operations support
- Connection pooling
- SSL/TLS support

This enables production deployment with PostgreSQL, offering superior performance and features compared to SQLite.

## PDF Generation

### reportlab 4.2.2

PDF document generation:
- Professional PDF creation
- Custom fonts and styling
- Table and chart support
- Page layout control
- Vector graphics

ReportLab enables branded PDF wage sheet export without requiring external dependencies or server-side rendering.

## Documentation PDF Generator

### Markdown 3.6

Markdown parsing and rendering:
- CommonMark compliance
- Extension support
- HTML output
- Custom rendering options

Used for converting documentation markdown files to HTML for PDF generation.

### beautifulsoup4 4.12.3

HTML parsing and manipulation:
- HTML/XML parsing
- Document tree navigation
- Search and modification
- Encoding handling

BeautifulSoup processes the HTML output from Markdown conversion for PDF generation.

## Server

### waitress 3.0.0

WSGI server for Windows:
- Production-ready WSGI server
- Windows compatibility
- Thread-based concurrency
- Graceful shutdown

Used for local development on Windows systems.

### gunicorn 22.0.0

WSGI HTTP server for Unix:
- Pre-fork worker model
- Process management
- Automatic worker restart
- SSL/TLS support
- Graceful worker reloading

Gunicorn is the production server for Railway and Oracle Cloud deployments, offering superior performance and reliability.

## Environment

### python-dotenv 1.0.1

Environment variable management:
- .env file loading
- Variable interpolation
- Default values
- Type conversion

Simplifies configuration management across different environments without hardcoding sensitive values.

## Testing

### pytest 8.2.2

Testing framework:
- Simple test discovery
- Fixture system
- Parameterized testing
- Plugin ecosystem
- Detailed failure reporting

Pytest provides a powerful and flexible testing framework with excellent integration with other testing tools.

### pytest-cov 5.0.0

Code coverage plugin:
- Coverage reporting
- HTML output
- Branch coverage
- Coverage thresholds

Ensures adequate test coverage and identifies untested code paths.

### coverage 7.5.3

Code coverage analysis:
- Line and branch coverage
- Multiple report formats
- Coverage combination
- Exclusion patterns

Works with pytest-cov to provide comprehensive coverage analysis.

## Code Quality

### ruff 0.4.8

Fast Python linter:
- PEP 8 compliance
- Import sorting
- Unused code detection
- Type checking integration
- Fast performance

Ruff provides rapid linting with comprehensive rule sets, replacing multiple older tools.

## Frontend Technologies

### Tailwind CSS 3.4.1 (via CDN)

Utility-first CSS framework:
- Responsive design utilities
- Custom color palette
- Typography scale
- Spacing system
- Dark mode support

Tailwind enables rapid UI development with consistent styling while keeping CSS bundle size minimal.

### Alpine.js 3.14.1 (via CDN)

Reactive JavaScript framework:
- Lightweight (~15KB)
- Declarative syntax
- Component-based
- No build step required
- Easy integration with existing HTML

Alpine.js provides reactive functionality for forms, modals, and dynamic UI elements without the complexity of larger frameworks.

### Chart.js 4.4.1 (via CDN)

Charting library:
- Responsive charts
- Multiple chart types
- Custom styling
- Animation support
- Plugin ecosystem

Chart.js powers the dashboard analytics with professional-looking visualizations.

### Google Fonts

Typography:
- Cormorant Garamond (display headings)
- DM Sans (body text)
- DM Mono (numbers and code)

These fonts provide a professional, branded appearance while maintaining readability.

## Deployment Platforms

### Vercel

Serverless deployment platform:
- Python runtime support
- Automatic scaling
- Global CDN
- Git integration
- Preview deployments

Vercel provides excellent static file serving via CDN with serverless API routes for dynamic content.

### Railway

Container-based deployment:
- Docker support
- Managed PostgreSQL
- Automatic scaling
- Environment variable management
- Preview deployments

Railway offers a complete containerized deployment with managed database services.

### Oracle Cloud Free Tier

Infrastructure as a service:
- Virtual machine hosting
- Autonomous database
- Load balancing
- Free tier resources
- Enterprise features

Oracle Cloud provides enterprise-grade infrastructure at no cost for eligible applications.

## Version Table

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.3 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | ORM integration |
| Flask-Login | 0.6.3 | Authentication |
| Flask-WTF | 1.2.1 | Forms and CSRF |
| Flask-Migrate | 4.0.7 | Database migrations |
| WTForms | 3.1.2 | Form validation |
| email-validator | 2.2.0 | Email validation |
| argon2-cffi | 23.1.0 | Password hashing |
| SQLAlchemy | 2.0.30 | Core ORM |
| psycopg2-binary | 2.9.9 | PostgreSQL adapter |
| reportlab | 4.2.2 | PDF generation |
| Markdown | 3.6 | Markdown parsing |
| beautifulsoup4 | 4.12.3 | HTML parsing |
| waitress | 3.0.0 | Windows WSGI server |
| gunicorn | 22.0.0 | Production WSGI server |
| python-dotenv | 1.0.1 | Environment management |
| pytest | 8.2.2 | Testing framework |
| pytest-cov | 5.0.0 | Coverage plugin |
| coverage | 7.5.3 | Coverage analysis |
| ruff | 0.4.8 | Code linting |

## Technology Rationale

### Why Flask Over Django?

Flask was chosen for its:
- Simplicity and minimal boilerplate
- Flexibility in architecture
- Smaller learning curve
- Better fit for the application's specific needs
- Easier testing and debugging

### Why PostgreSQL Over Other Databases?

PostgreSQL offers:
- Superior performance for complex queries
- Advanced features (JSON, arrays, etc.)
- Better concurrency handling
- Strong data integrity
- Excellent tooling and community support

### Why Argon2 Over Other Hashing Algorithms?

Argon2 provides:
- Resistance to GPU/ASIC attacks
- Memory-hard computation
- Configurable security parameters
- Winner of Password Hashing Competition
- Future-proof security

### Why Tailwind CSS Over Traditional CSS?

Tailwind enables:
- Rapid UI development
- Consistent design system
- Smaller CSS bundles
- Easy customization
- Better maintainability

### Why Alpine.js Over Larger Frameworks?

Alpine.js offers:
- Minimal bundle size
- No build step required
- Easy integration
- Sufficient for application needs
- Lower complexity

This technology stack provides a solid foundation for the Hilltop Tea system while ensuring security, performance, and maintainability for years to come.

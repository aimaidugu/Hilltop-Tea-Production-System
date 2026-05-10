# Construction Decisions

## Overview

This document details the critical architectural and technical decisions made during the development of the Hilltop Tea Wage Tracking & Payroll System. Each decision includes the rationale, alternatives considered, and implications for the project.

## Decision 1: Configuration Management

### Decision: Use environment-based configuration with config.py

**Rationale:**
Environment-based configuration provides flexibility across development, testing, and production environments without code changes. The config.py pattern allows for:
- Clear separation of environment-specific settings
- Easy testing with isolated configuration
- Secure handling of sensitive values via environment variables
- Simple deployment to multiple platforms

**Alternatives Considered:**
- Hardcoded configuration values (rejected for security and flexibility)
- Configuration files like config.yaml (rejected for additional complexity)
- Database-backed configuration (rejected for over-engineering)

**Implications:**
- Requires proper environment variable management
- Simplifies deployment to different platforms
- Enables secure secret management
- Makes testing easier with isolated configurations

## Decision 2: Password Hashing with Argon2

### Decision: Use Argon2id for all password hashing

**Rationale:**
Argon2 is the winner of the Password Hashing Competition and provides superior security:
- Memory-hard computation resists GPU/ASIC attacks
- Configurable parameters for security vs. performance trade-offs
- Resistance to side-channel attacks
- Future-proof security design

**Alternatives Considered:**
- bcrypt (rejected as Argon2 is more secure)
- PBKDF2 (rejected as Argon2 is more secure)
- SHA-256 (rejected as not suitable for password hashing)

**Implications:**
- Requires argon2-cffi dependency
- Slightly slower than older algorithms (acceptable for security)
- Configurable parameters for different environments
- Fast parameters used in testing to maintain speed

## Decision 3: PDF Generation with ReportLab

### Decision: Use ReportLab for PDF generation

**Rationale:**
ReportLab provides comprehensive PDF generation capabilities:
- Pure Python implementation
- No external dependencies
- Professional document formatting
- Custom styling and branding
- In-memory generation (no temp files)

**Alternatives Considered:**
- WeasyPrint (rejected for additional dependencies and complexity)
- wkhtmltopdf (rejected for external binary requirement)
- HTML to PDF services (rejected for privacy and cost)

**Implications:**
- Larger dependency footprint
- Steeper learning curve for complex layouts
- Excellent for Vercel deployment (no temp files needed)
- Full control over document appearance

## Decision 4: Table-Driven Wage Calculation

### Decision: Implement wage calculation as table-driven lookup

**Rationale:**
Table-driven design eliminates conditional logic in business rules:
- Clear separation of data and logic
- Easy to modify rates without code changes
- Transparent calculation process
- Testable and maintainable

**Alternatives Considered:**
- If-else chains (rejected for maintainability)
- Database-stored rates (rejected for over-engineering)
- Configuration file rates (rejected for unnecessary complexity)

**Implications:**
- Wage tiers defined as module constants
- Easy to audit and verify calculations
- Simple to add new tiers
- Clear business rule documentation

## Decision 5: Immutable Daily Wage Storage

### Decision: Store daily_wage at record creation, never recalculate

**Rationale:**
Immutable wage storage preserves historical accuracy:
- Payroll remains accurate even if rates change
- Audit trail of wages at time of work
- Prevents retroactive wage changes
- Simplifies payroll calculations

**Alternatives Considered:**
- Calculate on demand (rejected for audit trail concerns)
- Store rate and calculate (rejected for complexity)
- Versioned rate tables (rejected for over-engineering)

**Implications:**
- Requires careful rate change management
- Clear audit trail for payroll
- Simplifies historical reporting
- Rate changes only affect future records

## Decision 6: Soft Delete for Employees

### Decision: Use active flag instead of hard deletion

**Rationale:**
Soft deletion preserves historical records:
- Production and payment records remain intact
- Audit trail maintained
- Easy to reactivate employees
- Prevents data integrity issues

**Alternatives Considered:**
- Hard deletion (rejected for data loss)
- Archive tables (rejected for complexity)
- Cascading deletion (rejected for data loss)

**Implications:**
- Requires active flag filtering in queries
- Historical data always available
- Simple reactivation process
- Additional storage for inactive records

## Decision 7: Blueprint Architecture

### Decision: Organize routes into functional blueprints

**Rationale:**
Blueprint architecture provides clear separation of concerns:
- Logical grouping of related routes
- Easy to add new features
- Simplifies testing
- Better code organization

**Alternatives Considered:**
- Single routes.py file (rejected for maintainability)
- Class-based views (rejected for unnecessary complexity)
- Microservices (rejected for over-engineering)

**Implications:**
- More files but better organization
- Clear module boundaries
- Easier to understand and maintain
- Simplifies feature addition

## Decision 8: Role-Based Access Control

### Decision: Implement custom @require_role decorator

**Rationale:**
Custom decorator provides clear and flexible access control:
- Explicit role requirements in code
- Easy to audit permissions
- Consistent error handling
- Simple to extend

**Alternatives Considered:**
- Flask-Security (rejected for additional complexity)
- Database-driven permissions (rejected for over-engineering)
- Middleware-based checks (rejected for less clarity)

**Implications:**
- Requires decorator on protected routes
- Clear permission model
- Easy to test and verify
- Simple to add new roles

## Decision 9: Monthly Payroll Isolation

### Decision: Calculate payroll independently per month

**Rationale:**
Monthly isolation simplifies accounting:
- Clear monthly reporting
- No carry-forward complexity
- Easy to audit specific periods
- Matches business accounting cycles

**Alternatives Considered:**
- Running balance (rejected for complexity)
- Quarterly aggregation (rejected for business mismatch)
- Year-to-date tracking (rejected for complexity)

**Implications:**
- Simple payroll calculations
- Clear monthly reporting
- Easy to understand balances
- Matches business processes

## Decision 10: Real-Time Wage Preview

### Decision: Implement client-side wage calculation with Alpine.js

**Rationale:**
Client-side calculation provides immediate feedback:
- No server round-trips for preview
- Better user experience
- Reduces server load
- Simple implementation

**Alternatives Considered:**
- Server-side AJAX (rejected for latency)
- No preview (rejected for poor UX)
- WebAssembly (rejected for complexity)

**Implications:**
- Requires JavaScript on client
- Must mirror server logic exactly
- Excellent user experience
- Reduced server load

## Decision 11: Static File Serving on Vercel

### Decision: Serve static files via Vercel CDN, not Lambda

**Rationale:**
CDN serving provides better performance:
- Faster asset delivery
- Reduced Lambda execution time
- Better caching control
- Lower costs

**Alternatives Considered:**
- Lambda serving (rejected for performance)
- CloudFront (rejected for complexity)
- No static files (rejected for poor UX)

**Implications:**
- Requires /public directory structure
- Custom static_url helper function
- Better performance and caching
- Slightly more complex deployment

## Decision 12: Database Choice by Environment

### Decision: Use SQLite for development, PostgreSQL for production

**Rationale:**
Environment-appropriate database selection:
- SQLite for simplicity in development
- PostgreSQL for production features
- Easy local development setup
- Production-ready database

**Alternatives Considered:**
- PostgreSQL everywhere (rejected for complexity)
- SQLite everywhere (rejected for production limitations)
- MySQL (rejected for fewer features)

**Implications:**
- Requires migration management
- Different SQL dialects handled by ORM
- Easy local development
- Production-ready features

## Decision 13: Test Database Strategy

### Decision: Use in-memory SQLite with db.create_all() for tests

**Rationale:**
In-memory SQLite provides fast, isolated test databases:
- Fast test execution
- Complete isolation between tests
- No external dependencies
- Simple setup and teardown

**Alternatives Considered:**
- Flask-Migrate in tests (rejected for complexity)
- Test PostgreSQL database (rejected for speed)
- File-based SQLite (rejected for cleanup complexity)

**Implications:**
- Fast test suite execution
- No migration management in tests
- Complete test isolation
- Simple test setup

## Decision 14: PRG Pattern for Form Submissions

### Decision: Use Post-Redirect-Get pattern for all form submissions

**Rationale:**
PRG pattern prevents duplicate submissions:
- No duplicate records on refresh
- Better user experience
- Standard web practice
- Simplifies error handling

**Alternatives Considered:**
- No redirect (rejected for duplicate submissions)
- AJAX submissions (rejected for complexity)
- Token-based prevention (rejected for complexity)

**Implications:**
- Standard web practice
- Prevents duplicate submissions
- Better user experience
- Slightly more complex flow

## Decision 15: Single Query Payroll Aggregation

### Decision: Use single SQL query with LEFT JOINs for payroll

**Rationale:**
Single query provides optimal performance:
- Avoids N+1 query problem
- Meets Vercel timeout requirements
- Efficient data retrieval
- Scales to large employee counts

**Alternatives Considered:**
- N+1 queries (rejected for performance)
- Multiple queries with aggregation (rejected for complexity)
- Materialized views (rejected for over-engineering)

**Implications:**
- Complex SQL query
- Excellent performance
- Scales well
- Requires careful query construction

## Decision 16: User Model Enhancements

### Decision: Add last_login field and nullable foreign keys

**Rationale:**
Enhanced user model provides better tracking:
- Last login timestamp for security
- Nullable foreign keys for record preservation
- Better audit trail
- Simplified deletion handling

**Alternatives Considered:**
- No last_login (rejected for security value)
- Cascading deletion (rejected for data loss)
- Separate audit tables (rejected for complexity)

**Implications:**
- Better security tracking
- Preserved historical records
- Clear audit trail
- Slightly more complex queries

## Decision 17: Error Page Customization

### Decision: Implement custom 403, 404, and 500 error pages

**Rationale:**
Custom error pages provide better user experience:
- Branded error messages
- Clear navigation options
- Professional appearance
- Better error handling

**Alternatives Considered:**
- Default error pages (rejected for poor UX)
- Generic error page (rejected for lack of context)
- AJAX error handling (rejected for complexity)

**Implications:**
- Better user experience
- Professional appearance
- Clear error communication
- Additional template files

## Decision 18: Chart.js for Analytics

### Decision: Use Chart.js for dashboard visualizations

**Rationale:**
Chart.js provides excellent charting capabilities:
- Responsive charts
- Multiple chart types
- Custom styling
- Easy integration

**Alternatives Considered:**
- D3.js (rejected for complexity)
- Plotly (rejected for larger bundle)
- No charts (rejected for poor UX)

**Implications:**
- Professional visualizations
- Better data understanding
- Additional CDN dependency
- Excellent user experience

## Decision 19: Alpine.js for Interactivity

### Decision: Use Alpine.js for reactive UI components

**Rationale:**
Alpine.js provides lightweight reactivity:
- Small bundle size
- No build step required
- Easy integration
- Sufficient for application needs

**Alternatives Considered:**
- Vue.js (rejected for larger bundle)
- React (rejected for complexity)
- Vanilla JS (rejected for maintainability)

**Implications:**
- Lightweight interactivity
- Better user experience
- Simple implementation
- No build process needed

## Decision 20: Tailwind CSS for Styling

### Decision: Use Tailwind CSS via CDN for styling

**Rationale:**
Tailwind provides rapid UI development:
- Utility-first approach
- Consistent design system
- Small bundle size
- Easy customization

**Alternatives Considered:**
- Bootstrap (rejected for larger bundle)
- Custom CSS (rejected for development time)
- Sass (rejected for build complexity)

**Implications:**
- Rapid development
- Consistent design
- Small bundle size
- CDN dependency

These decisions collectively shape the architecture and implementation of the Hilltop Tea system, balancing security, performance, maintainability, and user experience while meeting the specific requirements of the tea factory's wage tracking and payroll needs.

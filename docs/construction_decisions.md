# HILLTOP TEA — Construction Decisions

## Overview

This document details the critical architectural and implementation decisions made during the development of Hilltop Tea. Each decision includes the rationale, alternatives considered, and implications for the system.

## Decision 1: Flask Framework Selection

**Decision:** Use Flask as the web framework.

**Rationale:** Flask provides a lightweight, flexible foundation that allows custom architecture without imposing unnecessary constraints. Its Blueprint system enables modular organization, which is essential for a system with multiple user roles and functional domains. Flask's extensive ecosystem and mature documentation reduce development risk.

**Alternatives Considered:**
- Django: Too opinionated for this scale, would require more boilerplate
- FastAPI: Excellent for APIs but less mature for traditional server-rendered applications
- Bottle: Too minimal, lacks ecosystem support

**Implications:** The application benefits from Flask's simplicity while having access to a rich ecosystem of extensions. The Blueprint structure provides clear separation of concerns and enables parallel development.

## Decision 2: Configuration Management

**Decision:** Use a config.py module with environment-based configuration classes.

**Rationale:** This approach provides clear separation between development, testing, and production configurations. Environment variables control which configuration is active, making deployment straightforward. The _resolve_db_url function handles Railway/Heroku legacy postgres:// prefixes.

**Alternatives Considered:**
- Single config file with if/else statements: Less maintainable
- Environment variables only: No default values, harder to document
- YAML/JSON config files: Additional dependency, less Pythonic

**Implications:** Configuration is centralized and type-safe. Different environments can have different settings without code changes. The DATABASE_URL resolution function ensures compatibility with multiple hosting platforms.

## Decision 3: Argon2 Password Hashing

**Decision:** Use Argon2 via argon2-cffi for all password hashing.

**Rationale:** Argon2 is the winner of the Password Hashing Competition and is recommended by security experts. Its memory-hard design resists GPU and ASIC attacks. The cffi implementation provides Python bindings without requiring compilation.

**Alternatives Considered:**
- bcrypt: Good but less resistant to GPU attacks
- PBKDF2: NIST-approved but less secure against modern attacks
- Werkzeug security: Deprecated and less secure

**Implications:** Passwords are stored with industry-best security. Fast parameters are used in tests to keep test execution time under 10 seconds. The needs_rehash method allows future parameter upgrades.

## Decision 4: Wage Calculator ADT

**Decision:** Implement wage calculation as a separate Abstract Data Type with table-driven rate lookup.

**Rationale:** This approach eliminates conditional business logic from the main codebase. The table-driven design makes rate changes straightforward and testable. The ADT encapsulation ensures that wage calculation logic is consistent across the application.

**Alternatives Considered:**
- Inline if/else chains: Harder to maintain, error-prone
- Database-stored rates: Adds complexity, not needed for this scale
- Configuration file rates: Less type-safe, harder to test

**Implications:** Wage calculation is centralized, testable, and maintainable. The get_tiers method returns a defensive copy, preventing accidental mutation. Rate changes only require updating the constant table.

## Decision 5: Immutable Daily Wage

**Decision:** Store daily_wage at record creation time and never update it.

**Rationale:** This preserves payroll accuracy across rate changes. If rates are updated, historical records retain the rate that was in effect at the time of production. This is critical for accounting and audit purposes.

**Alternatives Considered:**
- Recalculate on demand: Loses historical accuracy
- Store rate ID and recalculate: Adds complexity without benefit
- Versioned rate tables: Overkill for this use case

**Implications:** Payroll is always accurate regardless of rate changes. The wage calculation happens once per record, improving performance. Historical analysis reflects actual wages paid.

## Decision 6: Role-Based Access Control

**Decision:** Implement @require_role decorator for route-level access control.

**Rationale:** Decorators provide a clean, declarative way to enforce access control. The decorator works with Flask-Login's @login_required to provide complete authentication and authorization. HTTP 403 responses are returned for unauthorized access.

**Alternatives Considered:**
- Middleware: More complex, harder to understand
- Inline checks in routes: Repetitive, error-prone
- Flask-Security: Overkill for this use case

**Implications:** Access control is consistent and easy to audit. The decorator can be applied to any route with minimal code. Custom 403 templates provide user-friendly error messages.

## Decision 7: Soft Delete for Employees

**Decision:** Implement soft delete using an active flag rather than hard deletion.

**Rationale:** Historical production and payment records must be preserved for accounting purposes. Soft delete allows employees to be deactivated while maintaining their historical data. Hard delete is only permitted if no records exist.

**Alternatives Considered:**
- Hard delete only: Loses historical data
- Archive tables: Adds complexity, not needed
- Timestamped deletion: Still loses data integrity

**Implications:** Employee records can be deactivated without affecting historical data. Reactivation is straightforward. Hard delete protection prevents accidental data loss.

## Decision 8: Single Query Payroll Aggregation

**Decision:** Use a single SQL query with LEFT JOINs and GROUP BY for payroll calculation.

**Rationale:** This approach avoids N+1 query problems that would exceed Vercel's 10-second timeout with large employee counts. The query is optimized with appropriate indexes and returns all necessary data in one round-trip.

**Alternatives Considered:**
- N+1 queries: Simple but slow, fails at scale
- Multiple aggregated queries: More round-trips, still slow
- Materialized views: Overkill for this use case

**Implications:** Payroll view performs well even with hundreds of employees. The query is maintainable and can be optimized further if needed. Grand totals are calculated efficiently.

## Decision 9: Alpine.js for Frontend Reactivity

**Decision:** Use Alpine.js for reactive components instead of a larger framework.

**Rationale:** Alpine.js provides reactivity with minimal overhead. It integrates seamlessly with existing HTML and requires no build step. The wageRow component provides real-time wage calculation without server round-trips.

**Alternatives Considered:**
- Vue.js: More powerful but larger footprint
- React: Overkill for this use case, requires build step
- Vanilla JavaScript: More code, harder to maintain

**Implications:** The frontend is lightweight and responsive. Real-time wage calculation improves user experience. No build step simplifies development and deployment.

## Decision 10: Vercel Static File Routing

**Decision:** Route static files through Vercel CDN rather than the Lambda function.

**Rationale:** Serving static files from CDN provides better performance and reduces Lambda execution time. The static_url context processor handles the URL difference between development and production. This approach is recommended by Vercel for Python applications.

**Alternatives Considered:**
- Serve through Lambda: Slower, higher cost
- Separate static site: More complex deployment
- CloudFront: Additional service, more configuration

**Implications:** Static files are served efficiently with proper caching. The application remains deployable to multiple platforms. The context processor abstracts the URL difference.

## Decision 11: ReportLab for PDF Generation

**Decision:** Use ReportLab for PDF generation instead of WeasyPrint.

**Rationale:** ReportLab is a pure Python library with comprehensive PDF capabilities. It works well in serverless environments where file system access is limited. The library provides fine-grained control over layout and styling.

**Alternatives Considered:**
- WeasyPrint: Requires additional system dependencies
- wkhtmltopdf: External binary, harder to deploy
- PDFKit: Node.js dependency, adds complexity

**Implications:** PDFs are generated entirely in memory, which is essential for Vercel. The library provides complete control over document layout. No external dependencies simplify deployment.

## Decision 12: Test Database Strategy

**Decision:** Use in-memory SQLite with db.create_all() for tests, not Flask-Migrate.

**Rationale:** In-memory SQLite is fast and provides complete isolation between tests. Using db.create_all() is simpler than running migrations for each test. Fast Argon2 parameters keep test execution under 10 seconds.

**Alternatives Considered:**
- Flask-Migrate in tests: Slower, more complex
- File-based SQLite: Slower, requires cleanup
- PostgreSQL in tests: Overkill, slower

**Implications:** Tests run quickly and are completely isolated. The test database is fresh for each test. No migration files are needed for the test suite.

## Decision 13: PPP Documentation Blocks

**Decision:** Document critical algorithms with PPP (Pre-conditions, Process, Post-conditions) blocks.

**Rationale:** PPP blocks provide clear documentation of algorithm behavior. They serve as executable documentation and help with code reviews. The blocks are particularly valuable for complex business logic like production entry and payroll calculation.

**Alternatives Considered:**
- Standard docstrings: Less structured, harder to parse
- External documentation: Can become outdated
- No documentation: Reduces maintainability

**Implications:** Critical algorithms are well-documented and easy to understand. The documentation is kept in sync with the code. Code reviews are more effective with clear algorithm documentation.

## Decision 14: User Model last_login Field

**Rationale:** Track when users last logged in for security auditing and activity monitoring.

**Decision:** Add a nullable last_login DateTime field to the User model.

**Alternatives Considered:**
- No tracking: Loses security visibility
- Separate audit table: Overkill for this use case
- Session-based tracking: Less reliable

**Implications:** Security teams can monitor user activity. Inactive accounts can be identified. The field is nullable to accommodate existing users.

## Decision 15: Nixpacks Configuration

**Decision:** Use nixpacks.toml to pin Python 3.11 and include PostgreSQL for Railway builds.

**Rationale:** Nixpacks provides declarative build configuration for Railway. Pinning Python 3.11 ensures consistent behavior across deployments. Including PostgreSQL ensures psycopg2-binary builds correctly.

**Alternatives Considered:**
- Railway defaults: May use older Python version
- Dockerfile: More complex, harder to maintain
- Buildpacks: Less control over dependencies

**Implications:** Railway deployments are reproducible and reliable. The Python version is pinned to prevent unexpected changes. PostgreSQL dependencies are included for psycopg2-binary.

## Decision 16: Error Handler Registration

**Decision:** Register error handlers for 403, 404, and 500 in the app factory.

**Rationale:** Custom error pages provide a better user experience than default browser errors. The 500 handler includes database rollback to prevent partial state. Error handlers are registered once in the factory for consistency.

**Alternatives Considered:**
- Default error pages: Poor user experience
- Blueprint-level handlers: Inconsistent across blueprints
- Middleware: More complex than needed

**Implications:** Users see branded error pages. Database errors are handled gracefully. Error handling is consistent across the application.

## Decision 17: Session Cookie Configuration

**Decision:** Configure session cookies with secure, HTTP-only, and SameSite=Lax attributes in production.

**Rationale:** These attributes provide protection against session hijacking and CSRF attacks. Secure ensures cookies are only sent over HTTPS. HTTP-only prevents JavaScript access. SameSite=Lax provides CSRF protection while allowing reasonable navigation.

**Alternatives Considered:**
- Default settings: Less secure
- SameSite=Strict: Too restrictive for some use cases
- No cookies: Would require custom implementation

**Implications:** Sessions are secure in production environments. The application is protected against common cookie-based attacks. Development uses less restrictive settings for convenience.

## Decision 18: Pagination Strategy

**Decision:** Implement pagination with a configurable page size defaulting to 25 records.

**Rationale:** Pagination prevents overwhelming the browser with large data sets. A default of 25 records provides a good balance between information density and performance. The pagination helper function provides consistent behavior across all paginated views.

**Alternatives Considered:**
- No pagination: Poor performance with large datasets
- Infinite scroll: Harder to implement, less predictable
- Fixed page size: Less flexible for different use cases

**Implications:** Large datasets are displayed efficiently. Users can navigate through data without performance issues. The pagination UI is consistent across the application.

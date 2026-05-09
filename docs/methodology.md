# HILLTOP TEA — Development Methodology

## Development Approach

Hilltop Tea follows a disciplined development methodology that emphasizes code quality, maintainability, and security. The project uses a test-driven approach where critical business logic is validated through comprehensive unit tests. The codebase is organized into clear modules following Flask's Blueprint pattern, promoting separation of concerns and enabling parallel development.

The development process begins with understanding requirements through detailed specification documents. Business rules are translated into test cases before implementation begins. This ensures that the code meets all functional requirements and that edge cases are handled appropriately. The wage calculation logic, being a critical business function, was developed with extensive test coverage including boundary conditions and error scenarios.

## Code Organization

The application is structured around Flask Blueprints, each representing a distinct domain of functionality. This modular approach allows for clear separation of concerns and makes the codebase easier to navigate and maintain. Each blueprint contains its own routes, templates, and business logic, while shared utilities and models are kept in separate modules.

The models module defines all database entities with comprehensive docstrings following Google style conventions. Relationships between models are explicitly defined using back_populates rather than backref, providing clearer bidirectional relationship definitions. All models include to_dict methods for easy serialization and __repr__ methods for debugging.

## Testing Strategy

The testing strategy focuses on achieving high code coverage while ensuring that critical business paths are thoroughly validated. Unit tests cover the wage calculator, production entry, payroll calculations, and authentication flows. Integration tests verify that components work together correctly, particularly database operations and form submissions.

Tests are organized by functionality, with each test file covering a specific domain. The conftest.py file provides shared fixtures including the test application, database session, and seeded test data. Fast Argon2 parameters are used in tests to keep the test suite execution time under 10 seconds while still validating password hashing functionality.

## Security Implementation

Security is implemented through multiple layers of protection. Password hashing uses Argon2, a memory-hard password hashing algorithm designed to resist GPU and ASIC attacks. The @require_role decorator enforces role-based access control on protected routes, ensuring that users can only access functionality appropriate to their role.

CSRF protection is enabled on all form submissions using Flask-WTF. Session cookies are configured with secure, HTTP-only, and SameSite attributes in production environments. All user inputs are validated before processing, with appropriate error messages displayed to users without revealing sensitive information.

## Database Design

The database schema is designed to support the business requirements while maintaining data integrity. Foreign key relationships are defined with appropriate ON DELETE actions to ensure referential integrity. Unique constraints prevent duplicate production records for the same employee on the same date. Check constraints validate that carton counts and payment amounts are non-negative.

The daily_wage field in the ProductionRecord model is set at insertion time and never updated. This immutability preserves payroll accuracy even if rate structures change in the future. The wage calculation logic is encapsulated in a separate ADT (Abstract Data Type) that implements table-driven rate lookup without conditional business logic.

## Frontend Development

The frontend uses a combination of Tailwind CSS for styling and Alpine.js for reactive components. This approach provides a modern, responsive interface without the complexity of a full JavaScript framework. Alpine.js components are defined in a single JavaScript file, keeping the frontend code organized and maintainable.

Real-time wage calculation is implemented in JavaScript using the same tier structure as the Python backend. This provides immediate feedback to users during data entry without requiring server round-trips. Chart.js is used for data visualization on the dashboard, providing clear insights into production trends and payroll distribution.

## Deployment Considerations

The application is designed for deployment across multiple platforms including Vercel, Railway, and Oracle Cloud Free Tier. Each platform has specific configuration files that define how the application is built and served. The static_url context processor ensures that static files are served correctly on Vercel, where they are served from the CDN rather than through the Lambda function.

Database initialization differs between development and production environments. SQLite databases are created automatically on startup, while PostgreSQL databases require manual migration using Flask-Migrate. The run.py script handles both scenarios appropriately, providing clear instructions for PostgreSQL setup.

## Documentation Practices

Comprehensive documentation is maintained throughout the development process. System specification documents capture functional and non-functional requirements. Architecture documents describe the system design and component relationships. Flowcharts illustrate key processes and decision trees. User documentation provides installation instructions and usage guides.

All code includes docstrings following Google style conventions. Complex business logic includes inline comments explaining the rationale behind implementation decisions. The PPP (Pre-conditions, Post-conditions, Process) comment blocks document the algorithm for critical functions like production entry and payroll calculation.

## Quality Assurance

Code quality is maintained through several practices. Ruff is used for linting and formatting, ensuring consistent code style across the codebase. Type hints are used throughout the codebase to improve IDE support and catch potential errors early. The codebase achieves over 80% test coverage, with particular attention to critical business logic.

Code reviews are conducted for all changes, with particular attention to security implications. The principle of least privilege is applied throughout the system, with users having only the permissions necessary for their role. Sensitive operations require confirmation dialogs to prevent accidental actions.

## Continuous Improvement

The development methodology includes provisions for continuous improvement. Error handling is comprehensive, with user-friendly error messages displayed to users while detailed error information is logged for debugging. Performance is monitored, with database queries optimized to avoid N+1 query problems.

The system is designed to be extensible, with clear separation between business logic and presentation. New features can be added by creating new blueprints or extending existing ones. The wage calculation ADT can be extended to support additional worker groups or rate structures without modifying core business logic.

## Collaboration Practices

The project uses Git for version control, with a clear commit message convention. Branches are used for feature development, with pull requests required for merging to the main branch. The .gitignore file ensures that sensitive information like environment variables and database files are not committed to version control.

Documentation is kept up to date alongside code changes. When new features are added, corresponding documentation is updated to reflect the changes. This ensures that the documentation remains an accurate reflection of the system's capabilities and behavior.

# System Flowcharts

## User Authentication Flow

```mermaid
flowchart TD
    A[Start: User visits application] --> B{Is user authenticated?}
    B -->|No| C[Redirect to /auth/login]
    B -->|Yes| D[Check must_change_password]
    C --> E[Display login form]
    E --> F[User submits credentials]
    F --> G[Validate form data]
    G -->|Invalid| H[Display error message]
    H --> E
    G -->|Valid| I[Query user by username]
    I --> J{User exists?}
    J -->|No| K[Display generic error]
    K --> E
    J -->|Yes| L[Verify password with Argon2]
    L --> M{Password correct?}
    M -->|No| K
    M -->|Yes| N[Update last_login timestamp]
    N --> O[Create user session]
    O --> P{must_change_password?}
    P -->|Yes| Q[Redirect to /auth/change-password]
    P -->|No| R[Redirect to dashboard]
    Q --> S[Display password change form]
    S --> T[User submits new password]
    T --> U[Validate and update password]
    U --> V[Clear must_change_password flag]
    V --> R
    R --> W[End: User logged in]
```

## Daily Production Entry Flow

```mermaid
flowchart TD
    A[Start: Supervisor navigates to production] --> B{User authenticated?}
    B -->|No| C[Redirect to login]
    B -->|Yes| D{User has supervisor or admin role?}
    D -->|No| E[Return 403 Forbidden]
    D -->|Yes| F[Determine entry date]
    F --> G{User is admin?}
    G -->|Yes| H[Use date from query param or today]
    G -->|No| I[Use today's date]
    H --> J[Query all active employees]
    I --> J
    J --> K[Query existing records for date]
    K --> L[Render production entry form]
    L --> M[User enters carton counts]
    M --> N[Alpine.js calculates wages in real-time]
    N --> O[User submits form]
    O --> P[Begin database transaction]
    P --> Q[Initialize WageCalculator]
    Q --> R[For each employee]
    R --> S[Read cartons from form]
    S --> T{Valid integer and >= 0?}
    T -->|No| U[Add to errors list]
    T -->|Yes| V{Cartons == 0?}
    V -->|Yes| W[Skip this employee]
    V -->|No| X[Calculate daily wage]
    X --> Y{Record exists for date?}
    Y -->|Yes| Z[Update existing record]
    Y -->|No| AA[Insert new record]
    Z --> AB[Increment saved counter]
    AA --> AB
    W --> AB
    U --> AC{More employees?}
    AB --> AC
    AC -->|Yes| R
    AC -->|No| AD{Any errors?}
    AD -->|Yes| AE[Rollback transaction]
    AE --> AF[Flash error messages]
    AF --> AG[Re-render form]
    AD -->|No| AH[Commit transaction]
    AH --> AI[Flash success message]
    AI --> AJ[Redirect with PRG pattern]
    AJ --> AK[End: Production saved]
```

## Payroll View and Payment Recording Flow

```mermaid
flowchart TD
    A[Start: User navigates to payroll] --> B{User authenticated?}
    B -->|No| C[Redirect to login]
    B -->|Yes| D[Get month from query param]
    D --> E{Valid month format?}
    E -->|No| F[Use previous month]
    E -->|Yes| G[Parse month string]
    F --> H[Calculate first and last day]
    G --> H
    H --> I[Build aggregation query]
    I --> J[Execute single SQL with LEFT JOINs]
    J --> K[Process results]
    K --> L[Calculate balance per employee]
    L --> M[Compute grand totals]
    M --> N[Apply group filter if present]
    N --> O[Render payroll table]
    O --> P{User clicks Record Payment?}
    P -->|No| Q[End: Display payroll]
    P -->|Yes| R[Open payment modal]
    R --> S[Display payment form]
    S --> T[User enters payment details]
    T --> U[User submits form]
    U --> V[Validate payment amount > 0]
    V -->|Invalid| W[Display validation error]
    W --> S
    V -->|Valid| X[Create payment record]
    X --> Y[Save to database]
    Y --> Z[Flash success message]
    Z --> AA[Redirect to payroll with month]
    AA --> Q
```

## PDF Export Flow

```mermaid
flowchart TD
    A[Start: User clicks Export PDF] --> B{User authenticated?}
    B -->|No| C[Redirect to login]
    B -->|Yes| D[Get month and group filter]
    D --> E[Validate month format]
    E -->|Invalid| F[Return error]
    E -->|Valid| G[Call payroll aggregation helper]
    G --> H[Get payroll data]
    H --> I[Create BytesIO buffer]
    I --> J[Initialize SimpleDocTemplate]
    J --> K[Build story elements]
    K --> L[Add title and subtitle]
    L --> M[Add month and metadata]
    M --> N[Add horizontal rule]
    N --> O[Create table with 7 columns]
    O --> P[Add header row with styling]
    P --> Q[Add data rows with alternating colors]
    Q --> R[Add grand totals row]
    R --> S[Add signature blocks]
    S --> T[Add footer]
    T --> U[Call doc.build]
    U --> V[Seek buffer to start]
    V --> W[Create Flask response]
    W --> X[Set headers for download]
    X --> Y[Stream PDF to client]
    Y --> Z[End: PDF downloaded]
```

## Role-Based Access Control Decision Tree

```mermaid
flowchart TD
    A[HTTP Request] --> B{Route requires authentication?}
    B -->|No| C[Execute route handler]
    B -->|Yes| D{User authenticated?}
    D -->|No| E[Redirect to /auth/login]
    D -->|Yes| F{Route requires specific role?}
    F -->|No| C
    F -->|Yes| G{User role in allowed list?}
    G -->|No| H[Return 403 Forbidden]
    G -->|Yes| I{Additional role checks?}
    I -->|No| C
    I -->|Yes| J{User is admin?}
    J -->|Yes| C
    J -->|No| K{User is GM?}
    K -->|Yes| L{Route allows GM?}
    L -->|Yes| C
    L -->|No| H
    K -->|No| M{User is supervisor?}
    M -->|Yes| N{Route allows supervisor?}
    N -->|Yes| C
    N -->|No| H
    M -->|No| H

    subgraph Route Permissions
        O[/auth/login/] --> P[All users]
        Q[/auth/logout/] --> R[Authenticated users]
        S[/production/] --> T[Supervisor, Admin]
        U[/production/history/] --> V[Admin, GM]
        W[/employees/] --> X[Admin only]
        Y[/users/] --> Z[Admin only]
        AA[/payroll/] --> AB[All authenticated]
        AC[/reports/] --> AD[All authenticated]
    end

    C --> EE[End: Request processed]
    E --> EF[End: Redirect to login]
    H --> EG[End: Access denied]
```

## Employee Management Flow

```mermaid
flowchart TD
    A[Start: Admin navigates to employees] --> B{User authenticated?}
    B -->|No| C[Redirect to login]
    B -->|Yes| D{User has admin role?}
    D -->|No| E[Return 403 Forbidden]
    D -->|Yes| F[Query active employees]
    F --> G[Render employee list]
    G --> H{Admin action?}
    H -->|Add Employee| I[Display employee form]
    H -->|Edit Employee| J[Load employee data]
    H -->|Deactivate| K[Confirm deactivation]
    H -->|Hard Delete| L[Check for existing records]
    H -->|View Inactive| M[Query inactive employees]
    H -->|Reactivate| N[Confirm reactivation]

    I --> O[User submits form]
    O --> P[Validate name and group]
    P -->|Invalid| Q[Display errors]
    P -->|Valid| R[Create employee record]
    R --> S[Save to database]
    S --> T[Redirect to employee list]

    J --> AA[Pre-fill form with data]
    AA --> AB[User submits form]
    AB --> AC[Validate and update]
    AC --> S

    K --> AD[Set active = False]
    AD --> S

    L --> AE{Has production or payment records?}
    AE -->|Yes| AF[Display error: Cannot delete]
    AE -->|No| AG[Delete employee record]
    AG --> S

    M --> AH[Render inactive list]
    AH --> AI[Display reactivate buttons]

    N --> AJ[Set active = True]
    AJ --> S

    T --> AK[End: Employee updated]
    Q --> AK
    AF --> AK
    AI --> AK

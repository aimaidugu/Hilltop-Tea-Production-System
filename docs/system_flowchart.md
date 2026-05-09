# HILLTOP TEA — System Flowcharts

## User Authentication Flow

```mermaid
flowchart TD
    A[User Requests Protected Page] --> B{Is User Authenticated?}
    B -->|No| C[Redirect to /auth/login]
    B -->|Yes| D{Is must_change_password True?}
    D -->|Yes| E[Redirect to /auth/change-password]
    D -->|No| F[Check User Role]
    F --> G{Role Authorized?}
    G -->|No| H[Return HTTP 403 Forbidden]
    G -->|Yes| I[Execute Route Handler]
    I --> J[Render Response]
    C --> K[Display Login Form]
    K --> L[User Submits Credentials]
    L --> M[Validate Form]
    M -->|Invalid| K
    M -->|Valid| N[Query User by Username]
    N --> O{User Found?}
    O -->|No| P[Flash Generic Error]
    P --> K
    O -->|Yes| Q[Verify Password with Argon2]
    Q -->|Invalid| P
    Q -->|Valid| R[Update last_login Timestamp]
    R --> S[Create Session with Flask-Login]
    S --> T{must_change_password?}
    T -->|Yes| E
    T -->|No| U[Redirect to Dashboard]
    E --> V[Display Change Password Form]
    V --> W[User Submits New Password]
    W --> X[Validate Current Password]
    X -->|Invalid| V
    X -->|Valid| Y[Set New Password]
    Y --> Z[Clear must_change_password Flag]
    Z --> U
```

## Daily Production Entry Flow

```mermaid
flowchart TD
    A[Supervisor Navigates to Production Entry] --> B[Load Active Employees]
    B --> C[Query Existing Records for Today]
    C --> D[Render Form with Pre-filled Data]
    D --> E[Supervisor Enters Carton Counts]
    E --> F[Alpine.js Calculates Real-time Wages]
    F --> G[Supervisor Submits Form]
    G --> H[Initialize WageCalculator]
    H --> I[Begin Database Transaction]
    I --> J{More Employees?}
    J -->|Yes| K[Read cartons_<id> from Form]
    K --> L{Valid Integer?}
    L -->|No| M[Add Error to List]
    M --> J
    L -->|Yes| N{Cartons >= 0?}
    N -->|No| M
    N -->|Yes| O{Cartons == 0?}
    O -->|Yes| P[Skip This Employee]
    P --> J
    O -->|No| Q[Calculate Daily Wage]
    Q --> R{Record Exists?}
    R -->|Yes| S[Update Existing Record]
    R -->|No| T[Insert New Record]
    S --> U[Increment Saved Counter]
    T --> U
    U --> J
    J -->|No| V{Errors Present?}
    V -->|Yes| W[Rollback Transaction]
    W --> X[Flash Each Error]
    X --> Y[Re-render Form]
    V -->|No| Z[Commit Transaction]
    Z --> AA[Flash Success Message]
    AA --> AB[Redirect to Production Entry]
```

## Payroll View and Payment Recording Flow

```mermaid
flowchart TD
    A[User Requests Payroll Page] --> B[Parse Month Parameter]
    B --> C{Valid Month?}
    C -->|No| D[Use Previous Month]
    C -->|Yes| E[Use Specified Month]
    D --> F[Calculate First and Last Day]
    E --> F
    F --> G[Execute Single Aggregation Query]
    G --> H[LEFT JOIN Production Records]
    H --> I[LEFT JOIN Payments]
    I --> J[GROUP BY Employee]
    J --> K[Calculate Totals per Employee]
    K --> L{Group Filter Specified?}
    L -->|Yes| M[Filter by Group]
    L -->|No| N[Use All Employees]
    M --> O[Sort by Employee Name]
    N --> O
    O --> P[Calculate Grand Totals]
    P --> Q[Render Payroll Table]
    Q --> R[User Clicks Record Payment]
    R --> S[Open Payment Modal]
    S --> T[User Enters Payment Details]
    T --> U[User Submits Payment Form]
    U --> V[Validate Payment Amount > 0]
    V -->|Invalid| W[Flash Error]
    W --> S
    V -->|Valid| X[Create Payment Record]
    X --> Y[Link to Employee]
    Y --> Z[Link to Current User]
    Z --> AA[Save to Database]
    AA --> AB[Flash Success]
    AB --> AC[Redirect to Payroll with Month Preserved]
```

## PDF Export Flow

```mermaid
flowchart TD
    A[User Clicks Export PDF] --> B[Request /reports/wage-sheet]
    B --> C[Validate Month Parameter]
    C -->|Invalid| D[Return 400 Bad Request]
    C -->|Valid| E[Parse Month to Date Range]
    E --> F[Execute Payroll Aggregation Query]
    F --> G[Get Payroll Data]
    G --> H[Apply Group Filter if Specified]
    H --> I[Create BytesIO Buffer]
    I --> J[Initialize ReportLab Document]
    J --> K[Build PDF Story Elements]
    K --> L[Add Title and Subtitle]
    L --> M[Add Month and Metadata]
    M --> N[Add Horizontal Rule]
    N --> O[Build Data Table]
    O --> P[Add Header Row]
    P --> Q[Add Employee Data Rows]
    Q --> R[Add Grand Totals Row]
    R --> S[Add Signature Block]
    S --> T[Add Footer]
    T --> U[Call doc.build]
    U --> V[Seek Buffer to 0]
    V --> W[Create Flask Response]
    W --> X[Set Content-Type to PDF]
    X --> Y[Set Content-Disposition Header]
    Y --> Z[Stream PDF to Browser]
```

## Role-Based Access Control Decision Tree

```mermaid
flowchart TD
    A[HTTP Request] --> B{Route Protected?}
    B -->|No| C[Execute Handler]
    B -->|Yes| D{@login_required Decorator}
    D --> E{User Authenticated?}
    E -->|No| F[Redirect to /auth/login]
    E -->|Yes| G{@require_role Decorator}
    G --> H{User Role in Allowed Roles?}
    H -->|No| I[Return HTTP 403]
    H -->|Yes| J{Specific Route Check}
    J --> K{/auth/login|/auth/logout|/auth/change-password}
    K -->|Yes| L[All Authenticated Users]
    J --> M{/production/}
    M -->|Yes| N{Role in supervisor, admin?}
    N -->|Yes| O[Execute Handler]
    N -->|No| I
    J --> P{/production/history}
    P -->|Yes| Q{Role in admin, gm?}
    Q -->|Yes| O
    Q -->|No| I
    J --> R{/employees/*}
    R -->|Yes| S{Role == admin?}
    S -->|Yes| O
    S -->|No| I
    J --> T{/users/*}
    T -->|Yes| S
    J --> U{/payroll/*|/reports/*|/}
    U -->|Yes| L
    C --> V[Render Response]
    O --> V
    I --> W[Render 403 Template]
    F --> X[Render Login Template]

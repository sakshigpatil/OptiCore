# Entity-Relationship Diagram (ERD)

## Database Schema Design

```mermaid
erDiagram
    User {
        int id PK
        string username UK
        string email UK
        string password
        string first_name
        string last_name
        string role
        datetime date_joined
        boolean is_active
        boolean is_staff
    }
    
    Employee {
        int id PK
        int user_id FK
        string employee_id UK
        string phone
        text address
        date date_of_birth
        date hire_date
        date termination_date
        string position
        decimal salary
        int department_id FK
        int manager_id FK
        string profile_picture
        string status
        datetime created_at
        datetime updated_at
    }
    
    Department {
        int id PK
        string name UK
        text description
        int head_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    Project {
        int id PK
        string name
        text description
        date start_date
        date end_date
        string status
        int manager_id FK
        datetime created_at
        datetime updated_at
    }
    
    Task {
        int id PK
        string title
        text description
        int project_id FK
        int assigned_to_id FK
        int created_by_id FK
        string priority
        string status
        date due_date
        datetime created_at
        datetime updated_at
    }
    
    Attendance {
        int id PK
        int employee_id FK
        date date
        time clock_in
        time clock_out
        decimal hours_worked
        string status
        text notes
        datetime created_at
    }
    
    LeaveRequest {
        int id PK
        int employee_id FK
        string leave_type
        date start_date
        date end_date
        int days_requested
        text reason
        string status
        int approved_by_id FK
        text rejection_reason
        datetime created_at
        datetime updated_at
    }
    
    ResignationRequest {
        int id PK
        int employee_id FK
        date resignation_date
        date last_working_day
        text reason
        string status
        int approved_by_id FK
        text rejection_reason
        datetime created_at
        datetime updated_at
    }
    
    PayrollRecord {
        int id PK
        int employee_id FK
        decimal base_salary
        decimal overtime_pay
        decimal bonuses
        decimal deductions
        decimal net_salary
        date pay_period_start
        date pay_period_end
        date pay_date
        string status
        datetime created_at
    }
    
    Notification {
        int id PK
        int recipient_id FK
        string title
        text message
        string type
        boolean is_read
        datetime created_at
    }
    
    ProjectEmployee {
        int id PK
        int project_id FK
        int employee_id FK
        date assigned_date
        boolean is_active
    }

    %% Relationships
    User ||--|| Employee : "has profile"
    Employee }|--|| Department : "belongs to"
    Employee ||--o{ Employee : "manages"
    Department ||--o| Employee : "headed by"
    
    Project ||--o{ Task : "contains"
    Project }|--|| Employee : "managed by"
    Project ||--o{ ProjectEmployee : "has members"
    Employee ||--o{ ProjectEmployee : "assigned to"
    
    Employee ||--|| Task : "assigned"
    Employee ||--|| Task : "created by"
    
    Employee ||--o{ Attendance : "records"
    Employee ||--o{ LeaveRequest : "submits"
    Employee ||--o{ ResignationRequest : "submits"
    Employee ||--o{ PayrollRecord : "receives"
    Employee ||--o{ Notification : "receives"
    
    Employee ||--o{ LeaveRequest : "approves"
    Employee ||--o{ ResignationRequest : "approves"
```

## Key Relationships

### User & Employee
- One-to-One relationship
- Employee extends User model with HR-specific fields
- User handles authentication, Employee handles business logic

### Department Structure
- Employees belong to departments
- Departments have heads (employees)
- Hierarchical structure support

### Project & Task Management
- Projects contain multiple tasks
- Projects have managers (employees)
- Many-to-many relationship between projects and employees
- Tasks assigned to specific employees

### Attendance System
- Daily attendance records per employee
- Clock-in/clock-out functionality
- Automatic hours calculation

### Leave & Resignation Management
- Employees submit requests
- HR/Managers approve/reject requests
- Status tracking and audit trail

### Payroll System
- Monthly/bi-weekly payroll records
- Salary calculations with overtime and deductions
- Payment history tracking

## Indexes and Performance

```sql
-- Key indexes for performance
CREATE INDEX idx_employee_user_id ON employees_employee(user_id);
CREATE INDEX idx_employee_department ON employees_employee(department_id);
CREATE INDEX idx_attendance_employee_date ON attendance_attendance(employee_id, date);
CREATE INDEX idx_task_assigned_to ON projects_task(assigned_to_id);
CREATE INDEX idx_leave_employee_status ON leaves_leaverequest(employee_id, status);
CREATE INDEX idx_notification_recipient ON notifications_notification(recipient_id, is_read);
```
# System Architecture Diagram

## High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React App]
        A1[HR Dashboard]
        A2[Employee Dashboard]
        A3[Authentication]
        A4[Redux Store]
    end
    
    subgraph "Backend Layer"
        B[Django API Server]
        B1[Authentication Service]
        B2[Employee Service]
        B3[Attendance Service]
        B4[Leave Service]
        B5[Payroll Service]
    end
    
    subgraph "Data Layer"
        C[(PostgreSQL Database)]
        C1[User Tables]
        C2[Employee Tables]
        C3[Business Logic Tables]
    end
    
    A --> B
    A1 --> B
    A2 --> B
    A3 --> B1
    B --> C
    B1 --> C1
    B2 --> C2
    B3 --> C3
    B4 --> C3
    B5 --> C3
```

## Component Architecture

### Frontend Components
```
src/
├── components/
│   ├── common/          # Reusable components
│   ├── layout/          # Layout components
│   ├── hr/             # HR-specific components
│   └── employee/       # Employee-specific components
├── pages/              # Page components
├── store/              # Redux store
├── services/           # API services
└── utils/              # Utility functions
```

### Backend Services
```
apps/
├── authentication/     # JWT auth, permissions
├── employees/         # Employee management
├── departments/       # Department management
├── attendance/        # Attendance tracking
├── leaves/           # Leave management
├── payroll/          # Payroll system
└── notifications/    # Notification system
```

## Data Flow

1. **Authentication Flow:**
   - User login → JWT token generation
   - Token-based API requests
   - Role-based access control

2. **CRUD Operations:**
   - Frontend forms → API calls → Database operations
   - Real-time updates via WebSocket (optional)

3. **File Uploads:**
   - Profile pictures, documents → Django media handling
   - Cloud storage integration (AWS S3/Cloudinary)

## Security Architecture

- JWT token authentication
- Role-based permissions (HR/Manager/Employee)
- CORS configuration
- Input validation and sanitization
- Rate limiting and throttling
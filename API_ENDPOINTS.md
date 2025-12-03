# API Endpoints Documentation

## Base URL
- Development: `http://localhost:8000/api/v1/`
- Production: `https://your-api-domain.com/api/v1/`

## Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/login/` | User login | No |
| POST | `/auth/logout/` | User logout | Yes |
| POST | `/auth/refresh/` | Refresh JWT token | No |
| POST | `/auth/register/` | User registration (optional) | No |
| POST | `/auth/password/change/` | Change password | Yes |
| POST | `/auth/password/reset/` | Request password reset | No |
| POST | `/auth/password/reset/confirm/` | Confirm password reset | No |

## User Management Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
|--------|----------|-------------|---------------|-------------|
| GET | `/auth/user/` | Get current user profile | Yes | Any |
| PUT | `/auth/user/` | Update user profile | Yes | Own profile |
| GET | `/auth/users/` | List all users | Yes | HR/Admin |
| POST | `/auth/users/` | Create new user | Yes | HR/Admin |
| GET | `/auth/users/{id}/` | Get user by ID | Yes | HR/Admin |
| PUT | `/auth/users/{id}/` | Update user | Yes | HR/Admin |
| DELETE | `/auth/users/{id}/` | Delete user | Yes | HR/Admin |

## Employee Management Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
|--------|----------|-------------|---------------|-------------|
| GET | `/employees/` | List employees | Yes | HR/Manager |
| POST | `/employees/` | Create employee | Yes | HR/Admin |
| GET | `/employees/{id}/` | Get employee details | Yes | HR/Manager/Self |
| PUT | `/employees/{id}/` | Update employee | Yes | HR/Admin/Self (limited) |
| DELETE | `/employees/{id}/` | Delete employee | Yes | HR/Admin |
| GET | `/employees/me/` | Get own employee profile | Yes | Any |
| PUT | `/employees/me/` | Update own profile | Yes | Any |
| POST | `/employees/{id}/terminate/` | Terminate employee | Yes | HR/Admin |

## Department Management Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
|--------|----------|-------------|---------------|-------------|
| GET | `/departments/` | List departments | Yes | Any |
| POST | `/departments/` | Create department | Yes | HR/Admin |
| GET | `/departments/{id}/` | Get department details | Yes | Any |
| PUT | `/departments/{id}/` | Update department | Yes | HR/Admin |
| DELETE | `/departments/{id}/` | Delete department | Yes | HR/Admin |
| GET | `/departments/{id}/employees/` | Get department employees | Yes | HR/Manager |

## Project Management Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
|--------|----------|-------------|---------------|-------------|
| GET | `/projects/` | List projects | Yes | Any |
| POST | `/projects/` | Create project | Yes | HR/Manager |
| GET | `/projects/{id}/` | Get project details | Yes | Team members |
| PUT | `/projects/{id}/` | Update project | Yes | Project manager |
| DELETE | `/projects/{id}/` | Delete project | Yes | HR/Admin |
| GET | `/projects/my/` | Get user's projects | Yes | Any |
| POST | `/projects/{id}/members/` | Add team member | Yes | Project manager |
| DELETE | `/projects/{id}/members/{user_id}/` | Remove team member | Yes | Project manager |

## Task Management Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
|--------|----------|-------------|---------------|-------------|
| GET | `/tasks/` | List tasks | Yes | Any |
| POST | `/tasks/` | Create task | Yes | HR/Manager |
| GET | `/tasks/{id}/` | Get task details | Yes | Assigned user/Manager |
| PUT | `/tasks/{id}/` | Update task | Yes | Assigned user/Manager |
| DELETE | `/tasks/{id}/` | Delete task | Yes | HR/Manager |
| GET | `/tasks/my/` | Get user's assigned tasks | Yes | Any |
| PUT | `/tasks/{id}/status/` | Update task status | Yes | Assigned user |

## Attendance Management Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
|--------|----------|-------------|---------------|-------------|
| GET | `/attendance/` | List attendance records | Yes | HR/Manager |
| POST | `/attendance/clock-in/` | Clock in | Yes | Employee |
| POST | `/attendance/clock-out/` | Clock out | Yes | Employee |
| GET | `/attendance/my/` | Get own attendance | Yes | Any |
| GET | `/attendance/{id}/` | Get attendance record | Yes | HR/Manager/Self |
| PUT | `/attendance/{id}/` | Update attendance | Yes | HR/Manager |
| DELETE | `/attendance/{id}/` | Delete attendance | Yes | HR/Admin |
| GET | `/attendance/report/` | Attendance report | Yes | HR/Manager |

## Leave Management Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
|--------|----------|-------------|---------------|-------------|
| GET | `/leaves/` | List leave requests | Yes | HR/Manager |
| POST | `/leaves/` | Apply for leave | Yes | Employee |
| GET | `/leaves/{id}/` | Get leave details | Yes | HR/Manager/Self |
| PUT | `/leaves/{id}/` | Update leave request | Yes | Self (if pending) |
| DELETE | `/leaves/{id}/` | Cancel leave request | Yes | Self (if pending) |
| POST | `/leaves/{id}/approve/` | Approve leave | Yes | HR/Manager |
| POST | `/leaves/{id}/reject/` | Reject leave | Yes | HR/Manager |
| GET | `/leaves/my/` | Get own leave requests | Yes | Any |
| GET | `/leaves/balance/` | Get leave balance | Yes | HR/Manager/Self |

## Resignation Management Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
|--------|----------|-------------|---------------|-------------|
| GET | `/resignations/` | List resignation requests | Yes | HR/Admin |
| POST | `/resignations/` | Submit resignation | Yes | Employee |
| GET | `/resignations/{id}/` | Get resignation details | Yes | HR/Admin/Self |
| PUT | `/resignations/{id}/` | Update resignation | Yes | Self (if pending) |
| POST | `/resignations/{id}/approve/` | Approve resignation | Yes | HR/Admin |
| POST | `/resignations/{id}/reject/` | Reject resignation | Yes | HR/Admin |
| GET | `/resignations/my/` | Get own resignations | Yes | Any |

## Payroll Management Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
|--------|----------|-------------|---------------|-------------|
| GET | `/payroll/` | List payroll records | Yes | HR/Admin |
| POST | `/payroll/` | Create payroll record | Yes | HR/Admin |
| GET | `/payroll/{id}/` | Get payroll details | Yes | HR/Admin/Self |
| PUT | `/payroll/{id}/` | Update payroll | Yes | HR/Admin |
| DELETE | `/payroll/{id}/` | Delete payroll | Yes | HR/Admin |
| GET | `/payroll/my/` | Get own payroll records | Yes | Any |
| GET | `/payroll/{id}/payslip/` | Generate payslip | Yes | HR/Admin/Self |
| POST | `/payroll/generate/` | Generate monthly payroll | Yes | HR/Admin |

## Notification Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
|--------|----------|-------------|---------------|-------------|
| GET | `/notifications/` | List notifications | Yes | Any |
| GET | `/notifications/{id}/` | Get notification details | Yes | Recipient |
| PUT | `/notifications/{id}/read/` | Mark as read | Yes | Recipient |
| PUT | `/notifications/read-all/` | Mark all as read | Yes | Any |
| DELETE | `/notifications/{id}/` | Delete notification | Yes | Recipient |
| GET | `/notifications/unread-count/` | Get unread count | Yes | Any |

## Dashboard & Analytics Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
|--------|----------|-------------|---------------|-------------|
| GET | `/dashboard/hr/` | HR dashboard data | Yes | HR/Admin |
| GET | `/dashboard/employee/` | Employee dashboard data | Yes | Employee |
| GET | `/analytics/employees/` | Employee analytics | Yes | HR/Manager |
| GET | `/analytics/attendance/` | Attendance analytics | Yes | HR/Manager |
| GET | `/analytics/leaves/` | Leave analytics | Yes | HR/Manager |
| GET | `/analytics/projects/` | Project analytics | Yes | HR/Manager |

## File Upload Endpoints

| Method | Endpoint | Description | Auth Required | Permissions |
|--------|----------|-------------|---------------|-------------|
| POST | `/upload/profile-picture/` | Upload profile picture | Yes | Self |
| POST | `/upload/documents/` | Upload documents | Yes | HR/Self |
| GET | `/upload/{file_id}/` | Download file | Yes | Owner/HR |
| DELETE | `/upload/{file_id}/` | Delete file | Yes | Owner/HR |

## Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Success message",
  "pagination": {
    "count": 100,
    "next": "http://api/endpoint/?page=2",
    "previous": null,
    "page_size": 10
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field_name": ["Error message"]
    }
  }
}
```

## HTTP Status Codes

- `200` - OK (successful GET, PUT)
- `201` - Created (successful POST)
- `204` - No Content (successful DELETE)
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error (server error)

## Rate Limiting

- Authentication endpoints: 5 requests per minute
- General endpoints: 100 requests per minute
- File upload endpoints: 10 requests per minute

## Pagination

All list endpoints support pagination with the following parameters:
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10, max: 100)

## Filtering & Searching

Most list endpoints support:
- `search` - General search across relevant fields
- `ordering` - Sort by field (prefix with `-` for descending)
- Field-specific filters (varies by endpoint)
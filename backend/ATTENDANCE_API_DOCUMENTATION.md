# Attendance Module API Documentation

## Overview
The Attendance module provides comprehensive clock-in/clock-out functionality with working hours calculation, attendance history, and statistics tracking.

## Models

### AttendanceRecord
Core model for tracking employee attendance with the following fields:
- `employee` (ForeignKey): Reference to Employee
- `date` (DateField): Attendance date
- `clock_in_time` (DateTimeField): Clock-in timestamp
- `clock_out_time` (DateTimeField): Clock-out timestamp
- `total_hours` (DecimalField): Total working hours
- `break_duration` (DecimalField): Break duration in hours
- `status` (CharField): PRESENT, ABSENT, LATE, PARTIAL, OVERTIME, etc.
- `notes` (TextField): Additional notes
- `location` (CharField): Clock-in/out location
- `ip_address` (GenericIPAddressField): IP address for tracking
- `is_overtime` (BooleanField): Overtime flag
- `overtime_hours` (DecimalField): Overtime hours

### AttendanceSettings
Global settings for attendance system:
- `standard_work_hours`: Standard work hours per day (default: 8.00)
- `late_threshold_minutes`: Late threshold in minutes (default: 15)
- `overtime_threshold_hours`: Overtime threshold (default: 8.00)
- `standard_start_time`: Standard work start time (default: 09:00)
- `standard_end_time`: Standard work end time (default: 17:00)

## API Endpoints

### Base URL: `/api/v1/attendance/`

### 1. List/Create Attendance Records
**GET** `/api/v1/attendance/`
- Returns paginated list of attendance records
- Supports filtering by date, employee, status
- Supports search by employee name/ID

**POST** `/api/v1/attendance/`
- Create new attendance record manually

### 2. Clock In
**POST** `/api/v1/attendance/clock-in/`

**Request Body:**
```json
{
  "employee": 1,
  "timestamp": "2025-12-03T09:00:00Z",  // optional
  "location": "Office Building A",       // optional
  "notes": "Started early today"         // optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully clocked in",
  "data": {
    "id": 1,
    "employee": 1,
    "employee_name": "John Doe",
    "employee_id": "EMP001",
    "date": "2025-12-03",
    "clock_in_time": "2025-12-03T09:00:00Z",
    "clock_out_time": null,
    "is_clocked_in": true,
    "status": "PRESENT",
    "location": "Office Building A"
  }
}
```

### 3. Clock Out
**POST** `/api/v1/attendance/clock-out/`

**Request Body:**
```json
{
  "employee": 1,
  "timestamp": "2025-12-03T17:30:00Z",  // optional
  "location": "Office Building A",       // optional
  "break_duration": 1.0,                // optional, in hours
  "notes": "Completed all tasks"        // optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully clocked out",
  "data": {
    "id": 1,
    "employee": 1,
    "employee_name": "John Doe",
    "date": "2025-12-03",
    "clock_in_time": "2025-12-03T09:00:00Z",
    "clock_out_time": "2025-12-03T17:30:00Z",
    "total_hours": 7.50,
    "is_clocked_in": false,
    "status": "PRESENT"
  }
}
```

### 4. Current Status
**GET** `/api/v1/attendance/current-status/?employee_id=1`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "is_clocked_in": true,
    "clock_in_time": "2025-12-03T09:00:00Z",
    "working_duration": 2.5,
    "status": "PRESENT"
  }
}
```

### 5. Attendance History
**GET** `/api/v1/attendance/history/`

**Query Parameters:**
- `employee_id`: Filter by employee ID
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `page`: Page number for pagination

**Response:**
```json
{
  "success": true,
  "count": 25,
  "next": "http://localhost:8000/api/v1/attendance/history/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "date": "2025-12-03",
      "employee_name": "John Doe",
      "employee_id": "EMP001",
      "department": "IT",
      "clock_in_time": "2025-12-03T09:00:00Z",
      "clock_out_time": "2025-12-03T17:30:00Z",
      "total_hours": 7.50,
      "status": "PRESENT",
      "is_overtime": false,
      "overtime_hours": 0
    }
  ]
}
```

### 6. Attendance Statistics
**GET** `/api/v1/attendance/stats/`

**Query Parameters:**
- `employee_id`: Filter by employee ID
- `start_date`: Start date (defaults to current month start)
- `end_date`: End date (defaults to current month end)

**Response:**
```json
{
  "success": true,
  "data": {
    "total_days": 20,
    "present_days": 18,
    "absent_days": 2,
    "late_days": 3,
    "total_hours": 144.00,
    "average_hours": 8.00,
    "overtime_hours": 12.50,
    "attendance_percentage": 90.00
  }
}
```

### 7. Today's Summary
**GET** `/api/v1/attendance/today-summary/`

**Response:**
```json
{
  "success": true,
  "data": {
    "date": "2025-12-03",
    "total_employees": 5,
    "present_count": 4,
    "currently_clocked_in": 3,
    "absent_count": 1,
    "recent_clock_ins": [
      {
        "employee_name": "John Doe",
        "employee_id": "EMP001",
        "clock_in_time": "2025-12-03T09:15:00Z"
      }
    ]
  }
}
```

### 8. Attendance Settings
**GET** `/api/v1/attendance-settings/current/`

**Response:**
```json
{
  "success": true,
  "data": {
    "standard_work_hours": 8.00,
    "late_threshold_minutes": 15,
    "overtime_threshold_hours": 8.00,
    "standard_start_time": "09:00:00",
    "standard_end_time": "17:00:00",
    "allow_early_clock_in_minutes": 30,
    "max_break_duration_hours": 1.00
  }
}
```

## Model Methods

### AttendanceRecord Methods

#### Properties:
- `is_clocked_in`: Returns True if employee is currently clocked in
- `working_duration`: Calculates current working hours (excluding breaks)

#### Methods:
- `clock_in(timestamp, location, ip_address)`: Clock in employee
- `clock_out(timestamp, location)`: Clock out employee
- `calculate_total_hours()`: Calculate and save total working hours

## Status Values

- **PRESENT**: Full day attendance (≥8 hours)
- **ABSENT**: No attendance or very short duration
- **LATE**: Arrived after standard start time + threshold
- **PARTIAL**: Partial day (4-8 hours)
- **OVERTIME**: More than standard working hours
- **HALF_DAY**: Exactly half day attendance
- **EARLY_OUT**: Left before completing standard hours

## Error Handling

### Common Error Responses:

**400 Bad Request:**
```json
{
  "success": false,
  "message": "Employee is already clocked in",
  "errors": {}
}
```

**404 Not Found:**
```json
{
  "success": false,
  "message": "Employee not found"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Usage Examples

### Frontend Integration Example:

```javascript
// Clock In
const clockIn = async (employeeId) => {
  const response = await fetch('/api/v1/attendance/clock-in/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      employee: employeeId,
      location: 'Main Office'
    })
  });
  
  const data = await response.json();
  if (data.success) {
    console.log('Clocked in successfully:', data.data);
  }
};

// Get Current Status
const getCurrentStatus = async (employeeId) => {
  const response = await fetch(`/api/v1/attendance/current-status/?employee_id=${employeeId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  return data.data;
};

// Get Monthly Stats
const getMonthlyStats = async (employeeId) => {
  const response = await fetch(`/api/v1/attendance/stats/?employee_id=${employeeId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  return data.data;
};
```

## Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Permissions
- **Employees**: Can view their own attendance records and clock in/out
- **HR/Managers**: Can view all attendance records and manage settings
- **Admin**: Full access to all attendance functionality

## Database Indexes
The model includes optimized indexes for:
- Employee + Date lookups
- Date range queries  
- Status filtering

This ensures fast query performance even with large attendance datasets.
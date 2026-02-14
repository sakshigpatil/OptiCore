#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, time, date, timedelta

# Add the project directory to Python path
sys.path.append('/home/sakshi/vsCode/MajorProject/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.employees.models import Employee
from apps.attendance.models import AttendanceRecord
from django.utils import timezone

User = get_user_model()

def create_attendance_data():
    print("Creating sample attendance data...")
    
    # Get all employees
    employees = Employee.objects.all()[:4]  # Get first 4 employees
    
    today = date.today()
    
    # Sample attendance data
    attendance_data = [
        {
            'clock_in': '09:15',
            'clock_out': '18:30',
            'status': 'PRESENT'
        },
        {
            'clock_in': '09:00',
            'clock_out': '17:45',
            'status': 'PRESENT'
        },
        {
            'clock_in': '09:30',
            'clock_out': '18:15',
            'status': 'LATE'
        },
        {
            'clock_in': '09:00',
            'clock_out': '18:00',
            'status': 'PRESENT'
        }
    ]
    
    for i, employee in enumerate(employees):
        if i >= len(attendance_data):
            break
            
        data = attendance_data[i]
        
        # Parse times
        clock_in_time = datetime.combine(today, datetime.strptime(data['clock_in'], '%H:%M').time())
        clock_out_time = datetime.combine(today, datetime.strptime(data['clock_out'], '%H:%M').time())
        
        # Make timezone aware
        clock_in_time = timezone.make_aware(clock_in_time)
        clock_out_time = timezone.make_aware(clock_out_time)
        
        # Calculate hours
        duration = clock_out_time - clock_in_time
        hours = duration.total_seconds() / 3600
        
        # Create or update attendance record
        attendance, created = AttendanceRecord.objects.update_or_create(
            employee=employee,
            date=today,
            defaults={
                'clock_in_time': clock_in_time,
                'clock_out_time': clock_out_time,
                'total_hours': hours,
                'status': data['status']
            }
        )
        
        action = "Created" if created else "Updated"
        print(f"{action} attendance for {employee.user.get_full_name()}: {data['clock_in']} - {data['clock_out']} ({hours:.2f}h)")
    
    # Add one absent employee (no attendance record means absent)
    print(f"\nTotal attendance records for today: {AttendanceRecord.objects.filter(date=today).count()}")
    
    # Show summary
    present = AttendanceRecord.objects.filter(date=today, status__in=['PRESENT', 'LATE']).count()
    late = AttendanceRecord.objects.filter(date=today, status='LATE').count()
    absent = Employee.objects.count() - AttendanceRecord.objects.filter(date=today).count()
    
    print(f"Summary: {present} Present, {absent} Absent, {late} Late")

if __name__ == "__main__":
    create_attendance_data()
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime, time, timedelta
from apps.employees.models import Employee


class AttendanceRecord(models.Model):
    """Attendance record model for employee clock-in/clock-out tracking"""
    
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('PARTIAL', 'Partial Day'),
        ('OVERTIME', 'Overtime'),
        ('HALF_DAY', 'Half Day'),
        ('EARLY_OUT', 'Early Out'),
    ]
    
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='attendance_records'
    )
    date = models.DateField()
    clock_in_time = models.DateTimeField(null=True, blank=True)
    clock_out_time = models.DateTimeField(null=True, blank=True)
    total_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    break_duration = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Break duration in hours"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABSENT')
    notes = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_overtime = models.BooleanField(default=False)
    overtime_hours = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date', '-clock_in_time']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.date}"
    
    @property
    def is_clocked_in(self):
        """Check if employee is currently clocked in"""
        return self.clock_in_time is not None and self.clock_out_time is None
    
    @property
    def working_duration(self):
        """Calculate working duration in hours"""
        if not self.clock_in_time:
            return 0
        
        end_time = self.clock_out_time or timezone.now()
        duration = end_time - self.clock_in_time
        hours = duration.total_seconds() / 3600
        return max(0, hours - float(self.break_duration))
    
    def calculate_total_hours(self):
        """Calculate and update total working hours"""
        if self.clock_in_time and self.clock_out_time:
            self.total_hours = self.working_duration
            self.save(update_fields=['total_hours'])
        return self.total_hours
    
    def clock_in(self, timestamp=None, location=None, ip_address=None):
        """Clock in the employee"""
        if self.is_clocked_in:
            raise ValueError("Employee is already clocked in")
        
        # If employee had completed work day and wants to clock in again,
        # reset the record for a new session
        if self.clock_in_time and self.clock_out_time:
            self.clock_out_time = None  # Clear previous clock out
            self.total_hours = None
            self.overtime_hours = 0  # Reset to 0, not None (field doesn't allow NULL)
        
        self.clock_in_time = timestamp or timezone.now()
        self.location = location
        self.ip_address = ip_address
        self.status = 'PRESENT'
        self.save()
        return self
    
    def clock_out(self, timestamp=None, location=None):
        """Clock out the employee"""
        if not self.is_clocked_in:
            raise ValueError("Employee is not clocked in")
        
        self.clock_out_time = timestamp or timezone.now()
        if location:
            self.location = location
        
        # Calculate total hours
        self.calculate_total_hours()
        
        # Determine status based on working hours
        if self.total_hours >= 8:
            self.status = 'PRESENT'
            if self.total_hours > 8:
                self.is_overtime = True
                self.overtime_hours = self.total_hours - 8
        elif self.total_hours >= 4:
            self.status = 'PARTIAL'
        else:
            self.status = 'ABSENT'
        
        self.save()
        return self
    
    def save(self, *args, **kwargs):
        # Auto-calculate total hours if both times are set
        if self.clock_in_time and self.clock_out_time and not self.total_hours:
            duration = self.clock_out_time - self.clock_in_time
            hours = duration.total_seconds() / 3600
            self.total_hours = max(0, hours - float(self.break_duration))
        
        # Set status and overtime based on total hours
        if self.total_hours:
            if self.total_hours >= 8:
                self.status = 'PRESENT'
                if self.total_hours > 8:
                    self.is_overtime = True
                    self.overtime_hours = self.total_hours - 8
            elif self.total_hours >= 4:
                self.status = 'HALF_DAY'
            else:
                self.status = 'EARLY_OUT'
        elif self.clock_in_time and not self.clock_out_time:
            self.status = 'PRESENT'
        
        super().save(*args, **kwargs)


class AttendanceSettings(models.Model):
    """Global attendance settings"""
    
    standard_work_hours = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=8.00,
        help_text="Standard work hours per day"
    )
    late_threshold_minutes = models.IntegerField(
        default=15,
        help_text="Minutes after which arrival is considered late"
    )
    overtime_threshold_hours = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=8.00,
        help_text="Hours after which overtime starts"
    )
    standard_start_time = models.TimeField(
        default='09:00:00',
        help_text="Standard work start time"
    )
    standard_end_time = models.TimeField(
        default='17:00:00', 
        help_text="Standard work end time"
    )
    allow_early_clock_in_minutes = models.IntegerField(
        default=30,
        help_text="Minutes before standard time employees can clock in"
    )
    max_break_duration_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.00,
        help_text="Maximum break duration per day in hours"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Attendance Settings"
        verbose_name_plural = "Attendance Settings"
    
    def __str__(self):
        return f"Attendance Settings (Updated: {self.updated_at.date()})"
    
    @classmethod
    def get_settings(cls):
        """Get or create attendance settings singleton"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


# Keep the old Attendance model for backward compatibility
class Attendance(AttendanceRecord):
    """Backward compatibility alias"""
    class Meta:
        proxy = True
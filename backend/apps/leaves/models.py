from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.employees.models import Employee


class LeaveType(models.Model):
    """Leave type model"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    days_allowed_per_year = models.IntegerField(validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    """Leave request model"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.IntegerField(validators=[MinValueValidator(1)])
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_leaves'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    applied_on = models.DateTimeField(auto_now_add=True)
    processed_on = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.leave_type.name} ({self.start_date} to {self.end_date})"


class ResignationRequest(models.Model):
    """Resignation request model"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='resignation_requests')
    resignation_date = models.DateField()
    last_working_day = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_resignations'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    submitted_on = models.DateTimeField(auto_now_add=True)
    processed_on = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - Resignation ({self.resignation_date})"
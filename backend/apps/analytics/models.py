from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ScheduledReport(models.Model):
    """Scheduled report configuration."""

    REPORT_TYPE_CHOICES = [
        ('employees', 'Employees'),
        ('attendance', 'Attendance'),
    ]

    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
    ]

    SCHEDULE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_reports')
    name = models.CharField(max_length=120)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    file_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='csv')

    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_CHOICES, default='weekly')
    day_of_week = models.PositiveSmallIntegerField(null=True, blank=True)  # 0=Mon .. 6=Sun
    day_of_month = models.PositiveSmallIntegerField(null=True, blank=True)  # 1..28/31
    time_of_day = models.TimeField(default=timezone.datetime(2000, 1, 1, 9, 0).time())

    is_active = models.BooleanField(default=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=20, default='pending')
    last_message = models.TextField(blank=True, null=True)
    last_report_file = models.FileField(upload_to='reports/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.report_type})"

    def compute_next_run(self, from_time=None):
        """Compute the next run timestamp based on schedule settings."""
        now = from_time or timezone.now()
        base_date = now.date()

        if self.schedule_type == 'daily':
            candidate = timezone.make_aware(
                timezone.datetime.combine(base_date, self.time_of_day)
            )
            if candidate <= now:
                candidate += timezone.timedelta(days=1)
            return candidate

        if self.schedule_type == 'weekly':
            target_dow = self.day_of_week if self.day_of_week is not None else 0
            days_ahead = (target_dow - base_date.weekday()) % 7
            candidate_date = base_date + timezone.timedelta(days=days_ahead)
            candidate = timezone.make_aware(
                timezone.datetime.combine(candidate_date, self.time_of_day)
            )
            if candidate <= now:
                candidate += timezone.timedelta(days=7)
            return candidate

        if self.schedule_type == 'monthly':
            target_dom = self.day_of_month if self.day_of_month is not None else 1
            candidate_date = base_date.replace(day=min(target_dom, 28))
            candidate = timezone.make_aware(
                timezone.datetime.combine(candidate_date, self.time_of_day)
            )
            if candidate <= now:
                next_month = (base_date.month % 12) + 1
                next_year = base_date.year + (1 if next_month == 1 else 0)
                candidate_date = candidate_date.replace(year=next_year, month=next_month)
                candidate = timezone.make_aware(
                    timezone.datetime.combine(candidate_date, self.time_of_day)
                )
            return candidate

        return None

    def save(self, *args, **kwargs):
        if not self.next_run_at and self.is_active:
            self.next_run_at = self.compute_next_run()
        super().save(*args, **kwargs)

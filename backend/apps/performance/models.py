from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Goal(models.Model):
    STATUS = [('OPEN', 'Open'), ('IN_PROGRESS', 'In Progress'), ('ACHIEVED', 'Achieved'), ('CLOSED', 'Closed')]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    progress_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit = models.CharField(max_length=50, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def progress_percent(self):
        try:
            return (self.progress_value / self.target_value) * 100 if self.target_value else 0
        except Exception:
            return 0

    def __str__(self):
        return f"{self.owner} - {self.title}"


class Review(models.Model):
    REVIEW_TYPE = [('SELF', 'Self'), ('MANAGER', 'Manager'), ('PEER', 'Peer'), ('360', '360')]
    STATUS = [('DRAFT', 'Draft'), ('SUBMITTED', 'Submitted'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='given_reviews')
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPE, default='MANAGER')
    period_start = models.DateField()
    period_end = models.DateField()
    summary = models.TextField(blank=True)
    overall_rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='DRAFT')
    submitted_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('employee', 'reviewer', 'period_start', 'period_end', 'review_type')

    def submit(self):
        self.status = 'SUBMITTED'
        self.submitted_at = timezone.now()
        self.save()

    def approve(self, approver=None):
        self.status = 'APPROVED'
        self.processed_at = timezone.now()
        self.save()

    def reject(self, reason=None):
        self.status = 'REJECTED'
        self.processed_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Review {self.employee} by {self.reviewer or 'N/A'} ({self.period_start}–{self.period_end})"


class Feedback(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField()
    rating = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback by {self.author} ({self.rating})"

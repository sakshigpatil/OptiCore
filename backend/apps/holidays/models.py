from django.db import models


class Holiday(models.Model):
    name = models.CharField(max_length=120)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False)
    country = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('date', 'country')
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} ({self.date})"

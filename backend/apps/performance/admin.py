from django.contrib import admin
from .models import Goal, Review, Feedback


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'due_date')
    search_fields = ('title', 'owner__username', 'owner__first_name')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('employee', 'reviewer', 'review_type', 'status', 'period_start', 'period_end')
    search_fields = ('employee__username', 'reviewer__username')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('author', 'rating', 'created_at')
    search_fields = ('author__username', 'comment')

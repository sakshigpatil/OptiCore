from rest_framework import serializers
from .models import Goal, Review, Feedback


class GoalSerializer(serializers.ModelSerializer):
    progress_percent = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_progress_percent(self, obj):
        return obj.progress_percent()


class ReviewSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('submitted_at', 'processed_at', 'created_at', 'updated_at')


class FeedbackSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ('created_at',)

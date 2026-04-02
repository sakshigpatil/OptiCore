from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Goal, Review, Feedback
from .serializers import GoalSerializer, ReviewSerializer, FeedbackSerializer
from django.db import models


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.select_related('owner').all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Goal.objects.all()
        return Goal.objects.filter(owner=user)

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        goal = self.get_object()
        progress = request.data.get('progress_value')
        if progress is None:
            return Response({'error': 'progress_value required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            goal.progress_value = progress
            if 'status' in request.data:
                goal.status = request.data['status']
            goal.save()
            return Response(self.get_serializer(goal).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('employee', 'reviewer').all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser or getattr(user, 'role', None) in ('ADMIN_HR', 'MANAGER'):
            return Review.objects.all()
        return Review.objects.filter(employee=user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        review = self.get_object()
        review.submit()
        return Response({'detail': 'submitted'})

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.approve(approver=request.user)
        return Response({'detail': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        review = self.get_object()
        reason = request.data.get('reason')
        review.reject(reason)
        return Response({'detail': 'rejected'})


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.select_related('author').all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Feedback.objects.all()
        return Feedback.objects.filter(models.Q(author=user) | models.Q(review__employee=user) | models.Q(goal__owner=user))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

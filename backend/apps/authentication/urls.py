from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet
from .dashboard_views import (
    DashboardSummaryAPIView,
    AttendanceTrendAPIView,
    DepartmentDistributionAPIView,
    RecentActivitiesAPIView
)

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/summary/', DashboardSummaryAPIView.as_view(), name='dashboard-summary'),
    path('dashboard/attendance-trend/', AttendanceTrendAPIView.as_view(), name='attendance-trend'),
    path('dashboard/department-distribution/', DepartmentDistributionAPIView.as_view(), name='department-distribution'),
    path('dashboard/recent-activities/', RecentActivitiesAPIView.as_view(), name='recent-activities'),
]
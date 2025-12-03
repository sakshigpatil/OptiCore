from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('attendance', views.AttendanceRecordViewSet, basename='attendance')
router.register('attendance-settings', views.AttendanceSettingsViewSet, basename='attendance-settings')

# Additional URL patterns for specific endpoints
urlpatterns = [
    path('', include(router.urls)),
    
    # Direct API endpoints (alternative to ViewSet actions)
    path('clock-in/', views.AttendanceRecordViewSet.as_view({'post': 'clock_in'}), name='clock-in'),
    path('clock-out/', views.AttendanceRecordViewSet.as_view({'post': 'clock_out'}), name='clock-out'),
    path('current-status/', views.AttendanceRecordViewSet.as_view({'get': 'current_status'}), name='current-status'),
    path('history/', views.AttendanceRecordViewSet.as_view({'get': 'history'}), name='attendance-history'),
    path('stats/', views.AttendanceRecordViewSet.as_view({'get': 'stats'}), name='attendance-stats'),
    path('today-summary/', views.AttendanceRecordViewSet.as_view({'get': 'today_summary'}), name='today-summary'),
]
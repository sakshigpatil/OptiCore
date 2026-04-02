from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('scheduled-reports', views.ScheduledReportViewSet, basename='scheduled-reports')

urlpatterns = [
    path('export/employees/', views.export_employee_data, name='export_employees'),
    path('export/employees', views.export_employee_data, name='export_employees_no_slash'),
    path('export/attendance/', views.export_attendance_data, name='export_attendance'),
    path('export/attendance', views.export_attendance_data, name='export_attendance_no_slash'),
    path('dashboard/', views.get_dashboard_analytics, name='dashboard_analytics'),
    path('custom-report/', views.generate_custom_report, name='custom_report'),
    path('', include(router.urls)),
]
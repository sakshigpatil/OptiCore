from django.urls import path
from . import views

urlpatterns = [
    path('export/employees/', views.export_employee_data, name='export_employees'),
    path('export/employees', views.export_employee_data, name='export_employees_no_slash'),
    path('export/attendance/', views.export_attendance_data, name='export_attendance'),
    path('export/attendance', views.export_attendance_data, name='export_attendance_no_slash'),
    path('dashboard/', views.get_dashboard_analytics, name='dashboard_analytics'),
]
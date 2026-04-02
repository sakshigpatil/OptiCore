from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, DepartmentViewSet, EmployeeDocumentViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'employee-documents', EmployeeDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
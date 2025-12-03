from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('leave-types', views.LeaveTypeViewSet)
router.register('leave-requests', views.LeaveRequestViewSet)
router.register('resignation-requests', views.ResignationRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
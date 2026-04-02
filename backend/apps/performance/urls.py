from rest_framework.routers import DefaultRouter
from .views import GoalViewSet, ReviewViewSet, FeedbackViewSet

router = DefaultRouter()
router.register(r'goals', GoalViewSet, basename='goal')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'feedbacks', FeedbackViewSet, basename='feedback')

urlpatterns = router.urls

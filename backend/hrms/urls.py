from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

def api_root(request):
    return JsonResponse({
        'message': 'HRMS API Server',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/v1/',
            'docs': '/api/docs/',
            'schema': '/api/schema/'
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.authentication.urls')),
    path('api/v1/', include('apps.employees.urls')),
    path('api/v1/', include('apps.projects.urls')),
    path('api/v1/', include('apps.attendance.urls')),
    path('api/v1/leaves/', include('apps.leaves.urls')),
    path('api/v1/payroll/', include('apps.payroll.urls')),
    path('api/v1/', include('apps.notifications.urls')),
    # Chatbot app archived - routes removed
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
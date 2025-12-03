import logging
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware to log all incoming requests for debugging"""
    
    def process_request(self, request):
        # Log request details
        logger.info(f"=== REQUEST START ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"Path: {request.path}")
        
        # Safely get full URL
        try:
            full_url = request.build_absolute_uri()
            logger.info(f"Full URL: {full_url}")
        except Exception as e:
            logger.warning(f"Could not build absolute URI: {e}")
            logger.info(f"Path only: {request.path}")
        
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Log request body for POST requests
        if request.method == 'POST' and request.content_type == 'application/json':
            try:
                body = json.loads(request.body.decode('utf-8'))
                logger.info(f"Request body: {body}")
            except Exception as e:
                logger.error(f"Error parsing request body: {e}")
        
        logger.info(f"Content Type: {request.content_type}")
        logger.info(f"User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")
        logger.info(f"Remote IP: {request.META.get('REMOTE_ADDR', 'Unknown')}")
        
        return None
    
    def process_response(self, request, response):
        # Log response details
        logger.info(f"=== RESPONSE ===")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.headers) if hasattr(response, 'headers') else 'N/A'}")
        
        # Log response content for non-200 responses
        if response.status_code >= 400:
            try:
                content = response.content.decode('utf-8')
                logger.error(f"Error Response Content: {content}")
            except Exception as e:
                logger.error(f"Error reading response content: {e}")
        
        logger.info(f"=== REQUEST END ===")
        return response
"""
Logging Middleware for Rent Management System
Middleware للتسجيل التلقائي
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from .logging_utils import log_api_request, get_client_ip, log_security_event

logger = logging.getLogger('dashboard')
api_logger = logging.getLogger('api')
security_logger = logging.getLogger('security')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware لتسجيل جميع الطلبات تلقائياً
    """
    
    def process_request(self, request):
        """تسجيل بداية الطلب"""
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """تسجيل نهاية الطلب"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # تسجيل طلبات API فقط
            if request.path.startswith('/api/'):
                log_api_request(request, response, duration)
            
            # تحذير للطلبات البطيئة
            if duration > 2.0:
                logger.warning(
                    f"SLOW REQUEST: {request.method} {request.path} | "
                    f"Duration: {duration:.3f}s | User: {request.user}"
                )
        
        return response
    
    def process_exception(self, request, exception):
        """تسجيل الاستثناءات"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            logger.error(
                f"Exception in request: {request.method} {request.path} | "
                f"Duration: {duration:.3f}s | User: {request.user} | "
                f"Error: {type(exception).__name__}: {str(exception)}",
                exc_info=True
            )
        
        return None


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    Middleware لتسجيل الأحداث الأمنية
    """
    
    def process_request(self, request):
        """تسجيل الأحداث الأمنية"""
        
        # تسجيل محاولات الوصول المشبوهة
        if self._is_suspicious_request(request):
            ip_address = get_client_ip(request)
            user = request.user if request.user.is_authenticated else 'Anonymous'
            
            security_logger.warning(
                f"Suspicious request | User: {user} | IP: {ip_address} | "
                f"Path: {request.path} | Method: {request.method}"
            )
        
        return None
    
    def _is_suspicious_request(self, request):
        """
        فحص الطلبات المشبوهة
        """
        suspicious_patterns = [
            '/admin/login/',
            '/.env',
            '/wp-admin/',
            '/phpmyadmin/',
            '../',
            'SELECT',
            'UNION',
            '<script>',
        ]
        
        path = request.path.lower()
        query = request.GET.urlencode().lower()
        
        for pattern in suspicious_patterns:
            if pattern.lower() in path or pattern.lower() in query:
                return True
        
        return False


class AuditTrailMiddleware(MiddlewareMixin):
    """
    Middleware لتتبع إجراءات المستخدمين
    """
    
    def process_request(self, request):
        """حفظ معلومات الطلب للتدقيق"""
        if request.user.is_authenticated:
            request._audit_user = request.user
            request._audit_ip = get_client_ip(request)
        
        return None
    
    def process_response(self, request, response):
        """تسجيل الإجراءات المهمة"""
        if hasattr(request, '_audit_user'):
            # تسجيل العمليات المهمة فقط
            if self._is_important_action(request, response):
                audit_logger = logging.getLogger('audit')
                
                audit_logger.info(
                    f"User Action | User: {request._audit_user.username} | "
                    f"IP: {request._audit_ip} | Method: {request.method} | "
                    f"Path: {request.path} | Status: {response.status_code}"
                )
        
        return response
    
    def _is_important_action(self, request, response):
        """
        تحديد الإجراءات المهمة التي يجب تسجيلها
        """
        # تسجيل POST, PUT, DELETE فقط
        if request.method not in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return False
        
        # تسجيل الإجراءات الناجحة فقط
        if response.status_code not in [200, 201, 204]:
            return False
        
        # تسجيل مسارات معينة
        important_paths = [
            '/dashboard/leases/',
            '/dashboard/payments/',
            '/dashboard/tenants/',
            '/dashboard/users/',
            '/api/',
        ]
        
        return any(request.path.startswith(path) for path in important_paths)


class PerformanceLoggingMiddleware(MiddlewareMixin):
    """
    Middleware لتسجيل الأداء
    """
    
    def process_request(self, request):
        """بداية قياس الأداء"""
        request._perf_start = time.time()
        return None
    
    def process_response(self, request, response):
        """تسجيل الأداء"""
        if hasattr(request, '_perf_start'):
            duration = time.time() - request._perf_start
            
            # تسجيل الطلبات البطيئة فقط
            if duration > 1.0:
                performance_logger = logging.getLogger('performance')
                
                performance_logger.warning(
                    f"Slow Response | Path: {request.path} | "
                    f"Method: {request.method} | Duration: {duration:.3f}s | "
                    f"User: {request.user} | Status: {response.status_code}"
                )
        
        return response

"""
Logging Utilities for Rent Management System
أدوات السجلات لنظام إدارة الإيجارات
"""

import logging
import time
import functools
from django.contrib.auth import get_user_model

User = get_user_model()

# ==================== Loggers ====================

# General logger
logger = logging.getLogger('dashboard')

# API logger
api_logger = logging.getLogger('api')

# Security logger
security_logger = logging.getLogger('security')

# Audit logger
audit_logger = logging.getLogger('audit')

# Performance logger
performance_logger = logging.getLogger('performance')


# ==================== Helper Functions ====================

def log_user_action(user, action, model_name=None, object_id=None, details=None):
    """
    تسجيل إجراء المستخدم في Audit Trail
    
    Args:
        user: المستخدم
        action: الإجراء (create, update, delete, view)
        model_name: اسم النموذج
        object_id: معرف الكائن
        details: تفاصيل إضافية
    """
    user_info = f"User: {user.username} (ID: {user.id})"
    
    if model_name and object_id:
        message = f"{user_info} | Action: {action} | Model: {model_name} | ID: {object_id}"
    else:
        message = f"{user_info} | Action: {action}"
    
    if details:
        message += f" | Details: {details}"
    
    audit_logger.info(message)


def log_api_request(request, response=None, duration=None):
    """
    تسجيل طلب API
    
    Args:
        request: Django request object
        response: Django response object
        duration: مدة التنفيذ بالثواني
    """
    user = request.user if request.user.is_authenticated else 'Anonymous'
    method = request.method
    path = request.path
    status = response.status_code if response else 'N/A'
    
    message = f"User: {user} | {method} {path} | Status: {status}"
    
    if duration:
        message += f" | Duration: {duration:.3f}s"
    
    # Query parameters
    if request.GET:
        message += f" | Query: {dict(request.GET)}"
    
    api_logger.info(message)


def log_security_event(event_type, user=None, ip_address=None, details=None):
    """
    تسجيل حدث أمني
    
    Args:
        event_type: نوع الحدث (login, logout, failed_login, permission_denied, etc.)
        user: المستخدم
        ip_address: عنوان IP
        details: تفاصيل إضافية
    """
    message = f"Security Event: {event_type}"
    
    if user:
        message += f" | User: {user.username} (ID: {user.id})"
    
    if ip_address:
        message += f" | IP: {ip_address}"
    
    if details:
        message += f" | Details: {details}"
    
    security_logger.warning(message)


def log_performance(operation, duration, details=None):
    """
    تسجيل أداء العملية
    
    Args:
        operation: اسم العملية
        duration: المدة بالثواني
        details: تفاصيل إضافية
    """
    message = f"Operation: {operation} | Duration: {duration:.3f}s"
    
    if details:
        message += f" | Details: {details}"
    
    # تحذير إذا كانت العملية بطيئة
    if duration > 1.0:
        performance_logger.warning(f"SLOW: {message}")
    else:
        performance_logger.info(message)


def log_error(error, context=None):
    """
    تسجيل خطأ مع السياق
    
    Args:
        error: الخطأ (Exception)
        context: سياق إضافي
    """
    message = f"Error: {type(error).__name__}: {str(error)}"
    
    if context:
        message += f" | Context: {context}"
    
    logger.error(message, exc_info=True)


# ==================== Decorators ====================

def log_view_access(view_name=None):
    """
    Decorator لتسجيل الوصول للـ view
    
    Usage:
        @log_view_access('lease_list')
        def lease_list_view(request):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            name = view_name or func.__name__
            user = request.user if request.user.is_authenticated else 'Anonymous'
            
            logger.info(f"View Access: {name} | User: {user} | Method: {request.method}")
            
            try:
                response = func(request, *args, **kwargs)
                return response
            except Exception as e:
                log_error(e, context=f"View: {name}, User: {user}")
                raise
        
        return wrapper
    return decorator


def log_api_call(endpoint_name=None):
    """
    Decorator لتسجيل استدعاء API مع قياس الأداء
    
    Usage:
        @log_api_call('lease_list_api')
        def list(self, request):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            name = endpoint_name or func.__name__
            start_time = time.time()
            
            try:
                response = func(self, request, *args, **kwargs)
                duration = time.time() - start_time
                
                log_api_request(request, response, duration)
                
                # تسجيل الأداء إذا كان بطيئاً
                if duration > 0.5:
                    log_performance(f"API: {name}", duration)
                
                return response
            
            except Exception as e:
                duration = time.time() - start_time
                log_error(e, context=f"API: {name}, Duration: {duration:.3f}s")
                raise
        
        return wrapper
    return decorator


def log_model_action(action_type):
    """
    Decorator لتسجيل إجراءات النموذج
    
    Usage:
        @log_model_action('create')
        def create_lease(request, data):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            user = request.user if hasattr(request, 'user') else None
            
            try:
                result = func(request, *args, **kwargs)
                
                # محاولة الحصول على معلومات الكائن
                if hasattr(result, '__class__'):
                    model_name = result.__class__.__name__
                    object_id = getattr(result, 'id', None)
                    
                    if user:
                        log_user_action(
                            user, 
                            action_type, 
                            model_name, 
                            object_id
                        )
                
                return result
            
            except Exception as e:
                log_error(e, context=f"Model Action: {action_type}")
                raise
        
        return wrapper
    return decorator


def measure_performance(operation_name=None):
    """
    Decorator لقياس أداء الدالة
    
    Usage:
        @measure_performance('calculate_financial_report')
        def calculate_report():
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                log_performance(name, duration)
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                log_error(e, context=f"Performance: {name}, Duration: {duration:.3f}s")
                raise
        
        return wrapper
    return decorator


# ==================== Context Managers ====================

class LogContext:
    """
    Context manager لتسجيل بداية ونهاية عملية
    
    Usage:
        with LogContext('Processing lease payments'):
            # Your code here
            process_payments()
    """
    def __init__(self, operation_name, log_level='INFO'):
        self.operation_name = operation_name
        self.log_level = log_level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.log(
            getattr(logging, self.log_level),
            f"START: {self.operation_name}"
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            logger.log(
                getattr(logging, self.log_level),
                f"END: {self.operation_name} | Duration: {duration:.3f}s"
            )
        else:
            logger.error(
                f"FAILED: {self.operation_name} | Duration: {duration:.3f}s | Error: {exc_val}",
                exc_info=True
            )
        
        return False  # لا تمنع انتشار الاستثناء


# ==================== Utility Functions ====================

def get_client_ip(request):
    """
    الحصول على عنوان IP للعميل
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_login_attempt(request, username, success=True):
    """
    تسجيل محاولة تسجيل الدخول
    """
    ip_address = get_client_ip(request)
    
    if success:
        security_logger.info(
            f"Successful login | Username: {username} | IP: {ip_address}"
        )
    else:
        security_logger.warning(
            f"Failed login attempt | Username: {username} | IP: {ip_address}"
        )


def log_permission_denied(request, permission):
    """
    تسجيل رفض الصلاحية
    """
    user = request.user if request.user.is_authenticated else 'Anonymous'
    ip_address = get_client_ip(request)
    
    security_logger.warning(
        f"Permission denied | User: {user} | Permission: {permission} | IP: {ip_address}"
    )


def log_data_export(user, export_type, record_count):
    """
    تسجيل تصدير البيانات
    """
    audit_logger.info(
        f"Data Export | User: {user.username} | Type: {export_type} | Records: {record_count}"
    )


def log_bulk_operation(user, operation, model_name, count):
    """
    تسجيل عملية جماعية
    """
    audit_logger.info(
        f"Bulk Operation | User: {user.username} | Operation: {operation} | Model: {model_name} | Count: {count}"
    )

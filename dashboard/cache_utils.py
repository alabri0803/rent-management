"""
Cache Utilities for Rent Management System
أدوات التخزين المؤقت لنظام إدارة الإيجارات
"""

from django.core.cache import caches
from django.core.cache.utils import make_template_fragment_key
from functools import wraps
import hashlib
import json


def get_cache_key(prefix, *args, **kwargs):
    """
    إنشاء مفتاح cache فريد بناءً على المعاملات
    """
    key_parts = [prefix]
    
    # إضافة args
    for arg in args:
        if hasattr(arg, 'pk'):
            key_parts.append(str(arg.pk))
        else:
            key_parts.append(str(arg))
    
    # إضافة kwargs
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    
    # إنشاء hash للمفتاح الطويل
    key_string = ':'.join(key_parts)
    if len(key_string) > 200:
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    return key_string


def cache_response(cache_name='default', timeout=300, key_prefix='view'):
    """
    Decorator لتخزين نتائج الـ view
    
    Usage:
        @cache_response(cache_name='api', timeout=600, key_prefix='lease_list')
        def my_view(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # إنشاء cache key
            cache_key = get_cache_key(
                key_prefix,
                request.path,
                request.GET.urlencode(),
                *args,
                **kwargs
            )
            
            # محاولة الحصول من الـ cache
            cache = caches[cache_name]
            cached_response = cache.get(cache_key)
            
            if cached_response is not None:
                return cached_response
            
            # تنفيذ الـ view
            response = func(request, *args, **kwargs)
            
            # حفظ في الـ cache
            cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator


def cache_method(cache_name='default', timeout=300, key_prefix='method'):
    """
    Decorator لتخزين نتائج الـ methods
    
    Usage:
        @cache_method(cache_name='reports', timeout=1800, key_prefix='financial_report')
        def get_financial_report(self, start_date, end_date):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # إنشاء cache key
            cache_key = get_cache_key(
                key_prefix,
                self.__class__.__name__,
                getattr(self, 'pk', ''),
                *args,
                **kwargs
            )
            
            # محاولة الحصول من الـ cache
            cache = caches[cache_name]
            cached_result = cache.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # تنفيذ الـ method
            result = func(self, *args, **kwargs)
            
            # حفظ في الـ cache
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(cache_name='default', key_prefix=None, pattern=None):
    """
    حذف cache معين أو مجموعة من الـ caches
    
    Usage:
        invalidate_cache('api', key_prefix='lease_list')
        invalidate_cache('reports', pattern='financial_*')
    """
    cache = caches[cache_name]
    
    if key_prefix:
        # حذف cache محدد
        cache.delete(key_prefix)
    elif pattern:
        # حذف مجموعة caches (يتطلب Redis أو Memcached)
        # للـ LocMemCache، نحتاج لحذف الـ cache بالكامل
        cache.clear()
    else:
        # حذف كل الـ cache
        cache.clear()


def invalidate_model_cache(model_name, instance_id=None):
    """
    حذف cache متعلق بـ model معين
    
    Usage:
        invalidate_model_cache('Lease', lease_id)
        invalidate_model_cache('Payment')  # حذف كل الـ cache للـ Payment
    """
    cache = caches['api']
    
    if instance_id:
        # حذف cache لـ instance محدد
        cache_key = f"{model_name}:{instance_id}"
        cache.delete(cache_key)
        
        # حذف cache للـ list views
        cache.delete(f"{model_name}_list")
        cache.delete(f"{model_name}_detail:{instance_id}")
    else:
        # حذف كل الـ cache للـ model
        cache.delete(f"{model_name}_list")


class CacheManager:
    """
    مدير الـ cache المركزي
    """
    
    @staticmethod
    def get_or_set(cache_name, key, callback, timeout=300):
        """
        الحصول من الـ cache أو تنفيذ الـ callback وحفظ النتيجة
        
        Usage:
            result = CacheManager.get_or_set(
                'reports',
                'monthly_report_2025_01',
                lambda: calculate_monthly_report(2025, 1),
                timeout=1800
            )
        """
        cache = caches[cache_name]
        result = cache.get(key)
        
        if result is None:
            result = callback()
            cache.set(key, result, timeout)
        
        return result
    
    @staticmethod
    def invalidate_all():
        """
        حذف كل الـ caches
        """
        for cache_name in ['default', 'api', 'reports']:
            caches[cache_name].clear()
    
    @staticmethod
    def get_stats():
        """
        الحصول على إحصائيات الـ cache (للـ debugging)
        """
        stats = {}
        for cache_name in ['default', 'api', 'reports']:
            cache = caches[cache_name]
            # LocMemCache لا يدعم stats، لكن يمكن إضافة معلومات أساسية
            stats[cache_name] = {
                'backend': cache.__class__.__name__,
                'timeout': getattr(cache, 'default_timeout', 'N/A'),
            }
        return stats


# ==================== Cache Decorators للـ API Views ====================

def cache_api_response(timeout=600):
    """
    Decorator خاص بالـ API responses
    
    Usage:
        @cache_api_response(timeout=600)
        class LeaseViewSet(viewsets.ModelViewSet):
            ...
    """
    def decorator(cls):
        original_list = cls.list
        original_retrieve = cls.retrieve
        
        @wraps(original_list)
        def cached_list(self, request, *args, **kwargs):
            cache_key = get_cache_key(
                f"{cls.__name__}_list",
                request.GET.urlencode()
            )
            
            cache = caches['api']
            cached_response = cache.get(cache_key)
            
            if cached_response is not None:
                return cached_response
            
            response = original_list(self, request, *args, **kwargs)
            cache.set(cache_key, response, timeout)
            
            return response
        
        @wraps(original_retrieve)
        def cached_retrieve(self, request, *args, **kwargs):
            pk = kwargs.get('pk')
            cache_key = get_cache_key(
                f"{cls.__name__}_detail",
                pk
            )
            
            cache = caches['api']
            cached_response = cache.get(cache_key)
            
            if cached_response is not None:
                return cached_response
            
            response = original_retrieve(self, request, *args, **kwargs)
            cache.set(cache_key, response, timeout)
            
            return response
        
        cls.list = cached_list
        cls.retrieve = cached_retrieve
        
        return cls
    return decorator

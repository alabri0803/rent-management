"""
Decorators for permission-based access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required


def permission_required(permission_name, redirect_url='dashboard'):
    """
    Decorator للتحقق من صلاحية معينة للمستخدم
    
    Args:
        permission_name: اسم الصلاحية المطلوبة (مثل: can_view_buildings)
        redirect_url: الصفحة المراد التحويل إليها في حالة عدم وجود الصلاحية
    
    Usage:
        @permission_required('can_manage_units')
        def add_unit(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # المستخدمون الإداريون لديهم جميع الصلاحيات
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # التحقق من وجود profile للمستخدم
            if not hasattr(request.user, 'profile'):
                messages.error(request, _('عذراً، ملفك الشخصي غير موجود. يرجى التواصل مع المدير.'))
                return redirect(redirect_url)
            
            # التحقق من الصلاحية
            if not request.user.profile.has_permission(permission_name):
                messages.error(request, _('عذراً، ليس لديك صلاحية للوصول إلى هذه الصفحة.'))
                return redirect(redirect_url)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def any_permission_required(*permission_names, redirect_url='dashboard'):
    """
    Decorator للتحقق من وجود أي صلاحية من قائمة الصلاحيات
    
    Args:
        *permission_names: قائمة بأسماء الصلاحيات المطلوبة
        redirect_url: الصفحة المراد التحويل إليها في حالة عدم وجود أي صلاحية
    
    Usage:
        @any_permission_required('can_view_units', 'can_manage_units')
        def unit_list(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # المستخدمون الإداريون لديهم جميع الصلاحيات
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # التحقق من وجود profile للمستخدم
            if not hasattr(request.user, 'profile'):
                messages.error(request, _('عذراً، ملفك الشخصي غير موجود. يرجى التواصل مع المدير.'))
                return redirect(redirect_url)
            
            # التحقق من وجود أي صلاحية
            has_any_permission = any(
                request.user.profile.has_permission(perm) 
                for perm in permission_names
            )
            
            if not has_any_permission:
                messages.error(request, _('عذراً، ليس لديك صلاحية للوصول إلى هذه الصفحة.'))
                return redirect(redirect_url)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def all_permissions_required(*permission_names, redirect_url='dashboard'):
    """
    Decorator للتحقق من وجود جميع الصلاحيات المطلوبة
    
    Args:
        *permission_names: قائمة بأسماء الصلاحيات المطلوبة
        redirect_url: الصفحة المراد التحويل إليها في حالة عدم وجود جميع الصلاحيات
    
    Usage:
        @all_permissions_required('can_view_payments', 'can_manage_payments')
        def payment_operations(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # المستخدمون الإداريون لديهم جميع الصلاحيات
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # التحقق من وجود profile للمستخدم
            if not hasattr(request.user, 'profile'):
                messages.error(request, _('عذراً، ملفك الشخصي غير موجود. يرجى التواصل مع المدير.'))
                return redirect(redirect_url)
            
            # التحقق من وجود جميع الصلاحيات
            has_all_permissions = all(
                request.user.profile.has_permission(perm) 
                for perm in permission_names
            )
            
            if not has_all_permissions:
                messages.error(request, _('عذراً، ليس لديك صلاحية للوصول إلى هذه الصفحة.'))
                return redirect(redirect_url)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

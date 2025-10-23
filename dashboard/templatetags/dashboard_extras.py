from django import template
from dashboard.models import Company

register = template.Library()

@register.simple_tag
def get_company_name():
    company = Company.objects.first()
    return company.name if company else 'Rent Management'

@register.simple_tag
def get_company_logo():
    company = Company.objects.first()
    return company.logo.url if company and company.logo else None

# ==== Building Delete Context Filters ====
@register.filter
def leaselist_active_count(units):
    """Return number of active leases for all units in a building."""
    from dashboard.models import Lease
    return Lease.objects.filter(unit__in=units, status='active').count()

@register.filter
def leaselist_tenants_count(units):
    """Return number of unique tenants with active leases for all units."""
    from dashboard.models import Lease
    return Lease.objects.filter(unit__in=units, status='active').values('tenant').distinct().count()

@register.filter
def split(value, separator):
    """Split a string by separator and return a list."""
    if not value:
        return []
    return str(value).split(separator)

@register.simple_tag(takes_context=True)
def user_display_name(context, user):
    """Get user's display name based on current language"""
    request = context.get('request')
    current_language = 'ar'  # Default to Arabic
    
    if request:
        # Get current language from request
        current_language = getattr(request, 'LANGUAGE_CODE', 'ar')
    
    # Try to get profile and use display name method
    try:
        if hasattr(user, 'profile') and user.profile:
            return user.profile.get_display_name(current_language)
    except:
        pass
    
    # Fallback to default full name or username
    full_name = user.get_full_name()
    if full_name and full_name.strip():
        return full_name
    else:
        return user.username or "-"


# ==== Permission Checking Template Tags ====
@register.simple_tag(takes_context=True)
def has_permission(context, permission_name):
    """
    التحقق من صلاحية المستخدم الحالي
    Usage: {% has_permission 'can_manage_units' as can_edit %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return False
    
    # المستخدمون الإداريون لديهم جميع الصلاحيات
    if request.user.is_superuser:
        return True
    
    # التحقق من الصلاحية
    if hasattr(request.user, 'profile'):
        return request.user.profile.has_permission(permission_name)
    
    return False


@register.filter
def has_perm(user, permission_name):
    """
    Filter للتحقق من صلاحية المستخدم
    Usage: {% if request.user|has_perm:'can_manage_units' %}
    """
    if not user or not user.is_authenticated:
        return False
    
    # المستخدمون الإداريون لديهم جميع الصلاحيات
    if user.is_superuser:
        return True
    
    # التحقق من الصلاحية
    if hasattr(user, 'profile'):
        return user.profile.has_permission(permission_name)
    
    return False
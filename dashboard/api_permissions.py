"""
Custom API Permissions
صلاحيات مخصصة لـ API
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    صلاحية مخصصة للسماح للمالكين فقط بتعديل الكائن
    """
    
    def has_object_permission(self, request, view, obj):
        # السماح بالقراءة للجميع
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # السماح بالكتابة للمالك فقط
        return obj.owner == request.user


class CanViewDashboard(permissions.BasePermission):
    """
    صلاحية عرض لوحة التحكم
    """
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        try:
            return request.user.profile.can_view_dashboard
        except:
            return False


class CanManageBuildings(permissions.BasePermission):
    """
    صلاحية إدارة المباني
    """
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        try:
            if request.method in permissions.SAFE_METHODS:
                return request.user.profile.can_view_buildings
            return request.user.profile.can_manage_buildings
        except:
            return False


class CanManageUnits(permissions.BasePermission):
    """
    صلاحية إدارة الوحدات
    """
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        try:
            if request.method in permissions.SAFE_METHODS:
                return request.user.profile.can_view_units
            return request.user.profile.can_manage_units
        except:
            return False


class CanManageLeases(permissions.BasePermission):
    """
    صلاحية إدارة العقود
    """
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        try:
            if request.method in permissions.SAFE_METHODS:
                return request.user.profile.can_view_leases
            return request.user.profile.can_manage_leases
        except:
            return False


class CanManageTenants(permissions.BasePermission):
    """
    صلاحية إدارة المستأجرين
    """
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        try:
            if request.method in permissions.SAFE_METHODS:
                return request.user.profile.can_view_tenants
            return request.user.profile.can_manage_tenants
        except:
            return False


class CanManagePayments(permissions.BasePermission):
    """
    صلاحية إدارة الدفعات
    """
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        try:
            if request.method in permissions.SAFE_METHODS:
                return request.user.profile.can_view_payments
            return request.user.profile.can_manage_payments
        except:
            return False


class CanManageExpenses(permissions.BasePermission):
    """
    صلاحية إدارة المصروفات
    """
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        try:
            if request.method in permissions.SAFE_METHODS:
                return request.user.profile.can_view_expenses
            return request.user.profile.can_manage_expenses
        except:
            return False


class CanViewReports(permissions.BasePermission):
    """
    صلاحية عرض التقارير
    """
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        try:
            return request.user.profile.can_view_reports
        except:
            return False

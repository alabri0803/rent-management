"""
Django REST Framework Serializers
Serializers للنماذج الرئيسية في نظام إدارة الإيجارات
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Building, Unit, Tenant, Lease, Payment,
    Expense, Invoice, InvoiceItem, SecurityDeposit,
    PaymentOverdueNotice, PaymentOverdueDetail,
    Notification, UserProfile
)


# ==================== User Serializers ====================

class UserSerializer(serializers.ModelSerializer):
    """Serializer للمستخدم"""
    
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer لملف المستخدم"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['id', 'user']


# ==================== Building & Unit Serializers ====================

class BuildingListSerializer(serializers.ModelSerializer):
    """Serializer مختصر للمباني (للقوائم)"""
    total_units = serializers.SerializerMethodField()
    occupied_units = serializers.SerializerMethodField()
    available_units = serializers.SerializerMethodField()
    
    class Meta:
        model = Building
        fields = '__all__'
        read_only_fields = ['id']
    
    def get_total_units(self, obj):
        """إجمالي الوحدات"""
        return obj.units.count()
    
    def get_occupied_units(self, obj):
        """الوحدات المشغولة"""
        return obj.units.filter(is_available=False).count()
    
    def get_available_units(self, obj):
        """الوحدات المتاحة"""
        return obj.units.filter(is_available=True).count()


class BuildingDetailSerializer(serializers.ModelSerializer):
    """Serializer مفصل للمباني"""
    total_units = serializers.SerializerMethodField()
    occupied_units = serializers.SerializerMethodField()
    available_units = serializers.SerializerMethodField()
    units = serializers.SerializerMethodField()
    
    class Meta:
        model = Building
        fields = '__all__'
        read_only_fields = ['id']
    
    def get_total_units(self, obj):
        """إجمالي الوحدات"""
        return obj.units.count()
    
    def get_occupied_units(self, obj):
        """الوحدات المشغولة"""
        return obj.units.filter(is_available=False).count()
    
    def get_available_units(self, obj):
        """الوحدات المتاحة"""
        return obj.units.filter(is_available=True).count()
    
    def get_units(self, obj):
        """الحصول على الوحدات"""
        units = obj.units.all()[:10]  # أول 10 وحدات
        return UnitListSerializer(units, many=True).data


class UnitListSerializer(serializers.ModelSerializer):
    """Serializer مختصر للوحدات"""
    building_name = serializers.CharField(source='building.name', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Unit
        fields = '__all__'
        read_only_fields = ['id']


class UnitDetailSerializer(serializers.ModelSerializer):
    """Serializer مفصل للوحدات"""
    building = BuildingListSerializer(read_only=True)
    building_id = serializers.PrimaryKeyRelatedField(
        queryset=Building.objects.all(),
        source='building',
        write_only=True
    )
    is_available = serializers.BooleanField(read_only=True)
    current_lease = serializers.SerializerMethodField()
    
    class Meta:
        model = Unit
        fields = '__all__'
        read_only_fields = ['id']
    
    def get_current_lease(self, obj):
        """الحصول على العقد الحالي"""
        lease = obj.leases.filter(status='active').first()
        if lease:
            return LeaseListSerializer(lease).data
        return None


# ==================== Tenant Serializers ====================

class TenantListSerializer(serializers.ModelSerializer):
    """Serializer مختصر للمستأجرين"""
    active_leases_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = '__all__'
        read_only_fields = ['id']
    
    def get_active_leases_count(self, obj):
        """عدد العقود النشطة"""
        return obj.leases.filter(status='active').count()


class TenantDetailSerializer(serializers.ModelSerializer):
    """Serializer مفصل للمستأجرين"""
    active_leases = serializers.SerializerMethodField()
    total_payments = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = '__all__'
        read_only_fields = ['id']
    
    def get_active_leases(self, obj):
        """العقود النشطة"""
        leases = obj.leases.filter(status='active')
        return LeaseListSerializer(leases, many=True).data
    
    def get_total_payments(self, obj):
        """إجمالي المدفوعات"""
        from django.db.models import Sum
        total = Payment.objects.filter(
            lease__tenant=obj
        ).aggregate(total=Sum('amount'))['total']
        return float(total) if total else 0.0


# ==================== Lease Serializers ====================

class LeaseListSerializer(serializers.ModelSerializer):
    """Serializer مختصر للعقود"""
    unit_info = serializers.SerializerMethodField()
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Lease
        fields = '__all__'
        read_only_fields = ['id', 'contract_number']
    
    def get_unit_info(self, obj):
        """معلومات الوحدة"""
        return f"{obj.unit.building.name} - {obj.unit.unit_number}"


class LeaseDetailSerializer(serializers.ModelSerializer):
    """Serializer مفصل للعقود"""
    unit = UnitListSerializer(read_only=True)
    unit_id = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        source='unit',
        write_only=True
    )
    tenant = TenantListSerializer(read_only=True)
    tenant_id = serializers.PrimaryKeyRelatedField(
        queryset=Tenant.objects.all(),
        source='tenant',
        write_only=True
    )
    days_until_expiry = serializers.IntegerField(read_only=True)
    payment_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Lease
        fields = '__all__'
        read_only_fields = ['id', 'contract_number', 'registration_fee', 'status']
    
    def get_payment_summary(self, obj):
        """كشف حساب الدفعات"""
        summary = obj.get_payment_summary()
        return summary[:6]  # أول 6 أشهر


# ==================== Payment Serializers ====================

class PaymentListSerializer(serializers.ModelSerializer):
    """Serializer مختصر للدفعات"""
    lease_info = serializers.SerializerMethodField()
    tenant_name = serializers.CharField(source='lease.tenant.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id']
    
    def get_lease_info(self, obj):
        """معلومات العقد"""
        return obj.lease.contract_number


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Serializer مفصل للدفعات"""
    lease = LeaseListSerializer(read_only=True)
    lease_id = serializers.PrimaryKeyRelatedField(
        queryset=Lease.objects.all(),
        source='lease',
        write_only=True
    )
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id']
    
    def validate(self, data):
        """التحقق من صحة البيانات"""
        # التحقق من بيانات الشيك
        if data.get('payment_method') == 'check':
            if not data.get('check_number'):
                raise serializers.ValidationError({
                    'check_number': 'رقم الشيك مطلوب عند الدفع بالشيك'
                })
        
        # التحقق من المبلغ
        if data.get('amount') and data.get('amount') <= 0:
            raise serializers.ValidationError({
                'amount': 'المبلغ يجب أن يكون أكبر من صفر'
            })
        
        return data


# ==================== Expense Serializers ====================

class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer للمصروفات"""
    building_name = serializers.CharField(source='building.name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


# ==================== Invoice Serializers ====================

class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer لبنود الفاتورة"""
    
    class Meta:
        model = InvoiceItem
        fields = '__all__'
        read_only_fields = ['id', 'amount']


class InvoiceListSerializer(serializers.ModelSerializer):
    """Serializer مختصر للفواتير"""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['id', 'invoice_number', 'total_amount']


class InvoiceDetailSerializer(serializers.ModelSerializer):
    """Serializer مفصل للفواتير"""
    tenant = TenantListSerializer(read_only=True)
    tenant_id = serializers.PrimaryKeyRelatedField(
        queryset=Tenant.objects.all(),
        source='tenant',
        write_only=True
    )
    items = InvoiceItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['id', 'invoice_number', 'total_amount']


# ==================== Overdue Notice Serializers ====================

class PaymentOverdueDetailSerializer(serializers.ModelSerializer):
    """Serializer لتفاصيل الإنذار"""
    
    class Meta:
        model = PaymentOverdueDetail
        fields = '__all__'
        read_only_fields = ['id']


class PaymentOverdueNoticeSerializer(serializers.ModelSerializer):
    """Serializer للإنذارات"""
    lease_info = serializers.SerializerMethodField()
    tenant_name = serializers.CharField(source='lease.tenant.name', read_only=True)
    details = PaymentOverdueDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = PaymentOverdueNotice
        fields = '__all__'
        read_only_fields = ['id', 'notice_number']
    
    def get_lease_info(self, obj):
        """معلومات العقد"""
        return obj.lease.contract_number


# ==================== Report Serializers ====================

class FinancialReportSerializer(serializers.Serializer):
    """Serializer لتقرير مالي"""
    period = serializers.CharField()
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_payments = serializers.IntegerField()
    total_leases = serializers.IntegerField()
    occupancy_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class LeaseReportSerializer(serializers.Serializer):
    """Serializer لتقرير العقود"""
    total_leases = serializers.IntegerField()
    active_leases = serializers.IntegerField()
    expired_leases = serializers.IntegerField()
    cancelled_leases = serializers.IntegerField()
    expiring_soon = serializers.IntegerField()
    total_monthly_rent = serializers.DecimalField(max_digits=12, decimal_places=2)


class OccupancyReportSerializer(serializers.Serializer):
    """Serializer لتقرير الإشغال"""
    total_units = serializers.IntegerField()
    occupied_units = serializers.IntegerField()
    available_units = serializers.IntegerField()
    occupancy_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    by_building = serializers.ListField()

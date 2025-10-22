"""
Django REST Framework API Views
API Views للنماذج الرئيسية في نظام إدارة الإيجارات
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import (
    Building, Unit, Tenant, Lease, Payment,
    Expense, Invoice, PaymentOverdueNotice
)
from .serializers import (
    BuildingListSerializer, BuildingDetailSerializer,
    UnitListSerializer, UnitDetailSerializer,
    TenantListSerializer, TenantDetailSerializer,
    LeaseListSerializer, LeaseDetailSerializer,
    PaymentListSerializer, PaymentDetailSerializer,
    ExpenseSerializer, InvoiceListSerializer, InvoiceDetailSerializer,
    PaymentOverdueNoticeSerializer,
    FinancialReportSerializer, LeaseReportSerializer, OccupancyReportSerializer
)


# ==================== Building ViewSet ====================

class BuildingViewSet(viewsets.ModelViewSet):
    """
    API endpoint للمباني
    
    list: الحصول على قائمة المباني
    retrieve: الحصول على تفاصيل مبنى
    create: إنشاء مبنى جديد
    update: تحديث مبنى
    partial_update: تحديث جزئي لمبنى
    destroy: حذف مبنى
    """
    queryset = Building.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address']
    ordering_fields = ['name', 'created_at', 'total_units']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BuildingDetailSerializer
        return BuildingListSerializer
    
    @action(detail=True, methods=['get'])
    def units(self, request, pk=None):
        """الحصول على وحدات المبنى"""
        building = self.get_object()
        units = building.units.all()
        serializer = UnitListSerializer(units, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """إحصائيات المبنى"""
        building = self.get_object()
        return Response({
            'total_units': building.total_units,
            'occupied_units': building.occupied_units_count(),
            'available_units': building.available_units_count(),
            'occupancy_rate': building.occupancy_rate(),
            'total_monthly_income': building.total_monthly_income()
        })


# ==================== Unit ViewSet ====================

class UnitViewSet(viewsets.ModelViewSet):
    """
    API endpoint للوحدات
    
    list: الحصول على قائمة الوحدات
    retrieve: الحصول على تفاصيل وحدة
    create: إنشاء وحدة جديدة
    update: تحديث وحدة
    partial_update: تحديث جزئي لوحدة
    destroy: حذف وحدة
    """
    queryset = Unit.objects.select_related('building').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['building', 'unit_type', 'is_available', 'floor']
    search_fields = ['unit_number', 'building__name']
    ordering_fields = ['unit_number', 'floor']
    ordering = ['building', 'unit_number']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UnitDetailSerializer
        return UnitListSerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """الوحدات المتاحة فقط"""
        units = self.queryset.filter(is_available=True)
        serializer = self.get_serializer(units, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def lease_history(self, request, pk=None):
        """سجل عقود الوحدة"""
        unit = self.get_object()
        leases = unit.leases.all().order_by('-start_date')
        serializer = LeaseListSerializer(leases, many=True)
        return Response(serializer.data)


# ==================== Tenant ViewSet ====================

class TenantViewSet(viewsets.ModelViewSet):
    """
    API endpoint للمستأجرين
    
    list: الحصول على قائمة المستأجرين
    retrieve: الحصول على تفاصيل مستأجر
    create: إنشاء مستأجر جديد
    update: تحديث مستأجر
    partial_update: تحديث جزئي لمستأجر
    destroy: حذف مستأجر
    """
    queryset = Tenant.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tenant_type']
    search_fields = ['name', 'phone', 'email', 'national_id']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TenantDetailSerializer
        return TenantListSerializer
    
    @action(detail=True, methods=['get'])
    def leases(self, request, pk=None):
        """عقود المستأجر"""
        tenant = self.get_object()
        leases = tenant.leases.all().order_by('-start_date')
        serializer = LeaseListSerializer(leases, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """دفعات المستأجر"""
        tenant = self.get_object()
        payments = Payment.objects.filter(lease__tenant=tenant).order_by('-payment_date')
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def financial_summary(self, request, pk=None):
        """ملخص مالي للمستأجر"""
        tenant = self.get_object()
        
        # إجمالي الدفعات
        total_payments = Payment.objects.filter(
            lease__tenant=tenant
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # إجمالي الإيجار المستحق
        active_leases = tenant.leases.filter(status='active')
        total_rent_due = sum(lease.total_rent for lease in active_leases)
        
        return Response({
            'total_payments': float(total_payments),
            'total_rent_due': float(total_rent_due),
            'balance': float(total_rent_due - total_payments),
            'active_leases_count': active_leases.count()
        })


# ==================== Lease ViewSet ====================

class LeaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint للعقود
    
    list: الحصول على قائمة العقود
    retrieve: الحصول على تفاصيل عقد
    create: إنشاء عقد جديد
    update: تحديث عقد
    partial_update: تحديث جزئي لعقد
    destroy: حذف عقد
    """
    queryset = Lease.objects.select_related('unit', 'tenant', 'unit__building').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['contract_number', 'tenant__name', 'unit__unit_number']
    ordering_fields = ['start_date', 'end_date', 'monthly_rent']
    ordering = ['-start_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LeaseDetailSerializer
        return LeaseListSerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """العقود النشطة فقط"""
        leases = self.queryset.filter(status='active')
        serializer = self.get_serializer(leases, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """العقود القريبة من الانتهاء (90 يوم)"""
        today = timezone.now().date()
        expiry_date = today + timedelta(days=90)
        
        leases = self.queryset.filter(
            status='active',
            end_date__lte=expiry_date,
            end_date__gte=today
        )
        serializer = self.get_serializer(leases, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """دفعات العقد"""
        lease = self.get_object()
        payments = lease.payments.all().order_by('-payment_date')
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payment_summary(self, request, pk=None):
        """كشف حساب العقد"""
        lease = self.get_object()
        summary = lease.get_payment_summary()
        return Response(summary)
    
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """تجديد العقد"""
        lease = self.get_object()
        
        # التحقق من إمكانية التجديد
        if lease.status != 'active':
            return Response(
                {'error': 'لا يمكن تجديد عقد غير نشط'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # بيانات التجديد
        new_start_date = request.data.get('start_date')
        new_end_date = request.data.get('end_date')
        new_monthly_rent = request.data.get('monthly_rent', lease.monthly_rent)
        
        # إنشاء عقد جديد
        new_lease = Lease.objects.create(
            unit=lease.unit,
            tenant=lease.tenant,
            start_date=new_start_date,
            end_date=new_end_date,
            monthly_rent=new_monthly_rent,
            deposit_amount=lease.deposit_amount,
            status='active'
        )
        
        # تحديث العقد القديم
        lease.status = 'renewed'
        lease.save()
        
        serializer = LeaseDetailSerializer(new_lease)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """إلغاء العقد"""
        lease = self.get_object()
        
        if lease.status != 'active':
            return Response(
                {'error': 'لا يمكن إلغاء عقد غير نشط'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cancellation_reason = request.data.get('cancellation_reason', '')
        
        lease.status = 'cancelled'
        lease.cancellation_reason = cancellation_reason
        lease.cancellation_date = timezone.now().date()
        lease.save()
        
        serializer = LeaseDetailSerializer(lease)
        return Response(serializer.data)


# ==================== Payment ViewSet ====================

class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint للدفعات
    
    list: الحصول على قائمة الدفعات
    retrieve: الحصول على تفاصيل دفعة
    create: إنشاء دفعة جديدة
    update: تحديث دفعة
    partial_update: تحديث جزئي لدفعة
    destroy: حذف دفعة
    """
    queryset = Payment.objects.select_related('lease', 'lease__tenant', 'lease__unit').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['lease', 'payment_method', 'payment_for_month', 'payment_for_year']
    search_fields = ['lease__contract_number', 'lease__tenant__name', 'check_number']
    ordering_fields = ['payment_date', 'amount', 'created_at']
    ordering = ['-payment_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PaymentDetailSerializer
        return PaymentListSerializer
    
    @action(detail=False, methods=['get'])
    def by_month(self, request):
        """الدفعات حسب الشهر"""
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not month or not year:
            return Response(
                {'error': 'يجب تحديد الشهر والسنة'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payments = self.queryset.filter(
            payment_for_month=month,
            payment_for_year=year
        )
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """إحصائيات الدفعات"""
        # الفترة الزمنية
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.queryset
        if start_date and end_date:
            queryset = queryset.filter(
                payment_date__gte=start_date,
                payment_date__lte=end_date
            )
        
        # الإحصائيات
        stats = queryset.aggregate(
            total_amount=Sum('amount'),
            total_payments=Count('id'),
            avg_payment=Avg('amount')
        )
        
        # حسب طريقة الدفع
        by_method = queryset.values('payment_method').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        return Response({
            'total_amount': float(stats['total_amount'] or 0),
            'total_payments': stats['total_payments'],
            'average_payment': float(stats['avg_payment'] or 0),
            'by_payment_method': list(by_method)
        })


# ==================== Expense ViewSet ====================

class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint للمصروفات
    
    list: الحصول على قائمة المصروفات
    retrieve: الحصول على تفاصيل مصروف
    create: إنشاء مصروف جديد
    update: تحديث مصروف
    partial_update: تحديث جزئي لمصروف
    destroy: حذف مصروف
    """
    queryset = Expense.objects.select_related('building').all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['building', 'category']
    search_fields = ['description']
    ordering_fields = ['expense_date', 'amount', 'created_at']
    ordering = ['-expense_date']
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """المصروفات حسب الفئة"""
        expenses = self.queryset.values('category').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        return Response(expenses)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """إحصائيات المصروفات"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.queryset
        if start_date and end_date:
            queryset = queryset.filter(
                expense_date__gte=start_date,
                expense_date__lte=end_date
            )
        
        stats = queryset.aggregate(
            total_amount=Sum('amount'),
            total_expenses=Count('id'),
            avg_expense=Avg('amount')
        )
        
        return Response({
            'total_amount': float(stats['total_amount'] or 0),
            'total_expenses': stats['total_expenses'],
            'average_expense': float(stats['avg_expense'] or 0)
        })


# ==================== Invoice ViewSet ====================

class InvoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint للفواتير
    
    list: الحصول على قائمة الفواتير
    retrieve: الحصول على تفاصيل فاتورة
    create: إنشاء فاتورة جديدة
    update: تحديث فاتورة
    partial_update: تحديث جزئي لفاتورة
    destroy: حذف فاتورة
    """
    queryset = Invoice.objects.select_related('tenant').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tenant', 'status']
    search_fields = ['invoice_number', 'tenant__name']
    ordering_fields = ['issue_date', 'due_date', 'total_amount', 'created_at']
    ordering = ['-issue_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InvoiceDetailSerializer
        return InvoiceListSerializer
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """الفواتير المتأخرة"""
        today = timezone.now().date()
        invoices = self.queryset.filter(
            status='pending',
            due_date__lt=today
        )
        serializer = self.get_serializer(invoices, many=True)
        return Response(serializer.data)


# ==================== Overdue Notice ViewSet ====================

class PaymentOverdueNoticeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint للإنذارات (قراءة فقط)
    
    list: الحصول على قائمة الإنذارات
    retrieve: الحصول على تفاصيل إنذار
    """
    queryset = PaymentOverdueNotice.objects.select_related('lease', 'lease__tenant').all()
    serializer_class = PaymentOverdueNoticeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['lease', 'status']
    search_fields = ['notice_number', 'lease__contract_number', 'lease__tenant__name']
    ordering_fields = ['issue_date', 'due_date', 'created_at']
    ordering = ['-issue_date']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """الإنذارات النشطة"""
        notices = self.queryset.filter(status__in=['draft', 'sent', 'acknowledged'])
        serializer = self.get_serializer(notices, many=True)
        return Response(serializer.data)


# ==================== Reports API ====================

class ReportsViewSet(viewsets.ViewSet):
    """
    API endpoint للتقارير
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def financial(self, request):
        """تقرير مالي"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'يجب تحديد تاريخ البداية والنهاية'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # إجمالي الدخل
        total_income = Payment.objects.filter(
            payment_date__gte=start_date,
            payment_date__lte=end_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # إجمالي المصروفات
        total_expenses = Expense.objects.filter(
            expense_date__gte=start_date,
            expense_date__lte=end_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # صافي الدخل
        net_income = total_income - total_expenses
        
        # عدد الدفعات والعقود
        total_payments = Payment.objects.filter(
            payment_date__gte=start_date,
            payment_date__lte=end_date
        ).count()
        
        total_leases = Lease.objects.filter(status='active').count()
        
        # نسبة الإشغال
        total_units = Unit.objects.count()
        occupied_units = Unit.objects.filter(is_available=False).count()
        occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
        
        data = {
            'period': f"{start_date} to {end_date}",
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'net_income': float(net_income),
            'total_payments': total_payments,
            'total_leases': total_leases,
            'occupancy_rate': round(occupancy_rate, 2)
        }
        
        serializer = FinancialReportSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def leases(self, request):
        """تقرير العقود"""
        total_leases = Lease.objects.count()
        active_leases = Lease.objects.filter(status='active').count()
        expired_leases = Lease.objects.filter(status='expired').count()
        cancelled_leases = Lease.objects.filter(status='cancelled').count()
        
        # العقود القريبة من الانتهاء
        today = timezone.now().date()
        expiry_date = today + timedelta(days=90)
        expiring_soon = Lease.objects.filter(
            status='active',
            end_date__lte=expiry_date,
            end_date__gte=today
        ).count()
        
        # إجمالي الإيجار الشهري
        total_monthly_rent = Lease.objects.filter(
            status='active'
        ).aggregate(total=Sum('monthly_rent'))['total'] or Decimal('0')
        
        data = {
            'total_leases': total_leases,
            'active_leases': active_leases,
            'expired_leases': expired_leases,
            'cancelled_leases': cancelled_leases,
            'expiring_soon': expiring_soon,
            'total_monthly_rent': float(total_monthly_rent)
        }
        
        serializer = LeaseReportSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def occupancy(self, request):
        """تقرير الإشغال"""
        total_units = Unit.objects.count()
        occupied_units = Unit.objects.filter(is_available=False).count()
        available_units = total_units - occupied_units
        occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
        
        # حسب المبنى
        by_building = []
        for building in Building.objects.all():
            building_total = building.units.count()
            building_occupied = building.units.filter(is_available=False).count()
            building_rate = (building_occupied / building_total * 100) if building_total > 0 else 0
            
            by_building.append({
                'building_id': building.id,
                'building_name': building.name,
                'total_units': building_total,
                'occupied_units': building_occupied,
                'occupancy_rate': round(building_rate, 2)
            })
        
        data = {
            'total_units': total_units,
            'occupied_units': occupied_units,
            'available_units': available_units,
            'occupancy_rate': round(occupancy_rate, 2),
            'by_building': by_building
        }
        
        serializer = OccupancyReportSerializer(data)
        return Response(serializer.data)

"""
نظام التقارير المتقدمة - Advanced Reporting System
يوفر تقارير شاملة وتحليلات متقدمة لنظام إدارة الإيجارات
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Avg, Q, F, DecimalField
from django.db.models.functions import TruncMonth, TruncYear, Coalesce
from decimal import Decimal
from dateutil.relativedelta import relativedelta
import calendar
from datetime import datetime, timedelta


class ReportType(models.TextChoices):
    """أنواع التقارير"""
    PROFITABILITY = 'profitability', _('تقرير الربحية')
    CASH_FLOW = 'cash_flow', _('تقرير التدفق النقدي')
    OCCUPANCY = 'occupancy', _('تقرير معدل الإشغال')
    OVERDUE_TENANTS = 'overdue_tenants', _('تقرير المستأجرين المتأخرين')
    REVENUE = 'revenue', _('تقرير الإيرادات')
    EXPENSES = 'expenses', _('تقرير المصروفات')
    LEASE_EXPIRY = 'lease_expiry', _('تقرير انتهاء العقود')
    TENANT_RATING = 'tenant_rating', _('تقرير تقييم المستأجرين')
    UNIT_PERFORMANCE = 'unit_performance', _('تقرير أداء الوحدات')
    CUSTOM = 'custom', _('تقرير مخصص')


class ReportFormat(models.TextChoices):
    """صيغ التقارير"""
    PDF = 'pdf', _('PDF')
    EXCEL = 'excel', _('Excel')
    CSV = 'csv', _('CSV')
    JSON = 'json', _('JSON')
    HTML = 'html', _('HTML')


class ReportFrequency(models.TextChoices):
    """تكرار التقارير المجدولة"""
    DAILY = 'daily', _('يومي')
    WEEKLY = 'weekly', _('أسبوعي')
    MONTHLY = 'monthly', _('شهري')
    QUARTERLY = 'quarterly', _('ربع سنوي')
    YEARLY = 'yearly', _('سنوي')
    CUSTOM = 'custom', _('مخصص')


class ScheduledReport(models.Model):
    """التقارير المجدولة"""
    
    name = models.CharField(_("اسم التقرير"), max_length=200)
    description = models.TextField(_("الوصف"), blank=True, null=True)
    
    report_type = models.CharField(
        _("نوع التقرير"),
        max_length=50,
        choices=ReportType.choices
    )
    
    frequency = models.CharField(
        _("التكرار"),
        max_length=20,
        choices=ReportFrequency.choices,
        default=ReportFrequency.MONTHLY
    )
    
    format = models.CharField(
        _("الصيغة"),
        max_length=20,
        choices=ReportFormat.choices,
        default=ReportFormat.PDF
    )
    
    # المستلمون
    recipients = models.ManyToManyField(
        User,
        verbose_name=_("المستلمون"),
        related_name='scheduled_reports',
        help_text=_("المستخدمون الذين سيستلمون التقرير")
    )
    
    recipient_emails = models.TextField(
        _("بريد إلكتروني إضافي"),
        blank=True,
        null=True,
        help_text=_("عناوين بريد إلكتروني إضافية مفصولة بفواصل")
    )
    
    # الفلاتر والإعدادات
    filters = models.JSONField(
        _("الفلاتر"),
        default=dict,
        blank=True,
        help_text=_("فلاتر التقرير (مباني، وحدات، تواريخ، إلخ)")
    )
    
    # الجدولة
    is_active = models.BooleanField(_("مفعّل"), default=True)
    next_run = models.DateTimeField(_("التشغيل التالي"), null=True, blank=True)
    last_run = models.DateTimeField(_("آخر تشغيل"), null=True, blank=True)
    
    # التواريخ
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_scheduled_reports',
        verbose_name=_("أنشئ بواسطة")
    )
    
    class Meta:
        verbose_name = _("تقرير مجدول")
        verbose_name_plural = _("التقارير المجدولة")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"
    
    def calculate_next_run(self):
        """حساب موعد التشغيل التالي"""
        now = timezone.now()
        
        if self.frequency == ReportFrequency.DAILY:
            self.next_run = now + timedelta(days=1)
        elif self.frequency == ReportFrequency.WEEKLY:
            self.next_run = now + timedelta(weeks=1)
        elif self.frequency == ReportFrequency.MONTHLY:
            self.next_run = now + relativedelta(months=1)
        elif self.frequency == ReportFrequency.QUARTERLY:
            self.next_run = now + relativedelta(months=3)
        elif self.frequency == ReportFrequency.YEARLY:
            self.next_run = now + relativedelta(years=1)
        
        self.save(update_fields=['next_run'])


class GeneratedReport(models.Model):
    """التقارير المُنشأة"""
    
    scheduled_report = models.ForeignKey(
        ScheduledReport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_reports',
        verbose_name=_("التقرير المجدول")
    )
    
    report_type = models.CharField(
        _("نوع التقرير"),
        max_length=50,
        choices=ReportType.choices
    )
    
    title = models.CharField(_("العنوان"), max_length=200)
    
    # الفترة الزمنية
    start_date = models.DateField(_("تاريخ البداية"), null=True, blank=True)
    end_date = models.DateField(_("تاريخ النهاية"), null=True, blank=True)
    
    # البيانات
    data = models.JSONField(
        _("البيانات"),
        default=dict,
        help_text=_("بيانات التقرير المُنشأ")
    )
    
    # الملف
    file = models.FileField(
        _("الملف"),
        upload_to='reports/%Y/%m/',
        null=True,
        blank=True
    )
    
    format = models.CharField(
        _("الصيغة"),
        max_length=20,
        choices=ReportFormat.choices
    )
    
    # الحالة
    status = models.CharField(
        _("الحالة"),
        max_length=20,
        choices=[
            ('generating', _('قيد الإنشاء')),
            ('completed', _('مكتمل')),
            ('failed', _('فشل')),
            ('sent', _('تم الإرسال')),
        ],
        default='generating'
    )
    
    error_message = models.TextField(_("رسالة الخطأ"), blank=True, null=True)
    
    # التواريخ
    generated_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports',
        verbose_name=_("أنشئ بواسطة")
    )
    
    # الإحصائيات
    file_size = models.BigIntegerField(_("حجم الملف"), null=True, blank=True)
    download_count = models.IntegerField(_("عدد التنزيلات"), default=0)
    
    class Meta:
        verbose_name = _("تقرير مُنشأ")
        verbose_name_plural = _("التقارير المُنشأة")
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} - {self.generated_at.strftime('%Y-%m-%d')}"
    
    def increment_download_count(self):
        """زيادة عداد التنزيلات"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class ReportAnalytics(models.Model):
    """تحليلات التقارير"""
    
    # الفترة
    period_start = models.DateField(_("بداية الفترة"))
    period_end = models.DateField(_("نهاية الفترة"))
    period_type = models.CharField(
        _("نوع الفترة"),
        max_length=20,
        choices=[
            ('daily', _('يومي')),
            ('weekly', _('أسبوعي')),
            ('monthly', _('شهري')),
            ('quarterly', _('ربع سنوي')),
            ('yearly', _('سنوي')),
        ]
    )
    
    # الإيرادات
    total_revenue = models.DecimalField(
        _("إجمالي الإيرادات"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    rent_revenue = models.DecimalField(
        _("إيرادات الإيجار"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    other_revenue = models.DecimalField(
        _("إيرادات أخرى"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # المصروفات
    total_expenses = models.DecimalField(
        _("إجمالي المصروفات"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    maintenance_expenses = models.DecimalField(
        _("مصروفات الصيانة"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    operational_expenses = models.DecimalField(
        _("مصروفات تشغيلية"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # الربحية
    net_profit = models.DecimalField(
        _("صافي الربح"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    profit_margin = models.DecimalField(
        _("هامش الربح %"),
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    # الإشغال
    total_units = models.IntegerField(_("إجمالي الوحدات"), default=0)
    occupied_units = models.IntegerField(_("الوحدات المشغولة"), default=0)
    vacant_units = models.IntegerField(_("الوحدات الشاغرة"), default=0)
    occupancy_rate = models.DecimalField(
        _("معدل الإشغال %"),
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    # العقود
    active_leases = models.IntegerField(_("العقود النشطة"), default=0)
    new_leases = models.IntegerField(_("عقود جديدة"), default=0)
    expired_leases = models.IntegerField(_("عقود منتهية"), default=0)
    renewed_leases = models.IntegerField(_("عقود مجددة"), default=0)
    
    # المدفوعات
    total_payments = models.DecimalField(
        _("إجمالي المدفوعات"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    on_time_payments = models.IntegerField(_("دفعات في الموعد"), default=0)
    late_payments = models.IntegerField(_("دفعات متأخرة"), default=0)
    
    overdue_amount = models.DecimalField(
        _("المبالغ المتأخرة"),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # المستأجرون
    total_tenants = models.IntegerField(_("إجمالي المستأجرين"), default=0)
    new_tenants = models.IntegerField(_("مستأجرون جدد"), default=0)
    churned_tenants = models.IntegerField(_("مستأجرون مغادرون"), default=0)
    
    # التواريخ
    calculated_at = models.DateTimeField(_("تاريخ الحساب"), auto_now_add=True)
    updated_at = models.DateTimeField(_("آخر تحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("تحليلات التقرير")
        verbose_name_plural = _("تحليلات التقارير")
        ordering = ['-period_end']
        unique_together = ['period_start', 'period_end', 'period_type']
    
    def __str__(self):
        return f"تحليلات {self.period_start} - {self.period_end}"
    
    def calculate_metrics(self):
        """حساب جميع المقاييس"""
        from .models import Lease, Payment, Expense, Unit
        
        # حساب الإيرادات
        payments = Payment.objects.filter(
            payment_date__gte=self.period_start,
            payment_date__lte=self.period_end
        )
        
        self.total_revenue = payments.aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']
        
        self.rent_revenue = self.total_revenue  # يمكن تخصيصه حسب نوع الدفعة
        
        # حساب المصروفات
        expenses = Expense.objects.filter(
            expense_date__gte=self.period_start,
            expense_date__lte=self.period_end
        )
        
        self.total_expenses = expenses.aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']
        
        # حساب الربحية
        self.net_profit = self.total_revenue - self.total_expenses
        
        if self.total_revenue > 0:
            self.profit_margin = (self.net_profit / self.total_revenue) * 100
        
        # حساب الإشغال
        self.total_units = Unit.objects.count()
        self.occupied_units = Unit.objects.filter(is_available=False).count()
        self.vacant_units = self.total_units - self.occupied_units
        
        if self.total_units > 0:
            self.occupancy_rate = (self.occupied_units / self.total_units) * 100
        
        # حساب العقود
        self.active_leases = Lease.objects.filter(
            status='active',
            start_date__lte=self.period_end,
            end_date__gte=self.period_start
        ).count()
        
        self.new_leases = Lease.objects.filter(
            start_date__gte=self.period_start,
            start_date__lte=self.period_end
        ).count()
        
        self.expired_leases = Lease.objects.filter(
            end_date__gte=self.period_start,
            end_date__lte=self.period_end,
            status='expired'
        ).count()
        
        self.save()


class DashboardWidget(models.Model):
    """ويدجت لوحة التحكم"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dashboard_widgets',
        verbose_name=_("المستخدم")
    )
    
    widget_type = models.CharField(
        _("نوع الويدجت"),
        max_length=50,
        choices=[
            ('revenue_chart', _('مخطط الإيرادات')),
            ('occupancy_gauge', _('مقياس الإشغال')),
            ('cash_flow', _('التدفق النقدي')),
            ('overdue_list', _('قائمة المتأخرين')),
            ('lease_expiry', _('انتهاء العقود')),
            ('recent_payments', _('المدفوعات الأخيرة')),
            ('kpi_cards', _('بطاقات المؤشرات')),
            ('tenant_rating', _('تقييم المستأجرين')),
        ]
    )
    
    title = models.CharField(_("العنوان"), max_length=200)
    
    # الإعدادات
    config = models.JSONField(
        _("الإعدادات"),
        default=dict,
        blank=True,
        help_text=_("إعدادات الويدجت (ألوان، فلاتر، إلخ)")
    )
    
    # الترتيب والعرض
    position = models.IntegerField(_("الموضع"), default=0)
    width = models.IntegerField(_("العرض"), default=6, help_text=_("من 1 إلى 12"))
    height = models.IntegerField(_("الارتفاع"), default=300)
    
    is_visible = models.BooleanField(_("مرئي"), default=True)
    
    # التواريخ
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("آخر تحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("ويدجت لوحة التحكم")
        verbose_name_plural = _("ويدجتات لوحة التحكم")
        ordering = ['user', 'position']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

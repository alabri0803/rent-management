from django.contrib import admin
from .models import (
    Building, Unit, Tenant, Lease, Payment, MaintenanceRequest, Document, Expense, Notification, Company, ContractTemplate, Invoice, InvoiceItem,
    RealEstateOffice, BuildingOwner, CommissionAgreement, RentCollection, CommissionDistribution, PaymentOverdueNotice, NoticeTemplate
)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'contact_phone')

@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ('title',)

# تخصيص عرض المباني والوحدات
@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name',)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'building', 'unit_type', 'floor', 'is_available')
    list_filter = ('building', 'unit_type', 'is_available')
    search_fields = ('unit_number', 'building__name')

# تخصيص عرض المستأجرين
@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant_type', 'phone', 'email', 'user', 'rating')
    list_filter = ('tenant_type', 'rating')
    search_fields = ('name', 'phone', 'email')

# تخصيص عرض العقود
@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'tenant', 'unit', 'start_date', 'end_date', 'monthly_rent', 'status')
    list_filter = ('status', 'unit__building')
    search_fields = ('contract_number', 'tenant__name', 'unit__unit_number')
    date_hierarchy = 'start_date'

# تخصيص عرض المدفوعات
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('lease', 'payment_date', 'amount', 'payment_for_month', 'payment_for_year')
    list_filter = ('payment_for_year',)
    search_fields = ('lease__contract_number', 'lease__tenant__name')
    date_hierarchy = 'payment_date'

# تخصيص عرض طلبات الصيانة
@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'lease', 'priority', 'status', 'reported_date')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'lease__contract_number')

# تخصيص عرض المصاريف
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'building', 'category', 'amount', 'expense_date')
    list_filter = ('category', 'building')
    search_fields = ('description',)
    date_hierarchy = 'expense_date'

# تسجيل نموذج المستندات (عرض افتراضي)
admin.site.register(Document)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'read', 'timestamp')
    list_filter = ('read', 'user')

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'tenant', 'lease', 'issue_date', 'due_date', 'total_amount', 'status')
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('invoice_number', 'tenant__name', 'lease__contract_number')
    inlines = [InvoiceItemInline]


# === Real Estate Office Management Admin ===

@admin.register(RealEstateOffice)
class RealEstateOfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_number', 'contact_person', 'phone', 'commission_rate', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'license_number', 'contact_person', 'phone')
    ordering = ('name',)


@admin.register(BuildingOwner)
class BuildingOwnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_type', 'phone', 'email', 'is_active')
    list_filter = ('owner_type', 'is_active')
    search_fields = ('name', 'phone', 'email', 'national_id')
    ordering = ('name',)


@admin.register(CommissionAgreement)
class CommissionAgreementAdmin(admin.ModelAdmin):
    list_display = ('agreement_number', 'real_estate_office', 'building_owner', 'building', 'commission_rate', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'real_estate_office', 'building')
    search_fields = ('agreement_number', 'real_estate_office__name', 'building_owner__name', 'building__name')
    date_hierarchy = 'start_date'
    ordering = ('-created_at',)


@admin.register(RentCollection)
class RentCollectionAdmin(admin.ModelAdmin):
    list_display = ('lease', 'real_estate_office', 'collection_date', 'amount_collected', 'collection_method', 'status')
    list_filter = ('status', 'collection_method', 'real_estate_office')
    search_fields = ('lease__contract_number', 'lease__tenant__name', 'real_estate_office__name')
    date_hierarchy = 'collection_date'
    ordering = ('-collection_date',)


@admin.register(CommissionDistribution)
class CommissionDistributionAdmin(admin.ModelAdmin):
    list_display = ('building_owner', 'rent_collection', 'owner_share', 'office_commission', 'distribution_date', 'status')
    list_filter = ('status', 'building_owner', 'commission_agreement__real_estate_office')
    search_fields = ('building_owner__name', 'rent_collection__lease__contract_number', 'payment_reference')
    date_hierarchy = 'distribution_date'
    ordering = ('-created_at',)


@admin.register(PaymentOverdueNotice)
class PaymentOverdueNoticeAdmin(admin.ModelAdmin):
    list_display = ('lease', 'overdue_month', 'overdue_year', 'overdue_amount', 'notice_date', 'legal_deadline', 'status')
    list_filter = ('status', 'overdue_year', 'potential_legal_action', 'notice_date')
    search_fields = ('lease__contract_number', 'lease__tenant__name', 'lease__unit__unit_number')
    date_hierarchy = 'notice_date'
    readonly_fields = ('legal_deadline',)
    
    fieldsets = (
        ('معلومات الإنذار', {
            'fields': ('lease', 'overdue_month', 'overdue_year', 'overdue_amount', 'due_date')
        }),
        ('تواريخ مهمة', {
            'fields': ('notice_date', 'legal_deadline', 'status', 'potential_legal_action')
        }),
        ('متابعة الإنذار', {
            'fields': ('sent_date', 'acknowledged_date', 'resolved_date', 'delivery_method', 'recipient_signature')
        }),
        ('ملاحظات', {
            'fields': ('notes',)
        }),
    )
    
    actions = ['mark_as_sent', 'mark_as_acknowledged', 'mark_as_resolved', 'generate_notice_content']
    
    def mark_as_sent(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='sent', sent_date=timezone.now())
        self.message_user(request, f"تم تحديث حالة {queryset.count()} إنذار إلى 'تم الإرسال'")
    mark_as_sent.short_description = "تحديد كـ مُرسل"
    
    def mark_as_acknowledged(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='acknowledged', acknowledged_date=timezone.now())
        self.message_user(request, f"تم تحديث حالة {queryset.count()} إنذار إلى 'تم الاستلام'")
    mark_as_acknowledged.short_description = "تحديد كـ مُستلم"
    
    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='resolved', resolved_date=timezone.now())
        self.message_user(request, f"تم تحديث حالة {queryset.count()} إنذار إلى 'تم الحل'")
    mark_as_resolved.short_description = "تحديد كـ محلول"
    
    def generate_notice_content(self, request, queryset):
        for notice in queryset:
            content = notice.get_notice_content()
            # يمكن إضافة منطق لحفظ المحتوى أو إرساله
        self.message_user(request, f"تم إنشاء محتوى الإنذار لـ {queryset.count()} إنذار")
    generate_notice_content.short_description = "إنشاء محتوى الإنذار"


@admin.register(NoticeTemplate)
class NoticeTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'is_active', 'created_date', 'updated_date')
    list_filter = ('template_type', 'is_active', 'created_date')
    search_fields = ('name', 'subject', 'content')
    
    fieldsets = (
        ('معلومات القالب', {
            'fields': ('name', 'template_type', 'subject', 'is_active')
        }),
        ('المحتوى', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('ملاحظات قانونية', {
            'fields': ('legal_compliance_notes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # تحرير قالب موجود
            return ('created_date', 'updated_date')
        return ()
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
import os
import io
import zipfile
import shutil
import tempfile
from datetime import datetime, timedelta
from django.core.management import call_command

def login_redirect(request):
    if request.user.is_staff:
        return redirect('dashboard_home')
    else:
        return redirect('portal_dashboard')
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.db import transaction
from dateutil.relativedelta import relativedelta
from io import BytesIO
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from django import forms
import json
from django.views.decorators.http import require_POST
import logging
from decimal import Decimal
logger = logging.getLogger(__name__)

from .models import (
    Tenant, Unit, Building, Lease, Document, MaintenanceRequest, 
    Expense, Payment, Company, Invoice, InvoiceItem,
    RealEstateOffice, BuildingOwner, CommissionAgreement, RentCollection, CommissionDistribution, SecurityDeposit,
    PaymentOverdueNotice, NoticeTemplate, LeaseRenewalReminder
)
from .forms import (
    TenantForm, UnitForm, BuildingForm, LeaseForm, DocumentForm, 
    MaintenanceRequestUpdateForm, ExpenseForm, PaymentForm, LeaseCancelForm, 
    CompanyForm, TenantRatingForm, InvoiceForm, InvoiceItemFormSet,
    RealEstateOfficeForm, BuildingOwnerForm, CommissionAgreementForm, 
    RentCollectionForm, CommissionDistributionForm, SecurityDepositForm,
    UserManagementForm
)
from .utils import render_to_pdf, generate_pdf_bytes

# --- Backup Utilities ---
def perform_backup() -> str:
    """Create a timestamped zip backup containing DB JSON dump and media files.
    Returns the absolute path to the created backup file.
    """
    backups_dir = os.path.join(str(settings.BASE_DIR), 'backups')
    os.makedirs(backups_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_zip_path = os.path.join(backups_dir, f'backup_{timestamp}.zip')

    # Create in-memory DB dump
    db_io = io.StringIO()
    call_command('dumpdata', '--natural-foreign', '--natural-primary', '--indent', '2', stdout=db_io)
    db_data = db_io.getvalue().encode('utf-8')

    with zipfile.ZipFile(backup_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        # Add DB dump
        zf.writestr('db.json', db_data)

        # Add media directory if exists
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root and os.path.isdir(media_root):
            for root, dirs, files in os.walk(media_root):
                for file in files:
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, media_root)
                    zf.write(abs_path, arcname=os.path.join('media', rel_path))

    return backup_zip_path

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
def backup_now(request):
    try:
        path = perform_backup()
        messages.success(request, _("تم إنشاء نسخة احتياطية بنجاح: ") + os.path.basename(path))
    except Exception as e:
        logger.exception("Backup failed")
        messages.error(request, _("فشل إنشاء النسخة الاحتياطية."))
    # Redirect back to dashboard or referrer
    return redirect(request.META.get('HTTP_REFERER') or 'dashboard_home')

from django.contrib.auth import logout as auth_logout

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
def custom_logout(request):
    """Trigger a backup, then log the user out and redirect to login page."""
    try:
        perform_backup()
    except Exception:
        logger.exception("Backup during logout failed")
        # Proceed with logout even if backup fails
    auth_logout(request)
    messages.info(request, _("تم تسجيل الخروج."))
    return redirect(settings.LOGOUT_REDIRECT_URL or 'login')

# --- Restore Utilities & Views ---
@login_required
@user_passes_test(lambda u: u.is_staff)
def backup_restore_page(request):
    """Simple page to upload or select an existing backup to restore."""
    backups_dir = os.path.join(str(settings.BASE_DIR), 'backups')
    os.makedirs(backups_dir, exist_ok=True)
    available = []
    try:
        for name in sorted(os.listdir(backups_dir), reverse=True):
            if name.endswith('.zip'):
                available.append(name)
    except Exception:
        logger.exception("Failed listing backups")
    return render(request, 'dashboard/backup_restore.html', {
        'available_backups': available
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
def restore_backup(request):
    """Restore database and media from a provided backup zip (upload or existing file name).
    WARNING: Restoring may overwrite existing data and media files.
    """
    backups_dir = os.path.join(str(settings.BASE_DIR), 'backups')
    os.makedirs(backups_dir, exist_ok=True)

    uploaded = request.FILES.get('backup_file')
    chosen_name = request.POST.get('backup_name', '').strip()

    if uploaded:
        # Save uploaded file to backups dir
        target_path = os.path.join(backups_dir, uploaded.name)
        with open(target_path, 'wb+') as dst:
            for chunk in uploaded.chunks():
                dst.write(chunk)
        backup_zip_path = target_path
    elif chosen_name:
        backup_zip_path = os.path.join(backups_dir, chosen_name)
        if not os.path.isfile(backup_zip_path):
            messages.error(request, _("الملف المحدد غير موجود."))
            return redirect('dashboard_backup_restore_page')
    else:
        messages.error(request, _("الرجاء اختيار أو رفع ملف النسخة الاحتياطية."))
        return redirect('dashboard_backup_restore_page')

    try:
        temp_dir = tempfile.mkdtemp(prefix='restore_', dir=backups_dir)
        with zipfile.ZipFile(backup_zip_path, 'r') as zf:
            zf.extractall(temp_dir)

        # Restore DB if db.json present
        db_json_path = os.path.join(temp_dir, 'db.json')
        if os.path.isfile(db_json_path):
            # Consider flushing? We avoid destructive flush by default.
            call_command('loaddata', db_json_path)

        # Restore media if present
        extracted_media = os.path.join(temp_dir, 'media')
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root and os.path.isdir(extracted_media):
            for root, dirs, files in os.walk(extracted_media):
                rel = os.path.relpath(root, extracted_media)
                dest_dir = os.path.join(media_root, rel) if rel != '.' else media_root
                os.makedirs(dest_dir, exist_ok=True)
                for f in files:
                    src = os.path.join(root, f)
                    dst = os.path.join(dest_dir, f)
                    shutil.copy2(src, dst)

        messages.success(request, _("تمت عملية الاسترجاع بنجاح."))
    except Exception:
        logger.exception("Restore failed")
        messages.error(request, _("فشلت عملية الاسترجاع. الرجاء التحقق من الملف والصلاحيات."))
    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

    return redirect('dashboard_backup_restore_page')

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

# --- Dashboard Home ---
class DashboardHomeView(StaffRequiredMixin, ListView):
    model = Lease
    template_name = 'dashboard/home.html'
    context_object_name = 'leases'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now()

        # Stats Cards
        active_leases = Lease.objects.filter(status__in=['active', 'expiring_soon'])
        monthly_expenses = Expense.objects.filter(expense_date__year=today.year, expense_date__month=today.month).aggregate(total=Sum('amount'))['total'] or 0
        expected_income = active_leases.aggregate(total=Sum('monthly_rent'))['total'] or 0

        context['stats'] = {
            'active_count': active_leases.count(),
            'expected_monthly_income': expected_income,
            'monthly_expenses': monthly_expenses,
            'net_income': expected_income - monthly_expenses
        }

        # Financial Trend Chart (Last 12 months)
        trend_chart = {'labels': [], 'income_data': [], 'expense_data': []}
        for i in range(12, 0, -1):
            date = today - relativedelta(months=i-1)
            month_name_en = date.strftime("%b")
            trend_chart['labels'].append(month_name_en)
            monthly_income = Payment.objects.filter(payment_date__year=date.year, payment_date__month=date.month).aggregate(total=Sum('amount'))['total'] or 0
            trend_chart['income_data'].append(float(monthly_income))
            monthly_expenses_trend = Expense.objects.filter(expense_date__year=date.year, expense_date__month=date.month).aggregate(total=Sum('amount'))['total'] or 0
            trend_chart['expense_data'].append(float(monthly_expenses_trend))
        context['trend_chart'] = trend_chart

        # Recent financial movements (locked behind password)
        finance_unlocked = self.request.session.get('finance_unlocked', False)
        context['finance_unlocked'] = finance_unlocked
        if finance_unlocked:
            recent_payments = Payment.objects.order_by('-payment_date')[:5]
            recent_expenses = Expense.objects.order_by('-expense_date')[:5]
            recent_distributions = CommissionDistribution.objects.select_related(
                'rent_collection__lease__tenant', 'commission_agreement__real_estate_office', 'building_owner'
            ).order_by('-created_at')[:5]
        else:
            recent_payments = []
            recent_expenses = []
            recent_distributions = []
        context['recent_payments'] = recent_payments
        context['recent_expenses'] = recent_expenses
        context['recent_distributions'] = recent_distributions

        context['recent_requests'] = MaintenanceRequest.objects.order_by('-reported_date')[:5]

        total_units = Unit.objects.count()
        occupied_units = Unit.objects.filter(is_available=False).count()
        available_units = total_units - occupied_units
        context['occupancy_chart'] = {
            'labels': [_("مشغولة"), _("متاحة")],
            'data': [occupied_units, available_units],
        }
        # ADDED: Calendar data for renewals
        renewals = Lease.objects.filter(end_date__gte=today.date())
        calendar_events = []
        for renewal in renewals:
            calendar_events.append({
                'title': f"{_('تجديد')}: {renewal.tenant.name} - {_('وحدة')} {renewal.unit.unit_number}",
                'start': renewal.end_date.isoformat(),
                'allDay': True,
                'url': reverse('lease_detail', kwargs={'pk': renewal.pk}),
                'extendedProps': {
                    'contract_number': renewal.contract_number,
                    'days_until_expiry': renewal.days_until_expiry()
                }
            })
        context['calendar_events'] = json.dumps(calendar_events)
        # Alerts for expiring leases
        expiring_soon = Lease.objects.filter(
            status='expiring_soon',
            end_date__gte=today.date()
        ).order_by('end_date')[:5]
        context['expiring_leases'] = expiring_soon

        return context

# --- User Management ---
class UserListView(StaffRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/user_management.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.all().prefetch_related('groups').order_by('username')

class UserCreateView(StaffRequiredMixin, CreateView):
    model = User
    form_class = UserManagementForm
    template_name = 'dashboard/user_form.html'
    success_url = reverse_lazy('user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Add New User")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("User created successfully!"))
        return super().form_valid(form)

class UserUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = UserManagementForm
    template_name = 'dashboard/user_form.html'
    success_url = reverse_lazy('user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Edit User")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("User updated successfully!"))
        return super().form_valid(form)

class UserDeleteView(StaffRequiredMixin, DeleteView):
    model = User
    template_name = 'dashboard/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        if self.object == self.request.user:
            messages.error(self.request, _("You cannot delete your own account."))
            return redirect(self.success_url)
        messages.success(self.request, _("User deleted successfully."))
        return super().form_valid(form)


# --- Finance Lock/Unlock ---
@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
def finance_unlock(request):
    """Unlock viewing of recent financial movements after confirming password."""
    password = request.POST.get('password', '')
    user = request.user
    if user.check_password(password):
        request.session['finance_unlocked'] = True
        messages.success(request, _("تم إظهار الحركات المالية بنجاح."))
    else:
        messages.error(request, _("كلمة المرور غير صحيحة."))
    return redirect('dashboard_home')

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
def finance_lock(request):
    """Lock viewing of recent financial movements."""
    request.session['finance_unlocked'] = False
    messages.info(request, _("تم إخفاء الحركات المالية."))
    return redirect('dashboard_home')

# --- Units Management ---
class UnitListView(StaffRequiredMixin, ListView):
    model = Unit
    template_name = 'dashboard/unit_list.html'
    context_object_name = 'units'
    paginate_by = 5

    def get_queryset(self):
        queryset = Unit.objects.all().select_related('building').order_by('building', 'unit_number')
        search_query = self.request.GET.get('q', '')
        building_filter = self.request.GET.get('building', '')
        status_filter = self.request.GET.get('status', '')
        unit_type_filter = self.request.GET.get('unit_type', '')
        
        if search_query:
            queryset = queryset.filter(Q(unit_number__icontains=search_query) | Q(building__name__icontains=search_query))
        if building_filter:
            queryset = queryset.filter(building_id=building_filter)
        if status_filter == 'available':
            queryset = queryset.filter(is_available=True)
        elif status_filter == 'occupied':
            queryset = queryset.filter(is_available=False)
        if unit_type_filter:
            queryset = queryset.filter(unit_type=unit_type_filter)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['buildings'] = Building.objects.all()
        context['unit_type_choices'] = Unit.UNIT_TYPE_CHOICES
        context['total_units'] = Unit.objects.count()
        context['available_units'] = Unit.objects.filter(is_available=True).count()
        context['occupied_units'] = Unit.objects.filter(is_available=False).count()
        return context

class UnitDetailView(StaffRequiredMixin, DetailView):
    model = Unit
    template_name = 'dashboard/unit_detail.html'
    context_object_name = 'unit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_lease'] = Lease.objects.filter(unit=self.object, status__in=['active', 'expiring_soon']).first()
        context['lease_history'] = Lease.objects.filter(unit=self.object).order_by('-start_date')
        return context

class UnitCreateView(StaffRequiredMixin, CreateView):
    model = Unit
    form_class = UnitForm
    template_name = 'dashboard/unit_form.html'
    success_url = reverse_lazy('unit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("إضافة وحدة جديدة")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تمت إضافة الوحدة بنجاح!"))
        return super().form_valid(form)

class UnitUpdateView(StaffRequiredMixin, UpdateView):
    model = Unit
    form_class = UnitForm
    template_name = 'dashboard/unit_form.html'
    success_url = reverse_lazy('unit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تعديل الوحدة")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث الوحدة بنجاح!"))
        return super().form_valid(form)

class UnitDeleteView(StaffRequiredMixin, DeleteView):
    model = Unit
    template_name = 'dashboard/unit_confirm_delete.html'
    success_url = reverse_lazy('unit_list')

    def form_valid(self, form):
        messages.success(self.request, _("تم حذف الوحدة بنجاح."))
        return super().form_valid(form)

# --- Tenants Management ---
class TenantListView(StaffRequiredMixin, ListView):
    model = Tenant
    template_name = 'dashboard/tenant_list.html'
    context_object_name = 'tenants'
    paginate_by = 20

    def get_queryset(self):
        from django.db.models import Q, Count, Sum
        qs = Tenant.objects.all()
        q = self.request.GET.get('q', '').strip()
        ttype = self.request.GET.get('type', '').strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(phone__icontains=q) | Q(email__icontains=q))
        if ttype in ['individual', 'company']:
            qs = qs.filter(tenant_type=ttype)
        # Annotate active/expiring leases count and total monthly rent
        qs = qs.annotate(
            active_leases_count=Count('lease', filter=Q(lease__status__in=['active', 'expiring_soon'])),
            total_monthly_rent=Sum('lease__monthly_rent', filter=Q(lease__status__in=['active', 'expiring_soon']))
        ).order_by('name')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # إحصائيات المستأجرين
        all_tenants = Tenant.objects.all()
        individual_count = all_tenants.filter(tenant_type='individual').count()
        company_count = all_tenants.filter(tenant_type='company').count()
        total_count = all_tenants.count()
        
        context['stats'] = {
            'individual_count': individual_count,
            'company_count': company_count,
            'total_count': total_count,
        }
        
        # للتوافق مع الكود القديم
        context['total_tenants'] = total_count
        context['individual_tenants'] = individual_count
        context['company_tenants'] = company_count
        
        return context

class TenantDetailView(StaffRequiredMixin, DetailView):
    model = Tenant
    template_name = 'dashboard/tenant_detail.html'
    context_object_name = 'tenant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_leases'] = Lease.objects.filter(tenant=self.object, status__in=['active', 'expiring_soon'])
        context['lease_history'] = Lease.objects.filter(tenant=self.object).order_by('-start_date')
        context['total_payments'] = Payment.objects.filter(lease__tenant=self.object).aggregate(total=Sum('amount'))['total'] or 0
        return context

class TenantCreateView(StaffRequiredMixin, CreateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'dashboard/tenant_form.html'
    success_url = reverse_lazy('tenant_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("إضافة مستأجر جديد")
        return context

    def form_valid(self, form):
        logger.info(f"Creating new tenant with data: {form.cleaned_data}")
        messages.success(self.request, _("تمت إضافة المستأجر بنجاح!"))
        return super().form_valid(form)
    
    def form_invalid(self, form):
        logger.error(f"Tenant form validation failed. Errors: {form.errors}")
        logger.error(f"Form data: {form.data}")
        messages.error(self.request, _("حدث خطأ في حفظ البيانات. يرجى التحقق من المعلومات المدخلة."))
        return super().form_invalid(form)

class TenantUpdateView(StaffRequiredMixin, UpdateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'dashboard/tenant_form.html'
    success_url = reverse_lazy('tenant_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تعديل بيانات المستأجر")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث بيانات المستأجر بنجاح!"))
        return super().form_valid(form)

class TenantDeleteView(StaffRequiredMixin, DeleteView):
    model = Tenant
    template_name = 'dashboard/tenant_confirm_delete.html'
    success_url = reverse_lazy('tenant_list')

    def form_valid(self, form):
        messages.success(self.request, _("تم حذف المستأجر بنجاح."))
        return super().form_valid(form)

# --- Buildings Management ---
class BuildingListView(StaffRequiredMixin, ListView):
    model = Building
    template_name = 'dashboard/building_list.html'
    context_object_name = 'buildings'
    paginate_by = 20

    def get_queryset(self):
        return Building.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for building in context['buildings']:
            building.total_units = building.unit_set.count()
            building.occupied_units = building.unit_set.filter(is_available=False).count()
            building.occupancy_rate = (building.occupied_units / building.total_units * 100) if building.total_units > 0 else 0
        return context

class BuildingCreateView(StaffRequiredMixin, CreateView):
    model = Building
    form_class = BuildingForm
    template_name = 'dashboard/building_form.html'
    success_url = reverse_lazy('building_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("إضافة مبنى جديد")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تمت إضافة المبنى بنجاح!"))
        return super().form_valid(form)

class BuildingUpdateView(StaffRequiredMixin, UpdateView):
    model = Building
    form_class = BuildingForm
    template_name = 'dashboard/building_form.html'
    success_url = reverse_lazy('building_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تعديل المبنى")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث المبنى بنجاح!"))
        return super().form_valid(form)

class BuildingDeleteView(StaffRequiredMixin, DeleteView):
    model = Building
    template_name = 'dashboard/building_confirm_delete.html'
    success_url = reverse_lazy('building_list')

    def form_valid(self, form):
        messages.success(self.request, _("تم حذف المبنى بنجاح."))
        return super().form_valid(form)

# --- Leases ---
class LeaseListView(StaffRequiredMixin, ListView):
    model = Lease
    template_name = 'dashboard/lease_list.html'
    context_object_name = 'leases'
    paginate_by = 10
    def get_queryset(self):
        # Support filtering by status via ?status=; default shows active+expiring_soon
        status = self.request.GET.get('status', '').strip()
        valid_statuses = {k for k, _ in Lease.STATUS_CHOICES}
        if status == 'all':
            queryset = Lease.objects.all()
        elif status in valid_statuses:
            queryset = Lease.objects.filter(status=status)
        else:
            queryset = Lease.objects.filter(status__in=['active', 'expiring_soon'])
        queryset = queryset.order_by('-start_date')
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(Q(contract_number__icontains=search_query) | Q(tenant__name__icontains=search_query) | Q(unit__unit_number__icontains=search_query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '').strip()
        context['status_choices'] = Lease.STATUS_CHOICES
        # This loop is inefficient, status should be updated by a scheduled task
        # for lease in Lease.objects.all(): lease.save() 
        active_leases = Lease.objects.filter(status='active')
        today = timezone.now()
        monthly_expenses = Expense.objects.filter(expense_date__year=today.year, expense_date__month=today.month).aggregate(total=Sum('amount'))['total'] or 0
        gross_income = active_leases.aggregate(total=Sum('monthly_rent'))['total'] or 0
        context['stats'] = {
            'active_count': active_leases.count(),
            'expiring_count': Lease.objects.filter(status='expiring_soon').count(),
            'expired_count': Lease.objects.filter(status='expired').count(),
            'total_units': Unit.objects.count(),
            'available_units': Unit.objects.filter(is_available=True).count(),
            'expected_monthly_income': gross_income,
            'monthly_expenses': monthly_expenses,
            'net_income': gross_income - monthly_expenses
        }
        status_counts = Lease.objects.values('status').annotate(count=Count('status'))
        chart_data = {'labels': [], 'data': []}
        status_display_map = dict(Lease.STATUS_CHOICES)
        for item in status_counts:
            chart_data['labels'].append(str(status_display_map.get(item['status'], item['status'])))
            chart_data['data'].append(item['count'])
        context['chart_data'] = chart_data
        return context

class LeaseDetailView(StaffRequiredMixin, DetailView):
    model = Lease
    template_name = 'dashboard/lease_detail.html'
    context_object_name = 'lease'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_form'] = DocumentForm()
        context['payment_summary'] = self.object.get_payment_summary() # MODIFIED name
        context['total_paid'] = self.object.payments.aggregate(total=Sum('amount'))['total'] or 0
        context['rating_form'] = TenantRatingForm(instance=self.object.tenant) # ADDED
        return context

# ADDED: View to handle tenant rating update
class UpdateTenantRatingView(StaffRequiredMixin, View):
    def post(self, request, pk):
        tenant = get_object_or_404(Tenant, pk=pk)
        form = TenantRatingForm(request.POST, instance=tenant)
        if form.is_valid():
            form.save()
            messages.success(request, _("تم تحديث تقييم العميل."))
        else:
            messages.error(request, _("حدث خطأ أثناء تحديث التقييم."))

        lease = Lease.objects.filter(tenant=tenant).first()
        return redirect('lease_detail', pk=lease.pk)

class LeaseCreateView(StaffRequiredMixin, CreateView):
    model = Lease; form_class = LeaseForm; template_name = 'dashboard/lease_form.html'; success_url = reverse_lazy('lease_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); context['title'] = _("إضافة عقد جديد"); return context
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("تمت إضافة العقد بنجاح!"))
        # Add message about registration invoice
        messages.info(self.request, _("يمكنك الآن إنشاء فاتورة رسوم التسجيل من صفحة تفاصيل العقد"))
        return response

class LeaseUpdateView(StaffRequiredMixin, UpdateView):
    model = Lease; form_class = LeaseForm; template_name = 'dashboard/lease_form.html'; success_url = reverse_lazy('lease_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); context['title'] = _("تعديل العقد"); return context
    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث العقد بنجاح!")); return super().form_valid(form)

class LeaseDeleteView(StaffRequiredMixin, DeleteView):
    model = Lease
    template_name = 'dashboard/lease_confirm_delete.html'
    success_url = reverse_lazy('lease_list')
    
    def form_valid(self, form):
        # حفظ مرجع للوحدة قبل حذف العقد
        unit = self.object.unit
        contract_number = self.object.contract_number
        
        try:
            # تحديث حالة الوحدة إلى متاحة عند حذف العقد
            if unit:
                unit.is_available = True
                unit.save()
                
            # حذف العقد
            result = super().form_valid(form)
            
            messages.success(self.request, _(f"تم حذف العقد {contract_number} بنجاح وتم تحرير الوحدة {unit}."))
            return result
            
        except Exception as e:
            messages.error(self.request, _(f"حدث خطأ أثناء حذف العقد: {str(e)}"))
            return self.form_invalid(form)

# ADDED: Lease Cancellation View
class LeaseCancelView(StaffRequiredMixin, UpdateView):
    model = Lease
    form_class = LeaseCancelForm
    template_name = 'dashboard/lease_cancel_form.html'
    context_object_name = 'lease'

    def get_success_url(self):
        return reverse('lease_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        lease = form.save(commit=False)
        lease.status = 'cancelled'
        lease.cancellation_date = timezone.now().date()
        lease.unit.is_available = True
        lease.unit.save()
        lease.save()
        # استمارة الإلغاء ستُنشأ تلقائياً من خلال دالة save() في النموذج
        messages.success(self.request, _("تم إلغاء العقد وإرفاق استمارة الإلغاء بنجاح."))
        return super().form_valid(form)

# ... (renew_lease, Document views, Maintenance views, Expense views remain similar) ...

@login_required
@user_passes_test(lambda u: u.is_staff)
def renew_lease(request, pk):
    original_lease = get_object_or_404(Lease, pk=pk)
    # Block renewal if not within 3 months window
    if not original_lease.can_renew():
        messages.error(request, _("لا يمكن تجديد العقد إلا قبل 3 أشهر من تاريخ الانتهاء."))
        return redirect('lease_detail', pk=pk)
    if request.method == 'POST':
        duration = request.POST.get('duration')
        new_start_date = original_lease.end_date + relativedelta(days=1)
        if duration == '1y': new_end_date = new_start_date + relativedelta(years=1, days=-1)
        elif duration == '6m': new_end_date = new_start_date + relativedelta(months=6, days=-1)
        elif duration == '3m': new_end_date = new_start_date + relativedelta(months=3, days=-1)
        else:
            new_end_date = request.POST.get('manual_date')
            if not new_end_date:
                messages.error(request, _("الرجاء إدخال تاريخ انتهاء صحيح.")); return redirect('lease_detail', pk=pk)

        # Create a new contract number to avoid unique constraint issues
        new_contract_number = f"{original_lease.contract_number}-R{Lease.objects.filter(contract_number__startswith=original_lease.contract_number).count()}"

        # First, mark the original lease as renewed (لا يظهر ضمن المنتهية)
        original_lease.status = 'renewed'; original_lease.save(update_fields=['status'])

        # Then create the new lease (this will set unit as occupied again)
        new_lease = Lease.objects.create(unit=original_lease.unit, tenant=original_lease.tenant, contract_number=new_contract_number, monthly_rent=original_lease.monthly_rent, start_date=new_start_date, end_date=new_end_date, electricity_meter=original_lease.electricity_meter, water_meter=original_lease.water_meter)

        # Ensure unit remains occupied after renewal
        new_lease.unit.is_available = False; new_lease.unit.save()

        # Attach renewal PDF notice to new lease documents
        try:
            context = {
                'old_lease': original_lease,
                'lease': new_lease,
                'today': timezone.now().date(),
                'company': Company.objects.first(),
            }
            pdf_bytes = generate_pdf_bytes('dashboard/reports/lease_renewal_notice.html', context)

            filename = f"lease_renewal_{new_lease.contract_number}.pdf"
            doc = Document(lease=new_lease, title=_('استمارة تجديد عقد') + f" - {new_lease.contract_number}")
            doc.file.save(filename, ContentFile(pdf_bytes))
            doc.save()
        except Exception as e:
            logger.exception("Failed to generate/save renewal PDF for new lease %s (from old %s)", new_lease.id, original_lease.id)
            messages.warning(request, _("تم التجديد، لكن تعذر إرفاق استمارة التجديد تلقائياً."))

        # Generate renewal invoice automatically
        try:
            renewal_invoice = new_lease._generate_renewal_invoice()
            if renewal_invoice:
                messages.success(request, _("تم تجديد العقد وإنشاء فاتورة رسوم التجديد بنجاح!"))
            else:
                messages.warning(request, _("تم التجديد، لكن تعذر إنشاء فاتورة رسوم التجديد تلقائياً."))
        except Exception as e:
            logger.exception("Failed to generate renewal invoice for new lease %s", new_lease.id)
            messages.warning(request, _("تم التجديد، لكن تعذر إنشاء فاتورة رسوم التجديد تلقائياً."))
            
        if 'renewal_invoice' not in locals() or not renewal_invoice:
            messages.success(request, _("تم تجديد العقد بنجاح!"))
        
        return redirect('lease_detail', pk=new_lease.pk)
    return render(request, 'dashboard/lease_renew.html', {'lease': original_lease})

class DocumentUploadView(StaffRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    
    def form_valid(self, form):
        try:
            lease = get_object_or_404(Lease, pk=self.kwargs.get('lease_pk'))
            form.instance.lease = lease
            response = super().form_valid(form)
            messages.success(self.request, _("تم رفع المستند بنجاح!"))
            return response
        except Exception as e:
            logger.exception(f"Failed to upload document for lease {self.kwargs.get('lease_pk')}")
            messages.error(self.request, _("فشل رفع المستند. الرجاء التحقق من صلاحيات الكتابة على السيرفر."))
            return redirect('lease_detail', pk=self.kwargs.get('lease_pk'))
    
    def form_invalid(self, form):
        logger.warning(f"Invalid document form: {form.errors}")
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")
        messages.error(self.request, _("خطأ في البيانات: ") + "; ".join(error_messages))
        return redirect('lease_detail', pk=self.kwargs.get('lease_pk'))
    
    def get_success_url(self):
        return reverse('lease_detail', kwargs={'pk': self.kwargs.get('lease_pk')})

class DocumentDeleteView(StaffRequiredMixin, DeleteView):
    model = Document; template_name = 'dashboard/document_confirm_delete.html'
    def get_success_url(self): return reverse('lease_detail', kwargs={'pk': self.object.lease.pk})
    def form_valid(self, form):
        messages.success(self.request, _("تم حذف المستند بنجاح.")); return super().form_valid(form)

class MaintenanceRequestAdminListView(StaffRequiredMixin, ListView):
    model = MaintenanceRequest; template_name = 'dashboard/maintenance_list.html'; context_object_name = 'requests'; paginate_by = 15

class MaintenanceRequestAdminUpdateView(StaffRequiredMixin, UpdateView):
    model = MaintenanceRequest; form_class = MaintenanceRequestUpdateForm; template_name = 'dashboard/maintenance_detail.html'; success_url = reverse_lazy('maintenance_admin_list')
    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث حالة طلب الصيانة بنجاح.")); return super().form_valid(form)

class ExpenseListView(StaffRequiredMixin, ListView):
    model = Expense; template_name = 'dashboard/expense_list.html'; context_object_name = 'expenses'; paginate_by = 20

class ExpenseCreateView(StaffRequiredMixin, CreateView):
    model = Expense; form_class = ExpenseForm; template_name = 'dashboard/expense_form.html'; success_url = reverse_lazy('expense_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); context['title'] = _("إضافة مصروف جديد"); return context
    def form_valid(self, form):
        messages.success(self.request, _("تم تسجيل المصروف بنجاح.")); return super().form_valid(form)

class ExpenseUpdateView(StaffRequiredMixin, UpdateView):
    model = Expense; form_class = ExpenseForm; template_name = 'dashboard/expense_form.html'; success_url = reverse_lazy('expense_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); context['title'] = _("تعديل المصروف"); return context
    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث المصروف بنجاح.")); return super().form_valid(form)

class ExpenseDeleteView(StaffRequiredMixin, DeleteView):
    model = Expense; template_name = 'dashboard/expense_confirm_delete.html'; success_url = reverse_lazy('expense_list')
    def form_valid(self, form):
        messages.success(self.request, _("تم حذف المصروف بنجاح.")); return super().form_valid(form)


class PaymentListView(StaffRequiredMixin, ListView):
    model = Payment
    template_name = 'dashboard/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        qs = Payment.objects.select_related('lease__tenant', 'lease__unit').all().order_by('-payment_date')
        q = self.request.GET.get('q', '').strip()
        method = self.request.GET.get('payment_method', '').strip()
        if q:
            qs = qs.filter(
                Q(lease__contract_number__icontains=q) |
                Q(lease__tenant__name__icontains=q) |
                Q(lease__unit__unit_number__icontains=q)
            )
        if method in dict(Payment.PAYMENT_METHOD_CHOICES):
            qs = qs.filter(payment_method=method)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_method_choices'] = Payment.PAYMENT_METHOD_CHOICES
        context['current_payment_method'] = self.request.GET.get('payment_method', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context

class PaymentCreateView(StaffRequiredMixin, CreateView):
    model = Payment; form_class = PaymentForm; template_name = 'dashboard/payment_form.html'; success_url = reverse_lazy('payment_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); context['title'] = _("إضافة دفعة جديدة"); return context
    def form_valid(self, form):
        messages.success(self.request, _("تم تسجيل الدفعة بنجاح.")); return super().form_valid(form)

class PaymentUpdateView(StaffRequiredMixin, UpdateView):
    model = Payment; form_class = PaymentForm; template_name = 'dashboard/payment_form.html'; success_url = reverse_lazy('payment_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs); context['title'] = _("تعديل الدفعة"); return context
    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث الدفعة بنجاح.")); return super().form_valid(form)

# ADDED
class PaymentDeleteView(StaffRequiredMixin, DeleteView):
    model = Payment
    template_name = 'dashboard/payment_confirm_delete.html'
    success_url = reverse_lazy('payment_list')
    def form_valid(self, form):
        messages.success(self.request, _("تم حذف الدفعة بنجاح.")); return super().form_valid(form)

# --- Security Deposits ---
class SecurityDepositListView(StaffRequiredMixin, ListView):
    model = SecurityDeposit
    template_name = 'dashboard/security_deposit_list.html'
    context_object_name = 'deposits'
    paginate_by = 20

    def get_queryset(self):
        queryset = SecurityDeposit.objects.select_related('lease__tenant', 'lease__unit').all().order_by('-received_date')
        search_query = self.request.GET.get('q', '')
        status_filter = self.request.GET.get('status', '')
        if search_query:
            queryset = queryset.filter(
                Q(lease__contract_number__icontains=search_query) |
                Q(lease__tenant__name__icontains=search_query) |
                Q(lease__unit__unit_number__icontains=search_query)
            )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['total_held'] = SecurityDeposit.objects.filter(status='held').aggregate(total=Sum('amount'))['total'] or 0
        context['total_refunded'] = SecurityDeposit.objects.filter(status='refunded').aggregate(total=Sum('amount'))['total'] or 0
        return context

class SecurityDepositCreateView(StaffRequiredMixin, CreateView):
    model = SecurityDeposit
    form_class = SecurityDepositForm
    template_name = 'dashboard/security_deposit_form.html'
    success_url = reverse_lazy('security_deposit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تسجيل تأمين جديد")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تم تسجيل التأمين بنجاح."))
        return super().form_valid(form)

class SecurityDepositUpdateView(StaffRequiredMixin, UpdateView):
    model = SecurityDeposit
    form_class = SecurityDepositForm
    template_name = 'dashboard/security_deposit_form.html'
    success_url = reverse_lazy('security_deposit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تعديل التأمين")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث التأمين بنجاح."))
        return super().form_valid(form)

class SecurityDepositDeleteView(StaffRequiredMixin, DeleteView):
    model = SecurityDeposit
    template_name = 'dashboard/security_deposit_confirm_delete.html'
    success_url = reverse_lazy('security_deposit_list')

    def form_valid(self, form):
        messages.success(self.request, _("تم حذف سجل التأمين بنجاح."))
        return super().form_valid(form)

class PaymentReceiptPDFView(View):
    def get(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
            lease = payment.lease

            context = {
                'payment': payment,
                'lease': lease,
                'company': {
                    'name': 'شركة الإدارة العقارية',
                    'logo': None
                },
                'today': timezone.now().date(),
            }

            # استخدام الدالة المباشرة بدلاً من generate_pdf_receipt
            return self.render_pdf_receipt('dashboard/reports/payment_receipt.html', context)

        except Payment.DoesNotExist:
            return HttpResponse("Payment not found", status=404)

    def render_pdf_receipt(self, template_path, context):
        """دالة مساعدة لتوليد PDF"""
        try:
            # حاول استخدام WeasyPrint أولاً
            from weasyprint import HTML

            template = get_template(template_path)
            html = template.render(context)

            pdf_file = HTML(string=html, base_url=settings.BASE_DIR).write_pdf()

            response = HttpResponse(pdf_file, content_type='application/pdf')
            filename = f"receipt_{context['payment'].id}.pdf"
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response

        except ImportError:
            # إذا لم يكن WeasyPrint مثبتاً، استخدم xhtml2pdf
            return self.render_pdf_with_xhtml2pdf(template_path, context)
        except Exception as e:
            # في حالة الخطأ، ارجع HTML للتصحيح
            template = get_template(template_path)
            html = template.render(context)
            return HttpResponse(f"Error: {str(e)}<hr>{html}")

    def render_pdf_with_xhtml2pdf(self, template_path, context):
        """استخدام xhtml2pdf كبديل"""
        try:
            from xhtml2pdf import pisa

            template = get_template(template_path)
            html = template.render(context)

            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

            if not pdf.err:
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                filename = f"receipt_{context['payment'].id}.pdf"
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                return response
            else:
                return HttpResponse("PDF generation failed")

        except Exception as e:
            template = get_template(template_path)
            html = template.render(context)
            return HttpResponse(f"PDF Error: {str(e)}<hr>{html}")

# --- Check Management ---
class CheckManagementView(StaffRequiredMixin, ListView):
    model = Payment
    template_name = 'dashboard/check_management.html'
    context_object_name = 'checks'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Payment.objects.filter(payment_method='check').select_related('lease__tenant', 'lease__unit')
        
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(check_status=status_filter)
        
        return queryset.order_by('-payment_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        
        context['pending_count'] = Payment.objects.filter(payment_method='check', check_status='pending').count()
        context['cashed_count'] = Payment.objects.filter(payment_method='check', check_status='cashed').count()
        context['returned_count'] = Payment.objects.filter(payment_method='check', check_status='returned').count()
        context['total_count'] = Payment.objects.filter(payment_method='check').count()
        
        return context

class CheckStatusUpdateView(StaffRequiredMixin, UpdateView):
    model = Payment
    fields = ['check_status', 'return_reason']
    template_name = 'dashboard/check_status_form.html'
    success_url = reverse_lazy('check_management')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تحديث حالة الشيك")
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث حالة الشيك بنجاح."))
        return super().form_valid(form)

# --- User Management ---
class UserManagementForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False, label=_("كلمة المرور"))
    is_staff = forms.BooleanField(required=False, label=_("موظف"))
    is_active = forms.BooleanField(required=False, initial=True, label=_("نشط"))
    phone_number = forms.CharField(
        max_length=15, 
        required=False, 
        label=_("رقم الهاتف"),
        help_text=_("رقم الهاتف العماني يبدأ بـ +968"),
        widget=forms.TextInput(attrs={'placeholder': '+968XXXXXXXX'})
    )
    first_name_english = forms.CharField(
        max_length=150,
        required=False,
        label=_("الاسم الأول بالإنجليزية"),
        help_text=_("ترجمة تلقائية للاسم الأول"),
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'bg-gray-100'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'is_staff', 'is_active']
        labels = {
            'username': _('اسم المستخدم'),
            'first_name': _('الاسم الأول'),
            'last_name': _('اسم العائلة'),
            'email': _('البريد الإلكتروني'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load phone number and English name from UserProfile if editing
        if self.instance and self.instance.pk:
            try:
                profile = self.instance.profile
                self.fields['phone_number'].initial = profile.phone_number
                self.fields['first_name_english'].initial = profile.first_name_english
            except:
                pass
        
        # Add CSS classes
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#993333]'})
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Validate Oman phone format
            if not phone_number.startswith('+968') or len(phone_number) != 12 or not phone_number[1:].isdigit():
                raise forms.ValidationError(_('يرجى إدخال رقم هاتف عماني صالح يبدأ بـ +968 (8 أرقام بعد المقدمة)'))
        return phone_number
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        phone_number = self.cleaned_data.get('phone_number')
        first_name_english = self.cleaned_data.get('first_name_english')
        
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
            # Create or update UserProfile
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'phone_number': phone_number, 'first_name_english': first_name_english}
            )
            if not created:
                profile.phone_number = phone_number
                profile.first_name_english = first_name_english
                profile.save()
        
        return user

class UserManagementView(StaffRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/user_management.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        from .models import UserProfile
        return User.objects.select_related('profile').all().order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = User.objects.count()
        context['staff_users'] = User.objects.filter(is_staff=True).count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        return context

class UserCreateView(StaffRequiredMixin, CreateView):
    model = User
    form_class = UserManagementForm
    template_name = 'dashboard/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("إضافة مستخدم جديد")
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _("تم إنشاء المستخدم بنجاح."))
        return super().form_valid(form)

class UserUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = UserManagementForm
    template_name = 'dashboard/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تعديل المستخدم")
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث المستخدم بنجاح."))
        return super().form_valid(form)

class UserDeleteView(StaffRequiredMixin, DeleteView):
    model = User
    template_name = 'dashboard/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')
    
    def form_valid(self, form):
        messages.success(self.request, _("تم حذف المستخدم بنجاح."))
        return super().form_valid(form)

# --- Reports ---
# --- Invoice Views ---
class InvoiceListView(StaffRequiredMixin, ListView):
    model = Invoice
    template_name = 'dashboard/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20

    def get_queryset(self):
        queryset = Invoice.objects.select_related('tenant', 'lease').all()
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search_query) |
                Q(tenant__name__icontains=search_query) |
                Q(lease__contract_number__icontains=search_query)
            )
        return queryset.order_by('-issue_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '').strip()
        filtered_qs = Invoice.objects.select_related('tenant', 'lease')
        if search_query:
            filtered_qs = filtered_qs.filter(
                Q(invoice_number__icontains=search_query) |
                Q(tenant__name__icontains=search_query) |
                Q(lease__contract_number__icontains=search_query)
            )

        status_totals = {'draft': 0, 'sent': 0, 'paid': 0, 'overdue': 0, 'cancelled': 0}
        for item in filtered_qs.values('status').annotate(total=Count('id')):
            status = item['status']
            if status in status_totals:
                status_totals[status] = item['total']

        context.update({
            'total_invoices': filtered_qs.count(),
            'draft_count': status_totals['draft'],
            'sent_count': status_totals['sent'],
            'paid_count': status_totals['paid'],
            'overdue_count': status_totals['overdue'],
            'cancelled_count': status_totals['cancelled'],
            'search_query': search_query,
        })
        return context

class InvoiceDetailView(StaffRequiredMixin, DetailView):
    model = Invoice
    template_name = 'dashboard/invoice_detail.html'
    context_object_name = 'invoice'

class InvoiceCreateView(StaffRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'dashboard/invoice_form.html'
    success_url = reverse_lazy('invoice_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = InvoiceItemFormSet(self.request.POST)
        else:
            data['items'] = InvoiceItemFormSet()
        data['title'] = _("إنشاء فاتورة جديدة")
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()
                messages.success(self.request, _("تم إنشاء الفاتورة بنجاح."))
            else:
                # If items are not valid, we prevent the form from being considered valid.
                return self.form_invalid(form)
        # Always redirect to invoice list after successful save
        print("DEBUG: Redirecting to invoice_list from InvoiceCreateView")
        return HttpResponseRedirect(reverse('invoice_list'))

class InvoiceUpdateView(StaffRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'dashboard/invoice_form.html'
    success_url = reverse_lazy('invoice_list')

    def get_success_url(self):
        return reverse_lazy('invoice_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = InvoiceItemFormSet(self.request.POST, instance=self.object)
        else:
            data['items'] = InvoiceItemFormSet(instance=self.object)
        data['title'] = _("تعديل الفاتورة")
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()
                messages.success(self.request, _("تم تحديث الفاتورة بنجاح."))
            else:
                return self.form_invalid(form)
        # Always redirect to invoice list after successful save
        print("DEBUG: Redirecting to invoice_list from InvoiceUpdateView")
        return HttpResponseRedirect(reverse('invoice_list'))

class InvoiceDeleteView(StaffRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'dashboard/invoice_confirm_delete.html'
    success_url = reverse_lazy('invoice_list')

    def form_valid(self, form):
        messages.success(self.request, _("تم حذف الفاتورة بنجاح."))
        return super().form_valid(form)

# --- Reports ---
class ReportSelectionView(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/report_selection.html')

# ADDED: Lease contracts report view
class LeaseReportView(StaffRequiredMixin, ListView):
    model = Lease
    template_name = 'dashboard/reports/lease_report.html'
    context_object_name = 'leases'
    paginate_by = 20

    def get_queryset(self):
        qs = Lease.objects.select_related('tenant', 'unit', 'unit__building').all()
        # Filters: date range on start_date/end_date and simple q search
        start = self.request.GET.get('start')
        end = self.request.GET.get('end')
        q = self.request.GET.get('q', '').strip()
        if start:
            qs = qs.filter(start_date__gte=start)
        if end:
            qs = qs.filter(end_date__lte=end)
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(contract_number__icontains=q) |
                Q(tenant__name__icontains=q) |
                Q(unit__unit_number__icontains=q) |
                Q(unit__building__name__icontains=q)
            )
        return qs.order_by('-start_date')

    def get_context_data(self, **kwargs):
        from django.db.models import Sum
        context = super().get_context_data(**kwargs)
        # Totals for the current page
        page_leases = context['leases']
        context['totals'] = {
            'count': page_leases.paginator.count if hasattr(page_leases, 'paginator') else len(page_leases),
            'monthly_rent_sum': sum(l.monthly_rent for l in page_leases),
        }
        context['filters'] = {
            'start': self.request.GET.get('start', ''),
            'end': self.request.GET.get('end', ''),
            'q': self.request.GET.get('q', ''),
        }
        return context

class GenerateTenantStatementPDF(StaffRequiredMixin, View):
    def get(self, request, lease_pk, *args, **kwargs):
        lease = get_object_or_404(Lease, pk=lease_pk)
        context = {
            'lease': lease, 
            'payments': lease.payments.all(), 
            'today': timezone.now(),
            'company': Company.objects.first() # ADDED
        }
        return render_to_pdf('dashboard/reports/tenant_statement.html', context)

# ADDED
class GeneratePaymentReceiptPDF(StaffRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        payment = get_object_or_404(Payment, pk=pk)
        context = {
            'payment': payment,
            'lease': payment.lease,
            'company': Company.objects.first()
        }
        return render_to_pdf('dashboard/reports/payment_receipt.html', context)

class GenerateMonthlyPLReportPDF(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        year = request.GET.get('year'); month = request.GET.get('month')
        if not year or not month:
            messages.error(request, _("الرجاء تحديد السنة والشهر.")); return redirect('report_selection')
        year, month = int(year), int(month)
        income = Payment.objects.filter(payment_date__year=year, payment_date__month=month)
        expenses = Expense.objects.filter(expense_date__year=year, expense_date__month=month)
        total_income = income.aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
        context = {
            'income_list': income, 'expenses_list': expenses, 'total_income': total_income,
            'total_expenses': total_expenses, 'net_profit': total_income - total_expenses,
            'report_month': month, 'report_year': year, 'company': Company.objects.first() # ADDED
        }
        return render_to_pdf('dashboard/reports/monthly_pl_report.html', context)

# ADDED
class GenerateAnnualPLReportPDF(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        year = request.GET.get('year')
        if not year:
            messages.error(request, _("الرجاء تحديد السنة.")); return redirect('report_selection')
        year = int(year)
        income = Payment.objects.filter(payment_date__year=year)
        expenses = Expense.objects.filter(expense_date__year=year)
        total_income = income.aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
        context = {
            'income_list': income, 'expenses_list': expenses, 'total_income': total_income,
            'total_expenses': total_expenses, 'net_profit': total_income - total_expenses,
            'report_year': year, 'company': Company.objects.first()
        }
        return render_to_pdf('dashboard/reports/annual_pl_report.html', context)

# ADDED
class GenerateOccupancyReportPDF(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        buildings = Building.objects.all().prefetch_related('unit_set')
        total_units = Unit.objects.count()
        occupied_units = Unit.objects.filter(is_available=False).count()
        occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
        context = {
            'buildings': buildings,
            'total_units': total_units,
            'occupied_units': occupied_units,
            'available_units': total_units - occupied_units,
            'occupancy_rate': occupancy_rate,
            'today': timezone.now().date(),
            'company': Company.objects.first()
        }
        return render_to_pdf('dashboard/reports/occupancy_report.html', context)

# --- Settings ---
# ADDED
class CompanyUpdateView(StaffRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'dashboard/company_form.html'
    success_url = reverse_lazy('company_update')

    def get_object(self):
        # Get or create the first company profile
        obj, created = Company.objects.get_or_create(pk=1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("إعدادات الشركة والهوية")
        return context
    
    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث بيانات الشركة بنجاح! ستظهر هذه البيانات في جميع الفواتير والتقارير."))
        return super().form_valid(form)


# === Real Estate Office Management Views ===

class RealEstateOfficeListView(StaffRequiredMixin, ListView):
    model = RealEstateOffice
    template_name = 'dashboard/real_estate_office_list.html'
    context_object_name = 'offices'
    paginate_by = 20

    def get_queryset(self):
        queryset = RealEstateOffice.objects.all().order_by('name')
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(license_number__icontains=search_query) |
                Q(contact_person__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_offices'] = RealEstateOffice.objects.count()
        context['active_offices'] = RealEstateOffice.objects.filter(is_active=True).count()
        return context


class RealEstateOfficeDetailView(StaffRequiredMixin, DetailView):
    model = RealEstateOffice
    template_name = 'dashboard/real_estate_office_detail.html'
    context_object_name = 'office'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agreements'] = CommissionAgreement.objects.filter(real_estate_office=self.object)
        context['collections'] = RentCollection.objects.filter(real_estate_office=self.object).order_by('-collection_date')[:10]
        return context


class RealEstateOfficeCreateView(StaffRequiredMixin, CreateView):
    model = RealEstateOffice
    form_class = RealEstateOfficeForm
    template_name = 'dashboard/real_estate_office_form.html'
    success_url = reverse_lazy('real_estate_office_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("إضافة مكتب عقاري جديد")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تمت إضافة المكتب العقاري بنجاح!"))
        return super().form_valid(form)


class RealEstateOfficeUpdateView(StaffRequiredMixin, UpdateView):
    model = RealEstateOffice
    form_class = RealEstateOfficeForm
    template_name = 'dashboard/real_estate_office_form.html'
    success_url = reverse_lazy('real_estate_office_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تعديل المكتب العقاري")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث المكتب العقاري بنجاح!"))
        return super().form_valid(form)


class RealEstateOfficeDeleteView(StaffRequiredMixin, DeleteView):
    model = RealEstateOffice
    template_name = 'dashboard/real_estate_office_confirm_delete.html'
    success_url = reverse_lazy('real_estate_office_list')

    def form_valid(self, form):
        messages.success(self.request, _("تم حذف المكتب العقاري بنجاح."))
        return super().form_valid(form)


class BuildingOwnerListView(StaffRequiredMixin, ListView):
    model = BuildingOwner
    template_name = 'dashboard/building_owner_list.html'
    context_object_name = 'owners'
    paginate_by = 20

    def get_queryset(self):
        queryset = BuildingOwner.objects.all().order_by('name')
        search_query = self.request.GET.get('q', '')
        owner_type = self.request.GET.get('type', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        if owner_type:
            queryset = queryset.filter(owner_type=owner_type)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_owners'] = BuildingOwner.objects.count()
        context['individual_owners'] = BuildingOwner.objects.filter(owner_type='individual').count()
        context['company_owners'] = BuildingOwner.objects.filter(owner_type='company').count()
        return context


class BuildingOwnerDetailView(StaffRequiredMixin, DetailView):
    model = BuildingOwner
    template_name = 'dashboard/building_owner_detail.html'
    context_object_name = 'owner'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agreements'] = CommissionAgreement.objects.filter(building_owner=self.object)
        context['distributions'] = CommissionDistribution.objects.filter(building_owner=self.object).order_by('-created_at')[:10]
        return context


class BuildingOwnerCreateView(StaffRequiredMixin, CreateView):
    model = BuildingOwner
    form_class = BuildingOwnerForm
    template_name = 'dashboard/building_owner_form.html'
    success_url = reverse_lazy('building_owner_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("إضافة مالك مبنى جديد")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تمت إضافة مالك المبنى بنجاح!"))
        return super().form_valid(form)


class BuildingOwnerUpdateView(StaffRequiredMixin, UpdateView):
    model = BuildingOwner
    form_class = BuildingOwnerForm
    template_name = 'dashboard/building_owner_form.html'
    success_url = reverse_lazy('building_owner_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تعديل مالك المبنى")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث مالك المبنى بنجاح!"))
        return super().form_valid(form)


class BuildingOwnerDeleteView(StaffRequiredMixin, DeleteView):
    model = BuildingOwner
    template_name = 'dashboard/building_owner_confirm_delete.html'
    success_url = reverse_lazy('building_owner_list')

    def form_valid(self, form):
        messages.success(self.request, _("تم حذف مالك المبنى بنجاح."))
        return super().form_valid(form)


class CommissionAgreementListView(StaffRequiredMixin, ListView):
    model = CommissionAgreement
    template_name = 'dashboard/commission_agreement_list.html'
    context_object_name = 'agreements'
    paginate_by = 20

    def get_queryset(self):
        queryset = CommissionAgreement.objects.select_related('real_estate_office', 'building_owner', 'building').all().order_by('-created_at')
        search_query = self.request.GET.get('q', '')
        status_filter = self.request.GET.get('status', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(agreement_number__icontains=search_query) |
                Q(real_estate_office__name__icontains=search_query) |
                Q(building_owner__name__icontains=search_query) |
                Q(building__name__icontains=search_query)
            )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['active_agreements'] = CommissionAgreement.objects.filter(status='active').count()
        context['expired_agreements'] = CommissionAgreement.objects.filter(status='expired').count()
        return context


class CommissionAgreementDetailView(StaffRequiredMixin, DetailView):
    model = CommissionAgreement
    template_name = 'dashboard/commission_agreement_detail.html'
    context_object_name = 'agreement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collections'] = RentCollection.objects.filter(
            lease__unit__building=self.object.building,
            real_estate_office=self.object.real_estate_office
        ).order_by('-collection_date')[:10]
        return context


class CommissionAgreementCreateView(StaffRequiredMixin, CreateView):
    model = CommissionAgreement
    form_class = CommissionAgreementForm
    template_name = 'dashboard/commission_agreement_form.html'
    success_url = reverse_lazy('commission_agreement_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("إضافة اتفاقية عمولة جديدة")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تمت إضافة اتفاقية العمولة بنجاح!"))
        return super().form_valid(form)


class CommissionAgreementUpdateView(StaffRequiredMixin, UpdateView):
    model = CommissionAgreement
    form_class = CommissionAgreementForm
    template_name = 'dashboard/commission_agreement_form.html'
    success_url = reverse_lazy('commission_agreement_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تعديل اتفاقية العمولة")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث اتفاقية العمولة بنجاح!"))
        return super().form_valid(form)


class CommissionAgreementDeleteView(StaffRequiredMixin, DeleteView):
    model = CommissionAgreement
    template_name = 'dashboard/commission_agreement_confirm_delete.html'
    success_url = reverse_lazy('commission_agreement_list')

    def form_valid(self, form):
        messages.success(self.request, _("تم حذف اتفاقية العمولة بنجاح."))
        return super().form_valid(form)


class RentCollectionListView(StaffRequiredMixin, ListView):
    model = RentCollection
    template_name = 'dashboard/rent_collection_list.html'
    context_object_name = 'collections'
    paginate_by = 20

    def get_queryset(self):
        queryset = RentCollection.objects.select_related('lease__tenant', 'lease__unit', 'real_estate_office').all().order_by('-collection_date')
        search_query = self.request.GET.get('q', '')
        status_filter = self.request.GET.get('status', '')
        office_filter = self.request.GET.get('office', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(lease__contract_number__icontains=search_query) |
                Q(lease__tenant__name__icontains=search_query) |
                Q(lease__unit__unit_number__icontains=search_query)
            )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if office_filter:
            queryset = queryset.filter(real_estate_office_id=office_filter)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['office_filter'] = self.request.GET.get('office', '')
        context['offices'] = RealEstateOffice.objects.filter(is_active=True)
        context['total_collected'] = RentCollection.objects.filter(status='collected').aggregate(total=Sum('amount_collected'))['total'] or 0
        context['pending_collections'] = RentCollection.objects.filter(status='pending').count()
        return context


class RentCollectionCreateView(StaffRequiredMixin, CreateView):
    model = RentCollection
    form_class = RentCollectionForm
    template_name = 'dashboard/rent_collection_form.html'
    success_url = reverse_lazy('rent_collection_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تسجيل استلام إيجار جديد")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تم تسجيل استلام الإيجار بنجاح!"))
        return super().form_valid(form)


class RentCollectionUpdateView(StaffRequiredMixin, UpdateView):
    model = RentCollection
    form_class = RentCollectionForm
    template_name = 'dashboard/rent_collection_form.html'
    success_url = reverse_lazy('rent_collection_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تعديل استلام الإيجار")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث استلام الإيجار بنجاح!"))
        return super().form_valid(form)


class RentCollectionDeleteView(StaffRequiredMixin, DeleteView):
    model = RentCollection
    template_name = 'dashboard/rent_collection_confirm_delete.html'
    success_url = reverse_lazy('rent_collection_list')

    def form_valid(self, form):
        messages.success(self.request, _("تم حذف استلام الإيجار بنجاح."))
        return super().form_valid(form)


class CommissionDistributionListView(StaffRequiredMixin, ListView):
    model = CommissionDistribution
    template_name = 'dashboard/commission_distribution_list.html'
    context_object_name = 'distributions'
    paginate_by = 20

    def get_queryset(self):
        queryset = CommissionDistribution.objects.select_related(
            'rent_collection__lease__tenant', 
            'building_owner', 
            'commission_agreement__real_estate_office'
        ).all().order_by('-created_at')
        
        search_query = self.request.GET.get('q', '')
        status_filter = self.request.GET.get('status', '')
        owner_filter = self.request.GET.get('owner', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(building_owner__name__icontains=search_query) |
                Q(rent_collection__lease__contract_number__icontains=search_query) |
                Q(payment_reference__icontains=search_query)
            )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if owner_filter:
            queryset = queryset.filter(building_owner_id=owner_filter)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['owner_filter'] = self.request.GET.get('owner', '')
        context['owners'] = BuildingOwner.objects.filter(is_active=True)
        context['total_distributed'] = CommissionDistribution.objects.filter(status='distributed').aggregate(
            total=Sum('owner_share'))['total'] or 0
        context['pending_distributions'] = CommissionDistribution.objects.filter(status='pending').count()
        return context


class CommissionDistributionCreateView(StaffRequiredMixin, CreateView):
    model = CommissionDistribution
    form_class = CommissionDistributionForm
    template_name = 'dashboard/commission_distribution_form.html'
    success_url = reverse_lazy('commission_distribution_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تسجيل توزيع عمولة جديد")
        return context

    def form_valid(self, form):
        # حساب العمولة تلقائياً
        distribution = form.save(commit=False)
        office_commission, owner_share = distribution.calculate_commission()
        distribution.office_commission = office_commission
        distribution.owner_share = owner_share
        distribution.save()
        
        messages.success(self.request, _("تم تسجيل توزيع العمولة بنجاح!"))
        return super().form_valid(form)


class CommissionDistributionUpdateView(StaffRequiredMixin, UpdateView):
    model = CommissionDistribution
    form_class = CommissionDistributionForm
    template_name = 'dashboard/commission_distribution_form.html'
    success_url = reverse_lazy('commission_distribution_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("تعديل توزيع العمولة")
        return context

    def form_valid(self, form):
        messages.success(self.request, _("تم تحديث توزيع العمولة بنجاح!"))
        return super().form_valid(form)


class CommissionDistributionDeleteView(StaffRequiredMixin, DeleteView):
    model = CommissionDistribution
    template_name = 'dashboard/commission_distribution_confirm_delete.html'
    success_url = reverse_lazy('commission_distribution_list')

    def form_valid(self, form):
        messages.success(self.request, _("تم حذف توزيع العمولة بنجاح."))
        return super().form_valid(form)


# View to automatically create commission distribution when rent is collected
@login_required
@user_passes_test(lambda u: u.is_staff)
def create_commission_distribution(request, collection_pk):
    """إنشاء توزيع عمولة تلقائياً عند استلام الإيجار"""
    collection = get_object_or_404(RentCollection, pk=collection_pk)
    
    # البحث عن اتفاقية عمولة نشطة للمبنى
    agreement = CommissionAgreement.objects.filter(
        building=collection.lease.unit.building,
        real_estate_office=collection.real_estate_office,
        status='active'
    ).first()
    
    if not agreement:
        messages.error(request, _("لا توجد اتفاقية عمولة نشطة لهذا المبنى والمكتب العقاري."))
        return redirect('rent_collection_list')
    
    # التحقق من عدم وجود توزيع سابق
    existing_distribution = CommissionDistribution.objects.filter(
        rent_collection=collection
    ).first()
    
    if existing_distribution:
        messages.warning(request, _("تم إنشاء توزيع عمولة لهذا الاستلام مسبقاً."))
        return redirect('commission_distribution_list')
    
    # إنشاء توزيع العمولة
    distribution = CommissionDistribution.objects.create(
        rent_collection=collection,
        commission_agreement=agreement,
        building_owner=agreement.building_owner,
        status='pending'
    )
    
    # حساب العمولة
    office_commission, owner_share = distribution.calculate_commission()
    distribution.office_commission = office_commission
    distribution.owner_share = owner_share
    distribution.save()
    
    messages.success(request, _("تم إنشاء توزيع العمولة تلقائياً."))
    return redirect('commission_distribution_detail', pk=distribution.pk)


# --- Media Diagnostics ---
@login_required
@user_passes_test(lambda u: u.is_staff)
def media_diagnostics(request):
    """صفحة تشخيص لفحص صلاحيات مجلد media"""
    import os
    import stat
    
    diagnostics = {
        'media_root': settings.MEDIA_ROOT,
        'media_url': settings.MEDIA_URL,
        'exists': os.path.exists(settings.MEDIA_ROOT),
        'is_dir': os.path.isdir(settings.MEDIA_ROOT) if os.path.exists(settings.MEDIA_ROOT) else False,
        'writable': os.access(settings.MEDIA_ROOT, os.W_OK) if os.path.exists(settings.MEDIA_ROOT) else False,
        'readable': os.access(settings.MEDIA_ROOT, os.R_OK) if os.path.exists(settings.MEDIA_ROOT) else False,
    }
    
    if diagnostics['exists']:
        try:
            stat_info = os.stat(settings.MEDIA_ROOT)
            diagnostics['permissions'] = oct(stat_info.st_mode)[-3:]
            diagnostics['owner_uid'] = stat_info.st_uid
            diagnostics['owner_gid'] = stat_info.st_gid
        except Exception as e:
            diagnostics['stat_error'] = str(e)
    
    # محاولة إنشاء ملف اختبار
    test_file_path = os.path.join(settings.MEDIA_ROOT, 'test_write.txt')
    try:
        with open(test_file_path, 'w') as f:
            f.write('test')
        diagnostics['write_test'] = 'SUCCESS'
        os.remove(test_file_path)
    except Exception as e:
        diagnostics['write_test'] = f'FAILED: {str(e)}'
    
    return HttpResponse(f"<pre>{json.dumps(diagnostics, indent=2)}</pre>")


# --- Serve Media Files (for production) ---
@login_required
def serve_protected_media(request, path):
    """
    خدمة ملفات الميديا بشكل آمن ومحمي.
    يتحقق من صلاحيات المستخدم قبل السماح بالوصول للملف.
    """
    import os
    from django.http import FileResponse, Http404
    
    # التحقق من أن المستخدم موظف أو مالك الملف
    if not request.user.is_staff:
        # يمكن إضافة منطق إضافي للتحقق من أن المستخدم يملك حق الوصول للملف
        return HttpResponse("Unauthorized", status=403)
    
    # بناء المسار الكامل للملف
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    # التحقق من وجود الملف
    if not os.path.exists(file_path):
        logger.warning(f"Media file not found: {file_path}")
        raise Http404("File not found")
    
    # إرجاع الملف
    try:
        return FileResponse(open(file_path, 'rb'))
    except Exception as e:
        logger.exception(f"Error serving media file {path}")
        raise Http404("Error serving file")


# ========== إدارة إنذارات عدم السداد ==========

class PaymentOverdueNoticeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = PaymentOverdueNotice
    template_name = 'dashboard/overdue_notices/list.html'
    context_object_name = 'notices'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = PaymentOverdueNotice.objects.select_related(
            'lease__tenant', 'lease__unit__building'
        ).order_by('-notice_date')
        
        # فلترة حسب العقد
        lease_id = self.request.GET.get('lease')
        if lease_id:
            queryset = queryset.filter(lease_id=lease_id)
        
        # فلترة حسب الحالة
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # فلترة حسب السنة
        year = self.request.GET.get('year')
        if year:
            queryset = queryset.filter(overdue_year=year)
        
        # البحث
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(lease__contract_number__icontains=search) |
                Q(lease__tenant__name__icontains=search) |
                Q(lease__unit__unit_number__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = PaymentOverdueNotice.NOTICE_STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['current_year'] = self.request.GET.get('year', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # إحصائيات سريعة
        context['stats'] = {
            'total': PaymentOverdueNotice.objects.count(),
            'draft': PaymentOverdueNotice.objects.filter(status='draft').count(),
            'sent': PaymentOverdueNotice.objects.filter(status='sent').count(),
            'overdue_legal': PaymentOverdueNotice.objects.filter(
                legal_deadline__lt=timezone.now().date(),
                status__in=['sent', 'acknowledged']
            ).count(),
        }
        
        return context


class LeaseOverdueNoticesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """عرض إنذارات عقد معين أو إنشاء إنذار جديد"""
    model = PaymentOverdueNotice
    template_name = 'dashboard/overdue_notices/lease_notices.html'
    context_object_name = 'notices'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        self.lease = get_object_or_404(Lease, pk=self.kwargs['lease_id'])
        return PaymentOverdueNotice.objects.filter(lease=self.lease).order_by('-notice_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lease'] = self.lease
        
        # فحص إمكانية إنشاء إنذار جديد
        can_create_notice = self.lease.has_overdue_payments
        context['can_create_notice'] = can_create_notice
        
        # معاينة الإنذار الجديد إذا كان ممكناً
        if can_create_notice:
            preview_notice = PaymentOverdueNotice.generate_automatic_notice(self.lease)
            if preview_notice:
                # حذف الإنذار المؤقت (كان للمعاينة فقط)
                preview_notice.delete()
                context['preview_available'] = True
            else:
                context['preview_available'] = False
        
        return context


class PaymentOverdueNoticeDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = PaymentOverdueNotice
    template_name = 'dashboard/overdue_notices/detail.html'
    context_object_name = 'notice'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notice = self.get_object()
        
        # إضافة معلومات إضافية
        try:
            # حساب متوسط الأيام منذ تاريخ الاستحقاق للتفاصيل
            if notice.details.exists():
                total_days = sum(detail.get_days_since_due() for detail in notice.details.all())
                avg_days_since_due = total_days // notice.details.count()
            else:
                avg_days_since_due = 0
            context['days_since_due'] = avg_days_since_due
        except:
            context['days_since_due'] = 0
            
        try:
            # حساب متوسط الأيام حتى الموعد النهائي
            today = timezone.now().date()
            total_days_until_deadline = sum((detail.due_date - today).days for detail in notice.details.all() if detail.due_date > today)
            if notice.details.exists():
                avg_days_until_deadline = total_days_until_deadline // notice.details.count()
            else:
                avg_days_until_deadline = (notice.legal_deadline - today).days if notice.legal_deadline > today else 0
            context['days_until_deadline'] = avg_days_until_deadline
        except:
            context['days_until_deadline'] = 0
        
        # الدفعات المرتبطة بنفس الفترة
        context['related_payments'] = Payment.objects.filter(
            lease=notice.lease,
            payment_for_month__in=[detail.overdue_month for detail in notice.details.all()],
            payment_for_year__in=[detail.overdue_year for detail in notice.details.all()]
        ).order_by('-payment_date')
        
        return context


@login_required
@user_passes_test(lambda u: u.is_staff)
def generate_automatic_notices(request):
    """عرض وتنفيذ إنشاء الإنذارات التلقائية"""
    if request.method == 'POST':
        try:
            # تنفيذ أمر إنشاء الإنذارات
            from io import StringIO
            import sys
            
            # التقاط مخرجات الأمر
            old_stdout = sys.stdout
            sys.stdout = buffer = StringIO()
            
            try:
                call_command('generate_overdue_notices')
                output = buffer.getvalue()
                messages.success(request, 'تم إنشاء الإنذارات التلقائية بنجاح!')
            finally:
                sys.stdout = old_stdout
            
            # إعادة توجيه إلى قائمة الإنذارات
            return redirect('overdue_notices_list')
            
        except Exception as e:
            messages.error(request, f'حدث خطأ أثناء إنشاء الإنذارات: {str(e)}')
    
    # عرض معاينة الإنذارات التي سيتم إنشاؤها
    context = {
        'title': 'إنشاء إنذارات تلقائية',
        'preview_notices': _get_preview_notices(),
    }
    
    return render(request, 'dashboard/overdue_notices/generate_automatic.html', context)


def _get_preview_notices():
    """الحصول على معاينة الإنذارات التي سيتم إنشاؤها"""
    from dateutil.relativedelta import relativedelta
    import datetime
    
    today = timezone.now().date()
    
    preview_notices = []
    active_leases = Lease.objects.filter(status='active')
    
    for lease in active_leases[:20]:  # معاينة أول 20 عقد
        try:
            payment_summary = lease.get_payment_summary()
            overdue_months = []
            
            for month_data in payment_summary:
                # فحص الدفعات المتأخرة لأكثر من شهر
                if (month_data['status'] == 'overdue' and
                    month_data['balance'] > 0 and
                    month_data['days_overdue'] >= 30):
                    
                    # فحص عدم وجود إنذار سابق لنفس الشهر والسنة
                    existing_detail = PaymentOverdueDetail.objects.filter(
                        notice__lease=lease,
                        overdue_month=month_data['month'],
                        overdue_year=month_data['year']
                    ).exists()
                    
                    if not existing_detail:
                        overdue_months.append({
                            'month': month_data['month'],
                            'year': month_data['year'],
                            'amount': month_data['balance'],
                            'due_date': month_data['due_date'],
                            'days_overdue': month_data['days_overdue']
                        })
            
            if overdue_months:
                total_amount = sum(month['amount'] for month in overdue_months)
                preview_notices.append({
                    'lease': lease,
                    'overdue_months': overdue_months,
                    'total_amount': total_amount,
                    'months_count': len(overdue_months)
                })
                
        except Exception as e:
            print(f"Error in preview for lease {lease.contract_number}: {e}")
            continue
    
    return preview_notices


@login_required
@user_passes_test(lambda u: u.is_staff)
def notice_update_status(request, pk):
    """تحديث حالة الإنذار"""
    notice = get_object_or_404(PaymentOverdueNotice, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status in dict(PaymentOverdueNotice.NOTICE_STATUS_CHOICES):
            old_status = notice.status
            notice.status = new_status
            
            # تحديث التواريخ المناسبة
            now = timezone.now()
            if new_status == 'sent' and old_status == 'draft':
                notice.sent_date = now
            elif new_status == 'acknowledged' and old_status == 'sent':
                notice.acknowledged_date = now
            elif new_status == 'resolved':
                notice.resolved_date = now
            
            # إضافة الملاحظات
            if notes:
                if notice.notes:
                    notice.notes += f"\n\n{now.strftime('%Y-%m-%d %H:%M')}: {notes}"
                else:
                    notice.notes = f"{now.strftime('%Y-%m-%d %H:%M')}: {notes}"
            
            notice.save()
            messages.success(request, f'تم تحديث حالة الإنذار إلى "{notice.get_status_display()}"')
        else:
            messages.error(request, 'حالة غير صحيحة')
    
    return redirect('overdue_notice_detail', pk=pk)


@login_required
@user_passes_test(lambda u: u.is_staff)
def notice_print_view(request, pk):
    """طباعة الإنذار"""
    notice = get_object_or_404(PaymentOverdueNotice, pk=pk)

    context = {
        'notice': notice,
        'company': Company.objects.first(),
    }

    return render(request, 'dashboard/overdue_notices/print.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def notices_bulk_actions(request):
    """إجراءات مجمعة على الإنذارات"""
    if request.method == 'POST':
        action = request.POST.get('action')
        notice_ids = request.POST.getlist('notice_ids')
        
        if not notice_ids:
            messages.error(request, 'يرجى اختيار إنذار واحد على الأقل')
            return redirect('overdue_notices_list')
        
        notices = PaymentOverdueNotice.objects.filter(id__in=notice_ids)
        
        if action == 'mark_sent':
            notices.update(status='sent', sent_date=timezone.now())
            messages.success(request, f'تم تحديث {notices.count()} إنذار إلى "مُرسل"')
        
        elif action == 'mark_acknowledged':
            notices.update(status='acknowledged', acknowledged_date=timezone.now())
            messages.success(request, f'تم تحديث {notices.count()} إنذار إلى "مُستلم"')
        
        elif action == 'mark_resolved':
            notices.update(status='resolved', resolved_date=timezone.now())
            messages.success(request, f'تم تحديث {notices.count()} إنذار إلى "محلول"')
        
        elif action == 'delete':
            count = notices.count()
            notices.delete()
            messages.success(request, f'تم حذف {count} إنذار')
        
        else:
            messages.error(request, 'إجراء غير صحيح')
    
    return redirect('overdue_notices_list')


@login_required
def registration_invoice_view(request, lease_id):
    """Generate and display registration fee invoice for a lease"""
    lease = get_object_or_404(Lease, id=lease_id)
    
    # Calculate fees based on example: monthly rent should be around 2166.67 to get 65.00 registration fee
    monthly_rent = lease.monthly_rent or Decimal('2166.67')
    registration_fee = (monthly_rent * Decimal('0.03')).quantize(Decimal('0.01'))  # 3% registration fee
    
    # New fee: (monthly_rent * 3% * 12 months) + 1
    annual_percentage_fee = ((monthly_rent * Decimal('0.03') * Decimal('12')) + Decimal('1')).quantize(Decimal('0.01'))
    
    admin_fee = lease.admin_fee or Decimal('1.0')
    office_fee = lease.office_fee or Decimal('5.0')
    
    # Calculate totals
    subtotal_without_office = registration_fee + annual_percentage_fee + admin_fee
    grand_total = subtotal_without_office + office_fee
    
    # Get company information from database
    try:
        company = Company.objects.first()
    except Company.DoesNotExist:
        company = None
    
    context = {
        'lease': lease,
        'registration_fee': registration_fee,
        'annual_percentage_fee': annual_percentage_fee,
        'admin_fee': admin_fee,
        'office_fee': office_fee,
        'subtotal_without_office': subtotal_without_office,
        'grand_total': grand_total,
        'company': company,
    }
    
    return render(request, 'dashboard/reports/lease_initial_invoice.html', context)


@login_required
def renewal_invoice_view(request, lease_id):
    """Generate and display renewal fee invoice for a lease"""
    lease = get_object_or_404(Lease, id=lease_id)
    
    # Calculate renewal fees
    renewal_fee = lease.office_fee or Decimal('5.0')
    admin_fee = lease.admin_fee or Decimal('1.0')
    total_fees = renewal_fee + admin_fee
    
    # Get company information from database
    try:
        company = Company.objects.first()
    except Company.DoesNotExist:
        company = None
    
    context = {
        'lease': lease,
        'renewal_fee': renewal_fee,
        'office_fee': renewal_fee,
        'admin_fee': admin_fee,
        'total_fees': total_fees,
        'company': company,
        'today': timezone.now().date(),
    }
    
    return render(request, 'dashboard/reports/lease_renewal_invoice.html', context)


@login_required
def cancellation_form_view(request, lease_id):
    """Generate and display lease cancellation form"""
    lease = get_object_or_404(Lease, id=lease_id)
    
    # Calculate outstanding amounts (example calculations)
    outstanding_rent = Decimal('0.00')  # Should be calculated based on actual payments
    outstanding_utilities = Decimal('0.00')  # Should be calculated based on actual utilities
    
    # Get security deposit from SecurityDeposit model
    try:
        security_deposit_obj = SecurityDeposit.objects.filter(lease=lease, status='held').first()
        security_deposit = security_deposit_obj.amount if security_deposit_obj else Decimal('0.00')
    except:
        security_deposit = Decimal('0.00')
    
    # Net amount calculation (positive = owed to office, negative = refund to tenant)
    net_amount = outstanding_rent + outstanding_utilities - security_deposit
    
    # Get company information from database
    try:
        company = Company.objects.first()
    except Company.DoesNotExist:
        company = None
    
    context = {
        'lease': lease,
        'outstanding_rent': outstanding_rent,
        'outstanding_utilities': outstanding_utilities,
        'security_deposit': security_deposit,
        'net_amount': net_amount,
        'company': company,
        'today': timezone.now().date(),
        'cancellation_reason': lease.cancellation_reason if hasattr(lease, 'cancellation_reason') else '',
    }
    
    return render(request, 'dashboard/reports/lease_cancellation_form.html', context)


@login_required
def renewal_form_view(request, lease_id):
    """Generate and display lease renewal form"""
    lease = get_object_or_404(Lease, id=lease_id)
    
    # Calculate renewal fees
    renewal_fee = lease.office_fee or Decimal('5.0')
    office_fee = lease.office_fee or Decimal('5.0')
    admin_fee = lease.admin_fee or Decimal('1.0')
    security_difference = Decimal('0.00')  # Difference in security deposit if any
    total_renewal_fees = renewal_fee + office_fee + admin_fee + security_difference
    
    # Get current security deposit from SecurityDeposit model
    try:
        security_deposit_obj = SecurityDeposit.objects.filter(lease=lease, status='held').first()
        current_security_deposit = security_deposit_obj.amount if security_deposit_obj else Decimal('0.00')
    except:
        current_security_deposit = Decimal('0.00')
    
    # Calculate current lease duration in months
    if lease.start_date and lease.end_date:
        current_duration = (lease.end_date - lease.start_date).days // 30  # Approximate months
    else:
        current_duration = 12  # Default
    
    # Suggested new terms (can be customized)
    new_start_date = lease.end_date if lease.end_date else timezone.now().date()
    new_end_date = new_start_date + timedelta(days=365) if new_start_date else None
    new_monthly_rent = lease.monthly_rent
    new_duration = current_duration  # Use current duration as default
    new_security_deposit = current_security_deposit
    
    # Get company information from database
    try:
        company = Company.objects.first()
    except Company.DoesNotExist:
        company = None
    
    context = {
        'lease': lease,
        'renewal_fee': renewal_fee,
        'office_fee': office_fee,
        'admin_fee': admin_fee,
        'security_difference': security_difference,
        'total_renewal_fees': total_renewal_fees,
        'current_duration': current_duration,
        'new_start_date': new_start_date,
        'new_end_date': new_end_date,
        'new_monthly_rent': new_monthly_rent,
        'new_duration': new_duration,
        'new_security_deposit': new_security_deposit,
        'company': company,
        'today': timezone.now().date(),
    }
    
    return render(request, 'dashboard/reports/lease_renewal_form.html', context)


@login_required
def tenant_comprehensive_report_view(request, tenant_id):
    """Generate comprehensive report for a tenant"""
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # Get all leases for this tenant
    current_leases = Lease.objects.filter(tenant=tenant, status='active')
    lease_history = Lease.objects.filter(tenant=tenant).order_by('-start_date')
    
    # Calculate financial statistics
    total_payments = Decimal('0.00')
    outstanding_amount = Decimal('0.00')
    total_expected_rent = Decimal('0.00')
    
    # Calculate totals from all leases
    for lease in lease_history:
        # Get payments for this lease
        lease_payments = Payment.objects.filter(lease=lease).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        total_payments += lease_payments
        
        # Calculate expected rent for active leases
        if lease.status == 'active' and lease.monthly_rent:
            if lease.start_date and lease.end_date:
                months_diff = (lease.end_date.year - lease.start_date.year) * 12 + \
                             (lease.end_date.month - lease.start_date.month)
                total_expected_rent += lease.monthly_rent * months_diff
    
    # Calculate outstanding amount (simplified calculation)
    outstanding_amount = total_expected_rent - total_payments
    
    # Calculate average monthly rent
    active_rents = [lease.monthly_rent for lease in current_leases if lease.monthly_rent]
    average_monthly_rent = sum(active_rents) / len(active_rents) if active_rents else Decimal('0.00')
    
    # Get company information
    try:
        company = Company.objects.first()
    except Company.DoesNotExist:
        company = None
    
    context = {
        'tenant': tenant,
        'current_leases': current_leases,
        'lease_history': lease_history,
        'total_payments': total_payments,
        'outstanding_amount': outstanding_amount,
        'average_monthly_rent': average_monthly_rent,
        'total_expected_rent': total_expected_rent,
        'company': company,
        'today': timezone.now().date(),
    }
    
@login_required
def renewal_reminder_view(request, lease_id):
    """Generate and display lease renewal reminder for a lease"""
    lease = get_object_or_404(Lease, id=lease_id)

    # Get or create renewal reminder for this lease
    reminder_date = lease.end_date - relativedelta(days=30)
    reminder, created = LeaseRenewalReminder.objects.get_or_create(
        lease=lease,
        reminder_date=reminder_date,
        defaults={'status': 'pending'}
    )

    # Get company information from database
    try:
        company = Company.objects.first()
    except Company.DoesNotExist:
        company = None

    context = {
        'reminder': reminder,
        'lease': lease,
        'company': company,
        'today': timezone.now().date(),
    }

    return render(request, 'dashboard/reports/lease_renewal_reminder.html', context)
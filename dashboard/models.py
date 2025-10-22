from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
import datetime
from django.db.models import Sum
import secrets
import string
from django.core.validators import RegexValidator

class LeaseManager(models.Manager):
    def delete(self):
        """تحديث حالة الوحدات إلى متاحة عند الحذف المجمع للعقود"""
        # تحديث حالة جميع الوحدات المرتبطة بالعقود المحددة للحذف
        units_to_update = self.values_list('unit', flat=True)
        Unit.objects.filter(id__in=units_to_update).update(is_available=True)
        
        # تنفيذ الحذف المجمع
        return super().delete()

class Company(models.Model):
    name = models.CharField(_("اسم الشركة"), max_length=200)
    company_id = models.CharField(_("هوية الشركة"), max_length=50, blank=True, null=True, help_text=_("رقم السجل التجاري أو الهوية الضريبية"))
    logo = models.ImageField(_("الشعار"), upload_to='company_logos/', blank=True, null=True)
    contact_email = models.EmailField(_("البريد الإلكتروني للتواصل"), blank=True, null=True)
    contact_phone = models.CharField(_(" الهاتف للتواصل"), max_length=20, blank=True, null=True)
    address = models.TextField(_("العنوان"), blank=True, null=True)

    class Meta:
        verbose_name = _("ملف الشركة")
        verbose_name_plural = _("ملف الشركة")

    def __str__(self):
        return self.name

class Building(models.Model):
    name = models.CharField(_("اسم المبنى"), max_length=100)
    address = models.TextField(_("العنوان"))
    
    class Meta:
        verbose_name = _("مبنى")
        verbose_name_plural = _("المباني")
        
    def __str__(self):
        return self.name

class Unit(models.Model):
    UNIT_TYPE_CHOICES = [
        ('apartment', _('شقة')),
        ('office', _('مكتب تجاري')),
        ('shop', _('محل تجاري')),
        ('warehouse', _('مستودع للتخزين')),
    ]
    building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name=_("المبنى"))
    unit_number = models.CharField(_("رقم الوحدة"), max_length=20)
    unit_type = models.CharField(_("نوع الوحدة"), max_length=30, choices=UNIT_TYPE_CHOICES)
    floor = models.IntegerField(_("الطابق"))
    is_available = models.BooleanField(_("متاحة للإيجار"), default=True)
    
    class Meta:
        verbose_name = _("وحدة")
        verbose_name_plural = _("الوحدات")
        
    def __str__(self):
        return f"{self.building.name} - {self.unit_number}"

class Tenant(models.Model):
    TENANT_TYPE_CHOICES = [
        ('sole_proprietorship', _('شركة الشخص الواحد')),
        ('limited_liability', _('الشركة ذات المسؤولية المحدودة')),
        ('joint_stock', _('الشركة المساهمة')),
        ('general_partnership', _('شركة التضامن')),
        ('limited_partnership', _('شركة التوصية البسيطة')),
        ('holding_company', _('الشركة القابضة')),
        ('representative_office', _('مكتب تمثيل تجاري')),
        ('foreign_branch', _('فرع شركة أجنبية')),
    ]
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("حساب المستخدم"), help_text=_("اربط المستأجر بحساب مستخدم لتسجيل الدخول إلى البوابة."))
    name = models.CharField(_("اسم المستأجر"), max_length=150)
    tenant_type = models.CharField(_("نوع المستأجر"), max_length=50, choices=TENANT_TYPE_CHOICES)
    phone = models.CharField(_("رقم الهاتف"), max_length=15)
    email = models.EmailField(_("البريد الإلكتروني"), blank=True, null=True)
    authorized_signatory = models.CharField(_("المفوض بالتوقيع"), max_length=150, blank=True, null=True, help_text=_("يُملأ فقط في حال كان المستأجر شركة"))
    rating = models.IntegerField(_("تقييم العميل"), default=3, choices=[(i, str(i)) for i in range(1, 6)], help_text= _("من 1 إلى 5 نجوم."))
    
    class Meta:
        verbose_name = _("مستأجر")
        verbose_name_plural = _("المستأجرين")
        
    def __str__(self):
        return self.name

class ContractTemplate(models.Model):
    title = models.CharField(_("عنوان القالب"), max_length=200)
    body = models.TextField(_("محتوى القالب"), help_text=_("استخدم HTML لتخصيص القالب."))

    class Meta:
        verbose_name = _("قالب عقد")
        verbose_name_plural = _("قوالب العقود")

    def __str__(self):
        return self.title

class Lease(models.Model):
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('expiring_soon', _('قريب الانتهاء')),
        ('expired', _('منتهي')),
        ('renewed', _('تم تجديد')),
        ('cancelled', _('ملغي')),
    ]
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name=_("الوحدة"))
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name=_("المستأجر"))
    contract_number = models.CharField(_("رقم العقد"), max_length=50, unique=True)
    contract_form_number = models.CharField(_("رقم نموذج العقد"), max_length=50, blank=True, null=True)
    monthly_rent = models.DecimalField(_("مبلغ الإيجار الشهري"), max_digits=10, decimal_places=2)
    start_date = models.DateField(_("تاريخ بدء العقد"))
    end_date = models.DateField(_("تاريخ انتهاء العقد"))
    electricity_meter = models.CharField(_("رقم عداد الكهرباء"), max_length=50, blank=True, null=True)
    water_meter = models.CharField(_("رقم عداد المياه"), max_length=50, blank=True, null=True)
    status = models.CharField(_("حالة العقد"), max_length=20, choices=STATUS_CHOICES, default='active', editable=False)
    office_fee = models.DecimalField(_("رسوم المكتب"), max_digits=10, decimal_places=2, default=5.00)
    admin_fee = models.DecimalField(_("الرسوم الإدارية"), max_digits=10, decimal_places=2, default=1.00)
    registration_fee = models.DecimalField(_("رسوم تسجيل العقد (3%)"), max_digits=10, decimal_places=2, blank=True)
    
    # أسباب الإلغاء
    CANCELLATION_REASON_CHOICES = [
        ('contract_term_ended', _('انتهاء المدة المحددة في العقد')),
        ('non_payment', _('عدم دفع الإيجار لأكثر من شهرين متتاليين')),
        ('tenant_violation', _('مخالفة شروط العقد من قبل المستأجر')),
        ('owner_reclaim', _('رغبة المالك في استرداد العقار')),
        ('tenant_request', _('رغبة المستأجر في إنهاء العقد')),
        ('other', _('أسباب أخرى')),
    ]
    
    cancellation_date = models.DateField(_("تاريخ الإلغاء"), blank=True, null=True)
    cancellation_reason = models.CharField(_("أسباب الإلغاء"), max_length=500, blank=True, null=True, help_text=_("يمكنك اختيار حتى 3 أسباب، مفصولة بفواصل"))
    cancellation_details = models.TextField(_("تفاصيل إضافية عن سبب الإلغاء"), blank=True, null=True)
    
    # المدير المخصص
    objects = LeaseManager()
    
    def get_cancellation_reasons_display(self):
        """تحويل أكواد أسباب الإلغاء إلى نصوص عربية"""
        if not self.cancellation_reason:
            return None
        
        reasons_dict = dict(self.CANCELLATION_REASON_CHOICES)
        reason_codes = self.cancellation_reason.split(',')
        reason_texts = [reasons_dict.get(code.strip(), code) for code in reason_codes]
        return reason_texts
    
    class Meta:
        verbose_name = _("عقد إيجار")
        verbose_name_plural = _("عقود الإيجار")
        permissions = [
            ("can_view_financial_reports", _("Can view financial reports")),
            ("can_manage_leases", _("Can manage leases")),
            ("can_manage_notices", _("Can manage notices")),
            ("can_access_settings", _("Can access settings")),
        ]
        
    def save(self, *args, **kwargs):
        self.registration_fee = (self.monthly_rent * 12) * Decimal('0.03')
        if self.pk:
            old_lease = Lease.objects.get(pk=self.pk)
            if old_lease.unit != self.unit:
                old_lease.unit.is_available = True
                old_lease.unit.save()
                
        if self.status in ['active', 'expiring_soon']:
            self.unit.is_available = False
        else:
            self.unit.is_available = True
        self.unit.save()

        is_being_cancelled = 'cancellation_reson' in kwargs.get('update_fields', [])
        if not is_being_cancelled:
            self.update_status()
        
        # إنشاء استمارة إلغاء تلقائياً عند إلغاء العقد
        if not self.pk:  # عند إنشاء عقد جديد
            print(f"Creating new lease {self.contract_number}")
            super().save(*args, **kwargs)
            print(f"New lease saved, calling _generate_initial_invoice")
            # إنشاء فاتورة أولية للعقد الجديد
            self._generate_initial_invoice()
        else:  # عند تحديث عقد موجود
            old_lease = Lease.objects.get(pk=self.pk)
            old_status = old_lease.status
            print(f"Updating lease {self.id}, old status: {old_status}, new status: {self.status}")
            super().save(*args, **kwargs)
            
            # إذا تم إلغاء العقد، أنشئ استمارة الإلغاء تلقائياً
            if old_status != 'cancelled' and self.status == 'cancelled':
                self._generate_cancellation_notice()
            # إذا تم تجديد العقد، أنشئ استمارة التجديد تلقائياً
            elif old_status not in ['renewed', 'cancelled'] and self.status == 'renewed':
                print(f"Calling _generate_renewal_notice for lease {self.id}")
                self._generate_renewal_notice()

    def update_status(self):
        today = timezone.now().date()
        if self.status in ['cancelled', 'renewed']:
            return
        if self.end_date < today: self.status = 'expired'
        elif self.end_date - relativedelta(months=1) <= today: self.status = 'expiring_soon'
        else: self.status = 'active'
            
    def get_status_color(self):
        if self.status == 'active': return 'active'
        if self.status == 'expiring_soon': return 'expiring'
        if self.status == 'expired': return 'expired'
        if self.status == 'renewed': return 'active'
        return 'cancelled'
    
    def days_until_expiry(self):
        today = timezone.now().date()
        if self.status == 'cancelled':
            return None
        delta = self.end_date - today
        return delta.days
    
    @property
    def is_renewed(self):
        """معرفة ما إذا كان العقد تم تجديده أم لا"""
        return self.status == 'renewed'
    
    @property
    def has_overdue_payments(self):
        """التحقق من وجود دفعات متأخرة لمدة 30 يوماً أو أكثر"""
        payment_summary = self.get_payment_summary()
        return any(
            month_data['status'] == 'overdue' and 
            month_data['balance'] > 0 and 
            month_data['days_overdue'] >= 30
            for month_data in payment_summary
        )
    
    def duration_display(self):
        """مدة العقد بصيغة (سنة، شهر، يوم) باستخدام start_date و end_date (حساب شامل ليوم الانتهاء)"""
        # اجعل الحساب شامل ليوم الانتهاء لتفادي نتائج مثل 11 شهر و 30 يوم لعقد سنة كاملة
        rd = relativedelta(self.end_date + datetime.timedelta(days=1), self.start_date)
        parts = []
        if rd.years:
            parts.append(_("%(years)s سنة") % {"years": rd.years})
        if rd.months:
            parts.append(_("%(months)s شهر") % {"months": rd.months})
        # أظهر الأيام دائماً إذا لا توجد أجزاء أخرى، أو إذا كانت > 0
        if rd.days or not parts:
            parts.append(_("%(days)s يوم") % {"days": rd.days})
        return "، ".join(parts)

    def overdue_duration_display(self):
        """مدة التأخير بصيغة (سنة، شهر، يوم) للعقود المنتهية"""
        if self.status not in ['expired', 'renewed']:
            return None
        today = timezone.now().date()
        if today <= self.end_date:
            return None
        rd = relativedelta(today, self.end_date)
        parts = []
        if rd.years:
            parts.append(_("%(years)s سنة") % {"years": rd.years})
        if rd.months:
            parts.append(_("%(months)s شهر") % {"months": rd.months})
        if rd.days or not parts:
            parts.append(_("%(days)s يوم") % {"days": rd.days})
        return "، ".join(parts)
    
    def days_overdue(self):
        """عدد أيام التأخير للعقود المنتهية"""
        if self.status not in ['expired', 'renewed']:
            return 0
        today = timezone.now().date()
        if today <= self.end_date:
            return 0
        return (today - self.end_date).days

    def can_renew(self):
        """يسمح بالتجديد فقط إذا كنا ضمن 3 أشهر من تاريخ الانتهاء أو بعد الانتهاء."""
        if self.status == 'cancelled':
            return False
        today = timezone.now().date()
        threshold = self.end_date - relativedelta(months=3)
        return today >= threshold
    
    def total_rent_without_fees(self):
        months = (self.end_date.year - self.start_date.year) * 12 + (self.end_date.month - self.start_date.month) + 1
        return self.monthly_rent * months
    
    def total_rent_with_fees(self):
        return self.total_rent_without_fees() + self.office_fee + self.admin_fee + (self.registration_fee or 0)
    
    def annual_rent(self):
        return self.monthly_rent * 12
    
    def registration_fee_without_office(self):
        return self.registration_fee or 0
    
    def registration_fee_with_office(self):
        return (self.registration_fee or 0) + self.office_fee
    
    def get_absolute_url(self):
        return reverse('lease_detail', kwargs={'pk': self.pk})

    def get_payment_summary(self):
        """الحصول على ملخص الدفعات مع حالات صحيحة للتأخير"""
        summary = []
        payments = self.payments.all().order_by('payment_for_year', 'payment_for_month')
        current_date = self.start_date
        today = timezone.now().date()
        
        while current_date <= self.end_date:
            year, month = current_date.year, current_date.month
            month_payments = payments.filter(payment_for_year=year, payment_for_month=month)
            paid_for_month = month_payments.aggregate(total=Sum('amount'))['total'] or 0
            balance = self.monthly_rent - paid_for_month
            payment_method = None
            payment_date = None
            
            # الحصول على معلومات الدفعة
            if month_payments.exists():
                latest_payment = month_payments.first()
                payment_method = latest_payment.get_payment_method_display()
                payment_date = latest_payment.payment_date
            
            # حساب تاريخ الاستحقاق (أول يوم من الشهر)
            due_date = datetime.date(year, month, 1)
            
            # تحديد حالة الدفعة
            if paid_for_month >= self.monthly_rent:
                status = 'paid'
            elif paid_for_month > 0:
                status = 'partial'
            elif due_date > today:
                status = 'upcoming'  # لم يحن موعدها بعد
            elif due_date <= today:
                if balance > 0:
                    status = 'overdue'  # متأخرة
                else:
                    status = 'due'  # مستحقة
            else:
                status = 'due'
            
            next_payment_date = datetime.date(year, month, 1) + relativedelta(months=1)

            summary.append({
                'month': month,
                'year': year,
                'month_name': _(current_date.strftime('%B')),
                'rent_due': self.monthly_rent,
                'amount_paid': paid_for_month,
                'balance': balance,
                'status': status,
                'payment_method': payment_method,
                'payment_date': payment_date,
                'due_date': due_date,
                'next_payment_date': next_payment_date,
                'days_overdue': (today - due_date).days if due_date <= today and balance > 0 else 0
            })
            current_date += relativedelta(months=1)
        return summary

    def get_absolute_url(self):
        return reverse('lease_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.contract_number} - {self.tenant.name}"
    
    def delete(self, *args, **kwargs):
        """تحديث حالة الوحدة إلى متاحة عند حذف العقد"""
        # تحديث حالة الوحدة إلى متاحة قبل حذف العقد
        if self.unit:
            self.unit.is_available = True
            self.unit.save()
        
        # حذف العقد
        super().delete(*args, **kwargs)

    def _generate_cancellation_notice(self):
        """إنشاء استمارة إلغاء تلقائياً وإرفاقها بالعقد"""
        try:
            from django.template.loader import get_template
            from django.conf import settings
            from io import BytesIO
            from django.core.files.base import ContentFile
            from django.utils.translation import gettext as _
            import logging
            
            logger = logging.getLogger(__name__)
            
            # التحقق من عدم وجود استمارة إلغاء مسبقة لتجنب التكرار
            existing_cancellation_doc = Document.objects.filter(
                lease=self,
                title__icontains='استمارة إلغاء عقد'
            ).first()
            
            if existing_cancellation_doc:
                logger.info(f"Cancellation notice already exists for lease {self.id}")
                return existing_cancellation_doc
            
            template = get_template('dashboard/reports/lease_cancellation_notice.html')
            context = {
                'lease': self,
                'today': timezone.now().date(),
                'company': Company.objects.first(),
            }
            html = template.render(context)
            
            try:
                from weasyprint import HTML
                pdf_bytes = HTML(string=html, base_url=settings.BASE_DIR).write_pdf()
            except Exception:
                # Fallback to xhtml2pdf
                from xhtml2pdf import pisa
                result = BytesIO()
                pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
                pdf_bytes = result.getvalue()

            filename = f"lease_cancellation_{self.contract_number}.pdf"
            doc = Document(lease=self, title=_('استمارة إلغاء عقد') + f" - {self.contract_number}")
            doc.file.save(filename, ContentFile(pdf_bytes))
            doc.save()
            logger.info(f"Cancellation notice generated for lease {self.id}")
            return doc
            
        except Exception as e:
            logger.exception(f"Failed to generate cancellation notice for lease {self.id}: {e}")
            # لا نحتاج إلى رسالة خطأ هنا لأنها عملية تلقائية
            return None
    
    def _generate_initial_invoice(self):
        """إنشاء فاتورة أولية تلقائياً عند إنشاء عقد جديد"""
        print(f"Generating initial invoice for lease {self.id}")
        try:
            from django.template.loader import get_template
            from django.conf import settings
            from io import BytesIO
            from django.core.files.base import ContentFile
            from django.utils.translation import gettext as _
            import logging
            
            logger = logging.getLogger(__name__)
            
            # التحقق من وجود شركة أو إنشاء واحدة افتراضية
            company = Company.objects.first()
            if not company:
                company = Company.objects.create(
                    name="شركة افتراضية",
                    contact_email="default@company.com",
                    contact_phone="1234567890"
                )
                print(f"Created default company for lease {self.id}")
            
            # حساب الرسوم
            office_fee = float(self.office_fee or 0)
            admin_fee = float(self.admin_fee or 0)
            registration_fee = float(self.registration_fee or 0)
            total_fees = office_fee + admin_fee + registration_fee
            logger.info(f"Initial fees for lease {self.id}: office={office_fee}, admin={admin_fee}, registration={registration_fee}, total={total_fees}")
            print(f"Fees calculated for lease {self.id}: office={office_fee}, admin={admin_fee}, registration={registration_fee}, total={total_fees}")
            
            # إنشاء الفاتورة دائماً للاختبار
            print(f"Creating initial invoice for lease {self.id}")
            try:
                from django.template.loader import get_template
                template_invoice = get_template('dashboard/reports/lease_initial_invoice.html')
                context_invoice = {
                    'lease': self,
                    'today': timezone.now().date(),
                    'company': company,
                    'total_fees': total_fees,
                }
                html_invoice = template_invoice.render(context_invoice)
                
                # استخدم generate_pdf_bytes للحصول على الدعم الكامل
                from .utils import generate_pdf_bytes
                pdf_bytes_invoice = generate_pdf_bytes('dashboard/reports/lease_initial_invoice.html', context_invoice)
                    
                contract_num = self.contract_number or f"lease_{self.id}"
                filename_invoice = f"lease_initial_invoice_{contract_num}.pdf"
                print(f"Saving document with title: فاتورة رسوم تسجيل عقد - {contract_num}")
                print(f"Document lease: {self}")
                print(f"Document file path: {filename_invoice}")
                doc_invoice = Document(lease=self, title=_('فاتورة رسوم تسجيل عقد') + f" - {contract_num}")
                doc_invoice.file.save(filename_invoice, ContentFile(pdf_bytes_invoice))
                doc_invoice.save()
                print(f"Document saved with ID: {doc_invoice.id}")
                print(f"Document title: {doc_invoice.title}")
                print(f"Document file: {doc_invoice.file}")
                logger.info(f"Initial invoice generated for lease {self.id}")
                print(f"Initial invoice saved for lease {self.id} - Document ID: {doc_invoice.id}")
            except Exception as e:
                logger.exception(f"Failed to generate initial invoice for lease {self.id}: {e}")
                print(f"Failed to generate initial invoice for lease {self.id}: {e}")
                # لا نحتاج إلى رسالة خطأ هنا لأنها عملية تلقائية
        except Exception as e:
            logger.exception(f"Failed to generate initial invoice for lease {self.id}: {e}")
            print(f"Failed to generate initial invoice for lease {self.id}: {e}")
            # لا نحتاج إلى رسالة خطأ هنا لأنها عملية تلقائية
    def _generate_renewal_notice(self):
        """إنشاء استمارة تجديد تلقائياً وإرفاقها بالعقد"""
        try:
            from django.template.loader import get_template
            from django.conf import settings
            from io import BytesIO
            from django.core.files.base import ContentFile
            from django.utils.translation import gettext as _
            import logging

            logger = logging.getLogger(__name__)

            template = get_template('dashboard/reports/lease_renewal_notice.html')
            context = {
                'lease': self,
                'today': timezone.now().date(),
                'company': Company.objects.first(),
            }
            html = template.render(context)

            try:
                from weasyprint import HTML
                pdf_bytes = HTML(string=html, base_url=settings.BASE_DIR).write_pdf()
            except Exception:
                # Fallback to xhtml2pdf
                from xhtml2pdf import pisa
                result = BytesIO()
                pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
                pdf_bytes = result.getvalue()

            filename = f"lease_renewal_{self.contract_number}.pdf"
            doc = Document(lease=self, title=_('استمارة تجديد عقد') + f" - {self.contract_number}")
            doc.file.save(filename, ContentFile(pdf_bytes))
            doc.save()
            logger.info(f"Renewal notice generated for lease {self.id}")

        except Exception as e:
            logger.exception(f"Failed to generate renewal notice for lease {self.id}: {e}")
            # لا نحتاج إلى رسالة خطأ هنا لأنها عملية تلقائية

    def _generate_renewal_invoice(self):
        """إنشاء فاتورة رسوم تجديد العقد تلقائياً"""
        try:
            from django.template.loader import get_template
            from django.conf import settings
            from io import BytesIO
            from django.core.files.base import ContentFile
            from django.utils.translation import gettext as _
            import logging
            from dateutil.relativedelta import relativedelta

            logger = logging.getLogger(__name__)

            # التحقق من وجود شركة أو إنشاء واحدة افتراضية
            company = Company.objects.first()
            if not company:
                company = Company.objects.create(
                    name="شركة افتراضية",
                    contact_email="default@company.com",
                    contact_phone="1234567890"
                )

            # حساب رسوم التجديد (يمكن تخصيصها حسب الحاجة)
            renewal_fee = self.office_fee or Decimal('5.00')  # رسوم المكتب
            admin_fee = self.admin_fee or Decimal('1.00')     # رسوم إدارية
            total_renewal_fees = renewal_fee + admin_fee

            # إنشاء فاتورة التجديد
            invoice_number = f"REN-{self.contract_number}-{timezone.now().strftime('%Y%m%d')}"
            
            # التحقق من عدم وجود فاتورة تجديد مسبقة لنفس العقد
            existing_invoice = Invoice.objects.filter(
                lease=self,
                invoice_number__startswith=f"REN-{self.contract_number}"
            ).first()
            
            if existing_invoice:
                logger.info(f"Renewal invoice already exists for lease {self.id}")
                return existing_invoice

            # إنشاء الفاتورة
            invoice = Invoice.objects.create(
                tenant=self.tenant,
                lease=self,
                invoice_number=invoice_number,
                issue_date=timezone.now().date(),
                due_date=timezone.now().date() + relativedelta(days=30),  # استحقاق خلال 30 يوم
                status='draft',
                notes=_('فاتورة رسوم تجديد عقد الإيجار')
            )

            # إضافة بنود الفاتورة
            InvoiceItem.objects.create(
                invoice=invoice,
                description=_('رسوم المكتب - تجديد العقد'),
                amount=renewal_fee
            )
            
            InvoiceItem.objects.create(
                invoice=invoice,
                description=_('رسوم إدارية - تجديد العقد'),
                amount=admin_fee
            )

            # إنشاء PDF للفاتورة وإرفاقه كمستند
            try:
                from .utils import generate_pdf_bytes
                context_invoice = {
                    'lease': self,
                    'invoice': invoice,
                    'today': timezone.now().date(),
                    'company': company,
                    'total_fees': total_renewal_fees,
                }
                
                pdf_bytes_invoice = generate_pdf_bytes('dashboard/reports/lease_renewal_invoice.html', context_invoice)
                
                filename_invoice = f"lease_renewal_invoice_{self.contract_number}.pdf"
                doc_invoice = Document(
                    lease=self, 
                    title=_('فاتورة رسوم تجديد عقد') + f" - {self.contract_number}"
                )
                doc_invoice.file.save(filename_invoice, ContentFile(pdf_bytes_invoice))
                doc_invoice.save()
                
                logger.info(f"Renewal invoice generated for lease {self.id} - Invoice ID: {invoice.id}")
                return invoice
                
            except Exception as e:
                logger.exception(f"Failed to generate renewal invoice PDF for lease {self.id}: {e}")
                # الفاتورة تم إنشاؤها، فقط PDF فشل
                return invoice

        except Exception as e:
            logger.exception(f"Failed to generate renewal invoice for lease {self.id}: {e}")
            return None

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('نقداً')),
        ('check', _('شيك')),
        ('bank_transfer', _('تحويل بنكي')),
        ('other', _('أخرى'))
    ]

    CHECK_STATUS_CHOICES = [
        ('pending', _('معلق - في الانتظار')),
        ('cashed', _('تم الصرف')),
        ('returned', _('مرتجع'))
    ]
    
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments', verbose_name=_("العقد"))
    payment_date = models.DateField(_("تاريخ الدفع"))
    amount = models.DecimalField(_("المبلغ المدفوع"), max_digits=10, decimal_places=2)
    payment_for_month = models.IntegerField(_("دفعة عن شهر"), choices=[(i, _(str(i))) for i in range(1, 13)])
    payment_for_year = models.IntegerField(_("دفعة عن سنة"), default=timezone.now().year)
    payment_method = models.CharField(_("طريقة الدفع"), max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    check_number = models.CharField(_("رقم الشيك"), max_length=50, blank=True, null=True)
    check_date = models.DateField(_("تاريخ الشيك"), blank=True, null=True)
    bank_name = models.CharField(_("اسم البنك"), max_length=100, blank=True, null=True)
    check_status = models.CharField(_("حالة الشيك"), max_length=20, choices=CHECK_STATUS_CHOICES, default='pending', blank=True, null=True)
    return_reason = models.TextField(_("سبب إرجاع الشيك"), blank=True, null=True)
    notes = models.TextField(_("ملاحظات"), blank=True, null=True)
    
    class Meta:
        verbose_name = _("دفعة")
        verbose_name_plural = _("الدفعات")
        ordering = ['-payment_date']
        
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.payment_method == 'check':
            if not self.check_status:
                raise ValidationError({'check_status': _('حالة الشيك مطلوبة عند اختيار طريقة الدفع بالشيك')})
            
            if self.check_status == 'returned' and not self.return_reason:
                raise ValidationError({'return_reason': _('سبب إرجاع الشيك مطلوب عند اختيار حالة "مرتجع"')})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.amount} for {self.lease.contract_number} ({self.payment_for_month}/{self.payment_for_year})"

    def get_receipt_url(self):
        return reverse('report_payment_receipt', kwargs={'pk': self.pk})

class SecurityDeposit(models.Model):
    """نموذج خاص باستلام مبلغ التأمين من المستأجر (كاش أو شيك)"""
    DEPOSIT_STATUS_CHOICES = [
        ('held', _('محجوز')),          # الإيداع محتجز لدى المكتب
        ('refunded', _('تم إرجاعه')),  # تم إرجاع التأمين للمستأجر
        ('applied', _('مستخدم')),      # تم استخدامه لتسوية مبالغ مستحقة
    ]

    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='security_deposits', verbose_name=_("العقد"))
    received_date = models.DateField(_("تاريخ الاستلام"), default=timezone.now)
    amount = models.DecimalField(_("مبلغ التأمين"), max_digits=10, decimal_places=2)
    payment_method = models.CharField(_("طريقة الدفع"), max_length=20, choices=Payment.PAYMENT_METHOD_CHOICES, default='cash')
    # حقول الشيك (اختيارية وتظهر عند الدفع بالشيك)
    check_number = models.CharField(_("رقم الشيك"), max_length=50, blank=True, null=True)
    check_date = models.DateField(_("تاريخ الشيك"), blank=True, null=True)
    bank_name = models.CharField(_("اسم البنك"), max_length=100, blank=True, null=True)
    check_status = models.CharField(_("حالة الشيك"), max_length=20, choices=Payment.CHECK_STATUS_CHOICES, default='pending', blank=True, null=True)
    return_reason = models.TextField(_("سبب إرجاع الشيك"), blank=True, null=True)
    status = models.CharField(_("حالة التأمين"), max_length=20, choices=DEPOSIT_STATUS_CHOICES, default='held')
    notes = models.TextField(_("ملاحظات"), blank=True, null=True)

    class Meta:
        verbose_name = _("تأمين")
        verbose_name_plural = _("التأمينات")
        ordering = ['-received_date']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.payment_method == 'check':
            if not self.check_status:
                raise ValidationError({'check_status': _("حالة الشيك مطلوبة عند اختيار طريقة الدفع بالشيك")})
            if self.check_status == 'returned' and not self.return_reason:
                raise ValidationError({'return_reason': _("سبب إرجاع الشيك مطلوب عند اختيار حالة \"مرتجع\"")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.amount} - {self.lease.contract_number} ({self.get_status_display()})"

class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [('submitted', _('تم الإرسال')), ('in_progress', _('قيد التنفيذ')), ('completed', _('مكتمل')), ('cancelled', _('ملغي'))]
    PRIORITY_CHOICES = [('low', _('منخفضة')), ('medium', _('متوسطة')), ('high', _('عالية'))]
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='maintenance_requests', verbose_name=_("العقد"))
    title = models.CharField(_("عنوان الطلب"), max_length=200)
    description = models.TextField(_("وصف المشكلة"))
    priority = models.CharField(_("الأولوية"), max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(_("الحالة"), max_length=20, choices=STATUS_CHOICES, default='submitted')
    image = models.ImageField(_("صورة مرفقة (اختياري)"), upload_to='maintenance_requests/', blank=True, null=True)
    reported_date = models.DateTimeField(_("تاريخ الإبلاغ"), auto_now_add=True)
    staff_notes = models.TextField(_("ملاحظات الموظف"), blank=True, null=True)
    
    class Meta:
        verbose_name = _("طلب صيانة")
        verbose_name_plural = _("طلبات الصيانة")
        ordering = ['-reported_date']
        
    def __str__(self):
        return self.title

class Document(models.Model):
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='documents', verbose_name=_("العقد"))
    title = models.CharField(_("عنوان المستند"), max_length=200)
    file = models.FileField(_("الملف"), upload_to='lease_documents/')
    uploaded_at = models.DateTimeField(_("تاريخ الرفع"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("مستند")
        verbose_name_plural = _("المستندات")
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return self.title

class Expense(models.Model):
    EXPENSE_CATEGORY_CHOICES = [('maintenance', _('صيانة')), ('utilities', _('خدمات (كهرباء، ماء)')), ('salaries', _('رواتب')), ('marketing', _('تسويق')), ('admin', _('رسوم إدارية/حكومية')), ('other', _('أخرى'))]
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='expenses', verbose_name=_("المبنى"))
    category = models.CharField(_("فئة المصروف"), max_length=50, choices=EXPENSE_CATEGORY_CHOICES)
    description = models.CharField(_("الوصف"), max_length=255)
    amount = models.DecimalField(_("المبلغ"), max_digits=10, decimal_places=2)
    expense_date = models.DateField(_("تاريخ المصروف"))
    receipt = models.FileField(_("إيصال/فاتورة (اختياري)"), upload_to='expense_receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("مصروف")
        verbose_name_plural = _("المصاريف")
        ordering = ['-expense_date']
        
    def __str__(self):
        return f"{self.get_category_display()} - {self.amount}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name=_("المستخدم"))
    message = models.TextField(_("الرسالة"))
    read = models.BooleanField(_("مقروءة"), default=False)
    timestamp = models.DateTimeField(_("الوقت"), auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _("إشعار")
        verbose_name_plural = _("الإشعارات")
        ordering = ['-timestamp']

    def __str__(self):
        return self.message

class Invoice(models.Model):
    INVOICE_STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('sent', _('مرسلة')),
        ('paid', _('مدفوعة')),
        ('overdue', _('متأخرة')),
        ('cancelled', _('ملغاة')),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='invoices', verbose_name=_("المستأجر"))
    lease = models.ForeignKey(Lease, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices', verbose_name=_("العقد"))
    invoice_number = models.CharField(_("رقم الفاتورة"), max_length=50, unique=True)
    issue_date = models.DateField(_("تاريخ الإصدار"), default=timezone.now)
    due_date = models.DateField(_("تاريخ الاستحقاق"))
    status = models.CharField(_("الحالة"), max_length=20, choices=INVOICE_STATUS_CHOICES, default='draft')
    notes = models.TextField(_("ملاحظات"), blank=True, null=True)

    class Meta:
        verbose_name = _("فاتورة")
        verbose_name_plural = _("الفواتير")
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.invoice_number} - {self.tenant.name}"

    @property
    def total_amount(self):
        return self.items.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    def get_absolute_url(self):
        return reverse('invoice_detail', kwargs={'pk': self.pk})

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items', verbose_name=_("الفاتورة"))
    description = models.CharField(_("الوصف"), max_length=255)
    amount = models.DecimalField(_("المبلغ"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("بند الفاتورة")
        verbose_name_plural = _("بنود الفواتير")

    def __str__(self):
        return self.description


class UserProfile(models.Model):
    """Extended user profile to add phone number for OTP authentication"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_("المستخدم"))
    phone_number = models.CharField(_("رقم الهاتف"), max_length=15, blank=True, null=True, help_text=_("رقم الهاتف للتحقق عبر OTP"), validators=[RegexValidator(regex=r'^\+968\d{8}$', message=_("الرجاء إدخال رقم هاتف عماني صالح يبدأ بـ +968 (8 أرقام بعد المقدمة)"))])
    first_name_english = models.CharField(_("الاسم الأول بالإنجليزية"), max_length=150, blank=True, null=True, help_text=_("ترجمة تلقائية للاسم الأول"))
    
    # === صلاحيات الوصول (Permissions) ===
    # لوحة التحكم
    can_view_dashboard = models.BooleanField(_("عرض لوحة التحكم"), default=True, help_text=_("الوصول إلى لوحة التحكم الرئيسية"))
    can_view_dashboard_stats = models.BooleanField(_("عرض إحصائيات العقود"), default=True, help_text=_("بطاقة العقود النشطة"))
    can_view_dashboard_financial = models.BooleanField(_("عرض البيانات المالية"), default=False, help_text=_("الدخل المتوقع، المصاريف، صافي الدخل"))
    can_view_dashboard_calendar = models.BooleanField(_("عرض تقويم التجديد"), default=True, help_text=_("تقويم تجديد العقود"))
    can_view_dashboard_charts = models.BooleanField(_("عرض المخططات البيانية"), default=True, help_text=_("اتجاه الإيرادات، إشغال الوحدات"))
    can_view_dashboard_transactions = models.BooleanField(_("عرض الحركات المالية"), default=False, help_text=_("آخر الدفعات والمصاريف"))
    
    # إدارة العقارات
    can_view_buildings = models.BooleanField(_("عرض المباني"), default=True)
    can_manage_buildings = models.BooleanField(_("إدارة المباني"), default=False, help_text=_("إضافة، تعديل، حذف المباني"))
    can_view_units = models.BooleanField(_("عرض الوحدات"), default=True)
    can_manage_units = models.BooleanField(_("إدارة الوحدات"), default=False, help_text=_("إضافة، تعديل، حذف الوحدات"))
    
    # إدارة العقود
    can_view_leases = models.BooleanField(_("عرض العقود"), default=True)
    can_manage_leases = models.BooleanField(_("إدارة العقود"), default=False, help_text=_("إضافة، تعديل، حذف، تجديد، إلغاء العقود"))
    
    # إدارة المستأجرين
    can_view_tenants = models.BooleanField(_("عرض المستأجرين"), default=True)
    can_manage_tenants = models.BooleanField(_("إدارة المستأجرين"), default=False, help_text=_("إضافة، تعديل، حذف المستأجرين"))
    
    # العمليات المالية
    can_view_payments = models.BooleanField(_("عرض الدفعات"), default=False)
    can_manage_payments = models.BooleanField(_("إدارة الدفعات"), default=False, help_text=_("إضافة، تعديل، حذف الدفعات"))
    can_view_invoices = models.BooleanField(_("عرض الفواتير"), default=False)
    can_manage_invoices = models.BooleanField(_("إدارة الفواتير"), default=False, help_text=_("إنشاء، تعديل، حذف الفواتير"))
    can_view_expenses = models.BooleanField(_("عرض المصروفات"), default=False)
    can_manage_expenses = models.BooleanField(_("إدارة المصروفات"), default=False, help_text=_("إضافة، تعديل، حذف المصروفات"))
    
    # الإنذارات والإشعارات
    can_view_notices = models.BooleanField(_("عرض الإنذارات"), default=False)
    can_manage_notices = models.BooleanField(_("إدارة الإنذارات"), default=False, help_text=_("إنشاء، تعديل، إرسال الإنذارات"))
    
    # التقارير
    can_view_reports = models.BooleanField(_("عرض التقارير"), default=False)
    can_export_reports = models.BooleanField(_("تصدير التقارير"), default=False, help_text=_("تصدير التقارير إلى PDF/Excel"))
    
    # إدارة المستخدمين والإعدادات
    can_manage_users = models.BooleanField(_("إدارة المستخدمين"), default=False, help_text=_("إضافة، تعديل، حذف المستخدمين وصلاحياتهم"))
    can_access_settings = models.BooleanField(_("الوصول إلى الإعدادات"), default=False, help_text=_("تعديل إعدادات النظام"))
    
    class Meta:
        verbose_name = _("ملف المستخدم")
        verbose_name_plural = _("ملفات المستخدمين")
    
    def __str__(self):
        return f"{self.user.username} - {self.phone_number or 'لا يوجد رقم هاتف'}"
    
    def get_display_name(self, language='ar'):
        """Get user's display name based on language preference"""
        if language == 'en' and self.first_name_english:
            # Use English translation if available and language is English
            english_name = self.first_name_english
            last_name = self.user.last_name or ''
            return f"{english_name} {last_name}".strip()
        else:
            # Use Arabic name (default behavior)
            return self.user.get_full_name() or self.user.username
    
    def has_permission(self, permission_name):
        """التحقق من وجود صلاحية معينة للمستخدم"""
        # المستخدمون الإداريون (superusers) لديهم جميع الصلاحيات
        if self.user.is_superuser:
            return True
        # التحقق من الصلاحية المحددة
        return getattr(self, permission_name, False)
    
    def get_all_permissions(self):
        """الحصول على جميع الصلاحيات المفعلة للمستخدم"""
        permissions = {}
        permission_fields = [
            'can_view_dashboard', 'can_view_dashboard_stats', 'can_view_dashboard_financial',
            'can_view_dashboard_calendar', 'can_view_dashboard_charts', 'can_view_dashboard_transactions',
            'can_view_buildings', 'can_manage_buildings',
            'can_view_units', 'can_manage_units',
            'can_view_leases', 'can_manage_leases',
            'can_view_tenants', 'can_manage_tenants',
            'can_view_payments', 'can_manage_payments',
            'can_view_invoices', 'can_manage_invoices',
            'can_view_expenses', 'can_manage_expenses',
            'can_view_notices', 'can_manage_notices',
            'can_view_reports', 'can_export_reports',
            'can_manage_users', 'can_access_settings',
        ]
        for field in permission_fields:
            permissions[field] = getattr(self, field, False)
        return permissions
    
    def set_role_permissions(self, role):
        """تعيين صلاحيات محددة مسبقاً حسب الدور الوظيفي"""
        role_permissions = {
            'property_manager': {  # مدير عقارات
                'can_view_dashboard': True,
                'can_view_dashboard_stats': True,
                'can_view_dashboard_financial': False,
                'can_view_dashboard_calendar': True,
                'can_view_dashboard_charts': False,
                'can_view_dashboard_transactions': False,
                'can_view_buildings': True, 'can_manage_buildings': False,
                'can_view_units': True, 'can_manage_units': True,
                'can_view_leases': True, 'can_manage_leases': True,
                'can_view_tenants': True, 'can_manage_tenants': False,
                'can_view_payments': False, 'can_manage_payments': False,
                'can_view_invoices': False, 'can_manage_invoices': False,
                'can_view_expenses': False, 'can_manage_expenses': False,
                'can_view_notices': False, 'can_manage_notices': False,
                'can_view_reports': False, 'can_export_reports': False,
                'can_manage_users': False, 'can_access_settings': False,
            },
            'financial_manager': {  # مدير مالي
                'can_view_dashboard': True,
                'can_view_dashboard_stats': True,
                'can_view_dashboard_financial': True,
                'can_view_dashboard_calendar': False,
                'can_view_dashboard_charts': True,
                'can_view_dashboard_transactions': True,
                'can_view_buildings': True, 'can_manage_buildings': False,
                'can_view_units': True, 'can_manage_units': False,
                'can_view_leases': True, 'can_manage_leases': False,
                'can_view_tenants': True, 'can_manage_tenants': False,
                'can_view_payments': True, 'can_manage_payments': True,
                'can_view_invoices': True, 'can_manage_invoices': True,
                'can_view_expenses': True, 'can_manage_expenses': True,
                'can_view_notices': True, 'can_manage_notices': True,
                'can_view_reports': True, 'can_export_reports': True,
                'can_manage_users': False, 'can_access_settings': False,
            },
            'tenant_manager': {  # مدير المستأجرين
                'can_view_dashboard': True,
                'can_view_dashboard_stats': True,
                'can_view_dashboard_financial': False,
                'can_view_dashboard_calendar': True,
                'can_view_dashboard_charts': False,
                'can_view_dashboard_transactions': False,
                'can_view_buildings': True, 'can_manage_buildings': False,
                'can_view_units': True, 'can_manage_units': False,
                'can_view_leases': True, 'can_manage_leases': False,
                'can_view_tenants': True, 'can_manage_tenants': True,
                'can_view_payments': False, 'can_manage_payments': False,
                'can_view_invoices': False, 'can_manage_invoices': False,
                'can_view_expenses': False, 'can_manage_expenses': False,
                'can_view_notices': False, 'can_manage_notices': False,
                'can_view_reports': False, 'can_export_reports': False,
                'can_manage_users': False, 'can_access_settings': False,
            },
            'viewer': {  # مشاهد فقط
                'can_view_dashboard': True,
                'can_view_dashboard_stats': True,
                'can_view_dashboard_financial': True,
                'can_view_dashboard_calendar': True,
                'can_view_dashboard_charts': True,
                'can_view_dashboard_transactions': True,
                'can_view_buildings': True, 'can_manage_buildings': False,
                'can_view_units': True, 'can_manage_units': False,
                'can_view_leases': True, 'can_manage_leases': False,
                'can_view_tenants': True, 'can_manage_tenants': False,
                'can_view_payments': True, 'can_manage_payments': False,
                'can_view_invoices': True, 'can_manage_invoices': False,
                'can_view_expenses': True, 'can_manage_expenses': False,
                'can_view_notices': True, 'can_manage_notices': False,
                'can_view_reports': True, 'can_export_reports': False,
                'can_manage_users': False, 'can_access_settings': False,
            },
        }
        
        if role in role_permissions:
            for permission, value in role_permissions[role].items():
                setattr(self, permission, value)
            self.save()


class OTP(models.Model):
    """OTP model for storing verification codes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps', verbose_name=_("المستخدم"))
    code = models.CharField(_("رمز التحقق"), max_length=6)
    phone_number = models.CharField(_("رقم الهاتف"), max_length=15, validators=[RegexValidator(regex=r'^\+968\d{8}$', message=_("الرجاء إدخال رقم هاتف عماني صالح يبدأ بـ +968 (8 أرقام بعد المقدمة)"))])
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    expires_at = models.DateTimeField(_("تاريخ الانتهاء"))
    is_used = models.BooleanField(_("مستخدم"), default=False)
    purpose = models.CharField(_("الغرض"), max_length=50, default='login', choices=[
        ('login', _('تسجيل الدخول')),
        ('reset_password', _('إعادة تعيين كلمة المرور')),
        ('verify_phone', _('التحقق من رقم الهاتف')),
    ])
    
    class Meta:
        verbose_name = _("رمز التحقق")
        verbose_name_plural = _("رموز التحقق")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.user.username} - {self.code}"
    
    @classmethod
    def generate_code(cls, length=6):
        """Generate a random OTP code"""
        return ''.join(secrets.choice(string.digits) for _ in range(length))
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()
    
    def mark_as_used(self):
        """Mark OTP as used"""
        self.is_used = True
        self.save()


# === Real Estate Office Management Models ===

class RealEstateOffice(models.Model):
    """نموذج مكتب عقاري"""
    name = models.CharField(_("اسم المكتب العقاري"), max_length=200)
    license_number = models.CharField(_("رقم الترخيص"), max_length=100, unique=True)
    contact_person = models.CharField(_("الشخص المسؤول"), max_length=150)
    phone = models.CharField(_("رقم الهاتف"), max_length=20)
    email = models.EmailField(_("البريد الإلكتروني"), blank=True, null=True)
    address = models.TextField(_("العنوان"))
    commission_rate = models.DecimalField(_("نسبة العمولة الافتراضية (%)"), max_digits=5, decimal_places=2, default=5.00, help_text=_("النسبة المئوية من الإيجار الشهري"))
    is_active = models.BooleanField(_("نشط"), default=True)
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("مكتب عقاري")
        verbose_name_plural = _("المكاتب العقارية")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BuildingOwner(models.Model):
    """نموذج مالك المبنى"""
    OWNER_TYPE_CHOICES = [
        ('individual', _('فرد')),
        ('company', _('شركة')),
        ('government', _('حكومي')),
    ]
    
    name = models.CharField(_("اسم المالك"), max_length=200)
    owner_type = models.CharField(_("نوع المالك"), max_length=20, choices=OWNER_TYPE_CHOICES, default='individual')
    phone = models.CharField(_("رقم الهاتف"), max_length=20)
    email = models.EmailField(_("البريد الإلكتروني"), blank=True, null=True)
    address = models.TextField(_("العنوان"), blank=True, null=True)
    national_id = models.CharField(_("رقم الهوية/السجل التجاري"), max_length=50, blank=True, null=True)
    bank_account = models.CharField(_("رقم الحساب البنكي"), max_length=50, blank=True, null=True)
    bank_name = models.CharField(_("اسم البنك"), max_length=100, blank=True, null=True)
    is_active = models.BooleanField(_("نشط"), default=True)
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("مالك مبنى")
        verbose_name_plural = _("مالكو المباني")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CommissionAgreement(models.Model):
    """نموذج اتفاقية العمولة بين المكتب العقاري ومالك المبنى"""
    STATUS_CHOICES = [
        ('active', _('نشط')),
        ('expired', _('منتهي')),
        ('cancelled', _('ملغي')),
    ]
    
    real_estate_office = models.ForeignKey(RealEstateOffice, on_delete=models.CASCADE, verbose_name=_("المكتب العقاري"))
    building_owner = models.ForeignKey(BuildingOwner, on_delete=models.CASCADE, verbose_name=_("مالك المبنى"))
    building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name=_("المبنى"))
    agreement_number = models.CharField(_("رقم الاتفاقية"), max_length=50, unique=True)
    commission_rate = models.DecimalField(_("نسبة العمولة (%)"), max_digits=5, decimal_places=2, help_text=_("النسبة المئوية من الإيجار الشهري"))
    start_date = models.DateField(_("تاريخ بدء الاتفاقية"))
    end_date = models.DateField(_("تاريخ انتهاء الاتفاقية"))
    status = models.CharField(_("حالة الاتفاقية"), max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(_("ملاحظات"), blank=True, null=True)
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("اتفاقية عمولة")
        verbose_name_plural = _("اتفاقيات العمولة")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.agreement_number} - {self.real_estate_office.name} & {self.building_owner.name}"
    
    def is_active(self):
        """تحقق من أن الاتفاقية نشطة"""
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date


class RentCollection(models.Model):
    """نموذج استلام الإيجارات من المستأجرين"""
    COLLECTION_STATUS_CHOICES = [
        ('collected', _('تم الاستلام')),
        ('pending', _('في الانتظار')),
        ('overdue', _('متأخر')),
    ]
    
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, verbose_name=_("العقد"))
    real_estate_office = models.ForeignKey(RealEstateOffice, on_delete=models.CASCADE, verbose_name=_("المكتب العقاري"))
    collection_date = models.DateField(_("تاريخ الاستلام"), default=timezone.now)
    amount_collected = models.DecimalField(_("المبلغ المستلم"), max_digits=10, decimal_places=2)
    collection_method = models.CharField(_("طريقة الاستلام"), max_length=20, choices=Payment.PAYMENT_METHOD_CHOICES)
    status = models.CharField(_("حالة الاستلام"), max_length=20, choices=COLLECTION_STATUS_CHOICES, default='collected')
    notes = models.TextField(_("ملاحظات"), blank=True, null=True)
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("استلام إيجار")
        verbose_name_plural = _("استلام الإيجارات")
        ordering = ['-collection_date']
    
    def __str__(self):
        return f"{self.lease.contract_number} - {self.amount_collected} - {self.collection_date}"


class CommissionDistribution(models.Model):
    """نموذج توزيع العمولات لمالك المبنى"""
    DISTRIBUTION_STATUS_CHOICES = [
        ('pending', _('في الانتظار')),
        ('distributed', _('تم التوزيع')),
        ('cancelled', _('ملغي')),
    ]
    
    rent_collection = models.ForeignKey(RentCollection, on_delete=models.CASCADE, verbose_name=_("استلام الإيجار"))
    commission_agreement = models.ForeignKey(CommissionAgreement, on_delete=models.CASCADE, verbose_name=_("اتفاقية العمولة"))
    building_owner = models.ForeignKey(BuildingOwner, on_delete=models.CASCADE, verbose_name=_("مالك المبنى"))
    owner_share = models.DecimalField(_("حصة المالك"), max_digits=10, decimal_places=2, help_text=_("المبلغ المستحق لمالك المبنى"))
    office_commission = models.DecimalField(_("عمولة المكتب"), max_digits=10, decimal_places=2, help_text=_("عمولة المكتب العقاري"))
    distribution_date = models.DateField(_("تاريخ التوزيع"), blank=True, null=True)
    status = models.CharField(_("حالة التوزيع"), max_length=20, choices=DISTRIBUTION_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(_("طريقة الدفع"), max_length=20, choices=Payment.PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_reference = models.CharField(_("مرجع الدفع"), max_length=100, blank=True, null=True)
    notes = models.TextField(_("ملاحظات"), blank=True, null=True)
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("توزيع عمولة")
        verbose_name_plural = _("توزيع العمولات")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.building_owner.name} - {self.owner_share} - {self.distribution_date or 'لم يتم التوزيع'}"
    
    def calculate_commission(self):
        """حساب العمولة بناءً على الاتفاقية"""
        if self.commission_agreement:
            commission_rate = self.commission_agreement.commission_rate / 100
            self.office_commission = self.rent_collection.amount_collected * commission_rate
            self.owner_share = self.rent_collection.amount_collected - self.office_commission
            return self.office_commission, self.owner_share
        return Decimal('0.00'), self.rent_collection.amount_collected


class PaymentOverdueNotice(models.Model):
    """نموذج إنذار عدم سداد الإيجار - متوافق مع القوانين العمانية"""

    NOTICE_STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('sent', _('تم الإرسال')),
        ('acknowledged', _('تم الاستلام')),
        ('resolved', _('تم الحل')),
        ('escalated', _('تم التصعيد')),
    ]

    LEGAL_ACTION_CHOICES = [
        ('none', _('لا يوجد')),
        ('contract_termination', _('فسخ العقد')),
        ('eviction', _('الإخلاء')),
        ('legal_proceedings', _('إجراءات قانونية')),
    ]

    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='overdue_notices', verbose_name=_("العقد"))
    notice_date = models.DateField(_("تاريخ الإنذار"), default=timezone.now)
    due_date = models.DateField(_("تاريخ الاستحقاق الأصلي"), blank=True, null=True, help_text=_("أقدم تاريخ استحقاق من التفاصيل"))
    legal_deadline = models.DateField(_("الموعد النهائي القانوني"))
    status = models.CharField(_("حالة الإنذار"), max_length=20, choices=NOTICE_STATUS_CHOICES, default='draft')
    potential_legal_action = models.CharField(_("الإجراء القانوني المحتمل"), max_length=30, choices=LEGAL_ACTION_CHOICES, default='contract_termination')

    # حقول إضافية للمتابعة
    sent_date = models.DateTimeField(_("تاريخ الإرسال"), blank=True, null=True)
    acknowledged_date = models.DateTimeField(_("تاريخ الاستلام"), blank=True, null=True)
    resolved_date = models.DateTimeField(_("تاريخ الحل"), blank=True, null=True)
    notes = models.TextField(_("ملاحظات"), blank=True, null=True)

    # معلومات الإرسال
    delivery_method = models.CharField(_("طريقة التسليم"), max_length=50, blank=True, null=True)
    recipient_signature = models.CharField(_("توقيع المستلم"), max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _("إنذار عدم سداد")
        verbose_name_plural = _("إنذارات عدم السداد")
        ordering = ['-notice_date']
        unique_together = ['lease', 'notice_date']

    def __str__(self):
        return f"إنذار {self.lease.contract_number} - {self.notice_date.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        # حساب الموعد النهائي القانوني (30 يوم من تاريخ الإنذار حسب القانون العماني)
        if not self.legal_deadline:
            self.legal_deadline = self.notice_date + relativedelta(days=30)

        # حفظ الكائن أولاً
        super().save(*args, **kwargs)

        # حساب due_date من أقدم تاريخ استحقاق في التفاصيل (بعد الحفظ)
        if self.pk and self.details.exists():
            try:
                earliest_due_date = self.details.order_by('due_date').first().due_date
                if self.due_date != earliest_due_date:
                    self.due_date = earliest_due_date
                    # حفظ مرة أخرى فقط إذا تغير التاريخ
                    super().save(update_fields=['due_date'])
            except:
                pass

    def generate_formal_payment_request(self):
        """إنشاء إنذار رسمي بطلب السداد"""
        from django.utils import timezone
        from datetime import datetime
        
        # تحديث محتوى الإنذار ليعكس الحالة الحالية
        overdue_months = []
        total_amount = 0
        
        for detail in self.details.all():
            # حساب أيام التأخير
            due_date = detail.due_date
            days_overdue = (timezone.now().date() - due_date).days
            
            overdue_months.append({
                'month': detail.overdue_month,
                'year': detail.overdue_year,
                'amount': detail.overdue_amount,
                'due_date': due_date,
                'days_overdue': days_overdue
            })
            total_amount += detail.overdue_amount
        
        # معلومات الشركة (يمكن تخصيصها لاحقاً)
        company_name = "شركة افتراضية"
        company_phone = "1234567890"
        company_email = "default@company.com"
        
        # إنشاء محتوى الإنذار الرسمي بتصميم كلاسيكي جميل
        content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
                body {{
                    font-family: 'Amiri', 'Times New Roman', serif;
                    line-height: 1.6;
                    color: #2c3e50;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                }}
                .document {{
                    background: white;
                    border: 3px solid #2c3e50;
                    border-radius: 15px;
                    padding: 40px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    position: relative;
                }}
                .document::before {{
                    content: '';
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    right: 10px;
                    bottom: 10px;
                    border: 1px solid #bdc3c7;
                    border-radius: 10px;
                    pointer-events: none;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px double #2c3e50;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .company-info {{
                    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                .title {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #c0392b;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                    margin: 20px 0;
                    text-decoration: underline;
                    text-decoration-color: #e74c3c;
                }}
                .info-section {{
                    background: linear-gradient(135deg, #ecf0f1 0%, #bdc3c7 100%);
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                    border-left: 5px solid #3498db;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin: 15px 0;
                }}
                .info-item {{
                    background: white;
                    padding: 10px 15px;
                    border-radius: 8px;
                    border-left: 3px solid #3498db;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .subject {{
                    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    font-weight: bold;
                    font-size: 18px;
                    margin: 20px 0;
                    box-shadow: 0 5px 15px rgba(231, 76, 60, 0.3);
                }}
                .content-section {{
                    background: #fdfefe;
                    padding: 25px;
                    border-radius: 10px;
                    border: 2px solid #ecf0f1;
                    margin: 20px 0;
                }}
                .amounts-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                .amounts-table th {{
                    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                    color: white;
                    padding: 15px;
                    text-align: center;
                    font-weight: bold;
                }}
                .amounts-table td {{
                    padding: 12px 15px;
                    text-align: center;
                    border-bottom: 1px solid #ecf0f1;
                }}
                .amounts-table tr:nth-child(even) {{
                    background: #f8f9fa;
                }}
                .amounts-table tr:hover {{
                    background: #e3f2fd;
                }}
                .total-row {{
                    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important;
                    color: white !important;
                    font-weight: bold;
                    font-size: 16px;
                }}
                .action-required {{
                    background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                    box-shadow: 0 5px 15px rgba(243, 156, 18, 0.3);
                }}
                .legal-notes {{
                    background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                    font-size: 14px;
                }}
                .signatures {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 30px;
                    margin-top: 40px;
                }}
                .signature-box {{
                    border: 2px solid #2c3e50;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    background: #f8f9fa;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 2px solid #ecf0f1;
                    font-size: 12px;
                    color: #7f8c8d;
                }}
                .highlight {{
                    color: #e74c3c;
                    font-weight: bold;
                }}
                .month-name {{
                    font-weight: bold;
                    color: #2c3e50;
                }}
            </style>
        </head>
        <body>
            <div class="document">
                <div class="company-info">
                    <h2 style="margin: 0; font-size: 24px;">🏢 {company_name}</h2>
                    <p style="margin: 5px 0;">📞 هاتف: {company_phone} | 📧 بريد إلكتروني: {company_email}</p>
                </div>
                
                <div class="header">
                    <div class="title">⚖️ إنذار رسمي بطلب السداد</div>
                </div>
                
                <div class="info-section">
                    <h3 style="color: #2c3e50; margin-top: 0;">📋 معلومات الإنذار</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <strong>🔢 رقم المرجع:</strong> {self.id}
                        </div>
                        <div class="info-item">
                            <strong>📅 تاريخ الإنذار:</strong> {self.notice_date.strftime('%d/%m/%Y')}
                        </div>
                        <div class="info-item">
                            <strong>👤 إلى السيد/السيدة:</strong> {self.lease.tenant.name}
                        </div>
                        <div class="info-item">
                            <strong>📄 رقم العقد:</strong> {self.lease.contract_number}
                        </div>
                        <div class="info-item">
                            <strong>🏠 الوحدة المؤجرة:</strong> {self.lease.unit.unit_number} - {self.lease.unit.building.name}
                        </div>
                        <div class="info-item">
                            <strong>📍 العنوان:</strong> {self.lease.unit.building.address or 'محافظة مسقط ولاية بوشر منطقة الخوير الجنوبية'}
                        </div>
                    </div>
                </div>
                
                <div class="subject">
                    📢 الموضوع: إنذار رسمي لعدم سداد إيجار الوحدة رقم {self.lease.unit.unit_number}
                </div>
                
                <div class="content-section">
                    <h3 style="color: #2c3e50;">📝 المحتوى:</h3>
                    <p style="font-size: 16px; line-height: 1.8;">
                        نتشرف بإحاطتكم علماً بأنه قد تأخر سداد إيجار الوحدة المؤجرة لكم لعدة شهور كما هو موضح في الجدول أدناه.
                    </p>
                    
                    <table class="amounts-table">
                        <thead>
                            <tr>
                                <th>🗓️ الشهر والسنة</th>
                                <th>💰 المبلغ المستحق (ر.ع)</th>
                                <th>📅 تاريخ الاستحقاق</th>
                                <th>⏰ عدد أيام التأخير</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # إضافة صفوف الشهور المتأخرة
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل', 5: 'مايو', 6: 'يونيو',
            7: 'يوليو', 8: 'أغسطس', 9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        
        for month_data in overdue_months:
            month_name = month_names.get(month_data['month'], str(month_data['month']))
            content += f"""
                            <tr>
                                <td class="month-name">{month_name} {month_data['year']}</td>
                                <td><strong>{month_data['amount']:,.2f}</strong></td>
                                <td>{month_data['due_date'].strftime('%d/%m/%Y')}</td>
                                <td class="highlight">{month_data['days_overdue']} يوم</td>
                            </tr>
            """
        
        content += f"""
                        </tbody>
                        <tfoot>
                            <tr class="total-row">
                                <td><strong>📊 إجمالي المبالغ المتأخرة:</strong></td>
                                <td colspan="3"><strong>{total_amount:,.2f} ريال عماني</strong></td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
                
                <div class="action-required">
                    <h3 style="margin-top: 0; color: white;">⚡ الإجراء المطلوب:</h3>
                    <p style="font-size: 16px; line-height: 1.8;">
                        يجب عليكم سداد جميع المبالغ المتأخرة المذكورة أعلاه كاملة خلال المدة القانونية المحددة في سلطنة عمان 
                        <strong>(30 يوماً)</strong> من تاريخ هذا الإنذار وذلك لتجنب اتخاذ الإجراءات القانونية اللازمة بما في ذلك فسخ العقد و/أو الإخلاء.
                    </p>
                    <div style="text-align: center; margin: 15px 0;">
                        <div style="background: white; color: #e67e22; padding: 10px; border-radius: 8px; display: inline-block;">
                            <strong>⏰ الموعد النهائي للسداد: {self.legal_deadline.strftime('%d/%m/%Y')}</strong>
                        </div>
                    </div>
                    <p><strong>🚨 الإجراء في حالة عدم السداد:</strong> {self.get_potential_legal_action_display()}</p>
                    <p><strong>📊 عدد شهور التأخير:</strong> {len(overdue_months)} شهر</p>
                </div>
                
                <div class="legal-notes">
                    <h3 style="margin-top: 0; color: white;">⚖️ ملاحظات قانونية هامة:</h3>
                    <ul style="text-align: right; padding-right: 20px;">
                        <li>هذا الإنذار صادر وفقاً لأحكام قانون الإيجار في سلطنة عمان</li>
                        <li>عدم الاستجابة خلال المدة المحددة قد يؤدي إلى اتخاذ الإجراءات القانونية اللازمة</li>
                        <li>يحق للمؤجر المطالبة بالتعويضات والأضرار الناتجة عن التأخير في السداد</li>
                        <li>في حالة عدم السداد خلال المدة المحددة، سيتم اتخاذ إجراءات فسخ العقد والإخلاء وفقاً للقانون</li>
                        <li>يمكن للمستأجر التواصل مع إدارة العقارات لمناقشة ترتيبات السداد قبل انتهاء المدة المحددة</li>
                        <li>هذا الإنذار يعتبر سارياً من تاريخ تسليمه أو إعلانه وفقاً للأصول القانونية</li>
                    </ul>
                    
                    <div style="text-align: center; margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 8px;">
                        <strong>📞 للاستفسار والتواصل:</strong><br>
                        الهاتف: {company_phone} | البريد الإلكتروني: {company_email}
                    </div>
                </div>
                
                <div class="signatures">
                    <div class="signature-box">
                        <h4 style="color: #2c3e50; margin-top: 0;">🏢 إدارة العقارات</h4>
                        <div style="height: 60px; border-bottom: 2px solid #2c3e50; margin: 15px 0;"></div>
                        <p><strong>التوقيع:</strong> ________________________</p>
                        <p><strong>الاسم:</strong> ________________________</p>
                        <p><strong>التاريخ:</strong> {self.notice_date.strftime('%d/%m/%Y')}</p>
                    </div>
                    
                    <div class="signature-box">
                        <h4 style="color: #2c3e50; margin-top: 0;">👤 استلام المستأجر</h4>
                        <div style="height: 60px; border-bottom: 2px solid #2c3e50; margin: 15px 0;"></div>
                        <p><strong>التوقيع:</strong> ________________________</p>
                        <p><strong>الاسم:</strong> {self.lease.tenant.name}</p>
                        <p><strong>التاريخ:</strong> ________________________</p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>
                        <strong>رقم المرجع:</strong> {self.id} | 
                        <strong>تاريخ الطباعة:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')} | 
                        هذا المستند مُنشأ إلكترونياً
                    </p>
                    <p style="margin-top: 10px; font-weight: bold; color: #2c3e50;">
                        🏢 {company_name} - نظام إدارة العقارات
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return content

    @property
    def overdue_month(self):
        """الحصول على الشهر الأول من التأخير (للتوافق مع Django Admin)"""
        try:
            first_detail = self.details.first()
            return first_detail.overdue_month if first_detail else None
        except:
            return None

    @property
    def overdue_year(self):
        """الحصول على السنة الأولى من التأخير (للتوافق مع Django Admin)"""
        try:
            first_detail = self.details.first()
            return first_detail.overdue_year if first_detail else None
        except:
            return None

    @property
    def overdue_amount(self):
        """الحصول على إجمالي مبلغ التأخير (للتوافق مع Django Admin)"""
        return self.total_overdue_amount

    @property
    def due_date(self):
        """الحصول على أقدم تاريخ استحقاق (للتوافق مع Django Admin)"""
        try:
            first_detail = self.details.order_by('due_date').first()
            return first_detail.due_date if first_detail else None
        except:
            return None

    @property
    def total_overdue_amount(self):
        """حساب المجموع الكلي للتأخير"""
        try:
            return self.details.aggregate(total=Sum('overdue_amount'))['total'] or Decimal('0.00')
        except:
            return Decimal('0.00')

    @property
    def overdue_months_count(self):
        """عدد شهور التأخير"""
        try:
            return self.details.count()
        except:
            return 0

    @classmethod
    def generate_automatic_notice(cls, lease):
        """إنشاء إنذار تلقائي لعقد متأخر في السداد"""
        from django.db.models import Q

        today = timezone.now().date()
        one_month_ago = today - relativedelta(months=1)

        # البحث عن شهور التأخير للعقد
        payment_summary = lease.get_payment_summary()
        overdue_months = []

        for month_data in payment_summary:
            # فحص الدفعات المتأخرة لأكثر من شهر
            if (month_data['status'] == 'overdue' and
                month_data['balance'] > 0 and
                month_data['days_overdue'] >= 30):  # متأخرة لأكثر من شهر

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
            # إنشاء إنذار جديد
            notice = cls.objects.create(
                lease=lease,
                notice_date=today,
                status='draft'
            )

            # إضافة تفاصيل كل شهر تأخير
            for overdue_month in overdue_months:
                try:
                    PaymentOverdueDetail.objects.create(
                        notice=notice,
                        overdue_month=overdue_month['month'],
                        overdue_year=overdue_month['year'],
                        overdue_amount=overdue_month['amount'],
                        due_date=overdue_month['due_date']
                    )
                except Exception as e:
                    print(f"خطأ في إنشاء تفاصيل الإنذار للشهر {overdue_month}: {e}")
                    continue

            # إنشاء محتوى الإنذار الرسمي
            notice.content = notice.generate_formal_payment_request()
            
            # حفظ الإنذار مرة أخرى لحساب due_date من التفاصيل
            notice.save()
            return notice

        return None

    @classmethod
    def generate_automatic_notices(cls):
        """إنشاء إنذارات تلقائية للعقود المتأخرة"""
        active_leases = Lease.objects.filter(status='active')
        notices_created = []

        for lease in active_leases:
            notice = cls.generate_automatic_notice(lease)
            if notice:
                notices_created.append(notice)

        return notices_created


class PaymentOverdueDetail(models.Model):
    """تفاصيل شهر تأخير محدد في الإنذار"""

    notice = models.ForeignKey(PaymentOverdueNotice, on_delete=models.CASCADE, related_name='details', verbose_name=_("الإنذار"))
    overdue_month = models.IntegerField(_("الشهر المتأخر"), choices=[(i, _(str(i))) for i in range(1, 13)])
    overdue_year = models.IntegerField(_("السنة المتأخرة"), default=timezone.now().year)
    overdue_amount = models.DecimalField(_("المبلغ المتأخر"), max_digits=10, decimal_places=2)
    due_date = models.DateField(_("تاريخ الاستحقاق الأصلي"))

    class Meta:
        verbose_name = _("تفصيل تأخير دفعة")
        verbose_name_plural = _("تفاصيل تأخير الدفعات")
        ordering = ['overdue_year', 'overdue_month']
        unique_together = ['notice', 'overdue_month', 'overdue_year']

    def __str__(self):
        return f"تأخير {self.overdue_month}/{self.overdue_year} - {self.overdue_amount}"

    def get_days_since_due(self):
        """حساب عدد الأيام منذ تاريخ الاستحقاق"""
        today = timezone.now().date()
        return (today - self.due_date).days

    def get_days_until_legal_deadline(self):
        """حساب عدد الأيام المتبقية حتى الموعد النهائي القانوني"""
        today = timezone.now().date()
        return (self.legal_deadline - today).days

    def get_month_name(self):
        """الحصول على اسم الشهر باللغة العربية"""
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        return month_names.get(self.overdue_month, str(self.overdue_month))


class LeaseRenewalReminder(models.Model):
    """نموذج تذكير تجديد عقد الإيجار - يصدر قبل 30 يوم من انتهاء العقد"""

    REMINDER_STATUS_CHOICES = [
        ('pending', _('في الانتظار')),
        ('sent', _('تم الإرسال')),
        ('acknowledged', _('تم الاستلام')),
        ('responded', _('تم الرد')),
        ('expired', _('منتهي الصلاحية')),
    ]

    RESPONSE_CHOICES = [
        ('no_response', _('لا رد')),
        ('interested', _('مهتم بالتجديد')),
        ('not_interested', _('غير مهتم بالتجديد')),
        ('negotiating', _('قيد التفاوض')),
    ]

    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='renewal_reminders', verbose_name=_("العقد"))
    reminder_date = models.DateField(_("تاريخ التذكير"), default=timezone.now)
    days_before_expiry = models.IntegerField(_("عدد الأيام قبل الانتهاء"), default=30)
    status = models.CharField(_("حالة التذكير"), max_length=20, choices=REMINDER_STATUS_CHOICES, default='pending')
    response = models.CharField(_("رد المستأجر"), max_length=20, choices=RESPONSE_CHOICES, default='no_response', blank=True, null=True)
    response_date = models.DateTimeField(_("تاريخ الرد"), blank=True, null=True)
    response_notes = models.TextField(_("ملاحظات الرد"), blank=True, null=True)

    # معلومات الإرسال
    sent_date = models.DateTimeField(_("تاريخ الإرسال"), blank=True, null=True)
    delivery_method = models.CharField(_("طريقة التسليم"), max_length=50, blank=True, null=True)
    recipient_signature = models.CharField(_("توقيع المستلم"), max_length=100, blank=True, null=True)

    # معلومات التجديد المقترحة
    proposed_renewal_date = models.DateField(_("تاريخ التجديد المقترح"), blank=True, null=True)
    proposed_monthly_rent = models.DecimalField(_("إيجار شهري مقترح"), max_digits=10, decimal_places=2, blank=True, null=True)
    proposed_terms = models.TextField(_("شروط التجديد المقترحة"), blank=True, null=True)

    notes = models.TextField(_("ملاحظات إضافية"), blank=True, null=True)

    class Meta:
        verbose_name = _("تذكير تجديد عقد")
        verbose_name_plural = _("تذكيرات تجديد العقود")
        ordering = ['-reminder_date']
        unique_together = ['lease', 'reminder_date']

    def __str__(self):
        return f"تذكير تجديد {self.lease.contract_number} - {self.reminder_date}"

    def save(self, *args, **kwargs):
        # حساب تاريخ التذكير (30 يوم قبل انتهاء العقد)
        if not self.reminder_date and self.days_before_expiry:
            self.reminder_date = self.lease.end_date - relativedelta(days=self.days_before_expiry)
        super().save(*args, **kwargs)

    def is_expired(self):
        """فحص ما إذا كان التذكير منتهي الصلاحية"""
        today = timezone.now().date()
        return today > self.lease.end_date

    def can_send(self):
        """فحص ما إذا كان يمكن إرسال التذكير"""
        today = timezone.now().date()
        return (self.status == 'pending' and
                today >= self.reminder_date and
                not self.is_expired())

    def mark_as_sent(self, delivery_method='email'):
        """تسجيل إرسال التذكير"""
        self.status = 'sent'
        self.sent_date = timezone.now()
        self.delivery_method = delivery_method
        self.save()

    def mark_response(self, response, notes=None):
        """تسجيل رد المستأجر"""
        self.status = 'responded'
        self.response = response
        self.response_date = timezone.now()
        if notes:
            self.response_notes = notes
        self.save()

    def get_reminder_content(self):
        """إنشاء محتوى رسالة التذكير باللغة العربية"""

        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }

        content = f"""
        <div style="text-align: right; font-family: 'Traditional Arabic', Arial, sans-serif; direction: rtl;">
            <h2 style="text-align: center; color: #2e7d32; font-weight: bold;">
                تذكير بتجديد عقد الإيجار
            </h2>

            <div style="margin: 20px 0; padding: 15px; border: 2px solid #2e7d32; background-color: #e8f5e8;">
                <h3 style="color: #2e7d32; margin-bottom: 10px;">هل عندك رغبة في تجديد عقد الإيجار؟</h3>
            </div>

            <div style="margin: 20px 0; line-height: 1.8;">
                <p><strong>إلى السيد/السيدة:</strong> {self.lease.tenant.name}</p>
                <p><strong>رقم العقد:</strong> {self.lease.contract_number}</p>
                <p><strong>الوحدة:</strong> {self.lease.unit.unit_number} - {self.lease.unit.building.name}</p>
                <p><strong>تاريخ التذكير:</strong> {self.reminder_date.strftime('%d/%m/%Y')}</p>
                <p><strong>تاريخ انتهاء العقد الحالي:</strong> {self.lease.end_date.strftime('%d/%m/%Y')}</p>
            </div>

            <div style="margin: 20px 0; padding: 15px; background-color: #fff3e0; border-right: 4px solid #ff9800;">
                <h4 style="color: #e65100; margin-bottom: 10px;">معلومات العقد الحالي:</h4>
                <p><strong>الإيجار الشهري:</strong> {self.lease.monthly_rent} ريال عماني</p>
                <p><strong>تاريخ البداية:</strong> {self.lease.start_date.strftime('%d/%m/%Y')}</p>
                <p><strong>تاريخ الانتهاء:</strong> {self.lease.end_date.strftime('%d/%m/%Y')}</p>
                <p><strong>مدة العقد:</strong> {self.lease.duration_display()}</p>
            </div>

            <div style="margin: 20px 0; padding: 15px; background-color: #e8f5e8; border-right: 4px solid #4caf50;">
                <h4 style="color: #2e7d32; margin-bottom: 10px;">الإجراء المطلوب:</h4>
                <p>نأمل منكم إبلاغنا برغبتكم في تجديد عقد الإيجار قبل تاريخ الانتهاء بـ 30 يوماً على الأقل</p>
                <p>في حالة الرغبة في التجديد، يرجى التواصل معنا لمناقشة شروط التجديد الجديدة</p>
                <p><strong>تاريخ انتهاء العقد:</strong> {self.lease.end_date.strftime('%d/%m/%Y')}</p>
            </div>

            <div style="margin: 20px 0; padding: 15px; background-color: #ffebee; border: 1px solid #f44336;">
                <h4 style="color: #c62828; margin-bottom: 10px;">ملاحظات هامة:</h4>
                <ul style="margin-right: 20px;">
                    <li>في حالة عدم الرغبة في التجديد، يرجى إخلاء الوحدة قبل تاريخ انتهاء العقد</li>
                    <li>عدم التواصل معنا قد يؤدي إلى إنهاء العقد تلقائياً في تاريخ الانتهاء</li>
                    <li>يمكنكم التواصل مع إدارة العقارات لمناقشة أي استفسارات أو مخاوف</li>
                    <li>نحن نقدر ثقتكم بنا ونتطلع لاستمرار التعاون معكم</li>
                </ul>
            </div>

            <div style="margin: 30px 0; text-align: center;">
                <p style="font-weight: bold;">إدارة العقارات</p>
                <p>هاتف: {Company.objects.first().contact_phone if Company.objects.exists() else '1234567890'}</p>
                <p>بريد إلكتروني: {Company.objects.first().contact_email if Company.objects.exists() else 'info@company.com'}</p>
            </div>

            <div style="margin-top: 40px; border-top: 1px solid #ccc; padding-top: 20px; font-size: 12px; color: #666;">
                <p><strong>للاستفسار:</strong> يرجى التواصل مع إدارة العقارات</p>
                <p><strong>رقم المرجع:</strong> {self.id if self.id else 'سيتم إنشاؤه'}</p>
                <p><strong>تاريخ الإنشاء:</strong> {timezone.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
        </div>
        """

        return content

    @classmethod
    def generate_automatic_reminders(cls):
        """إنشاء تذكيرات تلقائية للعقود التي ستنتهي خلال 30 يوم"""
        from django.db.models import Q

        today = timezone.now().date()
        thirty_days_from_now = today + relativedelta(days=30)

        # البحث عن العقود النشطة التي ستنتهي خلال 30 يوم
        expiring_leases = Lease.objects.filter(
            status__in=['active', 'expiring_soon'],
            end_date__lte=thirty_days_from_now,
            end_date__gte=today
        )

        reminders_created = []

        for lease in expiring_leases:
            # فحص عدم وجود تذكير سابق لنفس العقد
            existing_reminder = cls.objects.filter(
                lease=lease,
                reminder_date=lease.end_date - relativedelta(days=30)
            ).first()

            if not existing_reminder:
                reminder = cls.objects.create(
                    lease=lease,
                    reminder_date=lease.end_date - relativedelta(days=30),
                    status='pending'
                )
                reminders_created.append(reminder)

        return reminders_created


class NoticeTemplate(models.Model):
    """قوالب الإنذارات والرسائل القانونية"""
    
    TEMPLATE_TYPE_CHOICES = [
        ('overdue_payment', _('إنذار عدم سداد')),
        ('contract_termination', _('إنذار فسخ عقد')),
        ('eviction_notice', _('إنذار إخلاء')),
        ('lease_renewal', _('تذكير تجديد عقد')),
        ('maintenance_notice', _('إشعار صيانة')),
    ]
    
    name = models.CharField(_("اسم القالب"), max_length=200)
    template_type = models.CharField(_("نوع القالب"), max_length=30, choices=TEMPLATE_TYPE_CHOICES)
    subject = models.CharField(_("الموضوع"), max_length=300)
    content = models.TextField(_("المحتوى"), help_text=_("استخدم المتغيرات مثل {tenant_name}, {unit_number}, {amount}, {due_date}"))
    is_active = models.BooleanField(_("نشط"), default=True)
    legal_compliance_notes = models.TextField(_("ملاحظات الامتثال القانوني"), blank=True, null=True)
    created_date = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_date = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("قالب إنذار")
        verbose_name_plural = _("قوالب الإنذارات")
        ordering = ['template_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def render_content(self, context):
        """تطبيق المتغيرات على محتوى القالب"""
        content = self.content
        for key, value in context.items():
            content = content.replace(f"{{{key}}}", str(value))
        return content
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from dashboard.models import NoticeTemplate
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'إنشاء قوالب افتراضية لرسائل تجديد العقود'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(_('بدء إنشاء قوالب رسائل التجديد الافتراضية...'))
        )

        # قالب رسالة تذكير التجديد
        renewal_template, created = NoticeTemplate.objects.get_or_create(
            name='تذكير تجديد العقد الافتراضي',
            template_type='lease_renewal',
            defaults={
                'subject': 'تذكير بتجديد عقد الإيجار - هل عندك رغبة في التجديد؟',
                'content': '''<div style="text-align: right; font-family: 'Traditional Arabic', Arial, sans-serif; direction: rtl;">
    <h2 style="text-align: center; color: #2e7d32; font-weight: bold;">تذكير بتجديد عقد الإيجار</h2>

    <div style="margin: 20px 0; padding: 15px; border: 2px solid #2e7d32; background-color: #e8f5e8;">
        <h3 style="color: #2e7d32; margin-bottom: 10px;">هل عندك رغبة في تجديد عقد الإيجار؟</h3>
    </div>

    <div style="margin: 20px 0; line-height: 1.8;">
        <p><strong>السيد/السيدة:</strong> {tenant_name}</p>
        <p><strong>رقم العقد:</strong> {contract_number}</p>
        <p><strong>الوحدة:</strong> {unit_number} - {building_name}</p>
        <p><strong>تاريخ انتهاء العقد الحالي:</strong> {expiry_date}</p>
        <p><strong>تاريخ إرسال التذكير:</strong> {notice_date}</p>
    </div>

    <div style="margin: 20px 0; padding: 15px; background-color: #fff3e0; border-right: 4px solid #ff9800;">
        <h4 style="color: #e65100; margin-bottom: 10px;">معلومات مهمة:</h4>
        <p>سيتم انتهاء عقد إيجاركم الحالي في تاريخ <strong>{expiry_date}</strong></p>
        <p>نأمل في معرفة رغبتكم في تجديد العقد قبل <strong>30 يوماً</strong> من تاريخ الانتهاء</p>
        <p><strong>المبلغ الحالي للإيجار الشهري:</strong> {monthly_rent} ريال عماني</p>
    </div>

    <div style="margin: 20px 0; padding: 15px; background-color: #e3f2fd; border-right: 4px solid #2196f3;">
        <h4 style="color: #1976d2; margin-bottom: 10px;">خيارات التجديد:</h4>
        <ul style="margin-right: 20px;">
            <li>تجديد العقد بنفس الشروط والمبلغ الحالي</li>
            <li>تجديد العقد مع تعديل المبلغ (زيادة أو نقصان)</li>
            <li>التفاوض على شروط جديدة للتجديد</li>
            <li>عدم الرغبة في التجديد (إخلاء الوحدة قبل تاريخ الانتهاء)</li>
        </ul>
    </div>

    <div style="margin: 20px 0; padding: 15px; background-color: #fce4ec; border-right: 4px solid #e91e63;">
        <h4 style="color: #c2185b; margin-bottom: 10px;">ملاحظات هامة:</h4>
        <ul style="margin-right: 20px;">
            <li>يرجى الرد خلال <strong>15 يوماً</strong> من تاريخ هذا التذكير</li>
            <li>في حالة عدم الرد، سنفترض عدم الرغبة في التجديد</li>
            <li>سيتم إرسال تذكير إضافي قبل أسبوعين من تاريخ الانتهاء</li>
            <li>يمكنكم التواصل مع إدارة العقارات لمناقشة خيارات التجديد</li>
        </ul>
    </div>

    <div style="margin: 30px 0; text-align: center;">
        <p style="font-weight: bold;">إدارة العقارات</p>
        <p>الهاتف: {company_phone}</p>
        <p>البريد الإلكتروني: {company_email}</p>
    </div>

    <div style="margin-top: 40px; border-top: 1px solid #ccc; padding-top: 20px; font-size: 12px; color: #666;">
        <p><strong>رقم المرجع:</strong> {notice_id}</p>
        <p><strong>تاريخ الإنشاء:</strong> {created_at}</p>
    </div>
</div>''',
                'legal_compliance_notes': 'قالب متوافق مع القوانين العمانية لإشعارات تجديد العقود'
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(_('تم إنشاء قالب تذكير التجديد الافتراضي'))
            )
        else:
            self.stdout.write(_('قالب تذكير التجديد موجود بالفعل'))

        # قالب تذكير نهائي (أسبوعين قبل الانتهاء)
        final_reminder_template, created = NoticeTemplate.objects.get_or_create(
            name='تذكير نهائي بتجديد العقد',
            template_type='lease_renewal',
            defaults={
                'subject': 'تذكير نهائي - انتهاء عقد الإيجار خلال أسبوعين',
                'content': '''<div style="text-align: right; font-family: 'Traditional Arabic', Arial, sans-serif; direction: rtl;">
    <h2 style="text-align: center; color: #f57c00; font-weight: bold;">تذكير نهائي بتجديد عقد الإيجار</h2>

    <div style="margin: 20px 0; padding: 15px; border: 2px solid #f57c00; background-color: #fff3e0;">
        <h3 style="color: #f57c00; margin-bottom: 10px;">تذكير هام: انتهاء عقد الإيجار خلال أسبوعين فقط</h3>
    </div>

    <div style="margin: 20px 0; line-height: 1.8;">
        <p><strong>السيد/السيدة:</strong> {tenant_name}</p>
        <p><strong>رقم العقد:</strong> {contract_number}</p>
        <p><strong>الوحدة:</strong> {unit_number} - {building_name}</p>
        <p><strong>تاريخ انتهاء العقد:</strong> {expiry_date}</p>
        <p><strong>الأيام المتبقية:</strong> {days_until_expiry} يوم</p>
    </div>

    <div style="margin: 20px 0; padding: 15px; background-color: #ffebee; border-right: 4px solid #d32f2f;">
        <h4 style="color: #d32f2f; margin-bottom: 10px;">تحذير هام:</h4>
        <p>سيتم انتهاء عقد إيجاركم خلال <strong>{days_until_expiry} يوم فقط</strong></p>
        <p>هذا هو التذكير النهائي قبل انتهاء العقد</p>
        <p>يرجى اتخاذ القرار المناسب في أسرع وقت ممكن</p>
    </div>

    <div style="margin: 20px 0; padding: 15px; background-color: #e8f5e8; border-right: 4px solid #2e7d32;">
        <h4 style="color: #2e7d32; margin-bottom: 10px;">خيارات متاحة:</h4>
        <ul style="margin-right: 20px;">
            <li><strong>تجديد العقد:</strong> تواصل معنا لمناقشة الشروط</li>
            <li><strong>عدم التجديد:</strong> قم بإخلاء الوحدة قبل تاريخ الانتهاء</li>
            <li><strong>التمديد المؤقت:</strong> يمكن مناقشة تمديد قصير الأمد</li>
        </ul>
    </div>

    <div style="margin: 20px 0; padding: 15px; background-color: #fff3e0; border: 2px solid #ff9800;">
        <h4 style="color: #e65100; margin-bottom: 10px;">إجراءات مطلوبة:</h4>
        <ul style="margin-right: 20px;">
            <li>الرد خلال 48 ساعة من استلام هذا التذكير</li>
            <li>في حالة عدم الرد، سنبدأ إجراءات إخلاء الوحدة</li>
            <li>سيتم إجراء معاينة للوحدة قبل أسبوع من تاريخ الانتهاء</li>
        </ul>
    </div>

    <div style="margin: 30px 0; text-align: center;">
        <p style="font-weight: bold;">إدارة العقارات</p>
        <p>الهاتف: {company_phone}</p>
        <p>البريد الإلكتروني: {company_email}</p>
    </div>

    <div style="margin-top: 40px; border-top: 1px solid #ccc; padding-top: 20px; font-size: 12px; color: #666;">
        <p><strong>رقم المرجع:</strong> {notice_id}</p>
        <p><strong>تاريخ الإنشاء:</strong> {created_at}</p>
    </div>
</div>''',
                'legal_compliance_notes': 'قالب تذكير نهائي متوافق مع القوانين العمانية'
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(_('تم إنشاء قالب التذكير النهائي'))
            )
        else:
            self.stdout.write(_('قالب التذكير النهائي موجود بالفعل'))

        self.stdout.write(
            self.style.SUCCESS(_('اكتمل إنشاء جميع قوالب رسائل التجديد'))
        )

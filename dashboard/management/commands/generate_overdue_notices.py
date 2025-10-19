from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import PaymentOverdueNotice, Lease, Payment
from dateutil.relativedelta import relativedelta
import datetime


class Command(BaseCommand):
    help = 'إنشاء إنذارات تلقائية للإيجارات المتأخرة لمدة شهر كامل'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='تشغيل تجريبي - عرض النتائج دون حفظ الإنذارات',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='إجبار إنشاء الإنذارات حتى لو كانت موجودة',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('بدء عملية إنشاء إنذارات عدم السداد التلقائية...')
        )

        dry_run = options['dry_run']
        force = options['force']
        
        today = timezone.now().date()
        one_month_ago = today - relativedelta(months=1)
        
        self.stdout.write(f'التاريخ الحالي: {today}')
        self.stdout.write(f'البحث عن الدفعات المتأخرة منذ: {one_month_ago}')

        # البحث عن العقود النشطة
        active_leases = Lease.objects.filter(status='active')
        self.stdout.write(f'عدد العقود النشطة: {active_leases.count()}')

        notices_created = 0
        notices_skipped = 0
        errors = 0

        for lease in active_leases:
            try:
                # الحصول على ملخص الدفعات للعقد
                payment_summary = lease.get_payment_summary()
                
                for month_data in payment_summary:
                    # فحص الدفعات المتأخرة
                    if month_data['balance'] > 0:
                        # حساب تاريخ الاستحقاق للشهر
                        due_date = datetime.date(month_data['year'], month_data['month'], 1)
                        
                        # فحص إذا كان متأخر لأكثر من شهر
                        if due_date <= one_month_ago:
                            # فحص وجود إنذار سابق
                            existing_notice = PaymentOverdueNotice.objects.filter(
                                lease=lease,
                                overdue_month=month_data['month'],
                                overdue_year=month_data['year']
                            ).first()
                            
                            if existing_notice and not force:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'تم تخطي إنذار موجود: {lease.contract_number} - '
                                        f'{month_data["month"]}/{month_data["year"]}'
                                    )
                                )
                                notices_skipped += 1
                                continue
                            
                            if not dry_run:
                                if existing_notice and force:
                                    # تحديث الإنذار الموجود
                                    existing_notice.overdue_amount = month_data['balance']
                                    existing_notice.notice_date = today
                                    existing_notice.status = 'draft'
                                    existing_notice.save()
                                    action = 'تم تحديث'
                                else:
                                    # إنشاء إنذار جديد
                                    PaymentOverdueNotice.objects.create(
                                        lease=lease,
                                        overdue_month=month_data['month'],
                                        overdue_year=month_data['year'],
                                        overdue_amount=month_data['balance'],
                                        due_date=due_date,
                                        status='draft'
                                    )
                                    action = 'تم إنشاء'
                                
                                notices_created += 1
                            else:
                                action = 'سيتم إنشاء'
                                notices_created += 1
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'{action} إنذار: {lease.contract_number} - '
                                    f'المستأجر: {lease.tenant.name} - '
                                    f'الوحدة: {lease.unit.unit_number} - '
                                    f'الشهر: {month_data["month"]}/{month_data["year"]} - '
                                    f'المبلغ: {month_data["balance"]} ر.ع'
                                )
                            )
                            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'خطأ في معالجة العقد {lease.contract_number}: {str(e)}'
                    )
                )
                errors += 1

        # عرض النتائج النهائية
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('تمت عملية الإنشاء بنجاح!'))
        self.stdout.write(f'عدد الإنذارات المنشأة/المحدثة: {notices_created}')
        self.stdout.write(f'عدد الإنذارات المتخطاة: {notices_skipped}')
        self.stdout.write(f'عدد الأخطاء: {errors}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('هذا كان تشغيل تجريبي - لم يتم حفظ أي إنذارات فعلياً')
            )
            self.stdout.write('لتنفيذ العملية فعلياً، قم بتشغيل الأمر بدون --dry-run')

        # إنشاء إحصائيات إضافية
        if not dry_run:
            total_notices = PaymentOverdueNotice.objects.count()
            draft_notices = PaymentOverdueNotice.objects.filter(status='draft').count()
            sent_notices = PaymentOverdueNotice.objects.filter(status='sent').count()
            
            self.stdout.write('\n' + 'إحصائيات الإنذارات:')
            self.stdout.write(f'إجمالي الإنذارات في النظام: {total_notices}')
            self.stdout.write(f'الإنذارات في المسودة: {draft_notices}')
            self.stdout.write(f'الإنذارات المرسلة: {sent_notices}')

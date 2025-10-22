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

        # البحث عن العقود النشطة والمنتهية (للعقود المنتهية التي لديها دفعات متأخرة)
        active_leases = Lease.objects.filter(status__in=['active', 'expired', 'expiring_soon'])
        self.stdout.write(f'عدد العقود (النشطة والمنتهية): {active_leases.count()}')

        notices_created = 0
        notices_skipped = 0
        errors = 0

        for lease in active_leases:
            try:
                if not dry_run:
                    # استخدام المنطق الجديد لإنشاء الإنذارات
                    notice = PaymentOverdueNotice.generate_automatic_notice(lease)
                    if notice:
                        notices_created += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'تم إنشاء إنذار: {lease.contract_number} - '
                                f'المستأجر: {lease.tenant.name} - '
                                f'الوحدة: {lease.unit.unit_number} - '
                                f'عدد الشهور المتأخرة: {notice.overdue_months_count} - '
                                f'إجمالي المبلغ: {notice.total_overdue_amount} ر.ع'
                            )
                        )
                    else:
                        # فحص إذا كان هناك دفعات متأخرة ولكن لديها إنذارات موجودة
                        payment_summary = lease.get_payment_summary()
                        has_overdue = any(
                            month_data['status'] == 'overdue' and 
                            month_data['balance'] > 0 and 
                            month_data['days_overdue'] >= 30
                            for month_data in payment_summary
                        )
                        
                        if has_overdue:
                            notices_skipped += 1
                            self.stdout.write(
                                self.style.WARNING(
                                    f'تم تخطي العقد (إنذارات موجودة): {lease.contract_number} - {lease.tenant.name}'
                                )
                            )
                else:
                    # في حالة التشغيل التجريبي
                    payment_summary = lease.get_payment_summary()
                    overdue_months = []
                    
                    for month_data in payment_summary:
                        if (month_data['status'] == 'overdue' and
                            month_data['balance'] > 0 and
                            month_data['days_overdue'] >= 30):
                            
                            # فحص عدم وجود إنذار سابق
                            from dashboard.models import PaymentOverdueDetail
                            existing_detail = PaymentOverdueDetail.objects.filter(
                                notice__lease=lease,
                                overdue_month=month_data['month'],
                                overdue_year=month_data['year']
                            ).exists()
                            
                            if not existing_detail:
                                overdue_months.append(month_data)
                    
                    if overdue_months:
                        notices_created += 1
                        total_amount = sum(month['balance'] for month in overdue_months)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'سيتم إنشاء إنذار: {lease.contract_number} - '
                                f'المستأجر: {lease.tenant.name} - '
                                f'الوحدة: {lease.unit.unit_number} - '
                                f'عدد الشهور المتأخرة: {len(overdue_months)} - '
                                f'إجمالي المبلغ: {total_amount} ر.ع'
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

from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import Lease, Payment, PaymentOverdueNotice
from decimal import Decimal
import datetime


class Command(BaseCommand):
    help = 'اختبار نظام تحديث الإنذارات عند الدفع'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lease-id',
            type=int,
            help='معرف العقد للاختبار'
        )
        parser.add_argument(
            '--amount',
            type=float,
            default=100.0,
            help='مبلغ الدفعة للاختبار'
        )
        parser.add_argument(
            '--month',
            type=int,
            default=6,
            help='الشهر المراد دفعه'
        )
        parser.add_argument(
            '--year',
            type=int,
            default=2025,
            help='السنة المراد دفعها'
        )

    def handle(self, *args, **options):
        lease_id = options.get('lease_id')
        amount = Decimal(str(options.get('amount')))
        month = options.get('month')
        year = options.get('year')

        if not lease_id:
            # البحث عن عقد لديه إنذارات
            lease = Lease.objects.filter(
                overdue_notices__isnull=False,
                status='active'
            ).first()
            
            if not lease:
                self.stdout.write(
                    self.style.ERROR('لا توجد عقود لديها إنذارات للاختبار')
                )
                return
        else:
            try:
                lease = Lease.objects.get(id=lease_id)
            except Lease.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'العقد رقم {lease_id} غير موجود')
                )
                return

        self.stdout.write(f'اختبار النظام للعقد: {lease.contract_number}')
        self.stdout.write(f'المستأجر: {lease.tenant.name}')
        
        # عرض الإنذارات الموجودة قبل الدفع
        notices_before = lease.overdue_notices.filter(
            status__in=['draft', 'sent', 'acknowledged']
        )
        
        self.stdout.write(f'\nالإنذارات قبل الدفع: {notices_before.count()}')
        for notice in notices_before:
            self.stdout.write(f'  - إنذار #{notice.id}: {notice.details.count()} شهر، إجمالي: {notice.total_overdue_amount} ر.ع')
            for detail in notice.details.all():
                self.stdout.write(f'    * {detail.overdue_month}/{detail.overdue_year}: {detail.overdue_amount} ر.ع')

        # إنشاء دفعة اختبارية
        self.stdout.write(f'\n💰 إنشاء دفعة: {amount} ر.ع لشهر {month}/{year}')
        
        payment = Payment.objects.create(
            lease=lease,
            amount=amount,
            payment_date=timezone.now().date(),
            payment_for_month=month,
            payment_for_year=year,
            payment_method='cash',
            notes=f'دفعة اختبارية من أمر الإدارة'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ تم إنشاء الدفعة #{payment.id}')
        )

        # عرض الإنذارات بعد الدفع
        notices_after = lease.overdue_notices.filter(
            status__in=['draft', 'sent', 'acknowledged', 'resolved']
        )
        
        self.stdout.write(f'\nالإنذارات بعد الدفع: {notices_after.count()}')
        for notice in notices_after:
            self.stdout.write(f'  - إنذار #{notice.id}: {notice.get_status_display()}')
            self.stdout.write(f'    الشهور المتبقية: {notice.details.count()}')
            self.stdout.write(f'    إجمالي متبقي: {notice.total_overdue_amount} ر.ع')
            
            if notice.details.exists():
                for detail in notice.details.all():
                    self.stdout.write(f'    * {detail.overdue_month}/{detail.overdue_year}: {detail.overdue_amount} ر.ع')
            else:
                self.stdout.write('    🎉 تم حل جميع الشهور المتأخرة!')
            
            # عرض آخر ملاحظة
            if notice.notes:
                last_note = notice.notes.split('\n')[-1]
                self.stdout.write(f'    آخر ملاحظة: {last_note}')

        self.stdout.write(
            self.style.SUCCESS('\n✅ تم اختبار النظام بنجاح!')
        )

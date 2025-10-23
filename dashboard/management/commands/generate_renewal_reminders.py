from django.core.management.base import BaseCommand
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from dashboard.models import Lease, LeaseRenewalReminder
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'إنشاء تذكيرات تلقائية لتجديد العقود قبل 30 يوم من الانتهاء'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='عرض التذكيرات التي سيتم إنشاؤها دون إنشائها فعلياً',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='إنشاء التذكيرات حتى لو كانت موجودة مسبقاً',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        today = timezone.now().date()
        thirty_days_from_now = today + relativedelta(days=30)

        self.stdout.write(
            self.style.SUCCESS(
                f'البحث عن العقود التي ستنتهي خلال 30 يوم (من {today} إلى {thirty_days_from_now})'
            )
        )

        # البحث عن العقود النشطة التي ستنتهي خلال 30 يوم
        expiring_leases = Lease.objects.filter(
            status__in=['active', 'expiring_soon'],
            end_date__lte=thirty_days_from_now,
            end_date__gte=today
        )

        total_leases = expiring_leases.count()
        self.stdout.write(
            self.style.SUCCESS(f'تم العثور على {total_leases} عقد ستنتهي خلال 30 يوم')
        )

        reminders_created = 0

        for lease in expiring_leases:
            # حساب تاريخ التذكير (30 يوم قبل الانتهاء)
            reminder_date = lease.end_date - relativedelta(days=30)

            # فحص عدم وجود تذكير سابق لنفس العقد إلا إذا كان force مفعل
            existing_reminder = LeaseRenewalReminder.objects.filter(
                lease=lease,
                reminder_date=reminder_date
            ).first()

            if existing_reminder and not force:
                self.stdout.write(
                    self.style.WARNING(
                        f'تذكير موجود مسبقاً للعقد {lease.contract_number}'
                    )
                )
                continue

            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'سيتم إنشاء تذكير للعقد {lease.contract_number} بتاريخ {reminder_date}'
                    )
                )
                reminders_created += 1
                continue

            # إنشاء التذكير الجديد
            try:
                if existing_reminder and force:
                    # تحديث التذكير الموجود
                    existing_reminder.status = 'pending'
                    existing_reminder.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'تم تحديث التذكير الموجود للعقد {lease.contract_number}'
                        )
                    )
                else:
                    # إنشاء تذكير جديد
                    reminder = LeaseRenewalReminder.objects.create(
                        lease=lease,
                        reminder_date=reminder_date,
                        status='pending'
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'تم إنشاء تذكير جديد للعقد {lease.contract_number}'
                        )
                    )
                reminders_created += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'خطأ في إنشاء التذكير للعقد {lease.contract_number}: {str(e)}'
                    )
                )
                logger.exception(f"Failed to create renewal reminder for lease {lease.id}")

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'معاينة انتهت: سيتم إنشاء {reminders_created} تذكير'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'تم إنشاء/تحديث {reminders_created} تذكير بنجاح'
                )
            )

        # إحصائيات إضافية
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('إحصائيات التذكيرات:'))

        # التذكيرات حسب الحالة
        status_stats = {}
        for status, display in LeaseRenewalReminder.REMINDER_STATUS_CHOICES:
            count = LeaseRenewalReminder.objects.filter(status=status).count()
            if count > 0:
                status_stats[display] = count

        for status_display, count in status_stats.items():
            self.stdout.write(f'  {status_display}: {count}')

        # التذكيرات التي ستصدر قريباً
        upcoming_reminders = LeaseRenewalReminder.objects.filter(
            status='pending',
            reminder_date__lte=today + relativedelta(days=7)
        ).count()

        if upcoming_reminders > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'تذكيرات ستصدر خلال الأسبوع القادم: {upcoming_reminders}'
                )
            )

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.conf import settings
from dashboard.models import LeaseRenewalNotice, Lease
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'إرسال رسائل تذكير تجديد العقود التلقائية'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='تشغيل تجريبي بدون إرسال فعلي',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='إرسال الرسائل حتى لو كانت خارج الوقت المحدد',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(
            self.style.SUCCESS(
                _('بدء عملية إرسال رسائل تذكير تجديد العقود...')
            )
        )

        # إنشاء الرسائل الجديدة
        notices_created = LeaseRenewalNotice.generate_automatic_notices()

        if notices_created:
            self.stdout.write(
                self.style.SUCCESS(
                    _('تم إنشاء {} رسالة تجديد جديدة').format(len(notices_created))
                )
            )
        else:
            self.stdout.write(
                _('لا توجد عقود جديدة تحتاج رسائل تجديد')
            )

        # الحصول على جميع الرسائل الجاهزة للإرسال
        if force:
            ready_notices = LeaseRenewalNotice.objects.filter(
                status__in=['draft', 'sent']
            ).order_by('reminder_date')
        else:
            ready_notices = LeaseRenewalNotice.objects.filter(
                status='draft',
                reminder_date__lte=timezone.now().date()
            ).order_by('reminder_date')

        if not ready_notices.exists():
            self.stdout.write(
                _('لا توجد رسائل جاهزة للإرسال')
            )
            return

        self.stdout.write(
            _('العثور على {} رسالة جاهزة للإرسال').format(ready_notices.count())
        )

        sent_count = 0
        failed_count = 0

        for notice in ready_notices:
            try:
                if dry_run:
                    self.stdout.write(
                        _('تجريبي: سيتم إرسال رسالة تجديد لـ {} ({})').format(
                            notice.lease.tenant.name,
                            notice.lease.contract_number
                        )
                    )
                    sent_count += 1
                else:
                    # إرسال البريد الإلكتروني
                    subject = f"تذكير بتجديد عقد الإيجار - {notice.lease.contract_number}"

                    # استخدام محتوى الرسالة المُعد مسبقاً
                    html_content = notice.get_notice_content()

                    # إرسال البريد الإلكتروني
                    send_mail(
                        subject=subject,
                        message='',  # نص فارغ لأننا نستخدم HTML
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[notice.lease.tenant.email] if notice.lease.tenant.email else [],
                        html_message=html_content,
                        fail_silently=False,
                    )

                    # تحديث حالة الرسالة
                    notice.mark_as_sent('email')

                    self.stdout.write(
                        self.style.SUCCESS(
                            _('تم إرسال رسالة تجديد لـ {} ({}) عبر البريد الإلكتروني').format(
                                notice.lease.tenant.name,
                                notice.lease.contract_number
                            )
                        )
                    )
                    sent_count += 1

            except Exception as e:
                logger.exception(f"فشل في إرسال رسالة التجديد {notice.id}: {e}")
                self.stdout.write(
                    self.style.ERROR(
                        _('فشل في إرسال رسالة تجديد لـ {}: {}').format(
                            notice.lease.contract_number, str(e)
                        )
                    )
                )
                failed_count += 1

        # تقرير النتائج
        self.stdout.write(
            self.style.SUCCESS(
                _('اكتملت العملية: {} نجح، {} فشل').format(sent_count, failed_count)
            )
        )

        if not dry_run and sent_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    _('تم إرسال جميع رسائل التجديد بنجاح')
                )
            )

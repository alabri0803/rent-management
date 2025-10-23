from django.core.management.base import BaseCommand
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.template.loader import get_template
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
from dashboard.models import Lease, Notification, Document, Company
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'فحص العقود المنتهية وإنشاء الإشعارات والإنذارات التلقائية'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='عرض الإشعارات التي سيتم إنشاؤها دون إنشائها فعلياً',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = timezone.now().date()
        
        self.stdout.write(self.style.SUCCESS(f'🔍 فحص العقود المنتهية بتاريخ {today}'))
        self.stdout.write('='*80)
        
        # 1. البحث عن العقود المنتهية (expired)
        expired_leases = Lease.objects.filter(status='expired')
        total_expired = expired_leases.count()
        
        self.stdout.write(self.style.WARNING(f'\n📊 إجمالي العقود المنتهية: {total_expired}'))
        
        renewal_reminders_count = 0
        renewal_warnings_count = 0
        pdfs_created = 0
        
        for lease in expired_leases:
            # حساب عدد الأشهر منذ الانتهاء
            months_overdue = relativedelta(today, lease.end_date).years * 12 + relativedelta(today, lease.end_date).months
            days_overdue = (today - lease.end_date).days
            
            self.stdout.write(f'\n📝 العقد: {lease.contract_number} | انتهى منذ: {months_overdue} شهر و {days_overdue % 30} يوم')
            
            # أ) رسالة "هل لديك رغبة في تجديد العقد" - للعقود الجديدة الانتهاء (0-3 أشهر)
            if 0 <= months_overdue < 3:
                renewal_message = f'عقد الإيجار رقم {lease.contract_number} انتهى في {lease.end_date.strftime("%d/%m/%Y")}. هل ترغب في تجديده؟'
                
                if lease.tenant.user:
                    exists = Notification.objects.filter(
                        user=lease.tenant.user,
                        message=renewal_message
                    ).exists()
                    
                    if not exists:
                        if dry_run:
                            self.stdout.write(self.style.SUCCESS(f'   ✉️  سيتم إرسال: رسالة تجديد للمستأجر'))
                        else:
                            Notification.objects.create(
                                user=lease.tenant.user,
                                message=renewal_message,
                                related_object=lease
                            )
                            self.stdout.write(self.style.SUCCESS(f'   ✅ تم إرسال: رسالة تجديد للمستأجر'))
                        renewal_reminders_count += 1
                    else:
                        self.stdout.write(f'   ℹ️  موجودة: رسالة تجديد للمستأجر')
                else:
                    self.stdout.write(self.style.WARNING(f'   ⚠️  المستأجر ليس له حساب مستخدم'))
            
            # ب) إنذار تأخير التجديد - بعد 3 أشهر
            elif months_overdue >= 3:
                warning_message = f'إنذار: تأخير في تجديد عقد الإيجار رقم {lease.contract_number} لأكثر من {months_overdue} شهر'
                
                # إنشاء إشعار للمستأجر
                if lease.tenant.user:
                    exists = Notification.objects.filter(
                        user=lease.tenant.user,
                        message=warning_message
                    ).exists()
                    
                    if not exists:
                        if dry_run:
                            self.stdout.write(self.style.WARNING(f'   ⚠️  سيتم إرسال: إنذار تأخير للمستأجر'))
                        else:
                            Notification.objects.create(
                                user=lease.tenant.user,
                                message=warning_message,
                                related_object=lease
                            )
                            self.stdout.write(self.style.WARNING(f'   ✅ تم إرسال: إنذار تأخير للمستأجر'))
                        renewal_warnings_count += 1
                    else:
                        self.stdout.write(f'   ℹ️  موجود: إنذار للمستأجر')
                
                # إنشاء إشعار للموظفين
                staff_message = f'تنبيه: عقد {lease.contract_number} متأخر في التجديد لمدة {months_overdue} شهر'
                staff_users = User.objects.filter(is_staff=True)
                
                for user in staff_users:
                    exists = Notification.objects.filter(
                        user=user,
                        message=staff_message
                    ).exists()
                    
                    if not exists:
                        if not dry_run:
                            Notification.objects.create(
                                user=user,
                                message=staff_message,
                                related_object=lease
                            )
                
                # إنشاء مستند PDF للإنذار
                doc_title = f"إنذار تأخير تجديد عقد - {lease.contract_number}"
                doc_exists = Document.objects.filter(lease=lease, title=doc_title).exists()
                
                if not doc_exists:
                    if dry_run:
                        self.stdout.write(self.style.WARNING(f'   📄 سيتم إنشاء: PDF إنذار تأخير التجديد'))
                        pdfs_created += 1
                    else:
                        try:
                            template = get_template('dashboard/reports/lease_overdue_notice.html')
                            context = {
                                'lease': lease,
                                'today': today,
                                'company': Company.objects.first(),
                                'type': 'renewal',
                                'months': months_overdue,
                            }
                            html = template.render(context)
                            
                            try:
                                from weasyprint import HTML
                                pdf_bytes = HTML(string=html, base_url=settings.BASE_DIR).write_pdf()
                            except Exception:
                                from xhtml2pdf import pisa
                                result = BytesIO()
                                pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
                                pdf_bytes = result.getvalue()
                            
                            filename = f"overdue_renewal_{lease.contract_number}.pdf"
                            doc = Document(lease=lease, title=doc_title)
                            doc.file.save(filename, ContentFile(pdf_bytes))
                            doc.save()
                            
                            self.stdout.write(self.style.SUCCESS(f'   ✅ تم إنشاء: PDF إنذار تأخير التجديد'))
                            pdfs_created += 1
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'   ❌ فشل إنشاء PDF: {str(e)}'))
                else:
                    self.stdout.write(f'   ℹ️  موجود: PDF إنذار تأخير التجديد')
        
        # ملخص النتائج
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('\n📈 ملخص العملية:'))
        self.stdout.write(f'  • إجمالي العقود المنتهية: {total_expired}')
        self.stdout.write(f'  • رسائل التجديد الجديدة: {renewal_reminders_count}')
        self.stdout.write(f'  • إنذارات التأخير الجديدة: {renewal_warnings_count}')
        self.stdout.write(f'  • ملفات PDF المُنشأة: {pdfs_created}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  هذا كان اختبار فقط (--dry-run). لم يتم إنشاء أي شيء فعلياً.'))
            self.stdout.write(self.style.SUCCESS('لتنفيذ العملية فعلياً، شغّل الأمر بدون --dry-run:'))
            self.stdout.write('  python manage.py check_expired_leases')
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ تمت العملية بنجاح!'))

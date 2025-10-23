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
    help = 'Send automatic notifications for late payments and lease renewals'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        created_count = 0
        
        # Create notifications for late payments (3 months) and attach PDF notice
        for lease in Lease.objects.filter(status__in=['active', 'expiring_soon']):
            summary = lease.get_payment_summary()
            unpaid_months = [m for m in summary if m['status'] == 'due' and m['balance'] > 0]
            if len(unpaid_months) >= 3:
                user = lease.tenant.user if hasattr(lease.tenant, 'user') else User.objects.filter(is_staff=True).first()
                if user:
                    obj, created = Notification.objects.get_or_create(
                        user=user,
                        message=f'إنذار: تأخر في سداد الإيجار لعقد {lease.contract_number} لمدة {len(unpaid_months)} شهر',
                        defaults={'read': False}
                    )
                    if created:
                        created_count += 1
                # Generate and attach payment overdue notice PDF
                try:
                    template = get_template('dashboard/reports/lease_overdue_notice.html')
                    context = {
                        'lease': lease,
                        'today': today,
                        'company': Company.objects.first(),
                        'type': 'payment',
                        'months': len(unpaid_months),
                    }
                    html = template.render(context)
                    try:
                        from weasyprint import HTML
                        pdf_bytes = HTML(string=html, base_url=settings.BASE_DIR).write_pdf()
                    except Exception:
                        from xhtml2pdf import pisa
                        result = BytesIO(); pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
                        pdf_bytes = result.getvalue()
                    filename = f"overdue_rent_{lease.contract_number}.pdf"
                    doc = Document(lease=lease, title=f"إنذار تأخر سداد الإيجار - {lease.contract_number}")
                    doc.file.save(filename, ContentFile(pdf_bytes)); doc.save()
                except Exception:
                    pass

        # Create notifications for lease renewal delay (expired >= 3 months) and attach PDF notice
        for lease in Lease.objects.filter(status='expired'):
            # احسب عدد الأشهر منذ تاريخ الانتهاء
            months_overdue = relativedelta(today, lease.end_date).years * 12 + relativedelta(today, lease.end_date).months
            if months_overdue >= 3:
                user = lease.tenant.user if hasattr(lease.tenant, 'user') else User.objects.filter(is_staff=True).first()
                if user:
                    obj, created = Notification.objects.get_or_create(
                        user=user,
                        message=f'إنذار: تأخير في تجديد عقد الإيجار رقم {lease.contract_number} لأكثر من {months_overdue} شهر',
                        defaults={'read': False}
                    )
                    if created:
                        created_count += 1
                # Generate and attach renewal overdue notice PDF
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
                        result = BytesIO(); pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
                        pdf_bytes = result.getvalue()
                    filename = f"overdue_renewal_{lease.contract_number}.pdf"
                    doc = Document(lease=lease, title=f"إنذار تأخير تجديد عقد - {lease.contract_number}")
                    doc.file.save(filename, ContentFile(pdf_bytes)); doc.save()
                except Exception:
                    pass

        # Create notifications for lease renewal (1 month before expiry)
        one_month_later = today + relativedelta(months=1)
        for lease in Lease.objects.filter(end_date__lte=one_month_later, end_date__gte=today, status='expiring_soon'):
            user = lease.tenant.user if hasattr(lease.tenant, 'user') else User.objects.filter(is_staff=True).first()
            if user:
                obj, created = Notification.objects.get_or_create(
                    user=user,
                    message=f'هل لديك رغبة في تجديد عقد الإيجار رقم {lease.contract_number}؟ ينتهي في {lease.end_date.strftime("%d/%m/%Y")}',
                    defaults={'read': False}
                )
                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} notifications'))

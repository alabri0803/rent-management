from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import Lease, PaymentOverdueNotice, PaymentOverdueDetail
from dateutil.relativedelta import relativedelta
import datetime


class Command(BaseCommand):
    help = 'اختبار اكتشاف الدفعات المتأخرة وإنشاء الإنذارات'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('بدء اختبار نظام اكتشاف الدفعات المتأخرة...')
        )

        today = timezone.now().date()
        active_leases = Lease.objects.filter(status='active')
        
        self.stdout.write(f'التاريخ الحالي: {today}')
        self.stdout.write(f'عدد العقود النشطة: {active_leases.count()}')
        self.stdout.write('='*60)

        total_overdue_found = 0
        total_notices_possible = 0

        for lease in active_leases:
            try:
                self.stdout.write(f'\n📋 فحص العقد: {lease.contract_number} - {lease.tenant.name}')
                
                # الحصول على ملخص الدفعات
                payment_summary = lease.get_payment_summary()
                overdue_months = []
                
                for month_data in payment_summary:
                    if month_data['status'] == 'overdue' and month_data['balance'] > 0:
                        total_overdue_found += 1
                        
                        # فحص إذا كان متأخر لأكثر من 30 يوم
                        if month_data['days_overdue'] >= 30:
                            # فحص عدم وجود إنذار سابق
                            existing_detail = PaymentOverdueDetail.objects.filter(
                                notice__lease=lease,
                                overdue_month=month_data['month'],
                                overdue_year=month_data['year']
                            ).exists()
                            
                            status_icon = "✅" if not existing_detail else "⚠️"
                            status_text = "يمكن إنشاء إنذار" if not existing_detail else "إنذار موجود"
                            
                            self.stdout.write(
                                f'  {status_icon} {month_data["month"]}/{month_data["year"]} - '
                                f'{month_data["balance"]} ر.ع - '
                                f'{month_data["days_overdue"]} يوم تأخير - '
                                f'{status_text}'
                            )
                            
                            if not existing_detail:
                                overdue_months.append(month_data)
                                total_notices_possible += 1
                        else:
                            self.stdout.write(
                                f'  ⏳ {month_data["month"]}/{month_data["year"]} - '
                                f'{month_data["balance"]} ر.ع - '
                                f'{month_data["days_overdue"]} يوم تأخير - '
                                f'لم يكمل 30 يوم بعد'
                            )
                
                if not any(m['status'] == 'overdue' for m in payment_summary):
                    self.stdout.write('  ✅ لا توجد دفعات متأخرة')
                
                if overdue_months:
                    total_amount = sum(month['balance'] for month in overdue_months)
                    self.stdout.write(
                        self.style.WARNING(
                            f'  💰 إجمالي المبلغ القابل للإنذار: {total_amount} ر.ع '
                            f'({len(overdue_months)} شهر)'
                        )
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ خطأ في فحص العقد {lease.contract_number}: {e}')
                )

        # عرض الإحصائيات النهائية
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 إحصائيات الفحص:'))
        self.stdout.write(f'إجمالي الدفعات المتأخرة: {total_overdue_found}')
        self.stdout.write(f'الدفعات القابلة لإنشاء إنذارات: {total_notices_possible}')
        
        # إحصائيات الإنذارات الموجودة
        existing_notices = PaymentOverdueNotice.objects.count()
        draft_notices = PaymentOverdueNotice.objects.filter(status='draft').count()
        
        self.stdout.write(f'الإنذارات الموجودة في النظام: {existing_notices}')
        self.stdout.write(f'الإنذارات في حالة مسودة: {draft_notices}')
        
        if total_notices_possible > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'\n🚨 يمكن إنشاء {total_notices_possible} إنذار جديد!'
                )
            )
            self.stdout.write('لإنشاء الإنذارات، استخدم الأمر:')
            self.stdout.write('python manage.py generate_overdue_notices')
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ لا توجد إنذارات جديدة للإنشاء')
            )

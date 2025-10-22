from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'أمر شامل لمعالجة جميع الإشعارات والإنذارات المتعلقة بالعقود'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='عرض التغييرات دون تطبيقها فعلياً',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.SUCCESS('🚀 نظام معالجة إشعارات وإنذارات العقود الشامل'))
        self.stdout.write(self.style.SUCCESS('='*80))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  وضع الاختبار (--dry-run) - لن يتم تطبيق التغييرات فعلياً\n'))
        
        # الخطوة 1: تحديث حالات العقود
        self.stdout.write(self.style.SUCCESS('\n📋 الخطوة 1: تحديث حالات العقود...'))
        self.stdout.write('-'*80)
        try:
            call_command('update_lease_statues')
            self.stdout.write(self.style.SUCCESS('✅ تم تحديث حالات العقود بنجاح\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ خطأ في تحديث حالات العقود: {str(e)}\n'))
        
        # الخطوة 2: فحص العقود المنتهية وإنشاء الإشعارات
        self.stdout.write(self.style.SUCCESS('\n📋 الخطوة 2: فحص العقود المنتهية وإنشاء الإشعارات...'))
        self.stdout.write('-'*80)
        try:
            if dry_run:
                call_command('check_expired_leases', '--dry-run')
            else:
                call_command('check_expired_leases')
            self.stdout.write(self.style.SUCCESS('✅ تم فحص العقود المنتهية بنجاح\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ خطأ في فحص العقود المنتهية: {str(e)}\n'))
        
        # الخطوة 3: إنشاء إنذارات عدم السداد
        self.stdout.write(self.style.SUCCESS('\n📋 الخطوة 3: إنشاء إنذارات عدم السداد للدفعات المتأخرة...'))
        self.stdout.write('-'*80)
        try:
            if dry_run:
                call_command('generate_overdue_notices', '--dry-run')
            else:
                call_command('generate_overdue_notices')
            self.stdout.write(self.style.SUCCESS('✅ تم إنشاء إنذارات عدم السداد بنجاح\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ خطأ في إنشاء إنذارات عدم السداد: {str(e)}\n'))
        
        # الخطوة 4: إنشاء تذكيرات التجديد
        self.stdout.write(self.style.SUCCESS('\n📋 الخطوة 4: إنشاء تذكيرات التجديد للعقود القريبة من الانتهاء...'))
        self.stdout.write('-'*80)
        try:
            if dry_run:
                call_command('generate_renewal_reminders', '--dry-run')
            else:
                call_command('generate_renewal_reminders')
            self.stdout.write(self.style.SUCCESS('✅ تم إنشاء تذكيرات التجديد بنجاح\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ خطأ في إنشاء تذكيرات التجديد: {str(e)}\n'))
        
        # الخلاصة
        self.stdout.write('\n' + '='*80)
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  انتهى وضع الاختبار'))
            self.stdout.write(self.style.SUCCESS('\nلتطبيق التغييرات فعلياً، شغّل الأمر بدون --dry-run:'))
            self.stdout.write('  python manage.py process_lease_notifications')
        else:
            self.stdout.write(self.style.SUCCESS('✅ اكتملت جميع العمليات بنجاح!'))
        
        self.stdout.write('\n💡 نصيحة: لجدولة هذا الأمر ليعمل تلقائياً يومياً، أضفه إلى crontab:')
        self.stdout.write('  0 9 * * * cd /path/to/project && python manage.py process_lease_notifications')
        self.stdout.write('='*80 + '\n')

"""
أمر إدارة لإعداد الصلاحيات الافتراضية للمستخدمين الموجودين
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import UserProfile
from django.utils.translation import gettext as _


class Command(BaseCommand):
    help = 'إعداد الصلاحيات الافتراضية للمستخدمين الموجودين'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='إعادة تعيين جميع الصلاحيات إلى القيم الافتراضية',
        )
        parser.add_argument(
            '--role',
            type=str,
            choices=['property_manager', 'financial_manager', 'tenant_manager', 'viewer'],
            help='تطبيق دور محدد على جميع المستخدمين غير الإداريين',
        )

    def handle(self, *args, **options):
        reset = options['reset']
        role = options.get('role')
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('بدء إعداد الصلاحيات الافتراضية'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # إحصائيات
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        # معالجة جميع المستخدمين
        all_users = User.objects.all()
        total_users = all_users.count()
        
        self.stdout.write(f'\nإجمالي المستخدمين: {total_users}')
        self.stdout.write('-' * 60)
        
        for user in all_users:
            # تخطي المستخدمين الإداريين
            if user.is_superuser:
                self.stdout.write(
                    self.style.WARNING(
                        f'⏭️  تخطي المستخدم الإداري: {user.username}'
                    )
                )
                skipped_count += 1
                continue
            
            # إنشاء أو الحصول على UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ تم إنشاء ملف للمستخدم: {user.username}'
                    )
                )
                created_count += 1
            
            # تطبيق دور محدد إذا تم تحديده
            if role:
                profile.set_role_permissions(role)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'🔄 تم تطبيق دور "{role}" على: {user.username}'
                    )
                )
                updated_count += 1
            # إعادة تعيين إلى القيم الافتراضية
            elif reset:
                # القيم الافتراضية: عرض فقط للعقارات والعقود والمستأجرين
                profile.can_view_buildings = True
                profile.can_manage_buildings = False
                profile.can_view_units = True
                profile.can_manage_units = False
                profile.can_view_leases = True
                profile.can_manage_leases = False
                profile.can_view_tenants = True
                profile.can_manage_tenants = False
                profile.can_view_payments = False
                profile.can_manage_payments = False
                profile.can_view_invoices = False
                profile.can_manage_invoices = False
                profile.can_view_expenses = False
                profile.can_manage_expenses = False
                profile.can_view_notices = False
                profile.can_manage_notices = False
                profile.can_view_reports = False
                profile.can_export_reports = False
                profile.can_manage_users = False
                profile.can_access_settings = False
                profile.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'🔄 تم إعادة تعيين صلاحيات: {user.username}'
                    )
                )
                updated_count += 1
        
        # عرض النتائج النهائية
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('📊 النتائج النهائية:'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'✅ تم إنشاء: {created_count} ملف مستخدم')
        self.stdout.write(f'🔄 تم التحديث: {updated_count} مستخدم')
        self.stdout.write(f'⏭️  تم التخطي: {skipped_count} مستخدم إداري')
        self.stdout.write(f'📈 الإجمالي: {total_users} مستخدم')
        
        # نصائح للاستخدام
        if not role and not reset:
            self.stdout.write('\n' + '-' * 60)
            self.stdout.write(self.style.WARNING('💡 نصائح الاستخدام:'))
            self.stdout.write(
                '\n  لتطبيق دور محدد على جميع المستخدمين:'
            )
            self.stdout.write(
                '  python manage.py setup_default_permissions --role=property_manager'
            )
            self.stdout.write(
                '\n  لإعادة تعيين جميع الصلاحيات إلى القيم الافتراضية:'
            )
            self.stdout.write(
                '  python manage.py setup_default_permissions --reset'
            )
            self.stdout.write(
                '\n  الأدوار المتاحة:'
            )
            self.stdout.write('    - property_manager: مدير عقارات')
            self.stdout.write('    - financial_manager: مدير مالي')
            self.stdout.write('    - tenant_manager: مدير مستأجرين')
            self.stdout.write('    - viewer: مشاهد فقط')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✨ تم الانتهاء بنجاح!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

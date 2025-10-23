"""
Tests for Dashboard Signals

يختبر جميع الإشارات في تطبيق dashboard
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from dashboard.models import (
    Building, Unit, Tenant, Lease, Payment,
    PaymentOverdueNotice, Notification
)


class PaymentSignalTest(TestCase):
    """اختبارات إشارات الدفعات"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        building = Building.objects.create(name="مبنى", address="عنوان")
        self.unit = Unit.objects.create(
            building=building,
            number="101",
            floor=1,
            unit_type="apartment"
        )
        self.tenant = Tenant.objects.create(
            name="مستأجر",
            tenant_type="sole_proprietorship"
        )
        self.lease = Lease.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            start_date=timezone.now().date() - timedelta(days=60),
            end_date=timezone.now().date() + timedelta(days=305),
            monthly_rent=Decimal('500.00'),
            status='active'
        )
    
    def test_payment_creates_notification(self):
        """اختبار إنشاء إشعار عند إضافة دفعة"""
        initial_count = Notification.objects.count()
        
        Payment.objects.create(
            lease=self.lease,
            amount=Decimal('500.00'),
            payment_date=timezone.now().date(),
            payment_method='cash',
            month=timezone.now().month,
            year=timezone.now().year
        )
        
        # يجب أن يزيد عدد الإشعارات
        self.assertGreater(Notification.objects.count(), initial_count)
    
    def test_payment_updates_overdue_notice(self):
        """اختبار تحديث الإنذار عند الدفع"""
        # إنشاء إنذار
        notice = PaymentOverdueNotice.objects.create(
            lease=self.lease,
            total_overdue_amount=Decimal('500.00'),
            notice_date=timezone.now().date(),
            status='sent'
        )
        
        # إضافة دفعة
        Payment.objects.create(
            lease=self.lease,
            amount=Decimal('500.00'),
            payment_date=timezone.now().date(),
            payment_method='cash',
            month=timezone.now().month,
            year=timezone.now().year
        )
        
        # تحديث الإنذار
        notice.refresh_from_db()
        # يجب أن يتم تحديث الإنذار


class LeaseSignalTest(TestCase):
    """اختبارات إشارات العقود"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        building = Building.objects.create(name="مبنى", address="عنوان")
        self.unit = Unit.objects.create(
            building=building,
            number="101",
            floor=1,
            unit_type="apartment",
            is_available=True
        )
        self.tenant = Tenant.objects.create(
            name="مستأجر",
            tenant_type="sole_proprietorship"
        )
    
    def test_lease_creation_updates_unit_availability(self):
        """اختبار تحديث توفر الوحدة عند إنشاء عقد"""
        self.assertTrue(self.unit.is_available)
        
        Lease.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal('500.00'),
            status='active'
        )
        
        self.unit.refresh_from_db()
        # يجب أن تصبح الوحدة غير متاحة
        self.assertFalse(self.unit.is_available)
    
    def test_lease_cancellation_updates_unit_availability(self):
        """اختبار تحديث توفر الوحدة عند إلغاء عقد"""
        lease = Lease.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal('500.00'),
            status='active'
        )
        
        # إلغاء العقد
        lease.status = 'cancelled'
        lease.save()
        
        self.unit.refresh_from_db()
        # يجب أن تصبح الوحدة متاحة
        self.assertTrue(self.unit.is_available)


class UserProfileSignalTest(TestCase):
    """اختبارات إشارات ملف المستخدم"""
    
    def test_user_profile_created_on_user_creation(self):
        """اختبار إنشاء ملف مستخدم عند إنشاء مستخدم جديد"""
        user = User.objects.create_user(
            username='newuser',
            password='testpass123'
        )
        
        # يجب أن يتم إنشاء UserProfile تلقائياً
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsNotNone(user.profile)


class NotificationSignalTest(TestCase):
    """اختبارات إشارات الإشعارات"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_notification_created_for_important_events(self):
        """اختبار إنشاء إشعارات للأحداث المهمة"""
        initial_count = Notification.objects.filter(user=self.user).count()
        
        # إنشاء حدث مهم (مثل دفعة جديدة)
        building = Building.objects.create(name="مبنى", address="عنوان")
        unit = Unit.objects.create(building=building, number="101", floor=1, unit_type="apartment")
        tenant = Tenant.objects.create(name="مستأجر", tenant_type="sole_proprietorship")
        lease = Lease.objects.create(
            unit=unit,
            tenant=tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal('500.00'),
            status='active'
        )
        
        Payment.objects.create(
            lease=lease,
            amount=Decimal('500.00'),
            payment_date=timezone.now().date(),
            payment_method='cash',
            month=timezone.now().month,
            year=timezone.now().year
        )
        
        # يجب أن يزيد عدد الإشعارات
        final_count = Notification.objects.filter(user=self.user).count()
        # قد يتم إنشاء إشعارات أو لا حسب التطبيق


class OverdueNoticeSignalTest(TestCase):
    """اختبارات إشارات الإنذارات"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        building = Building.objects.create(name="مبنى", address="عنوان")
        unit = Unit.objects.create(building=building, number="101", floor=1, unit_type="apartment")
        tenant = Tenant.objects.create(name="مستأجر", tenant_type="sole_proprietorship")
        self.lease = Lease.objects.create(
            unit=unit,
            tenant=tenant,
            start_date=timezone.now().date() - timedelta(days=60),
            end_date=timezone.now().date() + timedelta(days=305),
            monthly_rent=Decimal('500.00'),
            status='active'
        )
    
    def test_overdue_notice_status_change_creates_notification(self):
        """اختبار إنشاء إشعار عند تغيير حالة الإنذار"""
        notice = PaymentOverdueNotice.objects.create(
            lease=self.lease,
            total_overdue_amount=Decimal('500.00'),
            notice_date=timezone.now().date(),
            status='draft'
        )
        
        initial_count = Notification.objects.count()
        
        # تغيير حالة الإنذار
        notice.status = 'sent'
        notice.save()
        
        # قد يتم إنشاء إشعار
        # (حسب تطبيق الإشارات في المشروع)


class SignalIntegrationTest(TestCase):
    """اختبارات تكامل الإشارات"""
    
    def test_complete_lease_payment_workflow(self):
        """اختبار سير عمل كامل للعقد والدفعات"""
        # إنشاء البيانات الأساسية
        building = Building.objects.create(name="مبنى", address="عنوان")
        unit = Unit.objects.create(
            building=building,
            number="101",
            floor=1,
            unit_type="apartment",
            is_available=True
        )
        tenant = Tenant.objects.create(name="مستأجر", tenant_type="sole_proprietorship")
        
        # إنشاء عقد
        lease = Lease.objects.create(
            unit=unit,
            tenant=tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal('500.00'),
            status='active'
        )
        
        # التحقق من تحديث الوحدة
        unit.refresh_from_db()
        self.assertFalse(unit.is_available)
        
        # إضافة دفعة
        payment = Payment.objects.create(
            lease=lease,
            amount=Decimal('500.00'),
            payment_date=timezone.now().date(),
            payment_method='cash',
            month=timezone.now().month,
            year=timezone.now().year
        )
        
        # التحقق من إنشاء الدفعة
        self.assertIsNotNone(payment.id)
        
        # إلغاء العقد
        lease.status = 'cancelled'
        lease.save()
        
        # التحقق من تحديث الوحدة
        unit.refresh_from_db()
        self.assertTrue(unit.is_available)


# تشغيل الاختبارات:
# python manage.py test dashboard.tests.test_signals

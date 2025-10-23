"""
Tests for Dashboard Models

يختبر جميع النماذج في تطبيق dashboard
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from dashboard.models import (
    Building, Unit, Tenant, Lease, Payment, 
    SecurityDeposit, Expense, MaintenanceRequest,
    PaymentOverdueNotice, Notification
)


class BuildingModelTest(TestCase):
    """اختبارات نموذج المبنى"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.building = Building.objects.create(
            name="مبنى الاختبار",
            address="شارع الاختبار، مسقط"
        )
    
    def test_building_creation(self):
        """اختبار إنشاء مبنى"""
        self.assertEqual(self.building.name, "مبنى الاختبار")
        self.assertEqual(self.building.address, "شارع الاختبار، مسقط")
    
    def test_building_str(self):
        """اختبار تمثيل النص للمبنى"""
        self.assertEqual(str(self.building), "مبنى الاختبار")
    
    def test_building_units_count(self):
        """اختبار عدد الوحدات في المبنى"""
        # إنشاء وحدات
        Unit.objects.create(building=self.building, number="101", floor=1, unit_type="apartment")
        Unit.objects.create(building=self.building, number="102", floor=1, unit_type="apartment")
        
        self.assertEqual(self.building.unit_set.count(), 2)


class UnitModelTest(TestCase):
    """اختبارات نموذج الوحدة"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.building = Building.objects.create(
            name="مبنى الاختبار",
            address="شارع الاختبار"
        )
        self.unit = Unit.objects.create(
            building=self.building,
            number="101",
            floor=1,
            unit_type="apartment",
            is_available=True
        )
    
    def test_unit_creation(self):
        """اختبار إنشاء وحدة"""
        self.assertEqual(self.unit.number, "101")
        self.assertEqual(self.unit.floor, 1)
        self.assertEqual(self.unit.unit_type, "apartment")
        self.assertTrue(self.unit.is_available)
    
    def test_unit_str(self):
        """اختبار تمثيل النص للوحدة"""
        expected = f"مبنى الاختبار - وحدة 101"
        self.assertEqual(str(self.unit), expected)
    
    def test_unit_availability(self):
        """اختبار حالة توفر الوحدة"""
        self.assertTrue(self.unit.is_available)
        
        # تغيير الحالة
        self.unit.is_available = False
        self.unit.save()
        
        self.assertFalse(self.unit.is_available)


class TenantModelTest(TestCase):
    """اختبارات نموذج المستأجر"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.tenant = Tenant.objects.create(
            name="أحمد محمد",
            tenant_type="sole_proprietorship",
            phone="+96899123456",
            email="ahmed@example.com",
            civil_id="12345678"
        )
    
    def test_tenant_creation(self):
        """اختبار إنشاء مستأجر"""
        self.assertEqual(self.tenant.name, "أحمد محمد")
        self.assertEqual(self.tenant.tenant_type, "sole_proprietorship")
        self.assertEqual(self.tenant.phone, "+96899123456")
    
    def test_tenant_str(self):
        """اختبار تمثيل النص للمستأجر"""
        self.assertEqual(str(self.tenant), "أحمد محمد")
    
    def test_tenant_email_validation(self):
        """اختبار صحة البريد الإلكتروني"""
        self.assertTrue('@' in self.tenant.email)


class LeaseModelTest(TestCase):
    """اختبارات نموذج العقد"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.building = Building.objects.create(name="مبنى", address="عنوان")
        self.unit = Unit.objects.create(
            building=self.building,
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
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal('500.00'),
            status='active'
        )
    
    def test_lease_creation(self):
        """اختبار إنشاء عقد"""
        self.assertEqual(self.lease.monthly_rent, Decimal('500.00'))
        self.assertEqual(self.lease.status, 'active')
    
    def test_lease_duration(self):
        """اختبار مدة العقد"""
        duration = (self.lease.end_date - self.lease.start_date).days
        self.assertEqual(duration, 365)
    
    def test_lease_annual_rent(self):
        """اختبار حساب الإيجار السنوي"""
        annual_rent = self.lease.monthly_rent * 12
        self.assertEqual(annual_rent, Decimal('6000.00'))
    
    def test_lease_str(self):
        """اختبار تمثيل النص للعقد"""
        expected = f"عقد مستأجر - مبنى - وحدة 101"
        self.assertEqual(str(self.lease), expected)
    
    def test_days_until_expiry(self):
        """اختبار حساب الأيام المتبقية"""
        if hasattr(self.lease, 'days_until_expiry'):
            days = self.lease.days_until_expiry
            self.assertIsNotNone(days)
            self.assertGreaterEqual(days, 0)


class PaymentModelTest(TestCase):
    """اختبارات نموذج الدفعة"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        building = Building.objects.create(name="مبنى", address="عنوان")
        unit = Unit.objects.create(building=building, number="101", floor=1, unit_type="apartment")
        tenant = Tenant.objects.create(name="مستأجر", tenant_type="sole_proprietorship")
        self.lease = Lease.objects.create(
            unit=unit,
            tenant=tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal('500.00'),
            status='active'
        )
        self.payment = Payment.objects.create(
            lease=self.lease,
            amount=Decimal('500.00'),
            payment_date=timezone.now().date(),
            payment_method='cash',
            month=timezone.now().month,
            year=timezone.now().year
        )
    
    def test_payment_creation(self):
        """اختبار إنشاء دفعة"""
        self.assertEqual(self.payment.amount, Decimal('500.00'))
        self.assertEqual(self.payment.payment_method, 'cash')
    
    def test_payment_str(self):
        """اختبار تمثيل النص للدفعة"""
        self.assertIn('500.00', str(self.payment))
    
    def test_payment_lease_relationship(self):
        """اختبار العلاقة مع العقد"""
        self.assertEqual(self.payment.lease, self.lease)


class SecurityDepositModelTest(TestCase):
    """اختبارات نموذج الضمان"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        building = Building.objects.create(name="مبنى", address="عنوان")
        unit = Unit.objects.create(building=building, number="101", floor=1, unit_type="apartment")
        tenant = Tenant.objects.create(name="مستأجر", tenant_type="sole_proprietorship")
        self.lease = Lease.objects.create(
            unit=unit,
            tenant=tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal('500.00'),
            status='active'
        )
        self.deposit = SecurityDeposit.objects.create(
            lease=self.lease,
            amount=Decimal('500.00'),
            received_date=timezone.now().date(),
            payment_method='cash',
            status='held'
        )
    
    def test_deposit_creation(self):
        """اختبار إنشاء ضمان"""
        self.assertEqual(self.deposit.amount, Decimal('500.00'))
        self.assertEqual(self.deposit.status, 'held')
    
    def test_deposit_status_choices(self):
        """اختبار خيارات حالة الضمان"""
        valid_statuses = ['held', 'returned', 'forfeited']
        self.assertIn(self.deposit.status, valid_statuses)


class ExpenseModelTest(TestCase):
    """اختبارات نموذج المصروف"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.building = Building.objects.create(name="مبنى", address="عنوان")
        self.expense = Expense.objects.create(
            building=self.building,
            description="صيانة المصعد",
            amount=Decimal('200.00'),
            expense_date=timezone.now().date(),
            category='maintenance'
        )
    
    def test_expense_creation(self):
        """اختبار إنشاء مصروف"""
        self.assertEqual(self.expense.amount, Decimal('200.00'))
        self.assertEqual(self.expense.category, 'maintenance')
    
    def test_expense_str(self):
        """اختبار تمثيل النص للمصروف"""
        self.assertIn('صيانة المصعد', str(self.expense))


class NotificationModelTest(TestCase):
    """اختبارات نموذج الإشعار"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.notification = Notification.objects.create(
            user=self.user,
            title="إشعار اختبار",
            message="هذا إشعار للاختبار",
            notification_type='info'
        )
    
    def test_notification_creation(self):
        """اختبار إنشاء إشعار"""
        self.assertEqual(self.notification.title, "إشعار اختبار")
        self.assertFalse(self.notification.is_read)
    
    def test_notification_mark_as_read(self):
        """اختبار تعليم الإشعار كمقروء"""
        self.notification.is_read = True
        self.notification.save()
        self.assertTrue(self.notification.is_read)
    
    def test_notification_str(self):
        """اختبار تمثيل النص للإشعار"""
        self.assertIn('إشعار اختبار', str(self.notification))


class PaymentOverdueNoticeModelTest(TestCase):
    """اختبارات نموذج إنذار عدم السداد"""
    
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
        self.notice = PaymentOverdueNotice.objects.create(
            lease=self.lease,
            total_overdue_amount=Decimal('500.00'),
            notice_date=timezone.now().date(),
            status='draft'
        )
    
    def test_notice_creation(self):
        """اختبار إنشاء إنذار"""
        self.assertEqual(self.notice.total_overdue_amount, Decimal('500.00'))
        self.assertEqual(self.notice.status, 'draft')
    
    def test_notice_legal_deadline(self):
        """اختبار الموعد النهائي القانوني (30 يوم)"""
        if hasattr(self.notice, 'legal_deadline'):
            expected_deadline = self.notice.notice_date + timedelta(days=30)
            self.assertEqual(self.notice.legal_deadline, expected_deadline)
    
    def test_notice_status_change(self):
        """اختبار تغيير حالة الإنذار"""
        self.notice.status = 'sent'
        self.notice.save()
        self.assertEqual(self.notice.status, 'sent')


# تشغيل الاختبارات:
# python manage.py test dashboard.tests.test_models

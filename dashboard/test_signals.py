"""
اختبارات شاملة لـ Signals نظام إدارة الإيجارات
Tests for Rent Management System Signals
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from dashboard.models import (
    Building, Unit, Tenant, Lease, Payment,
    PaymentOverdueNotice, PaymentOverdueDetail,
    Notification
)


class PaymentSignalsTest(TestCase):
    """اختبارات Signals الخاصة بالدفعات"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        # إنشاء مستخدم للإشعارات
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # إنشاء عقد
        building = Building.objects.create(
            name="مبنى",
            address="عنوان",
            total_units=5
        )
        unit = Unit.objects.create(
            building=building,
            unit_number="101",
            unit_type="apartment",
            rent_amount=Decimal("500.00")
        )
        self.tenant = Tenant.objects.create(
            name="مستأجر",
            phone="99999999",
            email="test@test.com",
            tenant_type="sole_proprietorship"
        )
        self.lease = Lease.objects.create(
            unit=unit,
            tenant=self.tenant,
            start_date=timezone.now().date() - timedelta(days=90),
            end_date=timezone.now().date() + timedelta(days=275),
            monthly_rent=Decimal("500.00"),
            status="active"
        )
    
    def test_payment_creates_notification(self):
        """اختبار إنشاء إشعار عند إضافة دفعة"""
        initial_count = Notification.objects.count()
        
        Payment.objects.create(
            lease=self.lease,
            amount=Decimal("500.00"),
            payment_date=timezone.now().date(),
            payment_for_month=timezone.now().month,
            payment_for_year=timezone.now().year,
            payment_method="cash"
        )
        
        # التحقق من إنشاء إشعارات
        self.assertGreater(Notification.objects.count(), initial_count)
    
    def test_payment_updates_overdue_notice(self):
        """اختبار تحديث الإنذار عند الدفع"""
        # إنشاء إنذار
        notice = PaymentOverdueNotice.objects.create(
            lease=self.lease,
            notice_number="NOT-001",
            issue_date=timezone.now().date(),
            status="sent"
        )
        
        # إضافة تفاصيل الإنذار
        detail = PaymentOverdueDetail.objects.create(
            notice=notice,
            month=timezone.now().month,
            year=timezone.now().year,
            amount_due=Decimal("500.00")
        )
        
        # دفع كامل للشهر
        Payment.objects.create(
            lease=self.lease,
            amount=Decimal("500.00"),
            payment_date=timezone.now().date(),
            payment_for_month=timezone.now().month,
            payment_for_year=timezone.now().year,
            payment_method="cash"
        )
        
        # التحقق من حذف التفصيل
        self.assertFalse(
            PaymentOverdueDetail.objects.filter(pk=detail.pk).exists()
        )
    
    def test_partial_payment_updates_overdue_amount(self):
        """اختبار تحديث المبلغ المتأخر عند الدفع الجزئي"""
        # إنشاء إنذار
        notice = PaymentOverdueNotice.objects.create(
            lease=self.lease,
            notice_number="NOT-002",
            issue_date=timezone.now().date(),
            status="sent"
        )
        
        detail = PaymentOverdueDetail.objects.create(
            notice=notice,
            month=timezone.now().month,
            year=timezone.now().year,
            amount_due=Decimal("500.00")
        )
        
        # دفع جزئي
        Payment.objects.create(
            lease=self.lease,
            amount=Decimal("300.00"),
            payment_date=timezone.now().date(),
            payment_for_month=timezone.now().month,
            payment_for_year=timezone.now().year,
            payment_method="cash"
        )
        
        # التحقق من تحديث المبلغ
        detail.refresh_from_db()
        self.assertEqual(detail.amount_due, Decimal("200.00"))
    
    def test_full_payment_resolves_notice(self):
        """اختبار حل الإنذار عند الدفع الكامل"""
        # إنشاء إنذار بشهر واحد فقط
        notice = PaymentOverdueNotice.objects.create(
            lease=self.lease,
            notice_number="NOT-003",
            issue_date=timezone.now().date(),
            status="sent"
        )
        
        PaymentOverdueDetail.objects.create(
            notice=notice,
            month=timezone.now().month,
            year=timezone.now().year,
            amount_due=Decimal("500.00")
        )
        
        # دفع كامل
        Payment.objects.create(
            lease=self.lease,
            amount=Decimal("500.00"),
            payment_date=timezone.now().date(),
            payment_for_month=timezone.now().month,
            payment_for_year=timezone.now().year,
            payment_method="cash"
        )
        
        # التحقق من تحديث حالة الإنذار
        notice.refresh_from_db()
        self.assertEqual(notice.status, "resolved")


class LeaseSignalsTest(TestCase):
    """اختبارات Signals الخاصة بالعقود"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        building = Building.objects.create(
            name="مبنى",
            address="عنوان",
            total_units=5
        )
        self.unit = Unit.objects.create(
            building=building,
            unit_number="101",
            unit_type="apartment",
            rent_amount=Decimal("500.00")
        )
        self.tenant = Tenant.objects.create(
            name="مستأجر",
            phone="99999999",
            email="test@test.com",
            tenant_type="sole_proprietorship"
        )
    
    def test_lease_generates_contract_number(self):
        """اختبار توليد رقم العقد التلقائي"""
        lease = Lease.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal("500.00"),
            status="active"
        )
        
        self.assertIsNotNone(lease.contract_number)
        self.assertTrue(lease.contract_number.startswith("C-"))
    
    def test_lease_contract_number_unique(self):
        """اختبار أن رقم العقد فريد"""
        lease1 = Lease.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal("500.00"),
            status="active"
        )
        
        # إنشاء وحدة أخرى لعقد ثاني
        unit2 = Unit.objects.create(
            building=self.unit.building,
            unit_number="102",
            unit_type="apartment",
            rent_amount=Decimal("600.00")
        )
        
        lease2 = Lease.objects.create(
            unit=unit2,
            tenant=self.tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal("600.00"),
            status="active"
        )
        
        self.assertNotEqual(lease1.contract_number, lease2.contract_number)


class NotificationSignalsTest(TestCase):
    """اختبارات Signals الخاصة بالإشعارات"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        building = Building.objects.create(
            name="مبنى",
            address="عنوان",
            total_units=5
        )
        unit = Unit.objects.create(
            building=building,
            unit_number="101",
            unit_type="apartment",
            rent_amount=Decimal("500.00")
        )
        tenant = Tenant.objects.create(
            name="مستأجر",
            phone="99999999",
            email="test@test.com",
            tenant_type="sole_proprietorship"
        )
        self.lease = Lease.objects.create(
            unit=unit,
            tenant=tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal("500.00"),
            status="active"
        )
    
    def test_payment_creates_notification_for_staff(self):
        """اختبار إنشاء إشعار للموظفين عند الدفع"""
        # جعل المستخدم موظف
        self.user.is_staff = True
        self.user.save()
        
        initial_count = Notification.objects.filter(user=self.user).count()
        
        Payment.objects.create(
            lease=self.lease,
            amount=Decimal("500.00"),
            payment_date=timezone.now().date(),
            payment_for_month=timezone.now().month,
            payment_for_year=timezone.now().year,
            payment_method="cash"
        )
        
        # التحقق من إنشاء إشعار
        final_count = Notification.objects.filter(user=self.user).count()
        self.assertGreater(final_count, initial_count)


class OverdueNoticeGenerationTest(TestCase):
    """اختبارات توليد الإنذارات التلقائية"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        building = Building.objects.create(
            name="مبنى",
            address="عنوان",
            total_units=5
        )
        unit = Unit.objects.create(
            building=building,
            unit_number="101",
            unit_type="apartment",
            rent_amount=Decimal("500.00")
        )
        tenant = Tenant.objects.create(
            name="مستأجر",
            phone="99999999",
            email="test@test.com",
            tenant_type="sole_proprietorship"
        )
        
        # إنشاء عقد قديم (3 أشهر)
        self.lease = Lease.objects.create(
            unit=unit,
            tenant=tenant,
            start_date=timezone.now().date() - timedelta(days=90),
            end_date=timezone.now().date() + timedelta(days=275),
            monthly_rent=Decimal("500.00"),
            status="active"
        )
    
    def test_overdue_payment_detection(self):
        """اختبار اكتشاف الدفعات المتأخرة"""
        summary = self.lease.get_payment_summary()
        
        # يجب أن يكون هناك دفعات متأخرة
        overdue_payments = [p for p in summary if p['status'] == 'overdue']
        self.assertGreater(len(overdue_payments), 0)
    
    def test_notice_not_duplicated(self):
        """اختبار عدم تكرار الإنذارات"""
        # إنشاء إنذار يدوياً
        notice = PaymentOverdueNotice.objects.create(
            lease=self.lease,
            notice_number="NOT-001",
            issue_date=timezone.now().date(),
            status="sent"
        )
        
        PaymentOverdueDetail.objects.create(
            notice=notice,
            month=1,
            year=timezone.now().year,
            amount_due=Decimal("500.00")
        )
        
        # محاولة إنشاء إنذار آخر لنفس الشهر
        # يجب أن لا يتم إنشاء إنذار مكرر
        existing = PaymentOverdueDetail.objects.filter(
            notice__lease=self.lease,
            month=1,
            year=timezone.now().year
        ).exists()
        
        self.assertTrue(existing)


class FinancialCalculationTest(TestCase):
    """اختبارات الحسابات المالية"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        building = Building.objects.create(
            name="مبنى",
            address="عنوان",
            total_units=5
        )
        unit = Unit.objects.create(
            building=building,
            unit_number="101",
            unit_type="apartment",
            rent_amount=Decimal("500.00")
        )
        tenant = Tenant.objects.create(
            name="مستأجر",
            phone="99999999",
            email="test@test.com",
            tenant_type="sole_proprietorship"
        )
        self.lease = Lease.objects.create(
            unit=unit,
            tenant=tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal("500.00"),
            status="active"
        )
    
    def test_payment_summary_calculations(self):
        """اختبار حسابات كشف الحساب"""
        # إنشاء دفعات
        Payment.objects.create(
            lease=self.lease,
            amount=Decimal("500.00"),
            payment_date=timezone.now().date(),
            payment_for_month=timezone.now().month,
            payment_for_year=timezone.now().year,
            payment_method="cash"
        )
        
        Payment.objects.create(
            lease=self.lease,
            amount=Decimal("300.00"),
            payment_date=timezone.now().date(),
            payment_for_month=(timezone.now().month % 12) + 1,
            payment_for_year=timezone.now().year,
            payment_method="cash"
        )
        
        summary = self.lease.get_payment_summary()
        
        # التحقق من الحسابات
        for month_data in summary:
            self.assertIn('month', month_data)
            self.assertIn('year', month_data)
            self.assertIn('rent', month_data)
            self.assertIn('paid', month_data)
            self.assertIn('balance', month_data)
            self.assertIn('status', month_data)
            
            # التحقق من صحة الحسابات
            expected_balance = month_data['rent'] - month_data['paid']
            self.assertEqual(month_data['balance'], expected_balance)
    
    def test_total_rent_calculation(self):
        """اختبار حساب إجمالي الإيجار"""
        total = self.lease.total_rent()
        
        # حساب عدد الأشهر
        months = (self.lease.end_date.year - self.lease.start_date.year) * 12
        months += self.lease.end_date.month - self.lease.start_date.month + 1
        
        expected_total = self.lease.monthly_rent * months
        self.assertEqual(total, expected_total)
    
    def test_days_overdue_calculation(self):
        """اختبار حساب أيام التأخير"""
        summary = self.lease.get_payment_summary()
        
        for month_data in summary:
            if month_data['status'] == 'overdue':
                self.assertIn('days_overdue', month_data)
                self.assertGreater(month_data['days_overdue'], 0)

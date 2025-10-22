"""
اختبارات شاملة لنماذج نظام إدارة الإيجارات
Tests for Rent Management System Models
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from dashboard.models import (
    Building, Unit, Tenant, Lease, Payment, 
    SecurityDeposit, Expense, Invoice, InvoiceItem,
    PaymentOverdueNotice, PaymentOverdueDetail,
    UserProfile, RealEstateOffice, BuildingOwner,
    CommissionAgreement, RentCollection, CommissionDistribution
)


class BuildingModelTest(TestCase):
    """اختبارات نموذج المبنى"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.building = Building.objects.create(
            name="مبنى الاختبار",
            address="شارع الاختبار، مسقط",
            total_units=10
        )
    
    def test_building_creation(self):
        """اختبار إنشاء مبنى"""
        self.assertEqual(self.building.name, "مبنى الاختبار")
        self.assertEqual(self.building.total_units, 10)
        self.assertIsNotNone(self.building.created_at)
    
    def test_building_str(self):
        """اختبار تمثيل النص للمبنى"""
        self.assertEqual(str(self.building), "مبنى الاختبار")
    
    def test_occupied_units_count(self):
        """اختبار حساب الوحدات المشغولة"""
        # إنشاء وحدات
        unit1 = Unit.objects.create(
            building=self.building,
            unit_number="101",
            unit_type="apartment",
            rent_amount=Decimal("500.00")
        )
        unit2 = Unit.objects.create(
            building=self.building,
            unit_number="102",
            unit_type="apartment",
            rent_amount=Decimal("600.00")
        )
        
        # إنشاء مستأجر وعقد
        tenant = Tenant.objects.create(
            name="مستأجر الاختبار",
            phone="99999999",
            email="test@test.com",
            tenant_type="sole_proprietorship"
        )
        
        Lease.objects.create(
            unit=unit1,
            tenant=tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal("500.00"),
            status="active"
        )
        
        self.assertEqual(self.building.occupied_units_count(), 1)
    
    def test_available_units_count(self):
        """اختبار حساب الوحدات المتاحة"""
        Unit.objects.create(
            building=self.building,
            unit_number="101",
            unit_type="apartment",
            rent_amount=Decimal("500.00")
        )
        Unit.objects.create(
            building=self.building,
            unit_number="102",
            unit_type="apartment",
            rent_amount=Decimal("600.00")
        )
        
        self.assertEqual(self.building.available_units_count(), 2)


class UnitModelTest(TestCase):
    """اختبارات نموذج الوحدة"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.building = Building.objects.create(
            name="مبنى الاختبار",
            address="شارع الاختبار",
            total_units=5
        )
        self.unit = Unit.objects.create(
            building=self.building,
            unit_number="101",
            unit_type="apartment",
            bedrooms=2,
            bathrooms=2,
            area=100.0,
            rent_amount=Decimal("500.00")
        )
    
    def test_unit_creation(self):
        """اختبار إنشاء وحدة"""
        self.assertEqual(self.unit.unit_number, "101")
        self.assertEqual(self.unit.bedrooms, 2)
        self.assertEqual(self.unit.rent_amount, Decimal("500.00"))
    
    def test_unit_str(self):
        """اختبار تمثيل النص للوحدة"""
        expected = f"{self.building.name} - 101"
        self.assertEqual(str(self.unit), expected)
    
    def test_is_available(self):
        """اختبار حالة توفر الوحدة"""
        self.assertTrue(self.unit.is_available())
        
        # إنشاء عقد نشط
        tenant = Tenant.objects.create(
            name="مستأجر",
            phone="99999999",
            email="test@test.com",
            tenant_type="sole_proprietorship"
        )
        Lease.objects.create(
            unit=self.unit,
            tenant=tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal("500.00"),
            status="active"
        )
        
        self.assertFalse(self.unit.is_available())


class TenantModelTest(TestCase):
    """اختبارات نموذج المستأجر"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.tenant = Tenant.objects.create(
            name="أحمد محمد",
            phone="99123456",
            email="ahmed@test.com",
            tenant_type="sole_proprietorship",
            national_id="12345678"
        )
    
    def test_tenant_creation(self):
        """اختبار إنشاء مستأجر"""
        self.assertEqual(self.tenant.name, "أحمد محمد")
        self.assertEqual(self.tenant.phone, "99123456")
        self.assertEqual(self.tenant.tenant_type, "sole_proprietorship")
    
    def test_tenant_str(self):
        """اختبار تمثيل النص للمستأجر"""
        self.assertEqual(str(self.tenant), "أحمد محمد")
    
    def test_active_leases(self):
        """اختبار العقود النشطة للمستأجر"""
        building = Building.objects.create(name="مبنى", address="عنوان", total_units=5)
        unit = Unit.objects.create(
            building=building,
            unit_number="101",
            unit_type="apartment",
            rent_amount=Decimal("500.00")
        )
        
        lease = Lease.objects.create(
            unit=unit,
            tenant=self.tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal("500.00"),
            status="active"
        )
        
        active_leases = self.tenant.leases.filter(status="active")
        self.assertEqual(active_leases.count(), 1)
        self.assertEqual(active_leases.first(), lease)


class LeaseModelTest(TestCase):
    """اختبارات نموذج العقد"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.building = Building.objects.create(
            name="مبنى الاختبار",
            address="شارع الاختبار",
            total_units=5
        )
        self.unit = Unit.objects.create(
            building=self.building,
            unit_number="101",
            unit_type="apartment",
            rent_amount=Decimal("500.00")
        )
        self.tenant = Tenant.objects.create(
            name="مستأجر الاختبار",
            phone="99999999",
            email="test@test.com",
            tenant_type="sole_proprietorship"
        )
        self.lease = Lease.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal("500.00"),
            deposit_amount=Decimal("500.00"),
            status="active"
        )
    
    def test_lease_creation(self):
        """اختبار إنشاء عقد"""
        self.assertEqual(self.lease.monthly_rent, Decimal("500.00"))
        self.assertEqual(self.lease.status, "active")
        self.assertIsNotNone(self.lease.contract_number)
    
    def test_contract_number_generation(self):
        """اختبار توليد رقم العقد التلقائي"""
        self.assertTrue(self.lease.contract_number.startswith("C-"))
    
    def test_days_until_expiry(self):
        """اختبار حساب الأيام المتبقية"""
        days = self.lease.days_until_expiry
        self.assertIsNotNone(days)
        self.assertGreater(days, 0)
    
    def test_total_rent(self):
        """اختبار حساب إجمالي الإيجار"""
        # العقد لمدة سنة (12 شهر)
        expected_total = Decimal("500.00") * 12
        self.assertEqual(self.lease.total_rent(), expected_total)
    
    def test_get_payment_summary(self):
        """اختبار كشف حساب الدفعات"""
        # إنشاء دفعة
        Payment.objects.create(
            lease=self.lease,
            amount=Decimal("500.00"),
            payment_date=timezone.now().date(),
            payment_for_month=timezone.now().month,
            payment_for_year=timezone.now().year,
            payment_method="cash"
        )
        
        summary = self.lease.get_payment_summary()
        self.assertIsInstance(summary, list)
        self.assertGreater(len(summary), 0)


class PaymentModelTest(TestCase):
    """اختبارات نموذج الدفعة"""
    
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
        self.payment = Payment.objects.create(
            lease=self.lease,
            amount=Decimal("500.00"),
            payment_date=timezone.now().date(),
            payment_for_month=timezone.now().month,
            payment_for_year=timezone.now().year,
            payment_method="cash"
        )
    
    def test_payment_creation(self):
        """اختبار إنشاء دفعة"""
        self.assertEqual(self.payment.amount, Decimal("500.00"))
        self.assertEqual(self.payment.payment_method, "cash")
    
    def test_payment_str(self):
        """اختبار تمثيل النص للدفعة"""
        expected = f"{self.payment.amount} for {self.lease.contract_number}"
        self.assertIn(str(self.payment.amount), str(self.payment))
    
    def test_check_payment_validation(self):
        """اختبار التحقق من دفعة الشيك"""
        check_payment = Payment.objects.create(
            lease=self.lease,
            amount=Decimal("500.00"),
            payment_date=timezone.now().date(),
            payment_for_month=(timezone.now().month % 12) + 1,
            payment_for_year=timezone.now().year,
            payment_method="check",
            check_number="123456",
            check_date=timezone.now().date(),
            bank_name="بنك الاختبار",
            check_status="cleared"
        )
        self.assertEqual(check_payment.check_status, "cleared")


class ExpenseModelTest(TestCase):
    """اختبارات نموذج المصروفات"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.building = Building.objects.create(
            name="مبنى",
            address="عنوان",
            total_units=5
        )
        self.expense = Expense.objects.create(
            building=self.building,
            category="maintenance",
            description="صيانة المصعد",
            amount=Decimal("200.00"),
            expense_date=timezone.now().date()
        )
    
    def test_expense_creation(self):
        """اختبار إنشاء مصروف"""
        self.assertEqual(self.expense.amount, Decimal("200.00"))
        self.assertEqual(self.expense.category, "maintenance")
    
    def test_expense_str(self):
        """اختبار تمثيل النص للمصروف"""
        self.assertIn("صيانة", str(self.expense))


class InvoiceModelTest(TestCase):
    """اختبارات نموذج الفاتورة"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.tenant = Tenant.objects.create(
            name="مستأجر",
            phone="99999999",
            email="test@test.com",
            tenant_type="sole_proprietorship"
        )
        self.invoice = Invoice.objects.create(
            tenant=self.tenant,
            invoice_number="INV-001",
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30),
            status="draft"
        )
    
    def test_invoice_creation(self):
        """اختبار إنشاء فاتورة"""
        self.assertEqual(self.invoice.invoice_number, "INV-001")
        self.assertEqual(self.invoice.status, "draft")
    
    def test_invoice_total_amount(self):
        """اختبار حساب إجمالي الفاتورة"""
        InvoiceItem.objects.create(
            invoice=self.invoice,
            description="بند 1",
            amount=Decimal("100.00")
        )
        InvoiceItem.objects.create(
            invoice=self.invoice,
            description="بند 2",
            amount=Decimal("150.00")
        )
        
        self.assertEqual(self.invoice.total_amount, Decimal("250.00"))


class UserProfileModelTest(TestCase):
    """اختبارات نموذج ملف المستخدم"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            first_name="أحمد",
            last_name="محمد"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone_number="+96899999999",
            first_name_english="Ahmed"
        )
    
    def test_profile_creation(self):
        """اختبار إنشاء ملف المستخدم"""
        self.assertEqual(self.profile.phone_number, "+96899999999")
        self.assertEqual(self.profile.first_name_english, "Ahmed")
    
    def test_get_display_name(self):
        """اختبار الحصول على اسم العرض"""
        # باللغة العربية
        arabic_name = self.profile.get_display_name('ar')
        self.assertIn("أحمد", arabic_name)
        
        # باللغة الإنجليزية
        english_name = self.profile.get_display_name('en')
        self.assertIn("Ahmed", english_name)
    
    def test_has_permission(self):
        """اختبار التحقق من الصلاحيات"""
        # المستخدم العادي ليس لديه صلاحيات افتراضياً
        self.assertFalse(self.profile.has_permission('can_manage_buildings'))
        
        # تفعيل صلاحية
        self.profile.can_manage_buildings = True
        self.profile.save()
        self.assertTrue(self.profile.has_permission('can_manage_buildings'))
    
    def test_superuser_has_all_permissions(self):
        """اختبار أن المستخدم الإداري لديه جميع الصلاحيات"""
        admin_user = User.objects.create_superuser(
            username="admin",
            password="admin123",
            email="admin@test.com"
        )
        admin_profile = UserProfile.objects.create(user=admin_user)
        
        self.assertTrue(admin_profile.has_permission('can_manage_buildings'))
        self.assertTrue(admin_profile.has_permission('can_manage_users'))


class PaymentOverdueNoticeTest(TestCase):
    """اختبارات نظام الإنذارات"""
    
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
            start_date=timezone.now().date() - timedelta(days=90),
            end_date=timezone.now().date() + timedelta(days=275),
            monthly_rent=Decimal("500.00"),
            status="active"
        )
    
    def test_overdue_notice_creation(self):
        """اختبار إنشاء إنذار"""
        notice = PaymentOverdueNotice.objects.create(
            lease=self.lease,
            notice_number="NOT-001",
            issue_date=timezone.now().date(),
            status="draft"
        )
        
        self.assertEqual(notice.notice_number, "NOT-001")
        self.assertEqual(notice.status, "draft")
    
    def test_overdue_detail_creation(self):
        """اختبار إنشاء تفاصيل الإنذار"""
        notice = PaymentOverdueNotice.objects.create(
            lease=self.lease,
            notice_number="NOT-001",
            issue_date=timezone.now().date(),
            status="draft"
        )
        
        detail = PaymentOverdueDetail.objects.create(
            notice=notice,
            month=1,
            year=2025,
            amount_due=Decimal("500.00")
        )
        
        self.assertEqual(detail.amount_due, Decimal("500.00"))
        self.assertEqual(detail.notice, notice)


class RealEstateOfficeTest(TestCase):
    """اختبارات نظام المكاتب العقارية"""
    
    def test_office_creation(self):
        """اختبار إنشاء مكتب عقاري"""
        office = RealEstateOffice.objects.create(
            name="مكتب العقارات الممتازة",
            license_number="LIC-12345",
            contact_person="أحمد محمد",
            phone="99123456",
            email="office@test.com",
            address="مسقط، عمان",
            commission_rate=Decimal("5.00")
        )
        
        self.assertEqual(office.name, "مكتب العقارات الممتازة")
        self.assertEqual(office.commission_rate, Decimal("5.00"))
    
    def test_building_owner_creation(self):
        """اختبار إنشاء مالك مبنى"""
        owner = BuildingOwner.objects.create(
            name="محمد علي",
            owner_type="individual",
            phone="99123456",
            email="owner@test.com",
            national_id="12345678"
        )
        
        self.assertEqual(owner.name, "محمد علي")
        self.assertEqual(owner.owner_type, "individual")

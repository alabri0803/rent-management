"""
Tests for Dashboard Forms

يختبر جميع النماذج في تطبيق dashboard
"""
from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from dashboard.models import Building, Unit, Tenant, Lease
from dashboard.forms import (
    BuildingForm, UnitForm, TenantForm, LeaseForm, PaymentForm
)


class BuildingFormTest(TestCase):
    """اختبارات نموذج المبنى"""
    
    def test_valid_building_form(self):
        """اختبار نموذج مبنى صحيح"""
        form_data = {
            'name': 'مبنى الاختبار',
            'address': 'شارع الاختبار، مسقط'
        }
        form = BuildingForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_building_form_missing_name(self):
        """اختبار نموذج مبنى بدون اسم"""
        form_data = {
            'address': 'شارع الاختبار'
        }
        form = BuildingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_building_form_save(self):
        """اختبار حفظ نموذج المبنى"""
        form_data = {
            'name': 'مبنى جديد',
            'address': 'عنوان جديد'
        }
        form = BuildingForm(data=form_data)
        if form.is_valid():
            building = form.save()
            self.assertEqual(building.name, 'مبنى جديد')


class UnitFormTest(TestCase):
    """اختبارات نموذج الوحدة"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.building = Building.objects.create(
            name="مبنى الاختبار",
            address="شارع الاختبار"
        )
    
    def test_valid_unit_form(self):
        """اختبار نموذج وحدة صحيح"""
        form_data = {
            'building': self.building.id,
            'number': '101',
            'floor': 1,
            'unit_type': 'apartment',
            'is_available': True
        }
        form = UnitForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_unit_form_missing_number(self):
        """اختبار نموذج وحدة بدون رقم"""
        form_data = {
            'building': self.building.id,
            'floor': 1,
            'unit_type': 'apartment'
        }
        form = UnitForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('number', form.errors)
    
    def test_unit_form_invalid_type(self):
        """اختبار نموذج وحدة بنوع غير صحيح"""
        form_data = {
            'building': self.building.id,
            'number': '101',
            'floor': 1,
            'unit_type': 'invalid_type'
        }
        form = UnitForm(data=form_data)
        self.assertFalse(form.is_valid())


class TenantFormTest(TestCase):
    """اختبارات نموذج المستأجر"""
    
    def test_valid_tenant_form(self):
        """اختبار نموذج مستأجر صحيح"""
        form_data = {
            'name': 'أحمد محمد',
            'tenant_type': 'sole_proprietorship',
            'phone': '+96899123456',
            'email': 'ahmed@example.com'
        }
        form = TenantForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_tenant_form_missing_name(self):
        """اختبار نموذج مستأجر بدون اسم"""
        form_data = {
            'tenant_type': 'sole_proprietorship',
            'phone': '+96899123456'
        }
        form = TenantForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_tenant_form_invalid_email(self):
        """اختبار نموذج مستأجر ببريد إلكتروني غير صحيح"""
        form_data = {
            'name': 'أحمد محمد',
            'tenant_type': 'sole_proprietorship',
            'email': 'invalid-email'
        }
        form = TenantForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class LeaseFormTest(TestCase):
    """اختبارات نموذج العقد"""
    
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
    
    def test_valid_lease_form(self):
        """اختبار نموذج عقد صحيح"""
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=365)
        
        form_data = {
            'unit': self.unit.id,
            'tenant': self.tenant.id,
            'start_date': start_date,
            'end_date': end_date,
            'monthly_rent': '500.00',
            'status': 'active'
        }
        form = LeaseForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_lease_form_end_before_start(self):
        """اختبار نموذج عقد بتاريخ انتهاء قبل البداية"""
        start_date = timezone.now().date()
        end_date = start_date - timedelta(days=10)
        
        form_data = {
            'unit': self.unit.id,
            'tenant': self.tenant.id,
            'start_date': start_date,
            'end_date': end_date,
            'monthly_rent': '500.00',
            'status': 'active'
        }
        form = LeaseForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_lease_form_negative_rent(self):
        """اختبار نموذج عقد بإيجار سالب"""
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=365)
        
        form_data = {
            'unit': self.unit.id,
            'tenant': self.tenant.id,
            'start_date': start_date,
            'end_date': end_date,
            'monthly_rent': '-500.00',
            'status': 'active'
        }
        form = LeaseForm(data=form_data)
        self.assertFalse(form.is_valid())


class PaymentFormTest(TestCase):
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
    
    def test_valid_payment_form(self):
        """اختبار نموذج دفعة صحيح"""
        form_data = {
            'lease': self.lease.id,
            'amount': '500.00',
            'payment_date': timezone.now().date(),
            'payment_method': 'cash',
            'month': timezone.now().month,
            'year': timezone.now().year
        }
        form = PaymentForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_payment_form_negative_amount(self):
        """اختبار نموذج دفعة بمبلغ سالب"""
        form_data = {
            'lease': self.lease.id,
            'amount': '-500.00',
            'payment_date': timezone.now().date(),
            'payment_method': 'cash',
            'month': timezone.now().month,
            'year': timezone.now().year
        }
        form = PaymentForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_payment_form_zero_amount(self):
        """اختبار نموذج دفعة بمبلغ صفر"""
        form_data = {
            'lease': self.lease.id,
            'amount': '0.00',
            'payment_date': timezone.now().date(),
            'payment_method': 'cash',
            'month': timezone.now().month,
            'year': timezone.now().year
        }
        form = PaymentForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_payment_form_invalid_month(self):
        """اختبار نموذج دفعة بشهر غير صحيح"""
        form_data = {
            'lease': self.lease.id,
            'amount': '500.00',
            'payment_date': timezone.now().date(),
            'payment_method': 'cash',
            'month': 13,  # شهر غير صحيح
            'year': timezone.now().year
        }
        form = PaymentForm(data=form_data)
        self.assertFalse(form.is_valid())


class FormValidationTest(TestCase):
    """اختبارات التحقق من صحة النماذج"""
    
    def test_required_fields(self):
        """اختبار الحقول المطلوبة"""
        form = BuildingForm(data={})
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) > 0)
    
    def test_field_max_length(self):
        """اختبار الحد الأقصى لطول الحقل"""
        form_data = {
            'name': 'أ' * 300,  # اسم طويل جداً
            'address': 'عنوان'
        }
        form = BuildingForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_clean_methods(self):
        """اختبار دوال التنظيف المخصصة"""
        # يمكن إضافة اختبارات لدوال clean المخصصة هنا
        pass


# تشغيل الاختبارات:
# python manage.py test dashboard.tests.test_forms

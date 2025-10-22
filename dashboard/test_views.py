"""
اختبارات شاملة لـ Views نظام إدارة الإيجارات
Tests for Rent Management System Views
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from dashboard.models import (
    Building, Unit, Tenant, Lease, Payment,
    UserProfile, Expense, Invoice
)


class DashboardViewsTest(TestCase):
    """اختبارات صفحات لوحة التحكم"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            can_view_dashboard=True
        )
    
    def test_dashboard_home_requires_login(self):
        """اختبار أن لوحة التحكم تتطلب تسجيل الدخول"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_home_with_login(self):
        """اختبار الوصول للوحة التحكم بعد تسجيل الدخول"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'لوحة التحكم')
    
    def test_dashboard_home_without_permission(self):
        """اختبار الوصول بدون صلاحية"""
        # إزالة صلاحية عرض لوحة التحكم
        self.profile.can_view_dashboard = False
        self.profile.save()
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 403)  # Forbidden


class BuildingViewsTest(TestCase):
    """اختبارات صفحات المباني"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            can_view_buildings=True,
            can_manage_buildings=True
        )
        self.building = Building.objects.create(
            name="مبنى الاختبار",
            address="شارع الاختبار",
            total_units=10
        )
    
    def test_building_list_view(self):
        """اختبار صفحة قائمة المباني"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('building_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'مبنى الاختبار')
    
    def test_building_create_view_get(self):
        """اختبار عرض نموذج إضافة مبنى"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('building_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_building_create_view_post(self):
        """اختبار إضافة مبنى جديد"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': 'مبنى جديد',
            'address': 'عنوان جديد',
            'total_units': 5
        }
        response = self.client.post(reverse('building_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Building.objects.filter(name='مبنى جديد').exists())
    
    def test_building_update_view(self):
        """اختبار تحديث مبنى"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': 'مبنى محدث',
            'address': 'عنوان محدث',
            'total_units': 15
        }
        response = self.client.post(
            reverse('building_update', kwargs={'pk': self.building.pk}),
            data
        )
        self.building.refresh_from_db()
        self.assertEqual(self.building.name, 'مبنى محدث')
    
    def test_building_delete_view(self):
        """اختبار حذف مبنى"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('building_delete', kwargs={'pk': self.building.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Building.objects.filter(pk=self.building.pk).exists())


class LeaseViewsTest(TestCase):
    """اختبارات صفحات العقود"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            can_view_leases=True,
            can_manage_leases=True
        )
        
        # إنشاء بيانات اختبار
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
            status="active"
        )
    
    def test_lease_list_view(self):
        """اختبار صفحة قائمة العقود"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('lease_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lease.contract_number)
    
    def test_lease_detail_view(self):
        """اختبار صفحة تفاصيل العقد"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('lease_detail', kwargs={'pk': self.lease.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lease.contract_number)
        self.assertContains(response, self.tenant.name)
    
    def test_lease_create_view(self):
        """اختبار إنشاء عقد جديد"""
        self.client.login(username='testuser', password='testpass123')
        
        # إنشاء وحدة جديدة
        unit2 = Unit.objects.create(
            building=self.unit.building,
            unit_number="102",
            unit_type="apartment",
            rent_amount=Decimal("600.00")
        )
        
        data = {
            'unit': unit2.pk,
            'tenant': self.tenant.pk,
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=365),
            'monthly_rent': '600.00',
            'deposit_amount': '600.00',
            'status': 'active'
        }
        response = self.client.post(reverse('lease_create'), data)
        self.assertEqual(response.status_code, 302)


class PaymentViewsTest(TestCase):
    """اختبارات صفحات الدفعات"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            can_view_payments=True,
            can_manage_payments=True
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
    
    def test_payment_list_view(self):
        """اختبار صفحة قائمة الدفعات"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('payment_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_payment_create_view(self):
        """اختبار إضافة دفعة جديدة"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'lease': self.lease.pk,
            'amount': '500.00',
            'payment_date': timezone.now().date(),
            'payment_for_month': (timezone.now().month % 12) + 1,
            'payment_for_year': timezone.now().year,
            'payment_method': 'cash'
        }
        response = self.client.post(reverse('payment_create'), data)
        self.assertEqual(response.status_code, 302)
    
    def test_quick_payment_create(self):
        """اختبار الدفع السريع"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'month': timezone.now().month,
            'year': timezone.now().year,
            'payment_type': 'full',
            'payment_method': 'cash',
            'notes': 'دفع سريع'
        }
        response = self.client.post(
            reverse('quick_payment_create', kwargs={'lease_id': self.lease.pk}),
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)


class TenantViewsTest(TestCase):
    """اختبارات صفحات المستأجرين"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            can_view_tenants=True,
            can_manage_tenants=True
        )
        self.tenant = Tenant.objects.create(
            name="مستأجر الاختبار",
            phone="99999999",
            email="test@test.com",
            tenant_type="sole_proprietorship"
        )
    
    def test_tenant_list_view(self):
        """اختبار صفحة قائمة المستأجرين"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('tenant_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'مستأجر الاختبار')
    
    def test_tenant_detail_view(self):
        """اختبار صفحة تفاصيل المستأجر"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('tenant_detail', kwargs={'pk': self.tenant.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tenant.name)
    
    def test_tenant_create_view(self):
        """اختبار إضافة مستأجر جديد"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': 'مستأجر جديد',
            'phone': '99888777',
            'email': 'new@test.com',
            'tenant_type': 'limited_liability'
        }
        response = self.client.post(reverse('tenant_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Tenant.objects.filter(name='مستأجر جديد').exists())


class ExpenseViewsTest(TestCase):
    """اختبارات صفحات المصروفات"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            can_view_expenses=True,
            can_manage_expenses=True
        )
        self.building = Building.objects.create(
            name="مبنى",
            address="عنوان",
            total_units=5
        )
        self.expense = Expense.objects.create(
            building=self.building,
            category="maintenance",
            description="صيانة",
            amount=Decimal("200.00"),
            expense_date=timezone.now().date()
        )
    
    def test_expense_list_view(self):
        """اختبار صفحة قائمة المصروفات"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('expense_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_expense_create_view(self):
        """اختبار إضافة مصروف جديد"""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'building': self.building.pk,
            'category': 'utilities',
            'description': 'فاتورة كهرباء',
            'amount': '150.00',
            'expense_date': timezone.now().date()
        }
        response = self.client.post(reverse('expense_create'), data)
        self.assertEqual(response.status_code, 302)


class ReportViewsTest(TestCase):
    """اختبارات صفحات التقارير"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            can_view_reports=True
        )
        
        # إنشاء بيانات للتقارير
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
    
    def test_report_selection_view(self):
        """اختبار صفحة اختيار التقارير"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('report_selection'))
        self.assertEqual(response.status_code, 200)
    
    def test_tenant_statement_view(self):
        """اختبار كشف حساب المستأجر"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('report_tenant_statement', kwargs={'lease_id': self.lease.pk})
        )
        self.assertEqual(response.status_code, 200)


class UserManagementViewsTest(TestCase):
    """اختبارات صفحات إدارة المستخدمين"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@test.com'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            can_manage_users=True
        )
    
    def test_user_management_view(self):
        """اختبار صفحة إدارة المستخدمين"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('user_management'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_permissions_view(self):
        """اختبار صفحة صلاحيات المستخدم"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(
            reverse('user_permissions', kwargs={'user_id': self.admin_user.pk})
        )
        self.assertEqual(response.status_code, 200)

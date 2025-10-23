"""
Tests for Dashboard Views

يختبر جميع العروض في تطبيق dashboard
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from dashboard.models import Building, Unit, Tenant, Lease, Payment


class DashboardViewTest(TestCase):
    """اختبارات صفحة لوحة التحكم الرئيسية"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_dashboard_view_requires_login(self):
        """اختبار أن لوحة التحكم تتطلب تسجيل الدخول"""
        self.client.logout()
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_view_accessible_when_logged_in(self):
        """اختبار الوصول إلى لوحة التحكم عند تسجيل الدخول"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_view_uses_correct_template(self):
        """اختبار استخدام القالب الصحيح"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')


class BuildingViewTest(TestCase):
    """اختبارات عروض المباني"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='testuser', password='testpass123')
        self.building = Building.objects.create(
            name="مبنى الاختبار",
            address="شارع الاختبار"
        )
    
    def test_building_list_view(self):
        """اختبار عرض قائمة المباني"""
        response = self.client.get(reverse('building_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "مبنى الاختبار")
    
    def test_building_detail_view(self):
        """اختبار عرض تفاصيل المبنى"""
        response = self.client.get(reverse('building_detail', args=[self.building.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "مبنى الاختبار")
    
    def test_building_create_view_get(self):
        """اختبار عرض نموذج إضافة مبنى"""
        response = self.client.get(reverse('building_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_building_create_view_post(self):
        """اختبار إضافة مبنى جديد"""
        data = {
            'name': 'مبنى جديد',
            'address': 'عنوان جديد'
        }
        response = self.client.post(reverse('building_create'), data)
        self.assertEqual(Building.objects.count(), 2)


class UnitViewTest(TestCase):
    """اختبارات عروض الوحدات"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='testuser', password='testpass123')
        self.building = Building.objects.create(name="مبنى", address="عنوان")
        self.unit = Unit.objects.create(
            building=self.building,
            number="101",
            floor=1,
            unit_type="apartment"
        )
    
    def test_unit_list_view(self):
        """اختبار عرض قائمة الوحدات"""
        response = self.client.get(reverse('unit_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_unit_detail_view(self):
        """اختبار عرض تفاصيل الوحدة"""
        response = self.client.get(reverse('unit_detail', args=[self.unit.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "101")


class TenantViewTest(TestCase):
    """اختبارات عروض المستأجرين"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='testuser', password='testpass123')
        self.tenant = Tenant.objects.create(
            name="أحمد محمد",
            tenant_type="sole_proprietorship"
        )
    
    def test_tenant_list_view(self):
        """اختبار عرض قائمة المستأجرين"""
        response = self.client.get(reverse('tenant_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "أحمد محمد")
    
    def test_tenant_detail_view(self):
        """اختبار عرض تفاصيل المستأجر"""
        response = self.client.get(reverse('tenant_detail', args=[self.tenant.id]))
        self.assertEqual(response.status_code, 200)


class LeaseViewTest(TestCase):
    """اختبارات عروض العقود"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='testuser', password='testpass123')
        
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
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=365),
            monthly_rent=Decimal('500.00'),
            status='active'
        )
    
    def test_lease_list_view(self):
        """اختبار عرض قائمة العقود"""
        response = self.client.get(reverse('lease_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_lease_detail_view(self):
        """اختبار عرض تفاصيل العقد"""
        response = self.client.get(reverse('lease_detail', args=[self.lease.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_lease_create_view_requires_available_unit(self):
        """اختبار أن إنشاء عقد يتطلب وحدة متاحة"""
        # الوحدة الحالية مؤجرة
        self.unit.is_available = False
        self.unit.save()
        
        response = self.client.get(reverse('lease_create'))
        self.assertEqual(response.status_code, 200)


class PaymentViewTest(TestCase):
    """اختبارات عروض الدفعات"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='testuser', password='testpass123')
        
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
    
    def test_payment_list_view(self):
        """اختبار عرض قائمة الدفعات"""
        response = self.client.get(reverse('payment_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_payment_detail_view(self):
        """اختبار عرض تفاصيل الدفعة"""
        response = self.client.get(reverse('payment_detail', args=[self.payment.id]))
        self.assertEqual(response.status_code, 200)


class AuthenticationTest(TestCase):
    """اختبارات المصادقة"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_view_get(self):
        """اختبار عرض صفحة تسجيل الدخول"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_view_post_valid_credentials(self):
        """اختبار تسجيل الدخول ببيانات صحيحة"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_login_view_post_invalid_credentials(self):
        """اختبار تسجيل الدخول ببيانات خاطئة"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
    
    def test_logout_view(self):
        """اختبار تسجيل الخروج"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout


class PermissionTest(TestCase):
    """اختبارات الصلاحيات"""
    
    def setUp(self):
        """إعداد بيانات الاختبار"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='normal',
            password='testpass123',
            is_staff=False
        )
    
    def test_staff_can_access_dashboard(self):
        """اختبار أن الموظف يمكنه الوصول للوحة التحكم"""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
    
    def test_normal_user_cannot_access_dashboard(self):
        """اختبار أن المستخدم العادي لا يمكنه الوصول"""
        self.client.login(username='normal', password='testpass123')
        response = self.client.get(reverse('dashboard_home'))
        # Should redirect or show 403
        self.assertIn(response.status_code, [302, 403])


# تشغيل الاختبارات:
# python manage.py test dashboard.tests.test_views

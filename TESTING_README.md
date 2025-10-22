# دليل الاختبارات الشامل - نظام إدارة الإيجارات
# Comprehensive Testing Guide - Rent Management System

## 📋 نظرة عامة | Overview

تم إنشاء نظام اختبارات شامل لضمان جودة وموثوقية نظام إدارة الإيجارات. يغطي النظام جميع المكونات الرئيسية من Models و Views و Signals والحسابات المالية.

A comprehensive testing system has been created to ensure the quality and reliability of the Rent Management System. The system covers all major components including Models, Views, Signals, and Financial Calculations.

---

## 📁 هيكل ملفات الاختبار | Test Files Structure

```
dashboard/
├── test_models.py          # اختبارات النماذج | Model Tests
├── test_views.py           # اختبارات العروض | View Tests
├── test_signals.py         # اختبارات الإشارات | Signal Tests
└── tests.py               # ملف الاختبارات الأساسي | Base test file

pytest.ini                  # تكوين pytest | pytest configuration
```

---

## 🧪 أنواع الاختبارات | Test Types

### 1. اختبارات Models (test_models.py)

**الفئات المختبرة:**
- `BuildingModelTest` - اختبارات المباني
- `UnitModelTest` - اختبارات الوحدات
- `TenantModelTest` - اختبارات المستأجرين
- `LeaseModelTest` - اختبارات العقود
- `PaymentModelTest` - اختبارات الدفعات
- `ExpenseModelTest` - اختبارات المصروفات
- `InvoiceModelTest` - اختبارات الفواتير
- `UserProfileModelTest` - اختبارات ملفات المستخدمين
- `PaymentOverdueNoticeTest` - اختبارات الإنذارات
- `RealEstateOfficeTest` - اختبارات المكاتب العقارية

**الاختبارات الرئيسية:**
- ✅ إنشاء الكائنات
- ✅ التحقق من الحقول
- ✅ العلاقات بين النماذج
- ✅ الدوال المخصصة
- ✅ التحقق من الصحة

### 2. اختبارات Views (test_views.py)

**الفئات المختبرة:**
- `DashboardViewsTest` - اختبارات لوحة التحكم
- `BuildingViewsTest` - اختبارات صفحات المباني
- `LeaseViewsTest` - اختبارات صفحات العقود
- `PaymentViewsTest` - اختبارات صفحات الدفعات
- `TenantViewsTest` - اختبارات صفحات المستأجرين
- `ExpenseViewsTest` - اختبارات صفحات المصروفات
- `ReportViewsTest` - اختبارات صفحات التقارير
- `UserManagementViewsTest` - اختبارات إدارة المستخدمين

**الاختبارات الرئيسية:**
- ✅ التحقق من الصلاحيات
- ✅ عرض القوائم
- ✅ إنشاء السجلات
- ✅ تحديث السجلات
- ✅ حذف السجلات
- ✅ الدفع السريع

### 3. اختبارات Signals (test_signals.py)

**الفئات المختبرة:**
- `PaymentSignalsTest` - اختبارات إشارات الدفعات
- `LeaseSignalsTest` - اختبارات إشارات العقود
- `NotificationSignalsTest` - اختبارات إشارات الإشعارات
- `OverdueNoticeGenerationTest` - اختبارات توليد الإنذارات
- `FinancialCalculationTest` - اختبارات الحسابات المالية

**الاختبارات الرئيسية:**
- ✅ إنشاء الإشعارات التلقائية
- ✅ تحديث الإنذارات عند الدفع
- ✅ الدفع الكامل والجزئي
- ✅ حل الإنذارات
- ✅ توليد أرقام العقود
- ✅ الحسابات المالية

---

## 🚀 تشغيل الاختبارات | Running Tests

### تثبيت المتطلبات | Install Requirements

```bash
pip install pytest pytest-django
```

### تشغيل جميع الاختبارات | Run All Tests

```bash
# باستخدام pytest
pytest

# باستخدام Django
python manage.py test dashboard
```

### تشغيل اختبارات محددة | Run Specific Tests

```bash
# اختبارات Models فقط
pytest dashboard/test_models.py

# اختبارات Views فقط
pytest dashboard/test_views.py

# اختبارات Signals فقط
pytest dashboard/test_signals.py

# اختبار فئة محددة
pytest dashboard/test_models.py::BuildingModelTest

# اختبار دالة محددة
pytest dashboard/test_models.py::BuildingModelTest::test_building_creation
```

### تشغيل الاختبارات بالعلامات | Run Tests by Markers

```bash
# اختبارات Models فقط
pytest -m models

# اختبارات Views فقط
pytest -m views

# اختبارات Signals فقط
pytest -m signals

# اختبارات الصلاحيات
pytest -m permissions

# اختبارات الحسابات المالية
pytest -m financial
```

### تشغيل مع تقرير التغطية | Run with Coverage Report

```bash
# تشغيل مع تغطية
pytest --cov=dashboard --cov-report=html

# عرض التقرير
open htmlcov/index.html
```

---

## 📊 تقارير الاختبارات | Test Reports

### تقرير مفصل | Detailed Report

```bash
pytest -v
```

### تقرير مختصر | Summary Report

```bash
pytest -q
```

### تقرير مع الأخطاء فقط | Report with Failures Only

```bash
pytest --tb=short
```

### إيقاف عند أول خطأ | Stop at First Failure

```bash
pytest -x
```

---

## 🎯 أفضل الممارسات | Best Practices

### 1. تنظيم الاختبارات | Test Organization

- **فصل الاختبارات حسب النوع**: Models, Views, Signals
- **استخدام setUp و tearDown**: لإعداد البيانات
- **تسمية واضحة**: `test_<what_is_being_tested>`

### 2. كتابة الاختبارات | Writing Tests

```python
def test_something(self):
    """وصف واضح للاختبار | Clear test description"""
    # Arrange - إعداد البيانات
    data = create_test_data()
    
    # Act - تنفيذ الإجراء
    result = perform_action(data)
    
    # Assert - التحقق من النتيجة
    self.assertEqual(result, expected_value)
```

### 3. استخدام Fixtures

```python
@pytest.fixture
def sample_building():
    """إنشاء مبنى للاختبار"""
    return Building.objects.create(
        name="مبنى الاختبار",
        address="عنوان الاختبار",
        total_units=10
    )
```

### 4. اختبار الحالات الحدية | Edge Cases

- ✅ قيم فارغة | Empty values
- ✅ قيم null
- ✅ قيم سالبة | Negative values
- ✅ قيم كبيرة جداً | Very large values
- ✅ سلاسل نصية طويلة | Long strings

---

## 🔍 أمثلة الاختبارات | Test Examples

### مثال 1: اختبار إنشاء مبنى | Building Creation Test

```python
def test_building_creation(self):
    """اختبار إنشاء مبنى"""
    building = Building.objects.create(
        name="مبنى الاختبار",
        address="شارع الاختبار",
        total_units=10
    )
    self.assertEqual(building.name, "مبنى الاختبار")
    self.assertEqual(building.total_units, 10)
```

### مثال 2: اختبار الصلاحيات | Permission Test

```python
def test_dashboard_requires_permission(self):
    """اختبار أن لوحة التحكم تتطلب صلاحية"""
    self.client.login(username='testuser', password='testpass123')
    response = self.client.get(reverse('dashboard_home'))
    
    if not self.user.profile.can_view_dashboard:
        self.assertEqual(response.status_code, 403)
```

### مثال 3: اختبار Signal | Signal Test

```python
def test_payment_creates_notification(self):
    """اختبار إنشاء إشعار عند الدفع"""
    initial_count = Notification.objects.count()
    
    Payment.objects.create(
        lease=self.lease,
        amount=Decimal("500.00"),
        payment_date=timezone.now().date(),
        payment_method="cash"
    )
    
    self.assertGreater(Notification.objects.count(), initial_count)
```

---

## 📈 تغطية الاختبارات | Test Coverage

### الهدف | Target

- **Models**: 90%+ تغطية
- **Views**: 80%+ تغطية
- **Signals**: 85%+ تغطية
- **Forms**: 75%+ تغطية

### قياس التغطية | Measure Coverage

```bash
pytest --cov=dashboard --cov-report=term-missing
```

---

## 🐛 تصحيح الأخطاء | Debugging Tests

### استخدام pdb

```python
def test_something(self):
    import pdb; pdb.set_trace()
    # الكود هنا
```

### طباعة المعلومات | Print Information

```python
def test_something(self):
    print(f"القيمة: {value}")
    self.assertEqual(value, expected)
```

### تشغيل اختبار واحد مع التفاصيل | Run Single Test with Details

```bash
pytest -vv dashboard/test_models.py::BuildingModelTest::test_building_creation
```

---

## 📝 قائمة التحقق | Checklist

قبل الدفع للإنتاج | Before Pushing to Production:

- [ ] جميع الاختبارات تعمل بنجاح
- [ ] التغطية أكثر من 80%
- [ ] لا توجد تحذيرات
- [ ] الاختبارات سريعة (< 5 دقائق)
- [ ] تم اختبار الحالات الحدية
- [ ] تم اختبار الصلاحيات
- [ ] تم اختبار Signals
- [ ] تم اختبار الحسابات المالية

---

## 🔧 استكشاف الأخطاء | Troubleshooting

### مشكلة: الاختبارات بطيئة | Tests are Slow

**الحل:**
```bash
# استخدام قاعدة بيانات في الذاكرة
# في settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
```

### مشكلة: فشل الاختبارات بشكل عشوائي | Tests Fail Randomly

**الحل:**
- تحقق من ترتيب الاختبارات
- استخدم `setUp` و `tearDown` بشكل صحيح
- تجنب الاعتماد على حالة مشتركة

### مشكلة: أخطاء الاستيراد | Import Errors

**الحل:**
```bash
# تأكد من تثبيت جميع المتطلبات
pip install -r requirements.txt

# تأكد من PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/project"
```

---

## 📚 موارد إضافية | Additional Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Django Documentation](https://pytest-django.readthedocs.io/)

---

## 🎉 الخلاصة | Summary

تم إنشاء نظام اختبارات شامل يغطي:

✅ **اختبارات Models** - 10 فئات اختبار
✅ **اختبارات Views** - 8 فئات اختبار
✅ **اختبارات Signals** - 5 فئات اختبار
✅ **تكوين pytest** - ملف pytest.ini كامل
✅ **توثيق شامل** - دليل الاستخدام

**إجمالي الاختبارات**: 50+ اختبار شامل

النظام جاهز للاستخدام ويضمن جودة وموثوقية التطبيق! 🚀

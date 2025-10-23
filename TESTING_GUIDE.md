# 🧪 دليل الاختبارات الشامل

## 📋 نظرة عامة

تم إنشاء مجموعة شاملة من الاختبارات لضمان جودة وموثوقية نظام إدارة الإيجارات.

---

## 📁 هيكل الاختبارات

```
dashboard/tests/
├── __init__.py
├── test_models.py      # اختبارات النماذج (10 فئات)
├── test_views.py       # اختبارات العروض (8 فئات)
├── test_forms.py       # اختبارات النماذج (6 فئات)
└── test_signals.py     # اختبارات الإشارات (6 فئات)
```

**الإجمالي:** 30 فئة اختبار

---

## 🧪 test_models.py

### الفئات المختبرة:

#### 1. BuildingModelTest
- ✅ إنشاء مبنى
- ✅ تمثيل النص
- ✅ عدد الوحدات

#### 2. UnitModelTest
- ✅ إنشاء وحدة
- ✅ تمثيل النص
- ✅ حالة التوفر

#### 3. TenantModelTest
- ✅ إنشاء مستأجر
- ✅ تمثيل النص
- ✅ التحقق من البريد الإلكتروني

#### 4. LeaseModelTest
- ✅ إنشاء عقد
- ✅ مدة العقد
- ✅ حساب الإيجار السنوي
- ✅ الأيام المتبقية

#### 5. PaymentModelTest
- ✅ إنشاء دفعة
- ✅ تمثيل النص
- ✅ العلاقة مع العقد

#### 6. SecurityDepositModelTest
- ✅ إنشاء ضمان
- ✅ خيارات الحالة

#### 7. ExpenseModelTest
- ✅ إنشاء مصروف
- ✅ تمثيل النص

#### 8. NotificationModelTest
- ✅ إنشاء إشعار
- ✅ تعليم كمقروء
- ✅ تمثيل النص

#### 9. PaymentOverdueNoticeModelTest
- ✅ إنشاء إنذار
- ✅ الموعد النهائي القانوني
- ✅ تغيير الحالة

### تشغيل الاختبارات:
```bash
python manage.py test dashboard.tests.test_models
```

---

## 🌐 test_views.py

### الفئات المختبرة:

#### 1. DashboardViewTest
- ✅ يتطلب تسجيل الدخول
- ✅ الوصول عند تسجيل الدخول
- ✅ استخدام القالب الصحيح

#### 2. BuildingViewTest
- ✅ عرض قائمة المباني
- ✅ عرض تفاصيل المبنى
- ✅ نموذج إضافة مبنى (GET)
- ✅ إضافة مبنى جديد (POST)

#### 3. UnitViewTest
- ✅ عرض قائمة الوحدات
- ✅ عرض تفاصيل الوحدة

#### 4. TenantViewTest
- ✅ عرض قائمة المستأجرين
- ✅ عرض تفاصيل المستأجر

#### 5. LeaseViewTest
- ✅ عرض قائمة العقود
- ✅ عرض تفاصيل العقد
- ✅ إنشاء عقد يتطلب وحدة متاحة

#### 6. PaymentViewTest
- ✅ عرض قائمة الدفعات
- ✅ عرض تفاصيل الدفعة

#### 7. AuthenticationTest
- ✅ عرض صفحة تسجيل الدخول
- ✅ تسجيل دخول ببيانات صحيحة
- ✅ تسجيل دخول ببيانات خاطئة
- ✅ تسجيل الخروج

#### 8. PermissionTest
- ✅ الموظف يمكنه الوصول
- ✅ المستخدم العادي لا يمكنه الوصول

### تشغيل الاختبارات:
```bash
python manage.py test dashboard.tests.test_views
```

---

## 📝 test_forms.py

### الفئات المختبرة:

#### 1. BuildingFormTest
- ✅ نموذج صحيح
- ✅ نموذج بدون اسم
- ✅ حفظ النموذج

#### 2. UnitFormTest
- ✅ نموذج صحيح
- ✅ نموذج بدون رقم
- ✅ نموذج بنوع غير صحيح

#### 3. TenantFormTest
- ✅ نموذج صحيح
- ✅ نموذج بدون اسم
- ✅ نموذج ببريد إلكتروني غير صحيح

#### 4. LeaseFormTest
- ✅ نموذج صحيح
- ✅ تاريخ انتهاء قبل البداية
- ✅ إيجار سالب

#### 5. PaymentFormTest
- ✅ نموذج صحيح
- ✅ مبلغ سالب
- ✅ مبلغ صفر
- ✅ شهر غير صحيح

#### 6. FormValidationTest
- ✅ الحقول المطلوبة
- ✅ الحد الأقصى لطول الحقل
- ✅ دوال التنظيف المخصصة

### تشغيل الاختبارات:
```bash
python manage.py test dashboard.tests.test_forms
```

---

## 🔔 test_signals.py

### الفئات المختبرة:

#### 1. PaymentSignalTest
- ✅ إنشاء إشعار عند الدفع
- ✅ تحديث الإنذار عند الدفع

#### 2. LeaseSignalTest
- ✅ تحديث توفر الوحدة عند إنشاء عقد
- ✅ تحديث توفر الوحدة عند إلغاء عقد

#### 3. UserProfileSignalTest
- ✅ إنشاء ملف مستخدم تلقائياً

#### 4. NotificationSignalTest
- ✅ إنشاء إشعارات للأحداث المهمة

#### 5. OverdueNoticeSignalTest
- ✅ إنشاء إشعار عند تغيير حالة الإنذار

#### 6. SignalIntegrationTest
- ✅ سير عمل كامل للعقد والدفعات

### تشغيل الاختبارات:
```bash
python manage.py test dashboard.tests.test_signals
```

---

## 🚀 تشغيل جميع الاختبارات

### تشغيل كل اختبارات dashboard:
```bash
python manage.py test dashboard.tests
```

### تشغيل اختبارات محددة:
```bash
# اختبار فئة واحدة
python manage.py test dashboard.tests.test_models.BuildingModelTest

# اختبار دالة واحدة
python manage.py test dashboard.tests.test_models.BuildingModelTest.test_building_creation
```

### مع تفاصيل أكثر:
```bash
python manage.py test dashboard.tests --verbosity=2
```

### مع تقرير التغطية:
```bash
# تثبيت coverage
pip install coverage

# تشغيل الاختبارات مع التغطية
coverage run --source='dashboard' manage.py test dashboard.tests
coverage report
coverage html
```

---

## 📊 إحصائيات الاختبارات

### العدد الإجمالي:
- **30** فئة اختبار
- **~80** اختبار فردي
- **4** ملفات اختبار

### التغطية المتوقعة:
- **Models:** ~70%
- **Views:** ~60%
- **Forms:** ~65%
- **Signals:** ~50%

**الهدف:** الوصول إلى 80%+ تغطية

---

## ✅ أفضل الممارسات

### 1. تسمية الاختبارات
```python
def test_<what_is_being_tested>_<expected_result>(self):
    """وصف واضح للاختبار"""
    pass
```

### 2. استخدام setUp و tearDown
```python
def setUp(self):
    """إعداد بيانات الاختبار"""
    self.user = User.objects.create_user(...)

def tearDown(self):
    """تنظيف بعد الاختبار"""
    pass
```

### 3. الاختبارات المستقلة
- كل اختبار يجب أن يعمل بشكل مستقل
- لا تعتمد على ترتيب التنفيذ
- استخدم setUp لإنشاء البيانات

### 4. التأكيدات الواضحة
```python
# ✅ جيد
self.assertEqual(building.name, "مبنى الاختبار")

# ❌ سيء
self.assertTrue(building.name == "مبنى الاختبار")
```

### 5. اختبار الحالات الحدية
- قيم فارغة
- قيم سالبة
- قيم كبيرة جداً
- أنواع بيانات خاطئة

---

## 🐛 تصحيح الأخطاء

### عرض الأخطاء التفصيلية:
```bash
python manage.py test dashboard.tests --verbosity=2 --debug-mode
```

### استخدام pdb:
```python
def test_something(self):
    import pdb; pdb.set_trace()
    # الكود هنا
```

### طباعة المخرجات:
```python
def test_something(self):
    print(f"Value: {some_value}")
    self.assertEqual(...)
```

---

## 📈 تحسين الاختبارات

### الأولويات التالية:

#### 🔴 عاجل
- [ ] إضافة اختبارات للـ API endpoints
- [ ] اختبارات التكامل للـ workflows الكاملة
- [ ] اختبارات الأداء

#### 🟡 مهم
- [ ] اختبارات الأمان
- [ ] اختبارات الصلاحيات
- [ ] اختبارات الترجمة

#### 🟢 تحسين
- [ ] اختبارات الواجهة (Selenium)
- [ ] اختبارات الحمل
- [ ] اختبارات التوافق

---

## 🎯 الأهداف

### الحالية:
- ✅ إنشاء هيكل الاختبارات
- ✅ اختبارات النماذج الأساسية
- ✅ اختبارات العروض الأساسية
- ✅ اختبارات النماذج
- ✅ اختبارات الإشارات

### المستقبلية:
- [ ] الوصول إلى 80%+ تغطية
- [ ] إضافة اختبارات التكامل
- [ ] إضافة اختبارات الأداء
- [ ] إعداد CI/CD للاختبارات التلقائية

---

## 📚 موارد إضافية

### التوثيق:
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [Coverage.py](https://coverage.readthedocs.io/)

### أدوات مفيدة:
- **pytest-django:** إطار اختبار بديل
- **factory_boy:** إنشاء بيانات اختبار
- **faker:** توليد بيانات وهمية
- **selenium:** اختبارات الواجهة

---

## 🎉 الخلاصة

تم إنشاء نظام اختبارات شامل يغطي:
- ✅ **النماذج** - التحقق من منطق العمل
- ✅ **العروض** - التحقق من الوصول والعرض
- ✅ **النماذج** - التحقق من صحة البيانات
- ✅ **الإشارات** - التحقق من التكامل

**الحالة:** جاهز للاستخدام والتوسع

---

**آخر تحديث:** 23 أكتوبر 2025  
**الإصدار:** 1.0.0  
**التغطية الحالية:** ~60%  
**الهدف:** 80%+

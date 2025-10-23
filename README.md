# 🏢 نظام إدارة الإيجارات المتكامل

نظام شامل ومتقدم لإدارة العقارات والإيجارات، مصمم خصيصاً للسوق العماني مع دعم كامل للغتين العربية والإنجليزية.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-9%2F10-brightgreen.svg)](SECURITY_FIXES.md)

---

## 📋 المحتويات

- [نظرة عامة](#-نظرة-عامة)
- [المميزات الرئيسية](#-المميزات-الرئيسية)
- [التقنيات المستخدمة](#-التقنيات-المستخدمة)
- [المتطلبات](#-المتطلبات)
- [التثبيت](#-التثبيت)
- [الإعداد](#-الإعداد)
- [الاستخدام](#-الاستخدام)
- [الأمان](#-الأمان)
- [المساهمة](#-المساهمة)

---

## 🎯 نظرة عامة

نظام إدارة الإيجارات هو تطبيق ويب متكامل مبني بـ Django يوفر حلاً شاملاً لإدارة العقارات والعقود والمستأجرين والدفعات. النظام مصمم خصيصاً للسوق العماني مع التوافق الكامل مع القوانين المحلية.

### 🎨 لقطات الشاشة

*(سيتم إضافة لقطات الشاشة قريباً)*

---

## ✨ المميزات الرئيسية

### 🏗️ إدارة العقارات
- ✅ إدارة المباني والوحدات (شقق، مكاتب، محلات، مستودعات)
- ✅ تتبع حالة الوحدات (متاحة/مؤجرة)
- ✅ سجل كامل لكل وحدة

### 👥 إدارة المستأجرين
- ✅ دعم 8 أنواع من الكيانات التجارية
- ✅ معلومات شاملة للمستأجرين
- ✅ مستندات المستأجرين

### 📝 إدارة العقود
- ✅ إنشاء وتجديد وإلغاء العقود
- ✅ تتبع حالة العقود (نشط، منتهي، ملغي، مجدد)
- ✅ تنبيهات تلقائية قبل انتهاء العقد (90 يوم)
- ✅ فواتير رسوم التسجيل والتجديد
- ✅ استمارات الإلغاء والتجديد

### 💰 إدارة المدفوعات
- ✅ تسجيل الدفعات (نقداً، شيك، تحويل بنكي)
- ✅ دفع سريع من كشف الحساب
- ✅ تتبع الشيكات (مستلم، مودع، مرتجع)
- ✅ كشف حساب تفصيلي لكل عقد
- ✅ سندات قبض قابلة للطباعة

### ⚠️ نظام الإنذارات
- ✅ إنذارات تلقائية لعدم السداد (30 يوم)
- ✅ متوافق مع قوانين سلطنة عمان
- ✅ تتبع حالة الإنذارات
- ✅ تغيير سريع للحالة
- ✅ طباعة احترافية

### 📊 التقارير والتحليلات
- ✅ تقرير الربحية
- ✅ تقرير التدفقات النقدية
- ✅ تقرير معدل الإشغال
- ✅ تقرير المستأجرين المتأخرين
- ✅ تقرير العقود المنتهية
- ✅ تصدير Excel/CSV

### 🔔 نظام الإشعارات
- ✅ إشعارات داخل التطبيق
- ✅ إشعارات البريد الإلكتروني
- ✅ دعم SMS (اختياري)
- ✅ دعم WhatsApp (اختياري)

### 🔒 الأمان والصلاحيات
- ✅ نظام صلاحيات متقدم
- ✅ Audit Logging شامل
- ✅ Rate Limiting
- ✅ Two-Factor Authentication
- ✅ Security Headers
- ✅ CSRF Protection

### 🌐 دعم متعدد اللغات
- ✅ واجهة كاملة بالعربية والإنجليزية
- ✅ تبديل فوري بين اللغات
- ✅ تواريخ متكيفة مع اللغة
- ✅ تقارير ثنائية اللغة

---

## 🛠️ التقنيات المستخدمة

### Backend
- **Python 3.9+**
- **Django 5.2** - Web Framework
- **MySQL** - Database
- **Django ORM** - Database Abstraction

### Frontend
- **HTML5 & CSS3**
- **Tailwind CSS** - Styling
- **JavaScript (Vanilla)** - Interactivity
- **Flatpickr** - Date Picker
- **Charts.js** - Data Visualization (optional)

### Libraries & Tools
- **django-allauth** - Authentication
- **WeasyPrint** - PDF Generation
- **openpyxl** - Excel Export
- **python-bidi** - Arabic Text Support
- **Pillow** - Image Processing

---

## 📦 المتطلبات

### System Requirements
- Python 3.9 أو أحدث
- MySQL 5.7 أو أحدث
- 2GB RAM (minimum)
- 500MB Disk Space

### Python Packages
انظر `requirements.txt` للقائمة الكاملة

---

## 🚀 التثبيت

### 1. استنساخ المشروع

```bash
git clone https://github.com/alabri0803/rent-management.git
cd rent-management
```

### 2. إنشاء بيئة افتراضية

```bash
# إنشاء البيئة الافتراضية
python3 -m venv venv

# تفعيل البيئة
# على macOS/Linux:
source venv/bin/activate
# على Windows:
venv\Scripts\activate
```

### 3. تثبيت التبعيات

```bash
pip install -r requirements.txt
```

---

## ⚙️ الإعداد

### 1. إنشاء ملف .env

```bash
cp .env.example .env
```

### 2. توليد SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

ضع المفتاح الناتج في ملف `.env`:

```env
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=rent_management
DB_USER=your_db_user
DB_PASSWORD=your_strong_password
DB_HOST=localhost
DB_PORT=3306
```

### 3. إعداد قاعدة البيانات

```bash
# إنشاء قاعدة البيانات في MySQL
mysql -u root -p
CREATE DATABASE rent_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# تطبيق Migrations
python manage.py migrate

# إنشاء superuser
python manage.py createsuperuser
```

### 4. جمع الملفات الثابتة

```bash
python manage.py collectstatic --noinput
```

### 5. تجميع الترجمات

```bash
python manage.py compilemessages
```

---

## 🎮 الاستخدام

### تشغيل خادم التطوير

```bash
python manage.py runserver
```

افتح المتصفح على: `http://localhost:8000`

### الوصول إلى لوحة الإدارة

```
URL: http://localhost:8000/admin/
Username: (الذي أنشأته في createsuperuser)
Password: (كلمة المرور التي أنشأتها)
```

### تغيير اللغة

- اضغط على أيقونة اللغة في أعلى الصفحة
- اختر العربية أو English
- الواجهة ستتحول فوراً

---

## 🔒 الأمان

### ⚠️ مهم جداً

1. **لا ترفع ملف .env إلى Git**
   ```bash
   # تأكد من وجوده في .gitignore
   echo ".env" >> .gitignore
   ```

2. **غير SECRET_KEY في الإنتاج**
   - استخدم مفتاح فريد لكل بيئة
   - لا تستخدم المفتاح الافتراضي أبداً

3. **عطّل DEBUG في الإنتاج**
   ```env
   DEBUG=False
   ```

4. **حدد ALLOWED_HOSTS**
   ```env
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

5. **استخدم HTTPS في الإنتاج**
   ```env
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

### فحص الأمان

```bash
python manage.py check --deploy
```

للمزيد من التفاصيل، راجع [SECURITY_FIXES.md](SECURITY_FIXES.md)

---

## 📚 التوثيق

- [SECURITY_FIXES.md](SECURITY_FIXES.md) - الإصلاحات الأمنية
- [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md) - خطة التحسينات
- [PERMISSIONS_SYSTEM.md](PERMISSIONS_SYSTEM.md) - نظام الصلاحيات
- [OVERDUE_NOTICES_GUIDE.md](OVERDUE_NOTICES_GUIDE.md) - دليل الإنذارات

---

## 🤝 المساهمة

نرحب بمساهماتكم! يرجى اتباع الخطوات التالية:

1. Fork المشروع
2. إنشاء فرع للميزة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push إلى الفرع (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

### قواعد المساهمة

- اتبع أسلوب الكود الموجود
- أضف اختبارات للميزات الجديدة
- حدّث التوثيق عند الحاجة
- تأكد من نجاح جميع الاختبارات

---

## 📝 الترخيص

هذا المشروع مرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل.

---

## 👨‍💻 المطور

**alabri0803**

- GitHub: [@alabri0803](https://github.com/alabri0803)
- Project Link: [https://github.com/alabri0803/rent-management](https://github.com/alabri0803/rent-management)

---

## 🙏 شكر وتقدير

- Django Framework
- Tailwind CSS
- جميع المساهمين في المكتبات المستخدمة

---

## 📞 الدعم

إذا واجهت أي مشاكل أو لديك أسئلة:

1. افتح [Issue](https://github.com/alabri0803/rent-management/issues) جديد
2. راجع [التوثيق](IMPROVEMENT_PLAN.md)
3. تحقق من [الأسئلة الشائعة](#)

---

**آخر تحديث:** 23 أكتوبر 2025
**الإصدار:** 1.0.0
**الحالة:** قيد التطوير النشط
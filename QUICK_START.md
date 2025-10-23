# 🚀 دليل البدء السريع

**آخر تحديث:** 23 أكتوبر 2025

---

## ⚡ البدء السريع (5 دقائق)

### 1. تنظيف المشروع (اختياري)
```bash
chmod +x cleanup_project.sh
./cleanup_project.sh
```

### 2. إعداد البيئة
```bash
# نسخ ملف المثال
cp .env.example .env

# توليد SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
# انسخ الناتج وضعه في .env
```

### 3. تحرير ملف .env
```env
SECRET_KEY=YOUR_GENERATED_KEY_HERE
DB_NAME=rent_management
DB_USER=your_username
DB_PASSWORD=your_password
ALLOWED_HOSTS=localhost,127.0.0.1
DEBUG=True
```

### 4. إنشاء البيئة الافتراضية
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# أو
venv\Scripts\activate  # Windows
```

### 5. تثبيت المكتبات
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. إعداد قاعدة البيانات
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. جمع الملفات الثابتة
```bash
python manage.py collectstatic --noinput
```

### 8. تشغيل المشروع
```bash
python manage.py runserver
```

### 9. الوصول للنظام
```
http://localhost:8000/
http://localhost:8000/admin/
```

---

## 🧪 تشغيل الاختبارات

```bash
# جميع الاختبارات
python manage.py test dashboard.tests

# اختبارات محددة
python manage.py test dashboard.tests.test_models
python manage.py test dashboard.tests.test_views

# مع التغطية
coverage run --source='dashboard' manage.py test dashboard.tests
coverage report
coverage html
```

---

## 🔒 التحقق من الأمان

```bash
# فحص الإعدادات
python manage.py check

# فحص إعدادات الإنتاج
python manage.py check --deploy
```

---

## 📚 الملفات المهمة

| الملف | الوصف |
|-------|--------|
| `SETUP_INSTRUCTIONS.md` | دليل الإعداد التفصيلي |
| `SECURITY_FIXES.md` | الإصلاحات الأمنية |
| `TESTING_GUIDE.md` | دليل الاختبارات |
| `IMPLEMENTATION_REPORT.md` | تقرير التنفيذ |
| `IMPROVEMENT_PLAN.md` | خطة التحسينات |
| `cleanup_project.sh` | سكريبت التنظيف |

---

## ⚠️ ملاحظات مهمة

### ❌ لا تفعل:
- ❌ لا ترفع ملف `.env` إلى Git
- ❌ لا تستخدم `DEBUG=True` في الإنتاج
- ❌ لا تستخدم كلمات مرور ضعيفة
- ❌ لا تستخدم `ALLOWED_HOSTS=['*']`

### ✅ افعل:
- ✅ ولّد `SECRET_KEY` جديد لكل بيئة
- ✅ استخدم كلمات مرور قوية
- ✅ حدد `ALLOWED_HOSTS` بدقة
- ✅ اعمل نسخ احتياطية منتظمة

---

## 🆘 حل المشاكل الشائعة

### المشكلة: "SECRET_KEY must be set"
**الحل:** تأكد من وجود `SECRET_KEY` في ملف `.env`

### المشكلة: "DB connection failed"
**الحل:** تأكد من:
- تشغيل MySQL
- صحة بيانات الاتصال في `.env`
- وجود قاعدة البيانات

### المشكلة: "Module not found"
**الحل:** 
```bash
pip install -r requirements.txt
```

### المشكلة: "Static files not found"
**الحل:**
```bash
python manage.py collectstatic
```

---

## 📞 الدعم

راجع الملفات التالية للمساعدة:
- `SETUP_INSTRUCTIONS.md` - للإعداد
- `SECURITY_FIXES.md` - للأمان
- `TESTING_GUIDE.md` - للاختبارات
- `IMPLEMENTATION_REPORT.md` - للتقرير الشامل

---

**جاهز للعمل! 🎉**

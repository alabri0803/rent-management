# 🚀 تعليمات الإعداد السريع

## ⚠️ **مهم جداً: يجب تنفيذ هذه الخطوات قبل تشغيل المشروع**

---

## 📋 الخطوات المطلوبة

### 1. إنشاء ملف .env

```bash
# انسخ ملف المثال
cp .env.example .env
```

### 2. توليد SECRET_KEY آمن

```bash
# قم بتشغيل هذا الأمر
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

**انسخ المفتاح الناتج وضعه في ملف .env:**
```env
SECRET_KEY=YOUR_GENERATED_KEY_HERE
```

### 3. إعداد قاعدة البيانات

افتح ملف `.env` وأضف:

```env
# قاعدة البيانات
DB_NAME=rent_management
DB_USER=your_database_username
DB_PASSWORD=your_strong_password
DB_HOST=localhost
DB_PORT=3306
```

### 4. إعداد ALLOWED_HOSTS

```env
# للتطوير المحلي
ALLOWED_HOSTS=localhost,127.0.0.1

# للإنتاج (غير هذا عند النشر)
# ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 5. إعداد DEBUG

```env
# للتطوير
DEBUG=True

# للإنتاج (مهم جداً!)
# DEBUG=False
```

---

## ✅ التحقق من الإعداد

بعد إكمال الخطوات أعلاه، قم بتشغيل:

```bash
# التحقق من الإعدادات
python manage.py check

# التحقق من إعدادات الإنتاج
python manage.py check --deploy
```

---

## 🔒 قائمة التحقق الأمنية

- [ ] تم توليد SECRET_KEY جديد وآمن
- [ ] تم تعيين جميع متغيرات قاعدة البيانات
- [ ] تم تعيين ALLOWED_HOSTS
- [ ] تم التأكد من عدم رفع .env إلى git
- [ ] تم اختبار الاتصال بقاعدة البيانات

---

## 🆘 إذا واجهت مشاكل

### خطأ: "SECRET_KEY environment variable must be set"
- تأكد من إنشاء ملف `.env`
- تأكد من وجود `SECRET_KEY` في الملف
- تأكد من عدم وجود مسافات قبل أو بعد القيمة

### خطأ: "DB_NAME, DB_USER, and DB_PASSWORD must be set"
- تأكد من تعيين جميع متغيرات قاعدة البيانات
- تأكد من صحة اسم المستخدم وكلمة المرور

### خطأ في الاتصال بقاعدة البيانات
- تأكد من تشغيل MySQL
- تأكد من صحة بيانات الاتصال
- تأكد من وجود قاعدة البيانات

---

## 📚 مراجع إضافية

- راجع `SECURITY_FIXES.md` للتفاصيل الكاملة
- راجع `.env.example` لجميع المتغيرات المتاحة

---

**ملاحظة:** لن يعمل المشروع بدون إكمال هذه الخطوات!

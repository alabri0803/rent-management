# 📬 نظام الإشعارات الشامل - Comprehensive Notification System

## 🎯 نظرة عامة

تم إنشاء نظام إشعارات متقدم وشامل يدعم قنوات متعددة للتواصل مع المستخدمين والمستأجرين.

### المميزات الرئيسية:
- ✅ **5 قنوات إشعارات**: داخل التطبيق، البريد الإلكتروني، SMS، WhatsApp، Push Notifications
- ✅ **قوالب إشعارات قابلة للتخصيص**
- ✅ **تفضيلات مستخدم متقدمة**
- ✅ **سجل إرسال شامل**
- ✅ **دعم الجدولة والانتهاء**
- ✅ **تتبع التكاليف**
- ✅ **أولويات وتصنيفات**

---

## 📊 المكونات الرئيسية

### 1. النماذج (Models)

#### EnhancedNotification
نموذج الإشعار الرئيسي مع دعم كامل لجميع القنوات.

**الحقول الرئيسية:**
```python
- user: المستخدم المستلم
- title: عنوان الإشعار
- message: محتوى الإشعار
- category: التصنيف (payment, lease, overdue, etc.)
- priority: الأولوية (low, normal, high, urgent)
- channels: القنوات المستخدمة (JSON)
- is_read: حالة القراءة
- sent_via_email/sms/whatsapp/push: حالة الإرسال
- action_url: رابط الإجراء
- scheduled_at: موعد الإرسال المجدول
- expires_at: تاريخ انتهاء الصلاحية
```

#### EnhancedNotificationTemplate
قوالب الإشعارات القابلة لإعادة الاستخدام.

**الحقول:**
```python
- name: اسم القالب (فريد)
- category: التصنيف
- subject: الموضوع
- body_text: المحتوى النصي
- body_html: المحتوى HTML
- channels: القنوات المفعلة
- variables: المتغيرات المتاحة
- is_active: حالة التفعيل
```

#### EnhancedNotificationPreference
تفضيلات الإشعارات لكل مستخدم.

**الحقول:**
```python
- user: المستخدم
- enable_in_app: تفعيل الإشعارات الداخلية
- enable_email: تفعيل البريد الإلكتروني
- enable_sms: تفعيل SMS
- enable_whatsapp: تفعيل WhatsApp
- enable_push: تفعيل Push Notifications
- categories: تفضيلات لكل تصنيف (JSON)
- quiet_hours_start/end: وقت الهدوء
```

#### EnhancedNotificationLog
سجل تفصيلي لكل عملية إرسال.

**الحقول:**
```python
- notification: الإشعار المرتبط
- channel: القناة المستخدمة
- status: الحالة (pending, sent, delivered, failed)
- recipient: المستلم
- provider: مزود الخدمة
- provider_id: معرف المزود
- cost: التكلفة
- error_message: رسالة الخطأ
```

---

## 🔌 مزودو الخدمات (Providers)

### 1. Email (SMTP)
**المزود:** Django Email Backend
**التكوين:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

**المميزات:**
- إرسال بريد نصي و HTML
- دعم المرفقات
- سجل إرسال كامل

### 2. SMS (Twilio / AWS SNS)
**المزودون المدعومون:**
- Twilio SMS
- AWS SNS

**تكوين Twilio:**
```python
SMS_PROVIDER = 'twilio'
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'
```

**تكوين AWS SNS:**
```python
SMS_PROVIDER = 'aws_sns'
AWS_ACCESS_KEY_ID = 'your_access_key'
AWS_SECRET_ACCESS_KEY = 'your_secret_key'
AWS_SNS_REGION = 'us-east-1'
```

### 3. WhatsApp (Twilio / Business API)
**المزودون المدعومون:**
- Twilio WhatsApp
- WhatsApp Business API

**تكوين Twilio WhatsApp:**
```python
WHATSAPP_PROVIDER = 'twilio'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'
```

**تكوين Business API:**
```python
WHATSAPP_PROVIDER = 'business_api'
WHATSAPP_API_URL = 'https://graph.facebook.com/v18.0'
WHATSAPP_API_TOKEN = 'your_token'
WHATSAPP_PHONE_NUMBER_ID = 'your_phone_id'
```

### 4. Push Notifications (Firebase)
**المزود:** Firebase Cloud Messaging (FCM)

**التكوين:**
```python
FIREBASE_SERVER_KEY = 'your_server_key'
FIREBASE_PROJECT_ID = 'your_project_id'
```

---

## 🚀 الاستخدام

### 1. إرسال إشعار بسيط

```python
from dashboard.notifications import NotificationService
from dashboard.models import NotificationCategory, NotificationPriority

# إنشاء إشعار
notification = NotificationService.create_notification(
    user=user,
    title="دفعة جديدة",
    message="تم استلام دفعة بمبلغ 500 ر.ع",
    category=NotificationCategory.PAYMENT,
    priority=NotificationPriority.NORMAL,
    channels=['in_app', 'email'],
    action_url='/dashboard/payments/123/',
    action_text='عرض الدفعة'
)
```

### 2. إرسال إشعار مجدول

```python
from datetime import timedelta
from django.utils import timezone

# إشعار يُرسل بعد ساعة
notification = NotificationService.create_notification(
    user=user,
    title="تذكير",
    message="موعد الدفعة غداً",
    scheduled_at=timezone.now() + timedelta(hours=1),
    channels=['in_app', 'sms']
)
```

### 3. استخدام قالب

```python
from dashboard.models import EnhancedNotificationTemplate

# الحصول على القالب
template = EnhancedNotificationTemplate.objects.get(name='payment_received')

# تطبيق المتغيرات
context = {
    'tenant_name': 'محمد أحمد',
    'amount': '500',
    'date': '2025-01-15'
}

rendered = template.render(context)

# إنشاء الإشعار
notification = NotificationService.create_notification(
    user=user,
    title=rendered['subject'],
    message=rendered['body_text'],
    channels=template.channels
)
```

### 4. إدارة التفضيلات

```python
from dashboard.models import EnhancedNotificationPreference

# الحصول على التفضيلات
prefs, created = EnhancedNotificationPreference.objects.get_or_create(user=user)

# تحديث التفضيلات
prefs.enable_email = True
prefs.enable_sms = False
prefs.enable_whatsapp = True
prefs.quiet_hours_start = '22:00'
prefs.quiet_hours_end = '08:00'
prefs.save()

# تفضيلات حسب التصنيف
prefs.categories = {
    'payment': {'email': True, 'sms': False},
    'overdue': {'email': True, 'sms': True, 'whatsapp': True}
}
prefs.save()
```

---

## 📋 التصنيفات والأولويات

### التصنيفات (Categories)
```python
PAYMENT = 'payment'      # دفعة
LEASE = 'lease'          # عقد
MAINTENANCE = 'maintenance'  # صيانة
OVERDUE = 'overdue'      # تأخير سداد
REMINDER = 'reminder'    # تذكير
SYSTEM = 'system'        # نظام
SECURITY = 'security'    # أمان
GENERAL = 'general'      # عام
```

### الأولويات (Priorities)
```python
LOW = 'low'          # منخفضة - إشعارات عامة
NORMAL = 'normal'    # عادية - معظم الإشعارات
HIGH = 'high'        # عالية - تحتاج انتباه
URGENT = 'urgent'    # عاجلة - تتجاوز وقت الهدوء
```

---

## 🎨 القنوات (Channels)

### 1. In-App (داخل التطبيق)
- **الاستخدام:** إشعارات فورية داخل النظام
- **المميزات:** 
  - عرض في شريط الإشعارات
  - تحديد كمقروء/غير مقروء
  - روابط إجراءات مباشرة
- **التكلفة:** مجاني

### 2. Email (البريد الإلكتروني)
- **الاستخدام:** إشعارات مفصلة ورسمية
- **المميزات:**
  - دعم HTML
  - إمكانية إرفاق ملفات
  - سجل إرسال كامل
- **التكلفة:** مجاني (SMTP) أو حسب المزود

### 3. SMS (رسالة نصية)
- **الاستخدام:** إشعارات عاجلة وقصيرة
- **المميزات:**
  - وصول فوري
  - لا يحتاج إنترنت
  - معدل قراءة عالي
- **التكلفة:** ~$0.05 لكل رسالة

### 4. WhatsApp
- **الاستخدام:** إشعارات تفاعلية
- **المميزات:**
  - دعم الوسائط
  - قوالب معتمدة
  - معدل قراءة عالي جداً
- **التكلفة:** ~$0.01 لكل رسالة

### 5. Push Notifications
- **الاستخدام:** إشعارات فورية على الأجهزة
- **المميزات:**
  - وصول فوري
  - تفاعل مباشر
  - دعم الصور والأصوات
- **التكلفة:** مجاني (Firebase)

---

## ⚙️ الإعدادات المتقدمة

### 1. وقت الهدوء (Quiet Hours)
منع إرسال الإشعارات غير العاجلة في أوقات محددة.

```python
# في التفضيلات
prefs.quiet_hours_start = '22:00'  # 10 مساءً
prefs.quiet_hours_end = '08:00'    # 8 صباحاً
```

**ملاحظة:** الإشعارات ذات الأولوية `URGENT` تتجاوز وقت الهدوء.

### 2. حدود الإرسال (Rate Limiting)
منع إساءة استخدام النظام.

```python
# في .env.notifications
MAX_SMS_PER_USER_PER_DAY = 10
MAX_WHATSAPP_PER_USER_PER_DAY = 20
MAX_EMAIL_PER_USER_PER_DAY = 50
```

### 3. تتبع التكاليف
حساب تكاليف الإشعارات المدفوعة.

```python
TRACK_NOTIFICATION_COSTS = True
SMS_COST_PER_MESSAGE = 0.05  # USD
WHATSAPP_COST_PER_MESSAGE = 0.01  # USD
```

### 4. وضع الاختبار
اختبار النظام بدون إرسال حقيقي.

```python
NOTIFICATION_TEST_MODE = True
NOTIFICATION_TEST_RECIPIENT = 'test@example.com'
NOTIFICATION_TEST_PHONE = '+96812345678'
```

---

## 📊 التقارير والإحصائيات

### 1. إحصائيات الإرسال

```python
from dashboard.models import EnhancedNotificationLog

# إحصائيات حسب القناة
stats = EnhancedNotificationLog.objects.values('channel').annotate(
    total=Count('id'),
    sent=Count('id', filter=Q(status='sent')),
    failed=Count('id', filter=Q(status='failed'))
)

# إحصائيات حسب المستخدم
user_stats = EnhancedNotification.objects.filter(user=user).aggregate(
    total=Count('id'),
    read=Count('id', filter=Q(is_read=True)),
    unread=Count('id', filter=Q(is_read=False))
)
```

### 2. تقرير التكاليف

```python
from django.db.models import Sum

# إجمالي التكاليف
total_cost = EnhancedNotificationLog.objects.aggregate(
    total=Sum('cost')
)['total']

# تكاليف حسب القناة
channel_costs = EnhancedNotificationLog.objects.values('channel').annotate(
    total_cost=Sum('cost'),
    count=Count('id')
)
```

---

## 🔧 استكشاف الأخطاء

### مشكلة: الإشعارات لا تُرسل

**الحلول:**
1. تحقق من تفعيل القناة في التفضيلات
2. تحقق من وقت الهدوء
3. تحقق من صحة بيانات المزود
4. راجع سجل الأخطاء في `EnhancedNotificationLog`

### مشكلة: فشل إرسال Email

**الحلول:**
1. تحقق من إعدادات SMTP
2. تحقق من صحة كلمة المرور
3. تأكد من تفعيل "Less secure apps" (Gmail)
4. استخدم App Password بدلاً من كلمة المرور العادية

### مشكلة: فشل إرسال SMS

**الحلول:**
1. تحقق من رصيد Twilio/AWS
2. تحقق من صحة رقم الهاتف (بصيغة دولية)
3. تحقق من صلاحيات API
4. راجع سجل المزود

---

## 📱 أمثلة عملية

### مثال 1: إشعار دفعة جديدة

```python
def notify_payment_received(payment):
    """إشعار عند استلام دفعة"""
    NotificationService.create_notification(
        user=payment.lease.tenant.user,
        title=f"تم استلام دفعة بمبلغ {payment.amount} ر.ع",
        message=f"شكراً لك على الدفع. رقم الإيصال: {payment.receipt_number}",
        category=NotificationCategory.PAYMENT,
        priority=NotificationPriority.NORMAL,
        channels=['in_app', 'email', 'sms'],
        related_object=payment,
        action_url=f'/dashboard/payments/{payment.id}/',
        action_text='عرض الإيصال'
    )
```

### مثال 2: تذكير تجديد عقد

```python
def notify_lease_renewal_reminder(lease):
    """تذكير بتجديد عقد قبل 30 يوم"""
    days_left = (lease.end_date - timezone.now().date()).days
    
    NotificationService.create_notification(
        user=lease.tenant.user,
        title="تذكير: تجديد عقد الإيجار",
        message=f"عقدك ينتهي بعد {days_left} يوم. يرجى التواصل لتجديد العقد.",
        category=NotificationCategory.REMINDER,
        priority=NotificationPriority.HIGH,
        channels=['in_app', 'email', 'whatsapp'],
        related_object=lease,
        action_url=f'/dashboard/leases/{lease.id}/',
        action_text='عرض تفاصيل العقد'
    )
```

### مثال 3: إنذار تأخير سداد

```python
def notify_payment_overdue(notice):
    """إشعار بإنذار تأخير سداد"""
    NotificationService.create_notification(
        user=notice.lease.tenant.user,
        title="⚠️ إنذار تأخير سداد",
        message=f"لديك مبلغ متأخر {notice.total_overdue_amount} ر.ع. الموعد النهائي: {notice.legal_deadline}",
        category=NotificationCategory.OVERDUE,
        priority=NotificationPriority.URGENT,
        channels=['in_app', 'email', 'sms', 'whatsapp'],
        related_object=notice,
        action_url=f'/dashboard/overdue-notices/{notice.id}/',
        action_text='عرض الإنذار'
    )
```

---

## 🔐 الأمان

### 1. حماية البيانات
- جميع بيانات الاتصال مشفرة
- استخدام HTTPS لجميع الاتصالات
- عدم تخزين كلمات المرور في قاعدة البيانات

### 2. التحقق من الصلاحيات
- التحقق من صلاحيات المستخدم قبل الإرسال
- منع الإرسال للمستخدمين المحظورين
- سجل كامل لجميع العمليات

### 3. منع الإساءة
- حدود إرسال يومية
- كشف الأنماط المشبوهة
- إمكانية حظر المستخدمين

---

## 📈 الأداء

### 1. التحسينات
- استخدام Celery للإرسال غير المتزامن
- تجميع الإشعارات (Batching)
- Cache للقوالب المستخدمة بكثرة

### 2. المراقبة
- سجلات مفصلة لكل عملية
- تتبع معدلات النجاح/الفشل
- تنبيهات عند الأخطاء المتكررة

---

## 🎓 أفضل الممارسات

### 1. اختيار القناة المناسبة
- **In-App:** للإشعارات العامة
- **Email:** للإشعارات المفصلة والرسمية
- **SMS:** للإشعارات العاجلة والقصيرة
- **WhatsApp:** للإشعارات التفاعلية
- **Push:** للإشعارات الفورية

### 2. كتابة الرسائل
- اجعلها قصيرة ومباشرة
- استخدم لغة واضحة
- أضف روابط إجراءات مفيدة
- تجنب المصطلحات التقنية

### 3. التوقيت
- احترم وقت الهدوء
- أرسل في الأوقات المناسبة
- استخدم الجدولة للإشعارات المستقبلية

### 4. التخصيص
- استخدم اسم المستخدم
- أضف تفاصيل ذات صلة
- اجعل الرسالة شخصية

---

## 📞 الدعم

للمساعدة أو الإبلاغ عن مشاكل:
- راجع سجلات الأخطاء في `/logs/`
- تحقق من `EnhancedNotificationLog` للتفاصيل
- راجع التوثيق الكامل في هذا الملف

---

## 🔄 التحديثات المستقبلية

### قيد التطوير:
- [ ] دعم Telegram
- [ ] دعم Slack
- [ ] إشعارات صوتية
- [ ] تحليلات متقدمة
- [ ] A/B Testing للرسائل
- [ ] قوالب متعددة اللغات

---

**آخر تحديث:** 2025-01-23  
**الإصدار:** 1.0.0  
**الحالة:** ✅ جاهز للإنتاج

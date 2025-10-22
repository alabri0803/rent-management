# 📝 نظام السجلات المتقدم (Advanced Logging System)

## 📋 نظرة عامة

تم إضافة نظام سجلات شامل ومتقدم لتتبع جميع الأحداث والأخطاء والأداء في النظام.

---

## 🎯 المميزات الرئيسية

### 1. **7 أنواع من ملفات السجلات**
- **all.log** - جميع السجلات
- **errors.log** - الأخطاء فقط
- **security.log** - الأحداث الأمنية
- **api.log** - طلبات API
- **database.log** - استعلامات قاعدة البيانات
- **audit.log** - تدقيق إجراءات المستخدمين
- **performance.log** - أداء النظام

### 2. **Rotating File Handlers**
- حجم أقصى: 10MB لكل ملف
- نسخ احتياطية تلقائية
- ضغط تلقائي للملفات القديمة

### 3. **Middleware تلقائي**
- تسجيل جميع الطلبات
- تتبع الأداء
- كشف الطلبات المشبوهة
- Audit trail للمستخدمين

### 4. **Decorators للتسجيل**
- `@log_view_access` - للـ views
- `@log_api_call` - للـ API
- `@log_model_action` - للنماذج
- `@measure_performance` - لقياس الأداء

---

## ⚙️ الإعدادات (settings.py)

### ملفات السجلات:

```python
logs/
├── all.log              # جميع السجلات (10 نسخ)
├── errors.log           # الأخطاء فقط (10 نسخ)
├── security.log         # الأمان (20 نسخة)
├── api.log             # API requests (15 نسخة)
├── database.log        # DB queries (5 نسخ)
├── audit.log           # Audit trail (30 نسخة)
└── performance.log     # الأداء (7 نسخ)
```

### Formatters:

```python
# Verbose Format
[ERROR] 2025-10-22 23:30:15 | dashboard | views.lease_create:145 | Error creating lease

# Simple Format
[INFO] 2025-10-22 23:30:15 | User logged in successfully

# JSON Format
{"time": "2025-10-22 23:30:15", "level": "ERROR", "logger": "api", "message": "API error"}
```

---

## 📚 الاستخدام

### 1. استخدام Loggers مباشرة

```python
from dashboard.logging_utils import logger, api_logger, security_logger, audit_logger

# General logging
logger.info("Processing lease payments")
logger.error("Failed to process payment", exc_info=True)

# API logging
api_logger.info("API request received")

# Security logging
security_logger.warning("Failed login attempt")

# Audit logging
audit_logger.info("User created new lease")
```

### 2. استخدام Helper Functions

```python
from dashboard.logging_utils import (
    log_user_action,
    log_api_request,
    log_security_event,
    log_performance,
    log_error
)

# تسجيل إجراء المستخدم
log_user_action(
    user=request.user,
    action='create',
    model_name='Lease',
    object_id=lease.id,
    details='Created new lease contract'
)

# تسجيل طلب API
log_api_request(request, response, duration=0.523)

# تسجيل حدث أمني
log_security_event(
    event_type='failed_login',
    user=username,
    ip_address='192.168.1.100',
    details='Invalid password'
)

# تسجيل الأداء
log_performance('calculate_financial_report', duration=2.5)

# تسجيل خطأ
try:
    # Your code
    pass
except Exception as e:
    log_error(e, context='Processing payment')
```

### 3. استخدام Decorators

```python
from dashboard.logging_utils import (
    log_view_access,
    log_api_call,
    log_model_action,
    measure_performance
)

# للـ Views
@log_view_access('lease_list')
def lease_list_view(request):
    return render(request, 'lease_list.html')

# للـ API
class LeaseViewSet(viewsets.ModelViewSet):
    @log_api_call('lease_list_api')
    def list(self, request):
        return super().list(request)

# للنماذج
@log_model_action('create')
def create_lease(request, data):
    lease = Lease.objects.create(**data)
    return lease

# لقياس الأداء
@measure_performance('calculate_report')
def calculate_financial_report(year, month):
    # Expensive calculation
    return report
```

### 4. استخدام Context Manager

```python
from dashboard.logging_utils import LogContext

# تسجيل عملية كاملة
with LogContext('Processing monthly payments'):
    process_all_payments()
    # يسجل تلقائياً: START, END, Duration
```

---

## 🔧 Middleware

### تفعيل Middleware في settings.py:

```python
MIDDLEWARE = [
    # ... other middleware
    'dashboard.logging_middleware.RequestLoggingMiddleware',
    'dashboard.logging_middleware.SecurityLoggingMiddleware',
    'dashboard.logging_middleware.AuditTrailMiddleware',
    'dashboard.logging_middleware.PerformanceLoggingMiddleware',
]
```

### ما يسجله كل Middleware:

#### 1. RequestLoggingMiddleware
- جميع طلبات API
- مدة كل طلب
- الطلبات البطيئة (>2s)
- الاستثناءات

#### 2. SecurityLoggingMiddleware
- الطلبات المشبوهة
- محاولات SQL Injection
- محاولات XSS
- الوصول لمسارات محظورة

#### 3. AuditTrailMiddleware
- إجراءات المستخدمين المهمة
- POST, PUT, DELETE operations
- عنوان IP
- الوقت والتاريخ

#### 4. PerformanceLoggingMiddleware
- الطلبات البطيئة (>1s)
- مدة التنفيذ
- حالة الاستجابة

---

## 🛠️ أوامر الإدارة

### 1. عرض إحصائيات السجلات

```bash
python manage.py manage_logs --action=stats
```

**Output:**
```
📊 Log Files Statistics

  📄 all.log              | Size: 5.23 MB    | Lines:  15234 | Modified: 2025-10-22 23:30
  📄 errors.log           | Size: 1.45 MB    | Lines:   3421 | Modified: 2025-10-22 23:25
  📄 security.log         | Size: 892.34 KB  | Lines:   2156 | Modified: 2025-10-22 23:20
  📄 api.log             | Size: 3.67 MB    | Lines:   8934 | Modified: 2025-10-22 23:30
  📄 audit.log           | Size: 2.11 MB    | Lines:   5678 | Modified: 2025-10-22 23:28

  Total Size: 13.35 MB
  Total Files: 5
```

### 2. حذف السجلات القديمة

```bash
# حذف السجلات أقدم من 30 يوم (افتراضي)
python manage.py manage_logs --action=clean

# حذف السجلات أقدم من 7 أيام
python manage.py manage_logs --action=clean --days=7
```

### 3. ضغط السجلات

```bash
python manage.py manage_logs --action=compress
```

**Output:**
```
📦 Compressing log files...

  📦 Compressed: all.log.1 | Original: 10.00 MB → Compressed: 1.23 MB | Saved: 8.77 MB
  📦 Compressed: errors.log.1 | Original: 5.45 MB → Compressed: 678.90 KB | Saved: 4.79 MB

✅ Compressed 2 files | Saved: 13.56 MB
```

### 4. تحليل السجلات

```bash
python manage.py manage_logs --action=analyze
```

**Output:**
```
🔍 Analyzing log files...

❌ Error Analysis:
  Total Errors: 145
  Top Error Types:
    - DoesNotExist: 45
    - ValidationError: 32
    - PermissionDenied: 18

🔒 Security Analysis:
  Failed Login Attempts: 23
  Suspicious Requests: 7

⚡ Performance Analysis:
  Total Operations: 1234
  Slow Operations (>1s): 89
  Average Duration: 0.456s
```

---

## 📊 أمثلة عملية

### مثال 1: تسجيل إنشاء عقد

```python
from dashboard.logging_utils import log_user_action, logger

def create_lease(request):
    try:
        lease = Lease.objects.create(
            unit=unit,
            tenant=tenant,
            monthly_rent=1000
        )
        
        # تسجيل الإجراء
        log_user_action(
            user=request.user,
            action='create',
            model_name='Lease',
            object_id=lease.id,
            details=f'Contract: {lease.contract_number}'
        )
        
        logger.info(f"Lease created successfully: {lease.contract_number}")
        
        return lease
    
    except Exception as e:
        logger.error(f"Failed to create lease: {str(e)}", exc_info=True)
        raise
```

### مثال 2: تسجيل محاولة تسجيل دخول

```python
from dashboard.logging_utils import log_login_attempt, log_security_event

def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        login(request, user)
        log_login_attempt(request, username, success=True)
        return redirect('dashboard')
    else:
        log_login_attempt(request, username, success=False)
        
        # تسجيل حدث أمني
        log_security_event(
            event_type='failed_login',
            user=username,
            ip_address=get_client_ip(request)
        )
        
        return render(request, 'login.html', {'error': 'Invalid credentials'})
```

### مثال 3: قياس أداء تقرير مالي

```python
from dashboard.logging_utils import measure_performance, LogContext

@measure_performance('financial_report')
def generate_financial_report(year, month):
    with LogContext('Calculating financial data'):
        # حسابات معقدة
        income = calculate_income(year, month)
        expenses = calculate_expenses(year, month)
        
        return {
            'income': income,
            'expenses': expenses,
            'net': income - expenses
        }
```

### مثال 4: تسجيل تصدير بيانات

```python
from dashboard.logging_utils import log_data_export

def export_leases_excel(request):
    leases = Lease.objects.all()
    
    # إنشاء ملف Excel
    workbook = create_excel(leases)
    
    # تسجيل التصدير
    log_data_export(
        user=request.user,
        export_type='leases_excel',
        record_count=leases.count()
    )
    
    return workbook
```

---

## 🔍 مراقبة السجلات

### 1. مراقبة الأخطاء في الوقت الفعلي

```bash
# Linux/Mac
tail -f logs/errors.log

# Windows
Get-Content logs/errors.log -Wait
```

### 2. البحث في السجلات

```bash
# البحث عن أخطاء محددة
grep "DoesNotExist" logs/errors.log

# البحث عن محاولات تسجيل دخول فاشلة
grep "Failed login" logs/security.log

# البحث عن عمليات بطيئة
grep "SLOW" logs/performance.log
```

### 3. تحليل السجلات بـ Python

```python
import re
from collections import Counter

def analyze_errors():
    with open('logs/errors.log', 'r') as f:
        errors = []
        for line in f:
            if '[ERROR]' in line:
                # استخراج نوع الخطأ
                match = re.search(r'(\w+Error):', line)
                if match:
                    errors.append(match.group(1))
        
        # عد الأخطاء
        error_counts = Counter(errors)
        
        print("Top 5 Errors:")
        for error, count in error_counts.most_common(5):
            print(f"  {error}: {count}")

analyze_errors()
```

---

## 📈 Best Practices

### ✅ DO:

1. **استخدم المستوى المناسب**
   ```python
   logger.debug("Detailed info for debugging")
   logger.info("General information")
   logger.warning("Warning message")
   logger.error("Error occurred")
   logger.critical("Critical error!")
   ```

2. **أضف سياق للأخطاء**
   ```python
   try:
       process_payment(payment_id)
   except Exception as e:
       logger.error(
           f"Payment processing failed | Payment ID: {payment_id}",
           exc_info=True
       )
   ```

3. **سجل الإجراءات المهمة**
   ```python
   log_user_action(user, 'delete', 'Lease', lease_id)
   ```

4. **راقب الأداء**
   ```python
   @measure_performance('expensive_operation')
   def expensive_operation():
       pass
   ```

### ❌ DON'T:

1. **لا تسجل معلومات حساسة**
   ```python
   # ❌ خطأ
   logger.info(f"User password: {password}")
   
   # ✅ صحيح
   logger.info(f"User logged in: {username}")
   ```

2. **لا تسجل في loops كثيرة**
   ```python
   # ❌ خطأ
   for item in items:  # 10000 items
       logger.info(f"Processing {item}")
   
   # ✅ صحيح
   logger.info(f"Processing {len(items)} items")
   for item in items:
       pass
   logger.info("Processing complete")
   ```

3. **لا تستخدم print()**
   ```python
   # ❌ خطأ
   print("Error occurred")
   
   # ✅ صحيح
   logger.error("Error occurred")
   ```

---

## 🔐 الأمان

### حماية ملفات السجلات:

```bash
# Linux/Mac - تعيين صلاحيات مناسبة
chmod 640 logs/*.log
chown www-data:www-data logs/*.log

# إضافة logs/ إلى .gitignore
echo "logs/" >> .gitignore
```

### تشفير السجلات الحساسة:

```python
import hashlib

def log_sensitive_data(data):
    # تشفير البيانات الحساسة
    hashed = hashlib.sha256(data.encode()).hexdigest()
    logger.info(f"Sensitive operation: {hashed[:8]}...")
```

---

## 📊 التكامل مع أدوات خارجية

### 1. Sentry (للـ Production)

```python
# settings.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### 2. ELK Stack (Elasticsearch, Logstash, Kibana)

```python
# استخدام JSON formatter
LOGGING['formatters']['json'] = {
    'format': '{"time": "{asctime}", "level": "{levelname}", ...}',
}
```

### 3. CloudWatch (AWS)

```python
# استخدام watchtower
import watchtower

LOGGING['handlers']['cloudwatch'] = {
    'class': 'watchtower.CloudWatchLogHandler',
}
```

---

## ✅ الخلاصة

تم إضافة نظام logging شامل يتضمن:

1. ✅ **7 ملفات سجلات** منفصلة
2. ✅ **Rotating handlers** تلقائي
3. ✅ **4 Middleware** للتسجيل التلقائي
4. ✅ **Decorators** للتسجيل السهل
5. ✅ **Helper functions** شاملة
6. ✅ **Management commands** للإدارة
7. ✅ **Context managers** للعمليات
8. ✅ **Security logging** متقدم
9. ✅ **Performance tracking** دقيق
10. ✅ **Audit trail** كامل

**النظام جاهز للاستخدام ويوفر تتبع شامل لجميع الأحداث! 🚀**

---

تم إنشاء التوثيق في: 2025-10-22

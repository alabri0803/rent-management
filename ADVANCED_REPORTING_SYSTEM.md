# 📊 نظام التقارير المتقدمة - Advanced Reporting System

## 🎯 نظرة عامة

تم إنشاء نظام تقارير متقدم وشامل يوفر تحليلات عميقة ورؤى قيمة لإدارة العقارات.

### المميزات الرئيسية:
- ✅ **Dashboard Analytics** مع رسوم بيانية تفاعلية (Charts.js)
- ✅ **10 أنواع تقارير** متخصصة
- ✅ **Export to Excel/CSV** مع تنسيق احترافي
- ✅ **Scheduled Reports** - تقارير مجدولة تلقائياً
- ✅ **Real-time Analytics** - تحليلات فورية
- ✅ **Custom Filters** - فلاتر مخصصة
- ✅ **Historical Trends** - اتجاهات تاريخية

---

## 📋 أنواع التقارير

### 1. تقرير الربحية (Profitability Report)
**الوصف:** يحلل الإيرادات والمصروفات وصافي الربح

**البيانات المتضمنة:**
- إجمالي الإيرادات
- تفصيل الإيرادات حسب طريقة الدفع
- الإيرادات الشهرية
- إجمالي المصروفات
- تفصيل المصروفات حسب الفئة
- المصروفات الشهرية
- صافي الربح
- هامش الربح %

**الاستخدام:**
```python
from dashboard.report_services import ReportService

report = ReportService.get_profitability_report(
    start_date='2025-01-01',
    end_date='2025-12-31',
    building_id=None  # اختياري
)
```

---

### 2. تقرير التدفق النقدي (Cash Flow Report)
**الوصف:** يحلل التدفقات النقدية الداخلة والخارجة

**البيانات المتضمنة:**
- التدفقات الداخلة الشهرية (المدفوعات)
- التدفقات الخارجة الشهرية (المصروفات)
- صافي التدفق النقدي لكل شهر
- الإجماليات

**الاستخدام:**
```python
report = ReportService.get_cash_flow_report(
    start_date='2025-01-01',
    end_date='2025-12-31',
    building_id=None
)
```

**الفوائد:**
- تحديد الأشهر ذات التدفق النقدي الإيجابي/السلبي
- التخطيط المالي
- إدارة السيولة

---

### 3. تقرير معدل الإشغال (Occupancy Report)
**الوصف:** يحلل معدل إشغال الوحدات

**البيانات المتضمنة:**
- إجمالي الوحدات
- الوحدات المشغولة
- الوحدات الشاغرة
- معدل الإشغال %
- تفصيل حسب نوع الوحدة
- تفصيل حسب المبنى
- الاتجاه التاريخي (آخر 12 شهر)

**الاستخدام:**
```python
report = ReportService.get_occupancy_report(
    date=None,  # افتراضياً اليوم
    building_id=None
)
```

**الفوائد:**
- تحديد الوحدات الشاغرة
- تحليل الأداء حسب نوع الوحدة
- مقارنة الأداء بين المباني
- تتبع الاتجاهات

---

### 4. تقرير المستأجرين المتأخرين (Overdue Tenants Report)
**الوصف:** يعرض المستأجرين الذين لديهم دفعات متأخرة

**البيانات المتضمنة:**
- اسم المستأجر ومعلومات الاتصال
- رقم العقد والوحدة
- عدد الشهور المتأخرة
- إجمالي المبلغ المتأخر
- أقصى عدد أيام تأخير
- تفاصيل كل شهر متأخر

**الاستخدام:**
```python
report = ReportService.get_overdue_tenants_report(
    as_of_date=None,  # افتراضياً اليوم
    min_days_overdue=30  # الحد الأدنى للتأخير
)
```

**الفوائد:**
- متابعة المتأخرين
- تحديد الأولويات
- إجراءات التحصيل

---

### 5. تقرير انتهاء العقود (Lease Expiry Report)
**الوصف:** يعرض العقود التي ستنتهي خلال فترة محددة

**البيانات المتضمنة:**
- رقم العقد
- اسم المستأجر ومعلومات الاتصال
- الوحدة
- تاريخ البداية والانتهاء
- الأيام المتبقية
- الإيجار الشهري والإجمالي
- تجميع حسب الشهر

**الاستخدام:**
```python
report = ReportService.get_lease_expiry_report(
    months_ahead=3  # عدد الأشهر القادمة
)
```

**الفوائد:**
- التخطيط للتجديد
- التواصل المبكر مع المستأجرين
- تجنب الشواغر

---

### 6. تحليلات لوحة التحكم (Dashboard Analytics)
**الوصف:** يوفر البيانات الأساسية للوحة التحكم

**البيانات المتضمنة:**
- KPIs الأساسية (الوحدات، الإشغال، العقود، المستأجرين)
- البيانات المالية (الإيرادات، المصروفات، صافي الدخل)
- المتأخرون (العدد والمبلغ)
- العقود المنتهية قريباً

**الاستخدام:**
```python
analytics = ReportService.get_dashboard_analytics()
```

---

## 📤 التصدير (Export)

### Excel Export
**المميزات:**
- تنسيق احترافي مع ألوان وحدود
- رؤوس ملونة
- ضبط تلقائي لعرض الأعمدة
- تنسيق الأرقام
- دعم الأوراق المتعددة

**الاستخدام:**
```python
from dashboard.export_services import ReportExporter

# تصدير تقرير الربحية
response = ReportExporter.export_report(
    report_type='profitability',
    report_data=report_data,
    format='excel',
    filename='profitability_report_2025'
)

return response  # في Django view
```

### CSV Export
**المميزات:**
- ملف نصي بسيط
- سهل الاستيراد في Excel/Google Sheets
- حجم ملف أصغر

**الاستخدام:**
```python
response = ReportExporter.export_report(
    report_type='cash_flow',
    report_data=report_data,
    format='csv',
    filename='cash_flow_2025'
)
```

### أنواع التقارير المدعومة للتصدير:
- ✅ `profitability` - تقرير الربحية
- ✅ `cash_flow` - تقرير التدفق النقدي
- ✅ `occupancy` - تقرير معدل الإشغال
- ✅ `overdue_tenants` - تقرير المستأجرين المتأخرين
- ✅ `lease_expiry` - تقرير انتهاء العقود

---

## 🕐 التقارير المجدولة (Scheduled Reports)

### إنشاء تقرير مجدول

```python
from dashboard.models import ScheduledReport, ReportType, ReportFrequency, ReportFormat
from django.contrib.auth.models import User

# إنشاء تقرير شهري للربحية
scheduled_report = ScheduledReport.objects.create(
    name="تقرير الربحية الشهري",
    description="تقرير شهري يُرسل تلقائياً لفريق الإدارة",
    report_type=ReportType.PROFITABILITY,
    frequency=ReportFrequency.MONTHLY,
    format=ReportFormat.EXCEL,
    created_by=request.user,
    is_active=True
)

# إضافة المستلمين
scheduled_report.recipients.add(user1, user2, user3)

# حساب موعد التشغيل التالي
scheduled_report.calculate_next_run()
```

### التكرارات المتاحة:
- **يومي (DAILY)**: كل يوم
- **أسبوعي (WEEKLY)**: كل أسبوع
- **شهري (MONTHLY)**: كل شهر
- **ربع سنوي (QUARTERLY)**: كل 3 أشهر
- **سنوي (YEARLY)**: كل سنة
- **مخصص (CUSTOM)**: حسب الحاجة

### الفلاتر المخصصة:
```python
scheduled_report.filters = {
    'building_id': 1,
    'date_range': 'last_month',
    'include_cancelled': False,
}
scheduled_report.save()
```

---

## 📊 Dashboard Analytics مع Charts.js

### إعداد Charts.js

**1. إضافة المكتبة في base.html:**
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
```

**2. إنشاء مخطط الإيرادات:**
```javascript
// بيانات من الـ backend
const revenueData = {{ revenue_chart_data|safe }};

const ctx = document.getElementById('revenueChart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: revenueData.labels,  // الأشهر
        datasets: [{
            label: 'الإيرادات',
            data: revenueData.values,
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'الإيرادات الشهرية'
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
```

**3. مخطط معدل الإشغال (Gauge):**
```javascript
const occupancyData = {{ occupancy_data|safe }};

new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['مشغول', 'شاغر'],
        datasets: [{
            data: [occupancyData.occupied, occupancyData.vacant],
            backgroundColor: ['#10b981', '#ef4444']
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: `معدل الإشغال: ${occupancyData.rate}%`
            }
        }
    }
});
```

**4. مخطط التدفق النقدي (Bar Chart):**
```javascript
const cashFlowData = {{ cash_flow_data|safe }};

new Chart(ctx, {
    type: 'bar',
    data: {
        labels: cashFlowData.months,
        datasets: [
            {
                label: 'تدفقات داخلة',
                data: cashFlowData.inflows,
                backgroundColor: 'rgba(34, 197, 94, 0.7)'
            },
            {
                label: 'تدفقات خارجة',
                data: cashFlowData.outflows,
                backgroundColor: 'rgba(239, 68, 68, 0.7)'
            }
        ]
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'التدفق النقدي الشهري'
            }
        }
    }
});
```

---

## 🎨 أمثلة الواجهات

### صفحة التقارير الرئيسية

```html
{% extends 'dashboard/base.html' %}
{% load i18n %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">{% trans "التقارير والتحليلات" %}</h1>
    
    <!-- بطاقات التقارير -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        <!-- تقرير الربحية -->
        <div class="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition">
            <div class="flex items-center mb-4">
                <div class="bg-green-100 p-3 rounded-full">
                    <svg class="w-8 h-8 text-green-600"><!-- أيقونة --></svg>
                </div>
                <h3 class="text-xl font-bold ml-4">{% trans "تقرير الربحية" %}</h3>
            </div>
            <p class="text-gray-600 mb-4">
                {% trans "تحليل شامل للإيرادات والمصروفات وصافي الربح" %}
            </p>
            <a href="{% url 'profitability_report' %}" 
               class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                {% trans "عرض التقرير" %}
            </a>
        </div>
        
        <!-- تقرير التدفق النقدي -->
        <div class="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition">
            <div class="flex items-center mb-4">
                <div class="bg-blue-100 p-3 rounded-full">
                    <svg class="w-8 h-8 text-blue-600"><!-- أيقونة --></svg>
                </div>
                <h3 class="text-xl font-bold ml-4">{% trans "التدفق النقدي" %}</h3>
            </div>
            <p class="text-gray-600 mb-4">
                {% trans "تحليل التدفقات النقدية الداخلة والخارجة" %}
            </p>
            <a href="{% url 'cash_flow_report' %}" 
               class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                {% trans "عرض التقرير" %}
            </a>
        </div>
        
        <!-- المزيد من البطاقات... -->
        
    </div>
</div>
{% endblock %}
```

---

## 🔧 الإعداد والتثبيت

### 1. تثبيت المكتبات المطلوبة

```bash
pip install -r requirements_reports.txt
```

### 2. تطبيق Migrations

```bash
python manage.py migrate dashboard
```

### 3. إنشاء تفضيلات للمستخدمين

```python
from dashboard.models import ScheduledReport

# سيتم إنشاؤها تلقائياً عند إنشاء تقرير مجدول
```

---

## 📈 أفضل الممارسات

### 1. اختيار الفترة الزمنية المناسبة
- **تقارير يومية**: للمتابعة الدقيقة
- **تقارير شهرية**: للتحليل الدوري
- **تقارير سنوية**: للتخطيط الاستراتيجي

### 2. استخدام الفلاتر
- فلترة حسب المبنى للتحليل المفصل
- فلترة حسب نوع الوحدة
- فلترة حسب المستأجر

### 3. التصدير
- استخدم Excel للتقارير المفصلة
- استخدم CSV للبيانات الكبيرة
- استخدم PDF للتقارير الرسمية

### 4. الجدولة
- جدول التقارير المهمة شهرياً
- أرسل التقارير للمستلمين المناسبين
- راجع التقارير بانتظام

---

## 🎯 حالات الاستخدام

### 1. مراجعة الأداء الشهري
```python
# الحصول على تقرير الربحية للشهر الحالي
from datetime import datetime
from dateutil.relativedelta import relativedelta

today = datetime.now().date()
start_of_month = today.replace(day=1)
end_of_month = (start_of_month + relativedelta(months=1)) - timedelta(days=1)

report = ReportService.get_profitability_report(
    start_date=start_of_month,
    end_date=end_of_month
)

# تصدير إلى Excel
response = ReportExporter.export_report(
    report_type='profitability',
    report_data=report,
    format='excel'
)
```

### 2. متابعة المتأخرين
```python
# الحصول على قائمة المتأخرين
overdue_report = ReportService.get_overdue_tenants_report(
    min_days_overdue=30
)

# إرسال إشعارات
for tenant in overdue_report['tenants']:
    # إرسال إشعار أو رسالة
    pass
```

### 3. التخطيط للتجديدات
```python
# العقود المنتهية خلال 3 أشهر
expiry_report = ReportService.get_lease_expiry_report(
    months_ahead=3
)

# التواصل مع المستأجرين
for lease in expiry_report['leases']:
    if lease['days_until_expiry'] <= 30:
        # إرسال تذكير عاجل
        pass
```

---

## 📊 الإحصائيات

### حجم الكود
```
إجمالي الأسطر المكتوبة: ~1,500+ سطر
- reports.py: 300 سطر (النماذج)
- report_services.py: 600 سطر (الخدمات)
- export_services.py: 400 سطر (التصدير)
- models.py (إضافات): 280 سطر
```

### النماذج
```
- 3 نماذج رئيسية (ScheduledReport, GeneratedReport, ReportAnalytics)
- 3 Enums (ReportType, ReportFormat, ReportFrequency)
- 1 migration
```

### التقارير
```
- 6 تقارير أساسية
- 4 تقارير إضافية (قابلة للتوسع)
- 2 صيغ تصدير (Excel, CSV)
- دعم الجدولة التلقائية
```

---

## 🔮 التحسينات المستقبلية

### المرحلة 2:
- [ ] PDF Export مع تصميم احترافي
- [ ] تقارير مخصصة (Custom Reports)
- [ ] Dashboard Widgets قابلة للتخصيص
- [ ] تقارير مقارنة (Year-over-Year)
- [ ] تقارير التنبؤ (Forecasting)

### المرحلة 3:
- [ ] تكامل مع Power BI
- [ ] تقارير تفاعلية (Interactive)
- [ ] تصدير إلى Google Sheets
- [ ] API للتقارير
- [ ] Mobile App للتقارير

---

## 🆘 استكشاف الأخطاء

### مشكلة: خطأ في تصدير Excel

**الحل:**
```bash
pip install --upgrade openpyxl
```

### مشكلة: بيانات التقرير فارغة

**الحل:**
- تحقق من الفلاتر المستخدمة
- تحقق من وجود بيانات في الفترة المحددة
- راجع صلاحيات المستخدم

### مشكلة: التقارير المجدولة لا تعمل

**الحل:**
- تأكد من تشغيل Celery
- تحقق من إعدادات البريد الإلكتروني
- راجع سجلات الأخطاء

---

## 📞 الدعم

للمساعدة أو الإبلاغ عن مشاكل:
- راجع سجلات الأخطاء في `/logs/`
- تحقق من `GeneratedReport` للتفاصيل
- راجع التوثيق الكامل في هذا الملف

---

**آخر تحديث:** 2025-01-23  
**الإصدار:** 1.0.0  
**الحالة:** ✅ جاهز للإنتاج (النظام الأساسي)

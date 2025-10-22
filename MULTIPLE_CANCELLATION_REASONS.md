# ✅ اختيار أسباب متعددة لإلغاء العقد (حتى 3 أسباب)

## 🎯 الميزة

تم تطوير نموذج إلغاء العقد ليدعم **اختيار أكثر من سبب واحد** (حتى 3 أسباب معاً) بدلاً من اختيار سبب واحد فقط.

---

## 📊 المقارنة

| قبل | بعد |
|-----|-----|
| ❌ اختيار سبب واحد فقط | ✅ اختيار حتى 3 أسباب |
| 🔘 Radio Buttons | ☑️ Checkboxes |
| ❌ لا يوجد عداد | ✅ عداد تفاعلي (0/3) |
| ❌ لا توجد حماية | ✅ منع اختيار أكثر من 3 |
| ❌ لا توجد ردود فعل بصرية | ✅ تعطيل البطاقات تلقائياً |

---

## 🎨 الواجهة

### 1️⃣ **العداد التفاعلي:**

```
┌────────────────────────────────┐
│ 📋 أسباب الإلغاء    [0 / 3 محدد] │
│                      (رمادي)   │
└────────────────────────────────┘

بعد اختيار سبب واحد:
┌────────────────────────────────┐
│ 📋 أسباب الإلغاء    [1 / 3 محدد] │
│                      (أزرق)    │
└────────────────────────────────┘

بعد اختيار 3 أسباب:
┌────────────────────────────────┐
│ 📋 أسباب الإلغاء    [3 / 3 محدد] │
│                      (برتقالي)  │
│ ⚠️ لقد وصلت للحد الأقصى        │
└────────────────────────────────┘
```

### 2️⃣ **البطاقات مع علامات الاختيار:**

```
☑️ بدون اختيار:
┌──────────────────┐
│ 📅 انتهاء المدة  │ ← حدود رمادية
└──────────────────┘

✅ مع الاختيار:
┌──────────────────┐
│ ✓  📅 انتهاء     │ ← حدود حمراء
│    المدة         │    خلفية وردية
└──────────────────┘

🚫 معطل (بعد 3 اختيارات):
┌──────────────────┐
│ 💰 عدم دفع       │ ← شفافية 50%
│    الإيجار       │    cursor: not-allowed
└──────────────────┘
```

---

## 🔧 كيف يعمل؟

### 1. **في النموذج (forms.py):**

```python
cancellation_reasons = forms.MultipleChoiceField(
    choices=Lease.CANCELLATION_REASON_CHOICES,
    widget=forms.CheckboxSelectMultiple(),
    label='أسباب الإلغاء',
    help_text='يمكنك اختيار حتى 3 أسباب'
)

def clean_cancellation_reasons(self):
    reasons = self.cleaned_data.get('cancellation_reasons', [])
    if len(reasons) > 3:
        raise forms.ValidationError('يمكنك اختيار 3 أسباب كحد أقصى')
    return reasons

def save(self, commit=True):
    instance = super().save(commit=False)
    reasons = self.cleaned_data.get('cancellation_reasons', [])
    # حفظ الأسباب مفصولة بفواصل
    instance.cancellation_reason = ','.join(reasons)
    if commit:
        instance.save()
    return instance
```

### 2. **في قاعدة البيانات:**

```sql
-- الحقل محدّث ليستوعب أسباب متعددة
cancellation_reason VARCHAR(500)

-- مثال على البيانات المحفوظة:
"non_payment,tenant_violation,other"
```

### 3. **JavaScript للتحكم:**

```javascript
function updateSelectedCount() {
    const count = checkboxes.length;
    
    // تحديث العداد
    countDisplay.textContent = count;
    
    // تغيير اللون حسب العدد
    if (count === 0) → رمادي
    if (count <= 2) → أزرق  
    if (count === 3) → برتقالي
    
    // منع الاختيار بعد 3
    if (count >= 3) {
        - إظهار التحذير
        - تعطيل باقي الخيارات
        - تقليل الشفافية إلى 50%
    }
}
```

---

## 💡 أمثلة الاستخدام

### **مثال 1: سبب واحد**
```
✅ عدم دفع الإيجار لأكثر من شهرين متتاليين

النتيجة في قاعدة البيانات:
cancellation_reason = "non_payment"

العرض:
- عدم دفع الإيجار لأكثر من شهرين متتاليين
```

### **مثال 2: سببان**
```
✅ عدم دفع الإيجار لأكثر من شهرين متتاليين
✅ مخالفة شروط العقد من قبل المستأجر

النتيجة في قاعدة البيانات:
cancellation_reason = "non_payment,tenant_violation"

العرض:
- عدم دفع الإيجار لأكثر من شهرين متتاليين
- مخالفة شروط العقد من قبل المستأجر
```

### **مثال 3: ثلاثة أسباب (الحد الأقصى)**
```
✅ عدم دفع الإيجار لأكثر من شهرين متتاليين
✅ مخالفة شروط العقد من قبل المستأجر
✅ رغبة المالك في استرداد العقار

النتيجة في قاعدة البيانات:
cancellation_reason = "non_payment,tenant_violation,owner_reclaim"

العرض:
- عدم دفع الإيجار لأكثر من شهرين متتاليين
- مخالفة شروط العقد من قبل المستأجر
- رغبة المالك في استرداد العقار

⚠️ التحذير يظهر: "لقد وصلت للحد الأقصى (3 أسباب)"
🚫 باقي الخيارات تصبح معطلة
```

---

## 📄 عرض الأسباب المحفوظة

### دالة مساعدة في النموذج:

```python
def get_cancellation_reasons_display(self):
    """تحويل أكواد أسباب الإلغاء إلى نصوص عربية"""
    if not self.cancellation_reason:
        return None
    
    reasons_dict = dict(self.CANCELLATION_REASON_CHOICES)
    reason_codes = self.cancellation_reason.split(',')
    reason_texts = [
        reasons_dict.get(code.strip(), code) 
        for code in reason_codes
    ]
    return reason_texts
```

### الاستخدام في Template:

```django
{% if lease.cancellation_reason %}
<div class="mb-4">
    <h4 class="font-bold">أسباب الإلغاء:</h4>
    <ul class="list-disc list-inside">
        {% for reason in lease.get_cancellation_reasons_display %}
        <li>{{ reason }}</li>
        {% endfor %}
    </ul>
</div>
{% endif %}
```

### النتيجة:
```html
أسباب الإلغاء:
• عدم دفع الإيجار لأكثر من شهرين متتاليين
• مخالفة شروط العقد من قبل المستأجر
• رغبة المالك في استرداد العقار
```

---

## 🔍 الإحصائيات والتقارير

يمكنك الآن تحليل أسباب الإلغاء بشكل أفضل:

```python
from dashboard.models import Lease
from collections import Counter

# جمع جميع الأسباب
all_reasons = []
for lease in Lease.objects.filter(status='cancelled', cancellation_reason__isnull=False):
    reasons = lease.cancellation_reason.split(',')
    all_reasons.extend([r.strip() for r in reasons])

# عد التكرارات
reason_counts = Counter(all_reasons)

# النتيجة
print(reason_counts)
# Counter({
#     'non_payment': 15,
#     'tenant_violation': 8,
#     'owner_reclaim': 5,
#     'contract_term_ended': 3,
#     'tenant_request': 2,
#     'other': 1
# })
```

---

## 🎨 التصميم التفاعلي

### 1. **الألوان:**
- 🟢 **رمادي** (0 اختيارات): لم يبدأ الاختيار
- 🔵 **أزرق** (1-2 اختيارات): يمكن إضافة المزيد
- 🟠 **برتقالي** (3 اختيارات): الحد الأقصى

### 2. **التأثيرات:**
- ✨ **Hover**: حدود حمراء + ظل
- ✅ **Selected**: خلفية وردية + علامة ✓
- 🚫 **Disabled**: شفافية 50% + cursor معطل

### 3. **الانتقالات:**
```css
transition: all 0.3s ease;
```
كل التغييرات تحدث بسلاسة!

---

## 📋 الحالات الخاصة

### 1. **محاولة اختيار أكثر من 3:**
```
✅ السبب الأول
✅ السبب الثاني  
✅ السبب الثالث
🚫 السبب الرابع ← معطل تلقائياً
🚫 السبب الخامس ← معطل تلقائياً
⚠️ "لقد وصلت للحد الأقصى (3 أسباب)"
```

### 2. **إلغاء اختيار سبب:**
```
عند إلغاء أحد الأسباب:
- ✅ العداد ينخفض
- ✅ التحذير يختفي
- ✅ الخيارات المعطلة تُفعّل
- ✅ اللون يرجع للأزرق
```

### 3. **بدون اختيار أي سبب:**
```
- العقد يُلغى بدون سبب محدد
- cancellation_reason = NULL
- يمكن إضافة الأسباب في التفاصيل الإضافية
```

---

## 🛠️ الملفات المعدلة

| الملف | التغيير |
|------|---------|
| `dashboard/models.py` | ✅ تحديث max_length إلى 500 + إضافة دالة العرض |
| `dashboard/forms.py` | ✅ MultipleChoiceField + validation + save logic |
| `templates/dashboard/lease_cancel_form.html` | ✅ Checkboxes + عداد + JavaScript تفاعلي |
| Database | ✅ ALTER TABLE ... MODIFY ... VARCHAR(500) |

---

## ✅ الفوائد

### 1. **دقة أعلى:**
- يمكن توثيق أسباب متعددة لنفس العقد
- مثال: عدم دفع + مخالفة شروط

### 2. **تحليل أفضل:**
- معرفة الأسباب الأكثر تكراراً
- تتبع التوجهات (مثلاً: زيادة في عدم الدفع)

### 3. **مرونة:**
- سبب واحد؟ ممكن ✓
- سببان؟ ممكن ✓
- ثلاثة أسباب؟ ممكن ✓
- أكثر من 3؟ ممنوع ✗

### 4. **تجربة مستخدم ممتازة:**
- عداد واضح
- تحذيرات فورية
- تعطيل تلقائي عند الحد الأقصى
- انتقالات سلسة

---

## 🚀 الاستخدام

```
1. افتح العقد المراد إلغاؤه
2. اضغط "استمارة إلغاء العقد"
3. اختر حتى 3 أسباب (checkboxes)
4. راقب العداد: 0/3 → 1/3 → 2/3 → 3/3
5. عند 3/3 → باقي الخيارات تُعطّل تلقائياً
6. أضف تفاصيل إضافية
7. اضغط "تأكيد الإلغاء"
```

---

## 📊 إحصائية سريعة

```python
# عدد العقود الملغاة بـ سبب واحد
single_reason = Lease.objects.filter(
    status='cancelled',
    cancellation_reason__isnull=False
).exclude(
    cancellation_reason__contains=','
).count()

# عدد العقود الملغاة بـ أسباب متعددة
multiple_reasons = Lease.objects.filter(
    status='cancelled',
    cancellation_reason__contains=','
).count()

print(f'سبب واحد: {single_reason}')
print(f'أسباب متعددة: {multiple_reasons}')
```

---

**التحديث:** 22 أكتوبر 2025  
**الحالة:** ✅ جاهز ومُختبَر  
**الميزة:** اختيار حتى 3 أسباب لإلغاء العقد مع واجهة تفاعلية ذكية! 🎉

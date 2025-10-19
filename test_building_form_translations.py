#!/usr/bin/env python3
"""
اختبار ترجمات صفحة نموذج المباني
"""

import os
import django
from django.conf import settings

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rent_management.settings')
django.setup()

from django.utils.translation import gettext as _, activate

def test_building_form_translations():
    """اختبار ترجمات صفحة نموذج المباني"""
    print("🏢 اختبار ترجمات صفحة نموذج المباني")
    print("=" * 50)
    
    # قائمة النصوص في صفحة نموذج المباني
    building_form_texts = [
        "أضف مبنى جديد إلى النظام بسهولة",
        "العودة إلى القائمة", 
        "معلومات المبنى الجديد",
        "اسم واضح للمبنى",
        "أمثلة على أسماء المباني:",
        "مبنى الأعمال المركزي",
        "برج الخليج التجاري",
        "مجمع الوادي السكني",
        "نصائح لكتابة العنوان:",
        "اذكر اسم الشارع والحي",
        "أضف رقم المبنى إن وجد",
        "حدد المدينة والمنطقة",
        "يمكن إضافة معالم قريبة للتوضيح",
        "معاينة المبنى",
        "اسم المبنى سيظهر هنا",
        "عنوان المبنى سيظهر هنا",
        "حفظ التعديلات",
        "حفظ المبنى",
        "إلغاء"
    ]
    
    print("\n🇸🇦 النصوص العربية (الافتراضية):")
    activate('ar')
    for text in building_form_texts[:3]:  # عرض أول 3 نصوص
        print(f"  {text}: {_(text)}")
    
    print("\n🇺🇸 الترجمات الإنجليزية:")
    activate('en')
    for text in building_form_texts:
        translation = _(text)
        status = "✅" if translation != text else "❌"
        print(f"  {status} {text}")
        if translation != text:
            print(f"      → {translation}")
    
    # حساب الإحصائيات
    translated_count = sum(1 for text in building_form_texts if _(text) != text)
    total_count = len(building_form_texts)
    percentage = (translated_count / total_count) * 100
    
    print(f"\n📊 إحصائيات الترجمة:")
    print(f"  المترجم: {translated_count}/{total_count}")
    print(f"  النسبة: {percentage:.1f}%")
    
    if percentage == 100:
        print("\n🎉 جميع نصوص صفحة نموذج المباني مترجمة!")
        print("\n🔍 الترجمات المطبقة:")
        print("  • أضف مبنى جديد إلى النظام بسهولة → Add a new building to the system easily")
        print("  • العودة إلى القائمة → Back to List")
        print("  • معلومات المبنى الجديد → New Building Information")
        print("  • معاينة المبنى → Building Preview")
        print("  • حفظ التعديلات → Save Changes")
        print("  • حفظ المبنى → Save Building")
    else:
        print(f"\n⚠️  يحتاج {total_count - translated_count} نص إضافي للترجمة")

if __name__ == "__main__":
    test_building_form_translations()

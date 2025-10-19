#!/usr/bin/env python3
"""
اختبار ترجمات القائمة الجانبية
"""

import os
import django
from django.conf import settings

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rent_management.settings')
django.setup()

from django.utils.translation import gettext as _, activate

def test_sidebar_translations():
    """اختبار ترجمات القائمة الجانبية"""
    print("🧪 اختبار ترجمات القائمة الجانبية")
    print("=" * 50)
    
    # قائمة النصوص في القائمة الجانبية
    sidebar_texts = [
        "لوحة المعلومات",
        "ادارة الايجارات", 
        "إدارة العقارات",
        "المباني",
        "الوحدات", 
        "العقود",
        "المالية",
        "المدفوعات",
        "المصاريف",
        "الفواتير",
        "التأمينات",
        "إدارة الشيكات",
        "إنذارات عدم السداد",
        "العمليات",
        "المستأجرين",
        "الصيانة",
        "إدارة المستخدمين",
        "التقارير",
        "الربح والخسارة (شهري)",
        "الربح والخسارة (سنوي)",
        "نسبة الإشغال",
        "الاعدادات",
        "نسخة احتياطية الآن",
        "تسجيل الخروج"
    ]
    
    print("\n🇸🇦 النصوص العربية (الافتراضية):")
    activate('ar')
    for text in sidebar_texts[:5]:  # عرض أول 5 نصوص
        print(f"  {text}: {_(text)}")
    
    print("\n🇺🇸 الترجمات الإنجليزية:")
    activate('en')
    for text in sidebar_texts:
        translation = _(text)
        status = "✅" if translation != text else "❌"
        print(f"  {status} {text} -> {translation}")
    
    # حساب الإحصائيات
    translated_count = sum(1 for text in sidebar_texts if _(text) != text)
    total_count = len(sidebar_texts)
    percentage = (translated_count / total_count) * 100
    
    print(f"\n📊 إحصائيات الترجمة:")
    print(f"  المترجم: {translated_count}/{total_count}")
    print(f"  النسبة: {percentage:.1f}%")
    
    if percentage == 100:
        print("\n🎉 جميع نصوص القائمة الجانبية مترجمة!")
    else:
        print(f"\n⚠️  يحتاج {total_count - translated_count} نص إضافي للترجمة")

if __name__ == "__main__":
    test_sidebar_translations()

#!/usr/bin/env python3
"""
اختبار ترجمات صفحة قائمة المباني
"""

import os
import django
from django.conf import settings

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rent_management.settings')
django.setup()

from django.utils.translation import gettext as _, activate

def test_building_list_translations():
    """اختبار ترجمات صفحة قائمة المباني"""
    print("🏢 اختبار ترجمات صفحة قائمة المباني")
    print("=" * 50)
    
    # قائمة النصوص في صفحة قائمة المباني
    building_list_texts = [
        "إدارة المباني",
        "إدارة وعرض جميع المباني ووحداتها ونسب الإشغال",
        "تصدير Excel",
        "إضافة مبنى جديد",
        "إجمالي الوحدات",
        "الوحدات المشغولة",
        "نسبة الإشغال",
        "إشغال ممتاز",
        "إشغال متوسط",
        "إشغال منخفض",
        "لا توجد مباني",
        "لم يتم العثور على أي مباني. ابدأ بإضافة مبنى جديد.",
        "الأولى",
        "السابق",
        "صفحة",
        "من",
        "التالي",
        "الأخيرة",
        "تعديل",
        "حذف"
    ]
    
    print("\n🇸🇦 النصوص العربية (الافتراضية):")
    activate('ar')
    for text in building_list_texts[:3]:  # عرض أول 3 نصوص
        print(f"  {text}: {_(text)}")
    
    print("\n🇺🇸 الترجمات الإنجليزية:")
    activate('en')
    for text in building_list_texts:
        translation = _(text)
        status = "✅" if translation != text else "❌"
        print(f"  {status} {text}")
        if translation != text:
            print(f"      → {translation}")
    
    # حساب الإحصائيات
    translated_count = sum(1 for text in building_list_texts if _(text) != text)
    total_count = len(building_list_texts)
    percentage = (translated_count / total_count) * 100
    
    print(f"\n📊 إحصائيات الترجمة:")
    print(f"  المترجم: {translated_count}/{total_count}")
    print(f"  النسبة: {percentage:.1f}%")
    
    if percentage == 100:
        print("\n🎉 جميع نصوص صفحة قائمة المباني مترجمة!")
        print("\n🔍 الترجمات الرئيسية:")
        print("  • إدارة المباني → Building Management")
        print("  • إدارة وعرض جميع المباني ووحداتها ونسب الإشغال → Manage and view all buildings, their units and occupancy rates")
        print("  • تصدير Excel → Export Excel")
        print("  • إجمالي الوحدات → Total Units")
        print("  • الوحدات المشغولة → Occupied Units")
        print("  • نسبة الإشغال → Occupancy Rate")
        print("  • إشغال ممتاز → Excellent Occupancy")
    else:
        print(f"\n⚠️  يحتاج {total_count - translated_count} نص إضافي للترجمة")

if __name__ == "__main__":
    test_building_list_translations()

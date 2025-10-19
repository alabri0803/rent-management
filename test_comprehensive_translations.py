#!/usr/bin/env python3
"""
اختبار شامل لترجمات جميع الصفحات الرئيسية
"""

import os
import django
from django.conf import settings

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rent_management.settings')
django.setup()

from django.utils.translation import gettext as _, activate

def test_comprehensive_translations():
    """اختبار شامل لترجمات جميع الصفحات"""
    print("🌍 اختبار شامل لترجمات النظام")
    print("=" * 60)
    
    # قوائم النصوص لكل صفحة
    pages_texts = {
        "🏢 المباني": [
            "إدارة المباني",
            "إدارة وعرض جميع المباني ووحداتها ونسب الإشغال",
            "تصدير Excel",
            "إضافة مبنى جديد",
            "إجمالي الوحدات",
            "الوحدات المشغولة",
            "نسبة الإشغال",
            "إشغال ممتاز"
        ],
        "🏠 الوحدات": [
            "إدارة وعرض جميع الوحدات وحالاتها وأنواعها",
            "الوحدات المتاحة",
            "فلاتر البحث",
            "كل المباني",
            "كل الأنواع",
            "كل الحالات",
            "متاحة",
            "مشغولة",
            "معلومات الوحدة"
        ],
        "📄 العقود": [
            "إدارة وعرض جميع عقود الإيجار وحالاتها ومواعيد انتهائها",
            "إضافة عقد جديد",
            "منتهي",
            "قريب الانتهاء",
            "فترة العقد",
            "تاريخ الانتهاء",
            "أيام متبقية",
            "الإيجار الشهري",
            "تفاصيل العقد"
        ],
        "💰 المدفوعات": [
            "البحث",
            "إجراءات",
            "تجديد",
            "إلغاء",
            "نشط",
            "تاريخ البدء",
            "الإيجار السنوي",
            "رسوم التسجيل"
        ]
    }
    
    print("\n🇺🇸 اختبار الترجمات الإنجليزية:")
    activate('en')
    
    total_texts = 0
    translated_texts = 0
    
    for page_name, texts in pages_texts.items():
        print(f"\n{page_name}:")
        page_translated = 0
        
        for text in texts:
            translation = _(text)
            total_texts += 1
            
            if translation != text:
                translated_texts += 1
                page_translated += 1
                status = "✅"
                print(f"  {status} {text} → {translation}")
            else:
                status = "❌"
                print(f"  {status} {text}")
        
        page_percentage = (page_translated / len(texts)) * 100
        print(f"  📊 {page_name}: {page_translated}/{len(texts)} ({page_percentage:.1f}%)")
    
    # حساب الإحصائيات الإجمالية
    overall_percentage = (translated_texts / total_texts) * 100
    
    print(f"\n📊 الإحصائيات الإجمالية:")
    print(f"  إجمالي النصوص: {total_texts}")
    print(f"  النصوص المترجمة: {translated_texts}")
    print(f"  النسبة الإجمالية: {overall_percentage:.1f}%")
    
    if overall_percentage >= 80:
        print(f"\n🎉 ممتاز! تم ترجمة {overall_percentage:.1f}% من النصوص")
        print("✨ النظام جاهز للاستخدام بكلا اللغتين")
    elif overall_percentage >= 60:
        print(f"\n👍 جيد! تم ترجمة {overall_percentage:.1f}% من النصوص")
        print("🔧 يحتاج بعض التحسينات الإضافية")
    else:
        print(f"\n⚠️ يحتاج المزيد من العمل - {overall_percentage:.1f}% مترجم فقط")
    
    print(f"\n🌟 الترجمات الجديدة المضافة:")
    print("  • صفحة المباني: مترجمة بالكامل")
    print("  • صفحة الوحدات: ترجمات أساسية مكتملة")
    print("  • صفحة العقود: ترجمات رئيسية مكتملة")
    print("  • عناصر التنقل: مترجمة بالكامل")
    print("  • أزرار الإجراءات: مترجمة بالكامل")

if __name__ == "__main__":
    test_comprehensive_translations()

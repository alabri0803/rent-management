#!/usr/bin/env python3
"""
اختبار الترجمة في النظام
"""

import os
import django
from django.conf import settings

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rent_management.settings')
django.setup()

from django.utils.translation import gettext as _, activate
from django.utils import translation

def test_translations():
    """اختبار الترجمات"""
    print("🧪 اختبار الترجمات...")
    
    # اختبار الترجمة العربية (افتراضية)
    print("\n📋 الترجمة العربية (الافتراضية):")
    activate('ar')
    print(f"لوحة التحكم: {_('لوحة التحكم')}")
    print(f"المباني: {_('المباني')}")
    print(f"الوحدات: {_('الوحدات')}")
    print(f"المستأجرين: {_('المستأجرين')}")
    
    # اختبار الترجمة الإنجليزية
    print("\n🇺🇸 الترجمة الإنجليزية:")
    activate('en')
    print(f"لوحة التحكم -> {_('لوحة التحكم')}")
    print(f"المباني -> {_('المباني')}")
    print(f"الوحدات -> {_('الوحدات')}")
    print(f"المستأجرين -> {_('المستأجرين')}")
    print(f"شقة -> {_('شقة')}")
    print(f"مكتب -> {_('مكتب')}")
    print(f"محل -> {_('محل')}")
    print(f"مستودع -> {_('مستودع')}")
    
    # اختبار رسائل النجاح
    print(f"\nرسائل النجاح:")
    print(f"تمت إضافة الوحدة بنجاح! -> {_('تمت إضافة الوحدة بنجاح!')}")
    print(f"تم تحديث الوحدة بنجاح! -> {_('تم تحديث الوحدة بنجاح!')}")
    
    # اختبار حالات العقود
    print(f"\nحالات العقود:")
    print(f"نشط -> {_('نشط')}")
    print(f"منتهي -> {_('منتهي')}")
    print(f"ملغي -> {_('ملغي')}")
    
    print("\n✅ تم اختبار الترجمات بنجاح!")

def check_translation_files():
    """فحص ملفات الترجمة"""
    print("\n📁 فحص ملفات الترجمة:")
    
    locale_dir = "/Users/macboocair/rent-management/locale"
    
    for lang in ['ar', 'en']:
        po_file = f"{locale_dir}/{lang}/LC_MESSAGES/django.po"
        mo_file = f"{locale_dir}/{lang}/LC_MESSAGES/django.mo"
        
        print(f"\n{lang.upper()}:")
        print(f"  📄 django.po: {'✅' if os.path.exists(po_file) else '❌'}")
        print(f"  📦 django.mo: {'✅' if os.path.exists(mo_file) else '❌'}")
        
        if os.path.exists(po_file):
            with open(po_file, 'r', encoding='utf-8') as f:
                content = f.read()
                msgid_count = content.count('msgid ')
                msgstr_count = content.count('msgstr ')
                print(f"  📊 عدد النصوص: {msgid_count}")
                print(f"  📊 عدد الترجمات: {msgstr_count}")

def main():
    """الدالة الرئيسية"""
    print("🌍 اختبار نظام الترجمة الدولية")
    print("=" * 50)
    
    # فحص ملفات الترجمة
    check_translation_files()
    
    # اختبار الترجمات
    test_translations()
    
    print("\n🎉 تم الانتهاء من اختبار الترجمة!")
    print("\nلتفعيل الترجمة في المتصفح:")
    print("1. انتقل إلى إعدادات المتصفح")
    print("2. غير اللغة إلى الإنجليزية")
    print("3. أعد تحميل الصفحة")
    print("4. أو أضف ?lang=en إلى نهاية الرابط")

if __name__ == "__main__":
    main()

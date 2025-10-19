#!/usr/bin/env python3
"""
نسكريپت لإصلاح ملف الترجمة وإزالة الأخطاء
"""

import os
import re

def fix_po_file(po_file_path):
    """إصلاح ملف .po وإزالة الأخطاء"""
    if not os.path.exists(po_file_path):
        print(f"ملف الترجمة غير موجود: {po_file_path}")
        return False
    
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إزالة العلامات fuzzy
    content = re.sub(r'#, fuzzy\n', '', content)
    content = re.sub(r'#\| msgid.*\n', '', content)
    
    # إصلاح رأس الملف
    content = content.replace('#, fuzzy', '')
    content = content.replace('YEAR-MO-DA HO:MI+ZONE', '2025-10-19 23:15+0400')
    content = content.replace('FULL NAME <EMAIL@ADDRESS>', 'Rent Management System <admin@rentmanagement.com>')
    content = content.replace('LANGUAGE <LL@li.org>', 'English <en@li.org>')
    content = content.replace('"Language: \\n"', '"Language: en\\n"')
    
    # حفظ الملف المحدث
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ تم إصلاح ملف الترجمة: {po_file_path}")
    return True

def main():
    """الدالة الرئيسية"""
    print("🔧 بدء إصلاح ملف الترجمة...")
    
    # مسار ملف الترجمة الإنجليزية
    en_po_path = "/Users/macboocair/rent-management/locale/en/LC_MESSAGES/django.po"
    
    # إصلاح ملف الترجمة
    if fix_po_file(en_po_path):
        print("\n✅ تم إصلاح ملف الترجمة بنجاح!")
        print("يمكنك الآن تشغيل: python3 manage.py compilemessages")
    else:
        print("\n❌ فشل في إصلاح ملف الترجمة")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

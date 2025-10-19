#!/usr/bin/env python3
"""
إصلاح النصوص المكررة في ملف الترجمة
"""

import re

def fix_duplicates():
    """إزالة النصوص المكررة من ملف الترجمة"""
    po_file = "/Users/macboocair/rent-management/locale/en/LC_MESSAGES/django.po"
    
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # تقسيم المحتوى إلى entries
    entries = re.split(r'\n(?=msgid)', content)
    
    # إزالة المكررات
    seen_msgids = set()
    unique_entries = []
    
    for entry in entries:
        if entry.strip():
            # استخراج msgid
            msgid_match = re.search(r'msgid "(.*?)"', entry)
            if msgid_match:
                msgid = msgid_match.group(1)
                if msgid not in seen_msgids:
                    seen_msgids.add(msgid)
                    unique_entries.append(entry)
                else:
                    print(f"تم حذف النص المكرر: {msgid}")
            else:
                # إضافة الرأس والمحتوى غير msgid
                unique_entries.append(entry)
    
    # إعادة تجميع المحتوى
    new_content = '\n'.join(unique_entries)
    
    # حفظ الملف المحدث
    with open(po_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ تم إصلاح ملف الترجمة وإزالة المكررات")

if __name__ == "__main__":
    fix_duplicates()

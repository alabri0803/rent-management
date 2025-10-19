#!/usr/bin/env python3
"""
إنشاء ملف ترجمة نظيف وصحيح
"""

import os

# محتوى ملف الترجمة الأساسي
PO_HEADER = '''# Arabic to English translations for Rent Management System
# Copyright (C) 2025 Rent Management System
# This file is distributed under the same license as the Rent Management System package.
# Admin <admin@rentmanagement.com>, 2025.
#
msgid ""
msgstr ""
"Project-Id-Version: Rent Management System 1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2025-10-19 23:15+0400\\n"
"PO-Revision-Date: 2025-10-19 23:15+0400\\n"
"Last-Translator: Admin <admin@rentmanagement.com>\\n"
"Language-Team: English <en@li.org>\\n"
"Language: en\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

'''

# الترجمات الأساسية
BASIC_TRANSLATIONS = [
    # الواجهة الأساسية
    ('لوحة التحكم', 'Dashboard'),
    ('الرئيسية', 'Home'),
    ('تسجيل الدخول', 'Login'),
    ('تسجيل الخروج', 'Logout'),
    
    # العمليات الأساسية
    ('إضافة', 'Add'),
    ('تعديل', 'Edit'),
    ('حذف', 'Delete'),
    ('حفظ', 'Save'),
    ('إلغاء', 'Cancel'),
    ('بحث', 'Search'),
    ('تفاصيل', 'Details'),
    ('عرض', 'View'),
    ('طباعة', 'Print'),
    
    # الكيانات الأساسية
    ('المباني', 'Buildings'),
    ('مبنى', 'Building'),
    ('اسم المبنى', 'Building Name'),
    ('العنوان', 'Address'),
    
    ('الوحدات', 'Units'),
    ('وحدة', 'Unit'),
    ('رقم الوحدة', 'Unit Number'),
    ('نوع الوحدة', 'Unit Type'),
    ('الطابق', 'Floor'),
    ('متاحة للإيجار', 'Available for Rent'),
    
    # أنواع الوحدات
    ('شقة', 'Apartment'),
    ('وحدة سكنية', 'Residential Unit'),
    ('مكتب', 'Office'),
    ('مساحة عمل مكتبية', 'Office Workspace'),
    ('محل', 'Shop'),
    ('محل تجاري', 'Commercial Shop'),
    ('مستودع', 'Warehouse'),
    ('معرض', 'Showroom'),
    
    # المستأجرين
    ('المستأجرين', 'Tenants'),
    ('مستأجر', 'Tenant'),
    ('اسم المستأجر', 'Tenant Name'),
    ('نوع المستأجر', 'Tenant Type'),
    ('رقم الهاتف', 'Phone Number'),
    ('البريد الإلكتروني', 'Email'),
    
    # أنواع المستأجرين
    ('فرد', 'Individual'),
    ('شخص طبيعي', 'Natural Person'),
    ('شركة', 'Company'),
    ('كيان قانوني', 'Legal Entity'),
    ('مؤسسة', 'Corporation'),
    ('شراكة', 'Partnership'),
    
    # العقود
    ('عقود الإيجار', 'Lease Contracts'),
    ('عقد إيجار', 'Lease Contract'),
    ('رقم العقد', 'Contract Number'),
    ('مبلغ الإيجار الشهري', 'Monthly Rent Amount'),
    ('تاريخ بدء العقد', 'Contract Start Date'),
    ('تاريخ انتهاء العقد', 'Contract End Date'),
    ('حالة العقد', 'Contract Status'),
    
    # حالات العقود
    ('نشط', 'Active'),
    ('قريب الانتهاء', 'Expiring Soon'),
    ('منتهي', 'Expired'),
    ('تم تجديد', 'Renewed'),
    ('ملغي', 'Cancelled'),
    
    # المدفوعات
    ('المدفوعات', 'Payments'),
    ('دفعة', 'Payment'),
    ('المبلغ', 'Amount'),
    ('تاريخ الدفع', 'Payment Date'),
    ('طريقة الدفع', 'Payment Method'),
    
    # طرق الدفع
    ('نقداً', 'Cash'),
    ('شيك', 'Cheque'),
    ('تحويل بنكي', 'Bank Transfer'),
    
    # الشركة
    ('ملف الشركة', 'Company Profile'),
    ('اسم الشركة', 'Company Name'),
    ('هوية الشركة', 'Company ID'),
    ('الشعار', 'Logo'),
    ('البريد الإلكتروني للتواصل', 'Contact Email'),
    ('الهاتف للتواصل', 'Contact Phone'),
    
    # رسائل النجاح
    ('تمت إضافة الوحدة بنجاح!', 'Unit added successfully!'),
    ('تم تحديث الوحدة بنجاح!', 'Unit updated successfully!'),
    ('تم حذف الوحدة بنجاح', 'Unit deleted successfully'),
    ('تمت إضافة المستأجر بنجاح!', 'Tenant added successfully!'),
    ('تم تحديث بيانات المستأجر بنجاح!', 'Tenant data updated successfully!'),
    ('تم حذف المستأجر بنجاح', 'Tenant deleted successfully'),
    ('تمت إضافة المبنى بنجاح!', 'Building added successfully!'),
    ('تم تحديث المبنى بنجاح!', 'Building updated successfully!'),
    ('تم حذف المبنى بنجاح', 'Building deleted successfully'),
    
    # رسائل الأخطاء
    ('حدث خطأ. حاول مرة أخرى', 'An error occurred. Please try again'),
    ('كلمة المرور غير صحيحة', 'Incorrect password'),
    ('اسم المستخدم أو كلمة المرور غير صحيحة', 'Invalid username or password'),
    
    # العناوين
    ('إضافة وحدة جديدة', 'Add New Unit'),
    ('تعديل الوحدة', 'Edit Unit'),
    ('إضافة مستأجر جديد', 'Add New Tenant'),
    ('تعديل بيانات المستأجر', 'Edit Tenant Data'),
    ('إضافة مبنى جديد', 'Add New Building'),
    ('تعديل المبنى', 'Edit Building'),
    ('تفاصيل المستأجر', 'Tenant Details'),
    ('تفاصيل العقد', 'Contract Details'),
    ('تفاصيل الوحدة', 'Unit Details'),
    ('تفاصيل المبنى', 'Building Details'),
]

def create_clean_po_file(po_file_path):
    """إنشاء ملف .po نظيف"""
    # إنشاء المجلد إذا لم يكن موجوداً
    os.makedirs(os.path.dirname(po_file_path), exist_ok=True)
    
    with open(po_file_path, 'w', encoding='utf-8') as f:
        # كتابة الرأس
        f.write(PO_HEADER)
        
        # كتابة الترجمات
        for arabic, english in BASIC_TRANSLATIONS:
            f.write(f'msgid "{arabic}"\n')
            f.write(f'msgstr "{english}"\n\n')
    
    print(f"✅ تم إنشاء ملف ترجمة نظيف: {po_file_path}")
    print(f"📊 تم إضافة {len(BASIC_TRANSLATIONS)} ترجمة")

def main():
    """الدالة الرئيسية"""
    print("🚀 إنشاء ملف ترجمة نظيف...")
    
    # مسار ملف الترجمة الإنجليزية
    en_po_path = "/Users/macboocair/rent-management/locale/en/LC_MESSAGES/django.po"
    
    # إنشاء ملف الترجمة النظيف
    create_clean_po_file(en_po_path)
    
    print("\n✅ تم إنشاء ملف الترجمة بنجاح!")
    print("الخطوات التالية:")
    print("1. قم بتشغيل: python3 manage.py compilemessages --locale=en")
    print("2. أعد تشغيل الخادم لتطبيق التغييرات")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

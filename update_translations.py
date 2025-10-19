#!/usr/bin/env python3
"""
نسكريپت لتحديث ملفات الترجمة تلقائياً
يقوم بإضافة الترجمات الإنجليزية للنصوص العربية
"""

import os
import re
import sys

# قاموس الترجمات الأساسية
TRANSLATIONS = {
    # رسائل المصادقة
    "اسم المستخدم وكلمة المرور مطلوبان": "Username and password are required",
    "اسم المستخدم أو كلمة المرور غير صحيحة": "Invalid username or password",
    "يرجى إدخال رقم هاتف عماني يبدأ بـ +968 ويتبعه 8 أرقام": "Please enter an Omani phone number starting with +968 followed by 8 digits",
    "رقم الهاتف مطلوب": "Phone number is required",
    "رمز التحقق مطلوب": "Verification code is required",
    "رمز التحقق غير صحيح أو منتهي الصلاحية": "Invalid or expired verification code",
    "لا يوجد مستخدم مسجل بهذا الرقم": "No user registered with this number",
    "تم تجاوز الحد المسموح من محاولات إرسال الرمز. حاول مرة أخرى لاحقاً": "Rate limit exceeded for sending codes. Please try again later",
    "فشل في إرسال الرسالة. حاول مرة أخرى": "Failed to send message. Please try again",
    "تم إرسال رمز التحقق إلى رقم هاتفك": "Verification code sent to your phone number",
    "حدث خطأ. حاول مرة أخرى": "An error occurred. Please try again",
    "رقم الهاتف ورمز التحقق مطلوبان": "Phone number and verification code are required",
    "تم تسجيل الدخول بنجاح": "Login successful",
    
    # النماذج والحقول
    "اسم الشركة": "Company Name",
    "هوية الشركة": "Company ID",
    "رقم السجل التجاري أو الهوية الضريبية": "Commercial registration number or tax ID",
    "الشعار": "Logo",
    "البريد الإلكتروني للتواصل": "Contact Email",
    "الهاتف للتواصل": "Contact Phone",
    "العنوان": "Address",
    "ملف الشركة": "Company Profile",
    "اسم المبنى": "Building Name",
    "مبنى": "Building",
    "المباني": "Buildings",
    "رقم الوحدة": "Unit Number",
    "نوع الوحدة": "Unit Type",
    "الطابق": "Floor",
    "متاحة للإيجار": "Available for Rent",
    "وحدة": "Unit",
    "الوحدات": "Units",
    
    # أنواع الوحدات
    "شقة": "Apartment",
    "وحدة سكنية": "Residential Unit",
    "مكتب": "Office",
    "مساحة عمل مكتبية": "Office Workspace",
    "محل": "Shop",
    "محل تجاري": "Commercial Shop",
    "مستودع": "Warehouse",
    "معرض": "Showroom",
    
    # أنواع المستأجرين
    "فرد": "Individual",
    "شخص طبيعي": "Natural Person",
    "شركة": "Company",
    "كيان قانوني": "Legal Entity",
    "مؤسسة": "Corporation",
    "شراكة": "Partnership",
    
    # المستأجرين
    "حساب المستخدم": "User Account",
    "اربط المستأجر بحساب مستخدم لتسجيل الدخول إلى البوابة.": "Link tenant to a user account to login to the portal.",
    "اسم المستأجر": "Tenant Name",
    "نوع المستأجر": "Tenant Type",
    "رقم الهاتف": "Phone Number",
    "البريد الإلكتروني": "Email",
    "المفوض بالتوقيع": "Authorized Signatory",
    "يُملأ فقط في حال كان المستأجر شركة": "Fill only if tenant is a company",
    "تقييم العميل": "Customer Rating",
    "من 1 إلى 5 نجوم.": "From 1 to 5 stars.",
    "مستأجر": "Tenant",
    "المستأجرين": "Tenants",
    
    # العقود
    "نشط": "Active",
    "قريب الانتهاء": "Expiring Soon",
    "منتهي": "Expired",
    "تم تجديد": "Renewed",
    "ملغي": "Cancelled",
    "الوحدة": "Unit",
    "المستأجر": "Tenant",
    "رقم العقد": "Contract Number",
    "رقم نموذج العقد": "Contract Form Number",
    "مبلغ الإيجار الشهري": "Monthly Rent Amount",
    "تاريخ بدء العقد": "Contract Start Date",
    "تاريخ انتهاء العقد": "Contract End Date",
    "رقم عداد الكهرباء": "Electricity Meter Number",
    "رقم عداد المياه": "Water Meter Number",
    "حالة العقد": "Contract Status",
    "رسوم المكتب": "Office Fee",
    "الرسوم الإدارية": "Administrative Fee",
    "رسوم تسجيل العقد (3%)": "Contract Registration Fee (3%)",
    "تاريخ الإلغاء": "Cancellation Date",
    "سبب الإلغاء": "Cancellation Reason",
    "عقد إيجار": "Lease Contract",
    "عقود الإيجار": "Lease Contracts",
    
    # المدفوعات
    "المبلغ": "Amount",
    "تاريخ الدفع": "Payment Date",
    "طريقة الدفع": "Payment Method",
    "نقداً": "Cash",
    "شيك": "Cheque",
    "تحويل بنكي": "Bank Transfer",
    "حالة الشيك": "Cheque Status",
    "مقبول": "Accepted",
    "مرتجع": "Returned",
    "سبب إرجاع الشيك": "Cheque Return Reason",
    "ملاحظات": "Notes",
    "دفعة": "Payment",
    "المدفوعات": "Payments",
    
    # المصروفات
    "وصف المصروف": "Expense Description",
    "تاريخ المصروف": "Expense Date",
    "نوع المصروف": "Expense Type",
    "صيانة": "Maintenance",
    "كهرباء": "Electricity",
    "مياه": "Water",
    "تنظيف": "Cleaning",
    "أمن": "Security",
    "أخرى": "Other",
    "مصروف": "Expense",
    "المصروفات": "Expenses",
    
    # الصيانة
    "طلب صيانة": "Maintenance Request",
    "طلبات الصيانة": "Maintenance Requests",
    "وصف المشكلة": "Problem Description",
    "حالة الطلب": "Request Status",
    "معلق": "Pending",
    "قيد التنفيذ": "In Progress",
    "مكتمل": "Completed",
    "ملغي": "Cancelled",
    "الأولوية": "Priority",
    "عادية": "Normal",
    "عالية": "High",
    "عاجلة": "Urgent",
    "تاريخ الطلب": "Request Date",
    "تاريخ الإنجاز": "Completion Date",
    
    # الواجهة العامة
    "لوحة التحكم": "Dashboard",
    "الرئيسية": "Home",
    "تسجيل الدخول": "Login",
    "تسجيل الخروج": "Logout",
    "إضافة": "Add",
    "تعديل": "Edit",
    "حذف": "Delete",
    "حفظ": "Save",
    "إلغاء": "Cancel",
    "بحث": "Search",
    "تصفية": "Filter",
    "تصدير": "Export",
    "طباعة": "Print",
    "تفاصيل": "Details",
    "قائمة": "List",
    "جديد": "New",
    "تحديث": "Update",
    "عرض": "View",
    "إجراءات": "Actions",
    "حالة": "Status",
    "تاريخ": "Date",
    "اسم": "Name",
    "نوع": "Type",
    "مبلغ": "Amount",
    "وصف": "Description",
    "ملاحظات": "Notes",
    
    # رسائل النجاح والأخطاء
    "تم إنشاء نسخة احتياطية بنجاح": "Backup created successfully",
    "فشل إنشاء النسخة الاحتياطية": "Failed to create backup",
    "تم تسجيل الخروج": "Logged out successfully",
    "الملف المحدد غير موجود": "Selected file does not exist",
    "الرجاء اختيار أو رفع ملف النسخة الاحتياطية": "Please select or upload backup file",
    "تمت عملية الاسترجاع بنجاح": "Restore completed successfully",
    "فشلت عملية الاسترجاع. الرجاء التحقق من الملف والصلاحيات": "Restore failed. Please check file and permissions",
    "تم إظهار الحركات المالية بنجاح": "Financial movements displayed successfully",
    "كلمة المرور غير صحيحة": "Incorrect password",
    "تم إخفاء الحركات المالية": "Financial movements hidden",
    "تمت إضافة الوحدة بنجاح!": "Unit added successfully!",
    "تم تحديث الوحدة بنجاح!": "Unit updated successfully!",
    "تم حذف الوحدة بنجاح": "Unit deleted successfully",
    "تمت إضافة المستأجر بنجاح!": "Tenant added successfully!",
    "تم تحديث بيانات المستأجر بنجاح!": "Tenant data updated successfully!",
    "تم حذف المستأجر بنجاح": "Tenant deleted successfully",
    "تمت إضافة المبنى بنجاح!": "Building added successfully!",
    "تم تحديث المبنى بنجاح!": "Building updated successfully!",
    "تم حذف المبنى بنجاح": "Building deleted successfully",
    "تم تحديث تقييم العميل": "Customer rating updated",
    "حدث خطأ في حفظ البيانات. يرجى التحقق من المعلومات المدخلة": "Error saving data. Please check entered information",
    
    # العناوين
    "إضافة وحدة جديدة": "Add New Unit",
    "تعديل الوحدة": "Edit Unit",
    "إضافة مستأجر جديد": "Add New Tenant",
    "تعديل بيانات المستأجر": "Edit Tenant Data",
    "إضافة مبنى جديد": "Add New Building",
    "تعديل المبنى": "Edit Building",
    "تفاصيل المستأجر": "Tenant Details",
    "تفاصيل العقد": "Contract Details",
    "تفاصيل الوحدة": "Unit Details",
    "تفاصيل المبنى": "Building Details",
    
    # الإحصائيات
    "مشغولة": "Occupied",
    "متاحة": "Available",
    "تجديد": "Renewal",
    "إجمالي": "Total",
    "عدد": "Count",
    "نسبة": "Percentage",
    
    # التقارير
    "كشف حساب شامل للمستأجر": "Comprehensive Tenant Statement",
    "كشف حساب المستأجر": "Tenant Statement",
    "تقرير العقود": "Contracts Report",
    "تقرير المدفوعات": "Payments Report",
    "تقرير المصروفات": "Expenses Report",
    "تقرير الإشغال": "Occupancy Report",
    "فاتورة رسوم التسجيل": "Registration Fee Invoice",
    "فاتورة رسوم التجديد": "Renewal Fee Invoice",
    "استمارة إلغاء العقد": "Contract Cancellation Form",
    "استمارة تجديد العقد": "Contract Renewal Form",
    "سند قبض": "Payment Receipt",
    
    # أخرى
    "يرجى ذكر سبب إلغاء العقد...": "Please state the reason for contract cancellation...",
    "مثال: نسخة من العقد الموقّع": "Example: A copy of the signed contract",
    "مستند": "Document",
    "اختر تاريخ المصروف": "Select expense date",
    "حالة الشيك مطلوبة عند اختيار طريقة الدفع بالشيك": "Cheque status is required when selecting cheque payment method",
    "سبب إرجاع الشيك مطلوب عند اختيار حالة \"مرتجع\"": "Reason for cheque return is required when selecting 'Returned' status",
    "تاريخ انتهاء الاتفاقية يجب أن يكون بعد تاريخ البداية": "Agreement end date must be after start date",
    "مجموع حصة المالك وعمولة المكتب يجب أن يساوي المبلغ المستلم": "Sum of owner's share and office commission must equal received amount",
}

def update_po_file(po_file_path):
    """تحديث ملف .po بالترجمات الجديدة"""
    if not os.path.exists(po_file_path):
        print(f"ملف الترجمة غير موجود: {po_file_path}")
        return False
    
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    updated_count = 0
    
    # تحديث الترجمات الفارغة
    for arabic, english in TRANSLATIONS.items():
        # البحث عن النمط: msgid "النص العربي" \n msgstr ""
        pattern = f'msgid "{re.escape(arabic)}"\nmsgstr ""'
        replacement = f'msgid "{arabic}"\nmsgstr "{english}"'
        
        if pattern in content:
            content = content.replace(pattern, replacement)
            updated_count += 1
            print(f"✅ تم تحديث: {arabic} -> {english}")
    
    # حفظ الملف المحدث
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n🎉 تم تحديث {updated_count} ترجمة في الملف: {po_file_path}")
    return True

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء تحديث ملفات الترجمة...")
    
    # مسار ملف الترجمة الإنجليزية
    en_po_path = "/Users/macboocair/rent-management/locale/en/LC_MESSAGES/django.po"
    
    # تحديث ملف الترجمة
    if update_po_file(en_po_path):
        print("\n✅ تم تحديث ملف الترجمة بنجاح!")
        print("\nالخطوات التالية:")
        print("1. قم بتشغيل: python3 manage.py compilemessages")
        print("2. أعد تشغيل الخادم لتطبيق التغييرات")
    else:
        print("\n❌ فشل في تحديث ملف الترجمة")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

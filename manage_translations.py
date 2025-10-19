#!/usr/bin/env python3
"""
نسكريپت شامل لإدارة الترجمة في نظام إدارة الإيجارات
يقوم بالبحث عن النصوص العربية غير المترجمة وإضافة ترجماتها
"""

import os
import re
import sys
import subprocess
from pathlib import Path

class TranslationManager:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.locale_dir = self.project_root / "locale"
        self.ar_po_file = self.locale_dir / "ar" / "LC_MESSAGES" / "django.po"
        self.en_po_file = self.locale_dir / "en" / "LC_MESSAGES" / "django.po"
        
        # قاموس الترجمات الشامل
        self.translations = {
            # الواجهة الأساسية
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
            
            # الكيانات الأساسية
            "المباني": "Buildings",
            "مبنى": "Building",
            "اسم المبنى": "Building Name",
            "العنوان": "Address",
            "الوحدات": "Units",
            "وحدة": "Unit",
            "رقم الوحدة": "Unit Number",
            "نوع الوحدة": "Unit Type",
            "الطابق": "Floor",
            "متاحة للإيجار": "Available for Rent",
            "المبنى": "Building",
            
            # أنواع الوحدات
            "شقة": "Apartment",
            "وحدة سكنية": "Residential Unit",
            "مكتب": "Office",
            "مساحة عمل مكتبية": "Office Workspace",
            "محل": "Shop",
            "محل تجاري": "Commercial Shop",
            "مستودع": "Warehouse",
            "معرض": "Showroom",
            
            # المستأجرين
            "المستأجرين": "Tenants",
            "مستأجر": "Tenant",
            "اسم المستأجر": "Tenant Name",
            "نوع المستأجر": "Tenant Type",
            "رقم الهاتف": "Phone Number",
            "البريد الإلكتروني": "Email",
            "المفوض بالتوقيع": "Authorized Signatory",
            "تقييم العميل": "Customer Rating",
            "حساب المستخدم": "User Account",
            
            # أنواع المستأجرين
            "فرد": "Individual",
            "شخص طبيعي": "Natural Person",
            "شركة": "Company",
            "كيان قانوني": "Legal Entity",
            "مؤسسة": "Corporation",
            "شراكة": "Partnership",
            
            # العقود
            "عقود الإيجار": "Lease Contracts",
            "عقد إيجار": "Lease Contract",
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
            "المستأجر": "Tenant",
            "الوحدة": "Unit",
            
            # حالات العقود
            "نشط": "Active",
            "قريب الانتهاء": "Expiring Soon",
            "منتهي": "Expired",
            "تم تجديد": "Renewed",
            "ملغي": "Cancelled",
            
            # المدفوعات
            "المدفوعات": "Payments",
            "دفعة": "Payment",
            "المبلغ": "Amount",
            "تاريخ الدفع": "Payment Date",
            "طريقة الدفع": "Payment Method",
            "حالة الشيك": "Cheque Status",
            "مقبول": "Accepted",
            "مرتجع": "Returned",
            "سبب إرجاع الشيك": "Cheque Return Reason",
            "ملاحظات": "Notes",
            
            # طرق الدفع
            "نقداً": "Cash",
            "شيك": "Cheque",
            "تحويل بنكي": "Bank Transfer",
            
            # المصروفات
            "المصروفات": "Expenses",
            "مصروف": "Expense",
            "وصف المصروف": "Expense Description",
            "تاريخ المصروف": "Expense Date",
            "نوع المصروف": "Expense Type",
            "صيانة": "Maintenance",
            "كهرباء": "Electricity",
            "مياه": "Water",
            "تنظيف": "Cleaning",
            "أمن": "Security",
            "أخرى": "Other",
            
            # الشركة
            "ملف الشركة": "Company Profile",
            "اسم الشركة": "Company Name",
            "هوية الشركة": "Company ID",
            "رقم السجل التجاري أو الهوية الضريبية": "Commercial registration number or tax ID",
            "الشعار": "Logo",
            "البريد الإلكتروني للتواصل": "Contact Email",
            "الهاتف للتواصل": "Contact Phone",
            
            # رسائل النجاح
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
            "تم إنشاء نسخة احتياطية بنجاح": "Backup created successfully",
            "فشل إنشاء النسخة الاحتياطية": "Failed to create backup",
            "تم تسجيل الخروج": "Logged out successfully",
            "تمت عملية الاسترجاع بنجاح": "Restore completed successfully",
            "تم إظهار الحركات المالية بنجاح": "Financial movements displayed successfully",
            "تم إخفاء الحركات المالية": "Financial movements hidden",
            
            # رسائل الأخطاء
            "حدث خطأ. حاول مرة أخرى": "An error occurred. Please try again",
            "كلمة المرور غير صحيحة": "Incorrect password",
            "اسم المستخدم أو كلمة المرور غير صحيحة": "Invalid username or password",
            "اسم المستخدم وكلمة المرور مطلوبان": "Username and password are required",
            "رقم الهاتف مطلوب": "Phone number is required",
            "رمز التحقق مطلوب": "Verification code is required",
            "رمز التحقق غير صحيح أو منتهي الصلاحية": "Invalid or expired verification code",
            "لا يوجد مستخدم مسجل بهذا الرقم": "No user registered with this number",
            "فشل في إرسال الرسالة. حاول مرة أخرى": "Failed to send message. Please try again",
            "رقم الهاتف ورمز التحقق مطلوبان": "Phone number and verification code are required",
            "تم تسجيل الدخول بنجاح": "Login successful",
            "حدث خطأ في حفظ البيانات. يرجى التحقق من المعلومات المدخلة": "Error saving data. Please check entered information",
            "الملف المحدد غير موجود": "Selected file does not exist",
            "الرجاء اختيار أو رفع ملف النسخة الاحتياطية": "Please select or upload backup file",
            "فشلت عملية الاسترجاع. الرجاء التحقق من الملف والصلاحيات": "Restore failed. Please check file and permissions",
            
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
            
            # النماذج
            "يرجى ذكر سبب إلغاء العقد...": "Please state the reason for contract cancellation...",
            "مثال: نسخة من العقد الموقّع": "Example: A copy of the signed contract",
            "مستند": "Document",
            "اختر تاريخ المصروف": "Select expense date",
            "حالة الشيك مطلوبة عند اختيار طريقة الدفع بالشيك": "Cheque status is required when selecting cheque payment method",
            "سبب إرجاع الشيك مطلوب عند اختيار حالة \"مرتجع\"": "Reason for cheque return is required when selecting 'Returned' status",
            "تاريخ انتهاء الاتفاقية يجب أن يكون بعد تاريخ البداية": "Agreement end date must be after start date",
            "مجموع حصة المالك وعمولة المكتب يجب أن يساوي المبلغ المستلم": "Sum of owner's share and office commission must equal received amount",
            
            # أخرى
            "يُملأ فقط في حال كان المستأجر شركة": "Fill only if tenant is a company",
            "من 1 إلى 5 نجوم.": "From 1 to 5 stars.",
            "اربط المستأجر بحساب مستخدم لتسجيل الدخول إلى البوابة.": "Link tenant to a user account to login to the portal.",
            "يرجى إدخال رقم هاتف عماني يبدأ بـ +968 ويتبعه 8 أرقام": "Please enter an Omani phone number starting with +968 followed by 8 digits",
            "تم تجاوز الحد المسموح من محاولات إرسال الرمز. حاول مرة أخرى لاحقاً": "Rate limit exceeded for sending codes. Please try again later",
            "تم إرسال رمز التحقق إلى رقم هاتفك": "Verification code sent to your phone number",
        }
    
    def find_arabic_text(self):
        """البحث عن النصوص العربية في الملفات"""
        print("🔍 البحث عن النصوص العربية...")
        
        arabic_texts = set()
        file_patterns = ['*.py', '*.html']
        
        for pattern in file_patterns:
            for file_path in self.project_root.rglob(pattern):
                if 'venv' in str(file_path) or '.venv' in str(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # البحث عن النصوص العربية
                        arabic_matches = re.findall(r'[\u0600-\u06FF\s]+', content)
                        for match in arabic_matches:
                            clean_text = match.strip()
                            if len(clean_text) > 2 and not clean_text.isdigit():
                                arabic_texts.add(clean_text)
                except:
                    continue
        
        print(f"📊 تم العثور على {len(arabic_texts)} نص عربي")
        return arabic_texts
    
    def create_makemessages(self):
        """إنشاء ملفات الترجمة"""
        print("📝 إنشاء ملفات الترجمة...")
        
        try:
            # إنشاء ملف الترجمة للإنجليزية
            result = subprocess.run([
                'python3', 'manage.py', 'makemessages', 
                '-l', 'en', '--ignore=venv', '--ignore=.venv'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ تم إنشاء ملف الترجمة الإنجليزية")
            else:
                print(f"❌ خطأ في إنشاء ملف الترجمة: {result.stderr}")
                
        except Exception as e:
            print(f"❌ خطأ: {e}")
    
    def update_translations(self):
        """تحديث الترجمات في ملف .po"""
        print("🔄 تحديث الترجمات...")
        
        if not self.en_po_file.exists():
            print("❌ ملف الترجمة الإنجليزية غير موجود")
            return False
        
        with open(self.en_po_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated_count = 0
        
        for arabic, english in self.translations.items():
            # البحث عن النمط: msgid "النص العربي" \n msgstr ""
            pattern = f'msgid "{re.escape(arabic)}"\nmsgstr ""'
            replacement = f'msgid "{arabic}"\nmsgstr "{english}"'
            
            if pattern in content:
                content = content.replace(pattern, replacement)
                updated_count += 1
                print(f"✅ {arabic} -> {english}")
        
        # حفظ الملف المحدث
        with open(self.en_po_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📊 تم تحديث {updated_count} ترجمة")
        return True
    
    def compile_messages(self):
        """تجميع ملفات الترجمة"""
        print("🔨 تجميع ملفات الترجمة...")
        
        try:
            result = subprocess.run([
                'python3', 'manage.py', 'compilemessages', '--locale=en'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ تم تجميع ملفات الترجمة بنجاح")
                return True
            else:
                print(f"❌ خطأ في تجميع الترجمة: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return False
    
    def run_full_process(self):
        """تشغيل العملية الكاملة"""
        print("🚀 بدء عملية إدارة الترجمة الشاملة")
        print("=" * 60)
        
        # 1. البحث عن النصوص العربية
        arabic_texts = self.find_arabic_text()
        
        # 2. إنشاء ملفات الترجمة
        self.create_makemessages()
        
        # 3. تحديث الترجمات
        if self.update_translations():
            # 4. تجميع الترجمات
            if self.compile_messages():
                print("\n🎉 تمت عملية الترجمة بنجاح!")
                print("\nلتفعيل الترجمة:")
                print("1. أعد تشغيل الخادم")
                print("2. أضف ?lang=en إلى نهاية الرابط")
                print("3. أو غير لغة المتصفح إلى الإنجليزية")
                return True
        
        print("\n❌ فشلت عملية الترجمة")
        return False

def main():
    """الدالة الرئيسية"""
    project_root = "/Users/macboocair/rent-management"
    
    if not os.path.exists(project_root):
        print(f"❌ مجلد المشروع غير موجود: {project_root}")
        return 1
    
    manager = TranslationManager(project_root)
    
    if manager.run_full_process():
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())

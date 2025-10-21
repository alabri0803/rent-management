/**
 * Arabic Name Translator
 * Automatically translates Arabic names to English
 */

// قاموس الأسماء العربية والإنجليزية
const arabicToEnglishNames = {
    // أسماء الذكور
    'محمد': 'Mohammed',
    'أحمد': 'Ahmed',
    'علي': 'Ali',
    'حسن': 'Hassan',
    'حسين': 'Hussein',
    'عبدالله': 'Abdullah',
    'عبدالرحمن': 'Abdulrahman',
    'خالد': 'Khalid',
    'سعد': 'Saad',
    'فهد': 'Fahad',
    'عمر': 'Omar',
    'يوسف': 'Youssef',
    'إبراهيم': 'Ibrahim',
    'عبدالعزيز': 'Abdulaziz',
    'سلطان': 'Sultan',
    'طارق': 'Tarek',
    'ماجد': 'Majed',
    'سالم': 'Salem',
    'راشد': 'Rashid',
    'ناصر': 'Nasser',
    'بدر': 'Badr',
    'زياد': 'Ziad',
    'وليد': 'Waleed',
    'سامي': 'Sami',
    'عادل': 'Adel',
    'كريم': 'Kareem',
    'هشام': 'Hisham',
    'عثمان': 'Othman',
    'صالح': 'Saleh',
    'مصطفى': 'Mustafa',
    
    // أسماء الإناث
    'فاطمة': 'Fatima',
    'عائشة': 'Aisha',
    'خديجة': 'Khadija',
    'مريم': 'Mariam',
    'زينب': 'Zainab',
    'أسماء': 'Asma',
    'هند': 'Hind',
    'نورا': 'Nora',
    'سارة': 'Sarah',
    'ليلى': 'Layla',
    'أمل': 'Amal',
    'رنا': 'Rana',
    'دينا': 'Dina',
    'منى': 'Mona',
    'هالة': 'Hala',
    'سمر': 'Samar',
    'رؤى': 'Rua',
    'شيماء': 'Shaima',
    'إيمان': 'Iman',
    'هدى': 'Huda',
    'نادية': 'Nadia',
    'سلمى': 'Salma',
    'ريم': 'Reem',
    'غادة': 'Ghada',
    'وفاء': 'Wafaa',
    
    // أسماء عمانية خاصة
    'سعيد': 'Said',
    'حمد': 'Hamad',
    'سالم': 'Salem',
    'راشد': 'Rashid',
    'محسن': 'Mohsen',
    'سليمان': 'Sulaiman',
    'عيسى': 'Issa',
    'يعقوب': 'Yaqoub',
    'موسى': 'Musa',
    'داود': 'Dawood',
    'سيف': 'Saif',
    'هلال': 'Hilal',
    'قيس': 'Qais',
    'عامر': 'Amer',
    'جابر': 'Jaber',
    'حارث': 'Harith',
    'عبدالمجيد': 'Abdulmajeed',
    'عبدالكريم': 'Abdulkareem',
    'عبدالحميد': 'Abdulhameed',
    'عبدالوهاب': 'Abdulwahab',
    
    // أسماء إناث عمانية
    'شمسة': 'Shamsa',
    'موزة': 'Moza',
    'عزة': 'Azza',
    'بثينة': 'Buthaina',
    'ثريا': 'Thuraya',
    'جميلة': 'Jamila',
    'كوثر': 'Kawthar',
    'لطيفة': 'Latifa',
    'منيرة': 'Munira',
    'نعيمة': 'Naima',
    'وردة': 'Warda',
    'يسرى': 'Yusra',
    'زهراء': 'Zahra',
    'حليمة': 'Halima',
    'رقية': 'Ruqaya',
    'سكينة': 'Sakina',
    'أميمة': 'Umaima',
    'جويرية': 'Juwayriya',
    'حفصة': 'Hafsa',
    'صفية': 'Safiya'
};

// دالة تنظيف النص العربي
function cleanArabicText(text) {
    if (!text) return '';
    
    // إزالة التشكيل والرموز الإضافية
    return text.replace(/[\u064B-\u0652\u0670\u0640]/g, '')
               .replace(/[أإآ]/g, 'ا')
               .replace(/[ة]/g, 'ه')
               .trim();
}

// دالة الترجمة الرئيسية
function translateArabicName(arabicName) {
    if (!arabicName || arabicName.trim() === '') {
        return '';
    }
    
    const cleanName = cleanArabicText(arabicName);
    
    // البحث المباشر في القاموس
    if (arabicToEnglishNames[cleanName]) {
        return arabicToEnglishNames[cleanName];
    }
    
    // البحث الجزئي للأسماء المركبة
    const nameParts = cleanName.split(/\s+/);
    const translatedParts = [];
    
    for (const part of nameParts) {
        if (arabicToEnglishNames[part]) {
            translatedParts.push(arabicToEnglishNames[part]);
        } else {
            // ترجمة صوتية بسيطة للأسماء غير الموجودة
            translatedParts.push(transliterateArabic(part));
        }
    }
    
    return translatedParts.join(' ');
}

// دالة الترجمة الصوتية البسيطة
function transliterateArabic(arabicText) {
    const transliterationMap = {
        'ا': 'a', 'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h',
        'خ': 'kh', 'د': 'd', 'ذ': 'th', 'ر': 'r', 'ز': 'z', 'س': 's',
        'ش': 'sh', 'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z', 'ع': 'a',
        'غ': 'gh', 'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm',
        'ن': 'n', 'ه': 'h', 'و': 'w', 'ي': 'y', 'ى': 'a', 'ء': 'a'
    };
    
    let result = '';
    for (const char of arabicText) {
        result += transliterationMap[char] || char;
    }
    
    // تنظيف النتيجة وتحويل الحرف الأول إلى كبير
    result = result.replace(/[^a-zA-Z\s]/g, '').trim();
    return result.charAt(0).toUpperCase() + result.slice(1).toLowerCase();
}

// دالة التحقق من النص العربي
function isArabicText(text) {
    if (!text) return false;
    const arabicRegex = /[\u0600-\u06FF]/;
    return arabicRegex.test(text);
}

// تصدير الدوال للاستخدام العام
window.ArabicNameTranslator = {
    translate: translateArabicName,
    isArabic: isArabicText,
    clean: cleanArabicText
};

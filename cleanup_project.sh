#!/bin/bash

# 🧹 سكريبت تنظيف المشروع
# يقلل حجم المشروع من 548 MB إلى ~50 MB

echo "🧹 بدء تنظيف المشروع..."
echo ""

# الحجم الحالي
echo "📊 الحجم الحالي:"
du -sh .
echo ""

# 1. حذف venv (174 MB) - يمكن إعادة إنشائه
echo "🗑️  حذف venv (سيتم إعادة إنشائه)..."
if [ -d "venv" ]; then
    rm -rf venv
    echo "✅ تم حذف venv"
else
    echo "⏭️  venv غير موجود"
fi
echo ""

# 2. حذف backups القديمة (74 MB) - الاحتفاظ بآخر 2 فقط
echo "🗑️  تنظيف backups (الاحتفاظ بآخر 2 فقط)..."
if [ -d "backups" ]; then
    cd backups
    # الاحتفاظ بآخر 2 ملفات فقط
    ls -t *.zip | tail -n +3 | xargs -r rm
    cd ..
    echo "✅ تم تنظيف backups"
else
    echo "⏭️  مجلد backups غير موجود"
fi
echo ""

# 3. حذف staticfiles (57 MB) - يمكن إعادة جمعها
echo "🗑️  حذف staticfiles (سيتم إعادة جمعها)..."
if [ -d "staticfiles" ]; then
    rm -rf staticfiles
    echo "✅ تم حذف staticfiles"
else
    echo "⏭️  staticfiles غير موجود"
fi
echo ""

# 4. تنظيف __pycache__ و *.pyc
echo "🗑️  حذف ملفات Python المؤقتة..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
echo "✅ تم حذف ملفات Python المؤقتة"
echo ""

# 5. تنظيف logs القديمة
echo "🗑️  تنظيف logs القديمة..."
if [ -d "logs" ]; then
    find logs -type f -name "*.log" -mtime +30 -delete
    echo "✅ تم تنظيف logs القديمة"
else
    echo "⏭️  مجلد logs غير موجود"
fi
echo ""

# 6. حذف ملفات backup.json الكبيرة
echo "🗑️  حذف ملفات backup كبيرة..."
if [ -f "backup.json" ]; then
    rm backup.json
    echo "✅ تم حذف backup.json"
fi
if [ -f "backup_data.json" ]; then
    rm backup_data.json
    echo "✅ تم حذف backup_data.json"
fi
echo ""

# 7. حذف node_modules إذا وجد
echo "🗑️  حذف node_modules إذا وجد..."
if [ -d "node_modules" ]; then
    rm -rf node_modules
    echo "✅ تم حذف node_modules"
else
    echo "⏭️  node_modules غير موجود"
fi
echo ""

# الحجم بعد التنظيف
echo "📊 الحجم بعد التنظيف:"
du -sh .
echo ""

echo "✅ اكتمل التنظيف بنجاح!"
echo ""
echo "📝 ملاحظات:"
echo "  - لإعادة إنشاء venv: python3 -m venv venv"
echo "  - لتثبيت المكتبات: pip install -r requirements.txt"
echo "  - لجمع الملفات الثابتة: python manage.py collectstatic"
echo ""

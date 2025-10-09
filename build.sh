#!/usr/bin/env bash
# build.sh

# تثبيت المتطلبا

# جمع الملفات الث
#!/usr/bin/env bash
# build.sh

set -o errexit

# إصلاح مشكلة psycopg لـ Python 3.13
python --version

# تحديث pip أولاً
pip install --upgrade pip

# تثبيت الاعتماديات النظامية اللازمة لـ psycopg (على Render)
apt-get update && apt-get install -y libpq-dev python3-dev || true

# تثبيت الاعتماديات
pip install -r requirements.txt

# إذا فشل psycopg، جرب البدائل
if ! python -c "import psycopg2" 2>/dev/null; then
    echo "Installing psycopg2 alternative..."
    pip install psycopg2-binary --force-reinstall --no-cache-dir
fi

# جمع الملفات الثابتة
python manage.py collectstatic --noinput

# تطبيق migrations
python manage.py migrate

# إنشاء superuser (اختياري)
echo "Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@rentmanagement.com', 'admin123')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
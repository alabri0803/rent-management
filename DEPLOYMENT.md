# 🚀 دليل النشر - نظام إدارة الإيجارات

## 📋 جدول المحتويات

1. [المتطلبات](#المتطلبات)
2. [النشر باستخدام Docker](#النشر-باستخدام-docker)
3. [النشر اليدوي](#النشر-اليدوي)
4. [إعدادات الإنتاج](#إعدادات-الإنتاج)
5. [النسخ الاحتياطي والاستعادة](#النسخ-الاحتياطي-والاستعادة)
6. [المراقبة والصيانة](#المراقبة-والصيانة)
7. [استكشاف الأخطاء](#استكشاف-الأخطاء)

---

## 🔧 المتطلبات

### الحد الأدنى من المتطلبات:
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+

### البرمجيات المطلوبة:
- Docker 20.10+
- Docker Compose 2.0+
- Git
- (اختياري) Nginx للـ reverse proxy

---

## 🐳 النشر باستخدام Docker

### 1. الإعداد الأولي

```bash
# استنساخ المشروع
git clone https://github.com/your-repo/rent-management.git
cd rent-management

# إنشاء ملف البيئة
cp .env.example .env
```

### 2. تكوين ملف .env

```bash
# Django Settings
SECRET_KEY=your-very-secret-key-here-change-in-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost

# Database
DB_NAME=rent_management
DB_USER=postgres
DB_PASSWORD=strong-password-here
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis-strong-password

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Localization
LANGUAGE_CODE=ar
TIME_ZONE=Asia/Muscat
```

### 3. بناء وتشغيل الحاويات

```bash
# بناء الصور
docker-compose build

# تشغيل الحاويات
docker-compose up -d

# التحقق من حالة الحاويات
docker-compose ps
```

### 4. إعداد قاعدة البيانات

```bash
# تطبيق migrations
docker-compose exec web python manage.py migrate

# إنشاء superuser
docker-compose exec web python manage.py createsuperuser

# جمع الملفات الثابتة
docker-compose exec web python manage.py collectstatic --noinput

# تجميع الترجمات
docker-compose exec web python manage.py compilemessages
```

### 5. التحقق من التشغيل

```bash
# فحص الصحة
curl http://localhost:8000/health/

# عرض السجلات
docker-compose logs -f web

# الوصول إلى التطبيق
# افتح المتصفح على: http://localhost
```

---

## 🛠️ النشر اليدوي (بدون Docker)

### 1. تثبيت المتطلبات

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python و PostgreSQL
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib redis-server nginx

# تثبيت gettext للترجمات
sudo apt install -y gettext
```

### 2. إعداد قاعدة البيانات

```bash
# الدخول إلى PostgreSQL
sudo -u postgres psql

# إنشاء قاعدة البيانات والمستخدم
CREATE DATABASE rent_management;
CREATE USER rent_user WITH PASSWORD 'strong_password';
ALTER ROLE rent_user SET client_encoding TO 'utf8';
ALTER ROLE rent_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE rent_user SET timezone TO 'Asia/Muscat';
GRANT ALL PRIVILEGES ON DATABASE rent_management TO rent_user;
\q
```

### 3. إعداد التطبيق

```bash
# إنشاء مستخدم للتطبيق
sudo useradd -m -s /bin/bash rentapp
sudo su - rentapp

# استنساخ المشروع
git clone https://github.com/your-repo/rent-management.git
cd rent-management

# إنشاء بيئة افتراضية
python3.11 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# إعداد ملف البيئة
cp .env.example .env
nano .env  # تحرير الإعدادات
```

### 4. تطبيق Migrations وجمع الملفات

```bash
# تطبيق migrations
python manage.py migrate

# إنشاء superuser
python manage.py createsuperuser

# جمع الملفات الثابتة
python manage.py collectstatic --noinput

# تجميع الترجمات
python manage.py compilemessages
```

### 5. إعداد Gunicorn

```bash
# إنشاء ملف systemd service
sudo nano /etc/systemd/system/rent-management.service
```

```ini
[Unit]
Description=Rent Management Gunicorn daemon
After=network.target

[Service]
User=rentapp
Group=www-data
WorkingDirectory=/home/rentapp/rent-management
Environment="PATH=/home/rentapp/rent-management/venv/bin"
ExecStart=/home/rentapp/rent-management/venv/bin/gunicorn \
          --workers 4 \
          --threads 2 \
          --bind unix:/home/rentapp/rent-management/gunicorn.sock \
          --timeout 60 \
          --access-logfile /home/rentapp/rent-management/logs/gunicorn-access.log \
          --error-logfile /home/rentapp/rent-management/logs/gunicorn-error.log \
          rent_management.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# تفعيل وتشغيل الخدمة
sudo systemctl start rent-management
sudo systemctl enable rent-management
sudo systemctl status rent-management
```

### 6. إعداد Nginx

```bash
# إنشاء ملف التكوين
sudo nano /etc/nginx/sites-available/rent-management
```

```nginx
upstream rent_management {
    server unix:/home/rentapp/rent-management/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/rentapp/rent-management/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/rentapp/rent-management/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://rent_management;
    }
}
```

```bash
# تفعيل الموقع
sudo ln -s /etc/nginx/sites-available/rent-management /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. إعداد SSL مع Let's Encrypt

```bash
# تثبيت Certbot
sudo apt install -y certbot python3-certbot-nginx

# الحصول على شهادة SSL
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# تجديد تلقائي
sudo systemctl status certbot.timer
```

---

## ⚙️ إعدادات الإنتاج

### 1. ملف .env للإنتاج

```bash
# Security
SECRET_KEY=generate-a-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=rent_management
DB_USER=rent_user
DB_PASSWORD=very-strong-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis-strong-password

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Security Headers
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Logging
LOG_LEVEL=INFO
```

### 2. إعدادات Django للإنتاج

في `settings.py`:

```python
# Security Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

---

## 💾 النسخ الاحتياطي والاستعادة

### 1. النسخ الاحتياطي التلقائي

```bash
# إنشاء سكريبت النسخ الاحتياطي
nano /home/rentapp/backup.sh
```

```bash
#!/bin/bash

# Variables
BACKUP_DIR="/home/rentapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="rent_management"
DB_USER="rent_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /home/rentapp/rent-management/media/

# Delete old backups (keep last 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
# جعل السكريبت قابل للتنفيذ
chmod +x /home/rentapp/backup.sh

# إضافة إلى crontab (يومياً في 2 صباحاً)
crontab -e
0 2 * * * /home/rentapp/backup.sh >> /home/rentapp/backup.log 2>&1
```

### 2. استعادة النسخة الاحتياطية

```bash
# استعادة قاعدة البيانات
gunzip -c /home/rentapp/backups/db_backup_YYYYMMDD_HHMMSS.sql.gz | psql -U rent_user rent_management

# استعادة ملفات الوسائط
tar -xzf /home/rentapp/backups/media_backup_YYYYMMDD_HHMMSS.tar.gz -C /
```

### 3. النسخ الاحتياطي مع Docker

```bash
# نسخ احتياطي لقاعدة البيانات
docker-compose exec db pg_dump -U postgres rent_management | gzip > backup_$(date +%Y%m%d).sql.gz

# استعادة
gunzip -c backup_YYYYMMDD.sql.gz | docker-compose exec -T db psql -U postgres rent_management
```

---

## 📊 المراقبة والصيانة

### 1. مراقبة السجلات

```bash
# Docker
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f redis

# Manual deployment
sudo journalctl -u rent-management -f
tail -f /home/rentapp/rent-management/logs/django.log
```

### 2. مراقبة الأداء

```bash
# استخدام الموارد
docker stats

# حالة قاعدة البيانات
docker-compose exec db psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# حالة Redis
docker-compose exec redis redis-cli INFO
```

### 3. تنظيف السجلات

```bash
# تنظيف السجلات القديمة
python manage.py manage_logs --action=clean --days=30

# ضغط السجلات
python manage.py manage_logs --action=compress
```

### 4. تحديث التطبيق

```bash
# مع Docker
git pull origin main
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput

# يدوياً
cd /home/rentapp/rent-management
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py compilemessages
sudo systemctl restart rent-management
```

---

## 🔍 استكشاف الأخطاء

### مشكلة: التطبيق لا يعمل

```bash
# فحص حالة الخدمات
docker-compose ps
# أو
sudo systemctl status rent-management

# فحص السجلات
docker-compose logs web
# أو
sudo journalctl -u rent-management -n 100
```

### مشكلة: خطأ في قاعدة البيانات

```bash
# فحص اتصال قاعدة البيانات
docker-compose exec web python manage.py dbshell

# إعادة تطبيق migrations
docker-compose exec web python manage.py migrate --run-syncdb
```

### مشكلة: الملفات الثابتة لا تظهر

```bash
# إعادة جمع الملفات الثابتة
docker-compose exec web python manage.py collectstatic --clear --noinput

# التحقق من الصلاحيات
ls -la /home/rentapp/rent-management/staticfiles/
```

### مشكلة: بطء في الأداء

```bash
# فحص استخدام الموارد
docker stats

# تحسين قاعدة البيانات
docker-compose exec db psql -U postgres rent_management -c "VACUUM ANALYZE;"

# مسح الـ cache
docker-compose exec redis redis-cli FLUSHALL
```

---

## 📞 الدعم والمساعدة

- **التوثيق**: راجع ملفات `README.md` و `LOGGING_SYSTEM.md` و `CACHING_SYSTEM.md`
- **السجلات**: تحقق من مجلد `/logs` للحصول على معلومات مفصلة
- **المجتمع**: افتح issue على GitHub للمساعدة

---

## ✅ قائمة التحقق قبل الإنتاج

- [ ] تغيير `SECRET_KEY` إلى قيمة عشوائية قوية
- [ ] تعيين `DEBUG=False`
- [ ] تكوين `ALLOWED_HOSTS` بشكل صحيح
- [ ] إعداد قاعدة بيانات PostgreSQL
- [ ] تكوين Redis للـ caching
- [ ] إعداد HTTPS/SSL
- [ ] تكوين البريد الإلكتروني
- [ ] إعداد النسخ الاحتياطي التلقائي
- [ ] تفعيل المراقبة والسجلات
- [ ] اختبار عملية الاستعادة
- [ ] تكوين جدار الحماية
- [ ] تحديث جميع الحزم
- [ ] مراجعة إعدادات الأمان
- [ ] اختبار الأداء تحت الحمل

---

**تم التحديث**: 2025-10-22  
**الإصدار**: 1.0.0

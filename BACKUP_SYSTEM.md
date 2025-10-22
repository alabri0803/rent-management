# 💾 نظام النسخ الاحتياطي التلقائي - Rent Management System

## 📋 جدول المحتويات

1. [نظرة عامة](#نظرة-عامة)
2. [المميزات](#المميزات)
3. [المكونات](#المكونات)
4. [الإعداد والتكوين](#الإعداد-والتكوين)
5. [الاستخدام](#الاستخدام)
6. [النسخ الاحتياطي التلقائي](#النسخ-الاحتياطي-التلقائي)
7. [التخزين السحابي](#التخزين-السحابي)
8. [الاستعادة](#الاستعادة)
9. [سياسة الاحتفاظ](#سياسة-الاحتفاظ)
10. [المراقبة والإشعارات](#المراقبة-والإشعارات)
11. [استكشاف الأخطاء](#استكشاف-الأخطاء)
12. [أفضل الممارسات](#أفضل-الممارسات)

---

## 🎯 نظرة عامة

نظام النسخ الاحتياطي التلقائي هو حل شامل لحماية بيانات نظام إدارة الإيجارات. يوفر النظام:

- ✅ **نسخ احتياطي تلقائي يومي** لقاعدة البيانات والملفات
- ✅ **رفع تلقائي للسحابة** (AWS S3 / Google Cloud Storage)
- ✅ **سياسة احتفاظ ذكية** (يومي، أسبوعي، شهري)
- ✅ **استعادة سريعة** مع اختبار تلقائي
- ✅ **إشعارات بالبريد الإلكتروني** عند النجاح أو الفشل
- ✅ **تشفير وضغط** للنسخ الاحتياطية

---

## ⭐ المميزات

### 1. أنواع النسخ الاحتياطي

| النوع | الوصف | التكرار الموصى به |
|-------|-------|-------------------|
| **Database** | نسخ احتياطي كامل لقاعدة البيانات PostgreSQL | يومي |
| **Media** | نسخ احتياطي لملفات الوسائط (الصور، المستندات) | يومي |
| **Application** | نسخ احتياطي لملفات التطبيق | أسبوعي |
| **Full** | نسخ احتياطي شامل لكل شيء | يومي |

### 2. وجهات التخزين

- 📁 **محلي**: `/backups` في مجلد المشروع
- ☁️ **AWS S3**: تخزين سحابي آمن ومتين
- ☁️ **Google Cloud Storage**: بديل موثوق
- 💾 **خادم بعيد**: عبر rsync/scp

### 3. الأمان

- 🔒 **ضغط gzip**: تقليل حجم الملفات
- 🔐 **تشفير اختياري**: حماية البيانات الحساسة
- 🔑 **صلاحيات محدودة**: مستخدم غير root
- 📝 **سجلات مفصلة**: تتبع جميع العمليات

---

## 🧩 المكونات

### 1. Bash Script (`scripts/backup.sh`)

سكريبت شامل لإدارة النسخ الاحتياطي:

```bash
# الميزات:
✅ نسخ احتياطي لقاعدة البيانات (PostgreSQL)
✅ نسخ احتياطي للملفات (Media + Application)
✅ ضغط تلقائي (gzip)
✅ رفع للسحابة (S3/GCS)
✅ سياسة احتفاظ (rotation)
✅ إشعارات بالبريد الإلكتروني
✅ تقارير مفصلة
```

**الاستخدام:**
```bash
# نسخ احتياطي كامل
./scripts/backup.sh

# مع متغيرات بيئة مخصصة
DB_NAME=mydb DB_USER=postgres ./scripts/backup.sh
```

### 2. Django Management Command (`manage.py backup`)

أمر Django متكامل لإدارة النسخ الاحتياطي:

```python
# الميزات:
✅ نسخ احتياطي (database, media, application, full)
✅ استعادة من نسخة احتياطية
✅ عرض قائمة النسخ المتاحة
✅ تنظيف النسخ القديمة
✅ التحقق من صحة النسخ
✅ اختبار النسخ والاستعادة
✅ رفع للسحابة
```

**الاستخدام:**
```bash
# نسخ احتياطي كامل
python manage.py backup --type=full

# نسخ احتياطي لقاعدة البيانات فقط
python manage.py backup --type=database

# نسخ احتياطي مع رفع للسحابة
python manage.py backup --type=full --upload

# عرض النسخ المتاحة
python manage.py backup --list

# استعادة من نسخة احتياطية
python manage.py backup --restore=/path/to/backup.sql.gz

# تنظيف النسخ القديمة
python manage.py backup --clean

# التحقق من صحة نسخة احتياطية
python manage.py backup --verify=/path/to/backup.sql.gz

# اختبار النسخ والاستعادة
python manage.py backup --test
```

---

## ⚙️ الإعداد والتكوين

### 1. المتطلبات

**البرمجيات المطلوبة:**
```bash
# أدوات قاعدة البيانات
sudo apt install postgresql-client

# أدوات الضغط
sudo apt install gzip tar

# أدوات البريد الإلكتروني (اختياري)
sudo apt install mailutils

# AWS CLI (للرفع على S3)
pip install awscli boto3

# Google Cloud SDK (للرفع على GCS)
pip install google-cloud-storage
```

### 2. متغيرات البيئة

إنشاء ملف `.env.backup`:

```bash
# Database Configuration
DB_NAME=rent_management
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Backup Configuration
BACKUP_ROOT=/path/to/backups
RETENTION_DAILY=7
RETENTION_WEEKLY=30
RETENTION_MONTHLY=90

# AWS S3 Configuration
ENABLE_S3_UPLOAD=true
S3_BUCKET=your-backup-bucket
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Google Cloud Storage Configuration
ENABLE_GCS_UPLOAD=false
GCS_BUCKET=your-gcs-bucket
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Email Notifications
ENABLE_EMAIL=true
EMAIL_TO=admin@yourdomain.com
EMAIL_FROM=backup@yourdomain.com

# Optional
BACKUP_APPLICATION=true  # Backup application files
```

### 3. إعداد AWS S3

```bash
# تثبيت AWS CLI
pip install awscli

# تكوين AWS CLI
aws configure
# AWS Access Key ID: your_access_key
# AWS Secret Access Key: your_secret_key
# Default region name: us-east-1
# Default output format: json

# إنشاء bucket للنسخ الاحتياطية
aws s3 mb s3://your-backup-bucket

# تفعيل versioning (اختياري)
aws s3api put-bucket-versioning \
    --bucket your-backup-bucket \
    --versioning-configuration Status=Enabled

# تفعيل lifecycle policy (حذف تلقائي بعد 90 يوم)
aws s3api put-bucket-lifecycle-configuration \
    --bucket your-backup-bucket \
    --lifecycle-configuration file://lifecycle.json
```

**lifecycle.json:**
```json
{
  "Rules": [
    {
      "Id": "DeleteOldBackups",
      "Status": "Enabled",
      "Prefix": "backups/",
      "Expiration": {
        "Days": 90
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
```

### 4. إعداد Google Cloud Storage

```bash
# تثبيت Google Cloud SDK
pip install google-cloud-storage

# تكوين المصادقة
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"

# إنشاء bucket
gsutil mb gs://your-gcs-bucket

# تفعيل versioning
gsutil versioning set on gs://your-gcs-bucket

# تفعيل lifecycle policy
gsutil lifecycle set lifecycle.json gs://your-gcs-bucket
```

---

## 🚀 الاستخدام

### 1. النسخ الاحتياطي اليدوي

#### باستخدام Bash Script:

```bash
# نسخ احتياطي كامل
./scripts/backup.sh

# مع متغيرات مخصصة
DB_NAME=mydb ./scripts/backup.sh
```

#### باستخدام Django Command:

```bash
# نسخ احتياطي كامل
python manage.py backup --type=full

# نسخ احتياطي لقاعدة البيانات فقط
python manage.py backup --type=database

# نسخ احتياطي للملفات فقط
python manage.py backup --type=media

# نسخ احتياطي مع رفع للسحابة
python manage.py backup --type=full --upload
```

### 2. عرض النسخ المتاحة

```bash
# عرض جميع النسخ الاحتياطية
python manage.py backup --list

# النتيجة:
# Database Backups:
#   db_rent_management_20250122_143000.sql.gz (15.2 MB) - 2025-01-22 14:30:00
#   db_rent_management_20250121_020000.sql.gz (14.8 MB) - 2025-01-21 02:00:00
# 
# Media Backups:
#   media_20250122_143000.tar.gz (125.5 MB) - 2025-01-22 14:30:00
```

### 3. التحقق من صحة النسخة الاحتياطية

```bash
# التحقق من نسخة احتياطية
python manage.py backup --verify=backups/database/db_backup.sql.gz

# النتيجة:
# ✓ Backup file is valid
```

### 4. تنظيف النسخ القديمة

```bash
# حذف النسخ الأقدم من 30 يوم
python manage.py backup --clean

# النتيجة:
# ✓ Deleted 15 old backups (2.3 GB)
```

---

## ⏰ النسخ الاحتياطي التلقائي

### 1. إعداد Cron Job

```bash
# تحرير crontab
crontab -e

# إضافة مهمة يومية في 2 صباحاً
0 2 * * * /path/to/rent-management/scripts/backup.sh >> /path/to/logs/backup.log 2>&1

# أو باستخدام Django command
0 2 * * * cd /path/to/rent-management && /path/to/venv/bin/python manage.py backup --type=full --upload >> /path/to/logs/backup.log 2>&1

# نسخ احتياطي كل 6 ساعات
0 */6 * * * /path/to/rent-management/scripts/backup.sh

# نسخ احتياطي أسبوعي (الأحد 3 صباحاً)
0 3 * * 0 cd /path/to/rent-management && /path/to/venv/bin/python manage.py backup --type=full --upload
```

### 2. إعداد Systemd Timer (بديل لـ Cron)

**backup.service:**
```ini
[Unit]
Description=Rent Management Backup Service
After=network.target postgresql.service

[Service]
Type=oneshot
User=rentapp
WorkingDirectory=/home/rentapp/rent-management
Environment="PATH=/home/rentapp/rent-management/venv/bin"
ExecStart=/home/rentapp/rent-management/venv/bin/python manage.py backup --type=full --upload
StandardOutput=append:/home/rentapp/logs/backup.log
StandardError=append:/home/rentapp/logs/backup-error.log

[Install]
WantedBy=multi-user.target
```

**backup.timer:**
```ini
[Unit]
Description=Daily Backup Timer
Requires=backup.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

**التفعيل:**
```bash
# نسخ الملفات
sudo cp backup.service /etc/systemd/system/
sudo cp backup.timer /etc/systemd/system/

# تفعيل وتشغيل
sudo systemctl daemon-reload
sudo systemctl enable backup.timer
sudo systemctl start backup.timer

# التحقق من الحالة
sudo systemctl status backup.timer
sudo systemctl list-timers
```

### 3. Docker Cron Service

إضافة خدمة cron في `docker-compose.yml`:

```yaml
services:
  backup:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: rent_management_backup
    restart: unless-stopped
    command: >
      sh -c "echo '0 2 * * * cd /app && python manage.py backup --type=full --upload >> /app/logs/backup.log 2>&1' | crontab - && crond -f"
    environment:
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - ENABLE_S3_UPLOAD=${ENABLE_S3_UPLOAD}
      - S3_BUCKET=${S3_BUCKET}
    volumes:
      - ./backups:/app/backups
      - ./logs:/app/logs
    depends_on:
      - db
    networks:
      - rent_network
```

---

## ☁️ التخزين السحابي

### 1. AWS S3

#### التكوين:

```python
# في settings.py
AWS_STORAGE_BUCKET_NAME = 'your-backup-bucket'
AWS_S3_REGION_NAME = 'us-east-1'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
```

#### الاستخدام:

```bash
# رفع يدوي
python manage.py backup --type=full --upload

# رفع تلقائي (في cron)
0 2 * * * python manage.py backup --type=full --upload
```

#### التحقق من الرفع:

```bash
# عرض الملفات في S3
aws s3 ls s3://your-backup-bucket/backups/ --recursive

# تحميل نسخة احتياطية
aws s3 cp s3://your-backup-bucket/backups/2025/01/db_backup.sql.gz ./
```

### 2. Google Cloud Storage

#### التكوين:

```python
# في settings.py
GS_BUCKET_NAME = 'your-gcs-bucket'
GS_PROJECT_ID = 'your-project-id'
GOOGLE_APPLICATION_CREDENTIALS = '/path/to/credentials.json'
```

#### الاستخدام:

```bash
# رفع يدوي
python manage.py backup --type=full --upload

# التحقق من الرفع
gsutil ls gs://your-gcs-bucket/backups/

# تحميل نسخة احتياطية
gsutil cp gs://your-gcs-bucket/backups/2025/01/db_backup.sql.gz ./
```

---

## 🔄 الاستعادة

### 1. استعادة قاعدة البيانات

#### باستخدام Django Command:

```bash
# استعادة من نسخة احتياطية محلية
python manage.py backup --restore=backups/database/db_backup_20250122.sql.gz

# استعادة من S3
aws s3 cp s3://your-bucket/backups/db_backup.sql.gz ./
python manage.py backup --restore=db_backup.sql.gz
```

#### يدوياً:

```bash
# فك الضغط
gunzip -c backups/database/db_backup.sql.gz > db_backup.sql

# استعادة
psql -U postgres -d rent_management < db_backup.sql

# أو مباشرة
gunzip -c db_backup.sql.gz | psql -U postgres -d rent_management
```

### 2. استعادة الملفات

```bash
# استعادة Media files
python manage.py backup --restore=backups/media/media_20250122.tar.gz

# يدوياً
tar -xzf backups/media/media_20250122.tar.gz -C /path/to/project/
```

### 3. استعادة كاملة

```bash
# 1. استعادة قاعدة البيانات
python manage.py backup --restore=backups/database/db_backup.sql.gz

# 2. استعادة الملفات
python manage.py backup --restore=backups/media/media_backup.tar.gz

# 3. استعادة التطبيق (إذا لزم الأمر)
tar -xzf backups/application/app_backup.tar.gz -C /path/to/

# 4. إعادة تشغيل الخدمات
sudo systemctl restart rent-management
```

---

## 📅 سياسة الاحتفاظ

### سياسة الاحتفاظ الافتراضية:

| النوع | المدة | الوصف |
|-------|------|--------|
| **يومي** | 7 أيام | نسخة احتياطية يومية |
| **أسبوعي** | 30 يوم | نسخة واحدة كل أسبوع |
| **شهري** | 90 يوم | نسخة واحدة كل شهر |

### التخصيص:

```bash
# في .env.backup
RETENTION_DAILY=7      # الاحتفاظ بآخر 7 أيام
RETENTION_WEEKLY=30    # الاحتفاظ بآخر 30 يوم
RETENTION_MONTHLY=90   # الاحتفاظ بآخر 90 يوم
```

### التطبيق التلقائي:

```bash
# يتم تطبيق السياسة تلقائياً عند كل نسخ احتياطي
./scripts/backup.sh

# أو يدوياً
python manage.py backup --clean
```

---

## 📧 المراقبة والإشعارات

### 1. إشعارات البريد الإلكتروني

#### التكوين:

```bash
# في .env.backup
ENABLE_EMAIL=true
EMAIL_TO=admin@yourdomain.com
EMAIL_FROM=backup@yourdomain.com
```

#### رسالة النجاح:

```
Subject: Backup Success - Rent Management System

================================================================================
Backup Report - 2025-01-22 02:00:15
================================================================================

Database Backup:
  File: db_rent_management_20250122_020015.sql.gz
  Size: 15.2 MB
  Status: ✓ Success

Media Backup:
  File: media_20250122_020015.tar.gz
  Size: 125.5 MB
  Status: ✓ Success

Cloud Storage:
  S3: Enabled
  GCS: Disabled

Backup Location: /home/rentapp/rent-management/backups
Total Backups: 45
Total Size: 2.3 GB

================================================================================
```

### 2. السجلات (Logs)

```bash
# عرض سجلات النسخ الاحتياطي
tail -f backups/logs/backup_2025-01-22.log

# عرض آخر 100 سطر
tail -n 100 backups/logs/backup_2025-01-22.log

# البحث عن أخطاء
grep "ERROR" backups/logs/*.log
```

### 3. المراقبة مع Monitoring Tools

#### مع Prometheus:

```python
# في Django
from prometheus_client import Counter, Gauge

backup_success = Counter('backup_success_total', 'Total successful backups')
backup_failure = Counter('backup_failure_total', 'Total failed backups')
backup_size = Gauge('backup_size_bytes', 'Size of last backup')
```

---

## 🔧 استكشاف الأخطاء

### المشاكل الشائعة:

#### 1. خطأ في الاتصال بقاعدة البيانات

```bash
# المشكلة
ERROR: could not connect to database

# الحل
# تحقق من بيانات الاتصال
psql -U postgres -d rent_management -c "SELECT 1"

# تحقق من أن PostgreSQL يعمل
sudo systemctl status postgresql
```

#### 2. مساحة القرص ممتلئة

```bash
# المشكلة
ERROR: No space left on device

# الحل
# حذف النسخ القديمة
python manage.py backup --clean

# تحقق من المساحة
df -h /path/to/backups
```

#### 3. فشل الرفع على S3

```bash
# المشكلة
ERROR: S3 upload failed

# الحل
# تحقق من بيانات AWS
aws s3 ls

# تحقق من الصلاحيات
aws iam get-user

# اختبار الرفع
aws s3 cp test.txt s3://your-bucket/
```

#### 4. النسخة الاحتياطية تالفة

```bash
# التحقق من صحة النسخة
python manage.py backup --verify=backup_file.sql.gz

# إذا كانت تالفة، استخدم نسخة أقدم
python manage.py backup --list
```

---

## ✅ أفضل الممارسات

### 1. الأمان

- ✅ **تشفير النسخ الاحتياطية** الحساسة
- ✅ **تخزين في مواقع متعددة** (محلي + سحابي)
- ✅ **صلاحيات محدودة** للملفات (600)
- ✅ **عدم تخزين كلمات المرور** في السكريبتات

### 2. الموثوقية

- ✅ **اختبار الاستعادة** بانتظام
- ✅ **مراقبة النسخ الاحتياطية** يومياً
- ✅ **الاحتفاظ بنسخ متعددة** (3-2-1 rule)
- ✅ **توثيق العملية** بوضوح

### 3. الأداء

- ✅ **جدولة في أوقات الذروة المنخفضة**
- ✅ **ضغط النسخ** لتوفير المساحة
- ✅ **نسخ تدريجي** للملفات الكبيرة
- ✅ **تنظيف النسخ القديمة** تلقائياً

### 4. قاعدة 3-2-1

- **3** نسخ من البيانات
- **2** وسائط تخزين مختلفة
- **1** نسخة خارج الموقع (سحابية)

---

## 📞 الدعم

للمساعدة أو الإبلاغ عن مشاكل:
- 📧 Email: support@yourdomain.com
- 📝 Documentation: `/docs/backup`
- 🐛 Issues: GitHub Issues

---

**تم التحديث**: 2025-01-22  
**الإصدار**: 1.0.0

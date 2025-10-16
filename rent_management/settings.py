"""
Django settings for rent_management project.
Optimized for Render deployment
"""

import os
from django.utils.translation import gettext_lazy as _
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
import pymysql
pymysql.install_as_MySQLdb()
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-rm=85vc+pgs=^4+m+=d*32)+j7xx*_5t%amcq(=d7iz5q8zp^e')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ✅ ALLOWED_HOSTS for local/LAN development
# You can override with env: ALLOWED_HOSTS="localhost,127.0.0.1,[::1],192.168.10.164"
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'dashboard',
    'portal',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'rent_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(str(BASE_DIR), 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
            'libraries': {
                'dashboard_extras': 'dashboard.templatetags.dashboard_extras',
            }
        },
    },
]



# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Use environment variable for DATABASE_URL if available, otherwise use SQLite for development
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Parse DATABASE_URL - respect SSL mode from URL
    # If sslmode=disable is in URL, don't force SSL
    ssl_required = 'sslmode=disable' not in database_url.lower()
    DATABASES = {
        'default': dj_database_url.parse(database_url, conn_max_age=600, ssl_require=ssl_required)
    }
else:
    # SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rent-management',
        'USER': 'root',
        'PASSWORD': '',  # كلمة المرور فارغة في XAMPP افتراضياً
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

 

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ar' # العربية

TIME_ZONE = 'Asia/Muscat'

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('ar', _('العربية')),
    ('en', _('English')),
]
LOCALE_PATHS = [
    os.path.join(str(BASE_DIR), 'locale')
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(str(BASE_DIR), 'static')]
STATIC_ROOT = os.path.join(str(BASE_DIR), 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(str(BASE_DIR), 'media')

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session settings to expire at browser close
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_AGE = 1209600 # 2 weeks in seconds, but will expire on browser close due to SESSION_EXPIRE_AT_BROWSER_CLOSE = True


LOGIN_REDIRECT_URL = '/login-redirect/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_URL = '/accounts/login/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

AUTHENTICATION_BACKENDS = (
    'dashboard.auth_backends.EmailUsernameBackend',
    'dashboard.auth_backends.OTPSMSBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1

# إعدادات Allauth
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # These are the permissions you want to request from Google.
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'github': {
        'SCOPE': [
            'user',
            'repo',
            'read:org',
        ],
    }
}

# SMS Configuration
SMS_PROVIDER = 'console'  # Options: 'console', 'twilio', 'aws_sns'

# Twilio Configuration (if using Twilio)
# TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
# TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
# TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'

# AWS SNS Configuration (if using AWS SNS)
# AWS_ACCESS_KEY_ID = 'your_aws_access_key_id'
# AWS_SECRET_ACCESS_KEY = 'your_aws_secret_access_key'
# AWS_SNS_REGION = 'us-east-1'

# ✅ إعدادات الأمان للإنتاج
# Only enable SSL redirect in production environments, not in Replit development
if not DEBUG and os.environ.get('REPLIT_DEPLOYMENT') == '1':
    # HTTPS settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Other security settings
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Referrer policy
    SECURE_REFERRER_POLICY = 'same-origin'
elif not DEBUG:
    # For Replit development with DEBUG=False
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'

# ✅ إعدادات البريد الإلكتروني (للتطوير)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ✅ Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# ✅ Create required directories on startup
def create_directories():
    directories = [
        os.path.join(str(BASE_DIR), 'staticfiles'),
        os.path.join(str(BASE_DIR), 'media'),
        os.path.join(str(BASE_DIR), 'locale'),
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Set write permissions for media directory
        if 'media' in directory:
            os.chmod(directory, 0o755)

create_directories()

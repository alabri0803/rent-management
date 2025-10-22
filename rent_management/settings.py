"""
Django settings for rent_management project.
"""

import os
from django.utils.translation import gettext_lazy as _
from pathlib import Path
from dotenv import load_dotenv
import pymysql

# تثبيت PyMySQL كبديل لـ MySQLdb
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
    # Django REST Framework
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',
    'corsheaders',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',  # Cache middleware (must be first after session)
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',  # Cache middleware (must be last)
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

# إعدادات قاعدة بيانات MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'rent-management'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),  # كلمة المرور فارغة في XAMPP افتراضياً
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
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

# ==================== CACHING CONFIGURATION ====================
# نظام التخزين المؤقت لتحسين الأداء

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'rent-management-cache',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    },
    # Cache منفصل للـ API responses
    'api': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'api-cache',
        'TIMEOUT': 600,  # 10 minutes for API
        'OPTIONS': {
            'MAX_ENTRIES': 500,
        }
    },
    # Cache للتقارير والإحصائيات
    'reports': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'reports-cache',
        'TIMEOUT': 1800,  # 30 minutes for reports
        'OPTIONS': {
            'MAX_ENTRIES': 200,
        }
    }
}

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
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
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

# ✅ إعدادات الأمان
if not DEBUG:
    # إعدادات HTTPS للإنتاج
    SECURE_SSL_REDIRECT = False  # تعيين True عند استخدام HTTPS
    SESSION_COOKIE_SECURE = False  # تعيين True عند استخدام HTTPS
    CSRF_COOKIE_SECURE = False  # تعيين True عند استخدام HTTPS
    
    # إعدادات أمان أخرى
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'same-origin'

# ✅ إعدادات البريد الإلكتروني (للتطوير)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ==================== ADVANCED LOGGING CONFIGURATION ====================
# نظام سجلات متقدم وشامل

# إنشاء مجلد logs
LOGS_DIR = os.path.join(str(BASE_DIR), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    # ==================== Formatters ====================
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} | {name} | {module}.{funcName}:{lineno} | {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {asctime} | {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'json': {
            'format': '{"time": "{asctime}", "level": "{levelname}", "logger": "{name}", "message": "{message}"}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    
    # ==================== Filters ====================
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    
    # ==================== Handlers ====================
    'handlers': {
        # Console Handler - للتطوير
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
        
        # File Handler - جميع السجلات
        'file_all': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'all.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        
        # File Handler - الأخطاء فقط
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'errors.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        
        # File Handler - أمان وصلاحيات
        'file_security': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'security.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 20,
            'formatter': 'verbose',
        },
        
        # File Handler - API requests
        'file_api': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'api.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 15,
            'formatter': 'verbose',
        },
        
        # File Handler - Database queries
        'file_db': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'database.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        
        # File Handler - User actions (Audit Trail)
        'file_audit': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'audit.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 30,  # حفظ 30 ملف للتدقيق
            'formatter': 'verbose',
        },
        
        # File Handler - Performance
        'file_performance': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'performance.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 7,
            'formatter': 'verbose',
        },
        
        # Email Handler - للأخطاء الحرجة
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
    },
    
    # ==================== Loggers ====================
    'loggers': {
        # Django Core
        'django': {
            'handlers': ['console', 'file_all', 'file_errors'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Django Request
        'django.request': {
            'handlers': ['console', 'file_errors', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        
        # Django Database
        'django.db.backends': {
            'handlers': ['file_db'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        
        # Django Security
        'django.security': {
            'handlers': ['file_security', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Dashboard App
        'dashboard': {
            'handlers': ['console', 'file_all', 'file_errors'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        
        # API Logger
        'api': {
            'handlers': ['file_api', 'file_errors'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Security & Authentication
        'security': {
            'handlers': ['file_security', 'file_errors'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Audit Trail
        'audit': {
            'handlers': ['file_audit'],
            'level': 'INFO',
            'propagate': False,
        },
        
        # Performance
        'performance': {
            'handlers': ['file_performance'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    
    # Root Logger
    'root': {
        'handlers': ['console', 'file_all'],
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

# ==================== Django REST Framework Configuration ====================

REST_FRAMEWORK = {
    # Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    
    # Permissions
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # Filtering
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # Rendering
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    
    # Throttling (Rate Limiting)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    
    # Error handling
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    
    # Date/Time formatting
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
    
    # Caching
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 600,  # 10 minutes
    'DEFAULT_USE_CACHE': 'api',  # Use 'api' cache
}

# ==================== JWT Configuration ====================

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    'JTI_CLAIM': 'jti',
}

# ==================== CORS Configuration ====================

# السماح بجميع الأصول في التطوير (قم بتقييده في الإنتاج)
CORS_ALLOW_ALL_ORIGINS = DEBUG

# في الإنتاج، حدد الأصول المسموح بها
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ==================== Swagger/OpenAPI Configuration ====================

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
        }
    },
    'USE_SESSION_AUTH': True,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': ['get', 'post', 'put', 'delete', 'patch'],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'list',
    'DEEP_LINKING': True,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_MODEL_RENDERING': 'example',
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': True,
}

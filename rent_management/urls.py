r"""
URL configuration for rent_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth import views as auth_views
from dashboard.views import login_redirect
from dashboard.auth_views import EnhancedLoginView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="Rent Management API",
        default_version='v1',
        description="REST API for Rent Management System - نظام إدارة الإيجارات",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@rentmanagement.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')), # Language switcher URL
    # Root homepage → portal (non-localized fallback)
    path('', include('portal.urls')),
]

# Language-prefixed URLs
urlpatterns += i18n_patterns(
    path('login-redirect/', login_redirect, name='login_redirect'),
    path('accounts/login/', EnhancedLoginView.as_view(), name='login'),  # Override default login
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('portal/', include('portal.urls')), # Portal is the homepage
    prefix_default_language=True # Don't prefix the default language (ar)
)

# Add OTP authentication endpoints (not language-prefixed for API compatibility)
from dashboard.auth_views import send_login_otp, verify_login_otp
from dashboard.otp_views import send_phone_verification_otp

urlpatterns += [
    path('api/auth/send-otp/', send_login_otp, name='api_send_login_otp'),
    path('api/auth/verify-otp/', verify_login_otp, name='api_verify_login_otp'),
    path('api/auth/send-phone-otp/', send_phone_verification_otp, name='api_send_phone_otp'),
    
    # REST API URLs
    path('api/v1/', include('dashboard.api_urls')),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='api-redoc'),
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='api-schema-json'),
]

# Serve media files
if settings.DEBUG:
    # Development helper
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production: use protected media serving
    from dashboard.views import serve_protected_media
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_protected_media, name='serve_media'),
    ]
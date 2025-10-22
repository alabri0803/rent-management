"""
API URLs Configuration
تكوين مسارات API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .api_views import (
    BuildingViewSet,
    UnitViewSet,
    TenantViewSet,
    LeaseViewSet,
    PaymentViewSet,
    ExpenseViewSet,
    InvoiceViewSet,
    PaymentOverdueNoticeViewSet,
    ReportsViewSet,
)

# إنشاء Router
router = DefaultRouter()

# تسجيل ViewSets
router.register(r'buildings', BuildingViewSet, basename='building')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'leases', LeaseViewSet, basename='lease')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'overdue-notices', PaymentOverdueNoticeViewSet, basename='overdue-notice')
router.register(r'reports', ReportsViewSet, basename='report')

# URL Patterns
urlpatterns = [
    # JWT Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API Endpoints
    path('', include(router.urls)),
]

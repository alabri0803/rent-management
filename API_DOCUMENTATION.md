# Rent Management System - REST API Documentation
# نظام إدارة الإيجارات - توثيق API

## 📋 نظرة عامة | Overview

نظام REST API شامل لإدارة الإيجارات مع دعم JWT Authentication و Swagger Documentation.

A comprehensive REST API system for rent management with JWT Authentication and Swagger Documentation support.

---

## 🚀 البدء السريع | Quick Start

### 1. تثبيت المكتبات | Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. تطبيق Migrations

```bash
python manage.py migrate
```

### 3. تشغيل الخادم | Run Server

```bash
python manage.py runserver
```

### 4. الوصول للتوثيق | Access Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **JSON Schema**: http://localhost:8000/api/swagger.json

---

## 🔐 المصادقة | Authentication

### JWT Token Authentication

#### الحصول على Token | Get Token

```http
POST /api/v1/auth/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### تحديث Token | Refresh Token

```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### استخدام Token | Use Token

```http
GET /api/v1/buildings/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 📚 API Endpoints

### 🏢 المباني | Buildings

#### قائمة المباني | List Buildings
```http
GET /api/v1/buildings/
```

#### تفاصيل مبنى | Building Details
```http
GET /api/v1/buildings/{id}/
```

#### إنشاء مبنى | Create Building
```http
POST /api/v1/buildings/
Content-Type: application/json

{
    "name": "مبنى السلام",
    "address": "شارع الرئيسي، مسقط",
    "total_units": 10,
    "description": "مبنى سكني حديث"
}
```

#### تحديث مبنى | Update Building
```http
PUT /api/v1/buildings/{id}/
PATCH /api/v1/buildings/{id}/
```

#### حذف مبنى | Delete Building
```http
DELETE /api/v1/buildings/{id}/
```

#### وحدات المبنى | Building Units
```http
GET /api/v1/buildings/{id}/units/
```

#### إحصائيات المبنى | Building Statistics
```http
GET /api/v1/buildings/{id}/statistics/
```

---

### 🏠 الوحدات | Units

#### قائمة الوحدات | List Units
```http
GET /api/v1/units/
```

#### الوحدات المتاحة فقط | Available Units Only
```http
GET /api/v1/units/available/
```

#### تفاصيل وحدة | Unit Details
```http
GET /api/v1/units/{id}/
```

#### إنشاء وحدة | Create Unit
```http
POST /api/v1/units/
Content-Type: application/json

{
    "building_id": 1,
    "unit_number": "101",
    "floor": 1,
    "unit_type": "apartment",
    "bedrooms": 2,
    "bathrooms": 2,
    "area": 120.5,
    "rent_amount": 500.00,
    "description": "شقة مفروشة بالكامل"
}
```

#### سجل عقود الوحدة | Unit Lease History
```http
GET /api/v1/units/{id}/lease_history/
```

---

### 👥 المستأجرين | Tenants

#### قائمة المستأجرين | List Tenants
```http
GET /api/v1/tenants/
```

#### تفاصيل مستأجر | Tenant Details
```http
GET /api/v1/tenants/{id}/
```

#### إنشاء مستأجر | Create Tenant
```http
POST /api/v1/tenants/
Content-Type: application/json

{
    "name": "أحمد محمد",
    "phone": "+96812345678",
    "email": "ahmed@example.com",
    "tenant_type": "sole_proprietorship",
    "national_id": "12345678",
    "address": "مسقط، سلطنة عمان"
}
```

#### عقود المستأجر | Tenant Leases
```http
GET /api/v1/tenants/{id}/leases/
```

#### دفعات المستأجر | Tenant Payments
```http
GET /api/v1/tenants/{id}/payments/
```

#### ملخص مالي للمستأجر | Tenant Financial Summary
```http
GET /api/v1/tenants/{id}/financial_summary/
```

---

### 📝 العقود | Leases

#### قائمة العقود | List Leases
```http
GET /api/v1/leases/
```

#### العقود النشطة فقط | Active Leases Only
```http
GET /api/v1/leases/active/
```

#### العقود القريبة من الانتهاء | Expiring Soon
```http
GET /api/v1/leases/expiring_soon/
```

#### تفاصيل عقد | Lease Details
```http
GET /api/v1/leases/{id}/
```

#### إنشاء عقد | Create Lease
```http
POST /api/v1/leases/
Content-Type: application/json

{
    "unit_id": 1,
    "tenant_id": 1,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "monthly_rent": 500.00,
    "deposit_amount": 500.00,
    "payment_frequency": "monthly",
    "notes": "عقد سنوي"
}
```

#### دفعات العقد | Lease Payments
```http
GET /api/v1/leases/{id}/payments/
```

#### كشف حساب العقد | Lease Payment Summary
```http
GET /api/v1/leases/{id}/payment_summary/
```

#### تجديد عقد | Renew Lease
```http
POST /api/v1/leases/{id}/renew/
Content-Type: application/json

{
    "start_date": "2026-01-01",
    "end_date": "2026-12-31",
    "monthly_rent": 550.00
}
```

#### إلغاء عقد | Cancel Lease
```http
POST /api/v1/leases/{id}/cancel/
Content-Type: application/json

{
    "cancellation_reason": "طلب المستأجر"
}
```

---

### 💰 الدفعات | Payments

#### قائمة الدفعات | List Payments
```http
GET /api/v1/payments/
```

#### تفاصيل دفعة | Payment Details
```http
GET /api/v1/payments/{id}/
```

#### إنشاء دفعة | Create Payment
```http
POST /api/v1/payments/
Content-Type: application/json

{
    "lease_id": 1,
    "amount": 500.00,
    "payment_date": "2025-01-15",
    "payment_for_month": 1,
    "payment_for_year": 2025,
    "payment_method": "cash",
    "notes": "دفعة شهر يناير"
}
```

#### الدفعات حسب الشهر | Payments by Month
```http
GET /api/v1/payments/by_month/?month=1&year=2025
```

#### إحصائيات الدفعات | Payments Statistics
```http
GET /api/v1/payments/statistics/?start_date=2025-01-01&end_date=2025-12-31
```

---

### 💸 المصروفات | Expenses

#### قائمة المصروفات | List Expenses
```http
GET /api/v1/expenses/
```

#### تفاصيل مصروف | Expense Details
```http
GET /api/v1/expenses/{id}/
```

#### إنشاء مصروف | Create Expense
```http
POST /api/v1/expenses/
Content-Type: application/json

{
    "building": 1,
    "category": "maintenance",
    "description": "صيانة المصعد",
    "amount": 150.00,
    "expense_date": "2025-01-20",
    "vendor": "شركة الصيانة"
}
```

#### المصروفات حسب الفئة | Expenses by Category
```http
GET /api/v1/expenses/by_category/
```

#### إحصائيات المصروفات | Expenses Statistics
```http
GET /api/v1/expenses/statistics/?start_date=2025-01-01&end_date=2025-12-31
```

---

### 📄 الفواتير | Invoices

#### قائمة الفواتير | List Invoices
```http
GET /api/v1/invoices/
```

#### الفواتير المتأخرة | Overdue Invoices
```http
GET /api/v1/invoices/overdue/
```

#### تفاصيل فاتورة | Invoice Details
```http
GET /api/v1/invoices/{id}/
```

#### إنشاء فاتورة | Create Invoice
```http
POST /api/v1/invoices/
Content-Type: application/json

{
    "tenant_id": 1,
    "issue_date": "2025-01-01",
    "due_date": "2025-01-15",
    "status": "pending",
    "notes": "فاتورة رسوم التسجيل"
}
```

---

### ⚠️ الإنذارات | Overdue Notices

#### قائمة الإنذارات | List Notices
```http
GET /api/v1/overdue-notices/
```

#### الإنذارات النشطة | Active Notices
```http
GET /api/v1/overdue-notices/active/
```

#### تفاصيل إنذار | Notice Details
```http
GET /api/v1/overdue-notices/{id}/
```

---

### 📊 التقارير | Reports

#### تقرير مالي | Financial Report
```http
GET /api/v1/reports/financial/?start_date=2025-01-01&end_date=2025-12-31
```

**Response:**
```json
{
    "period": "2025-01-01 to 2025-12-31",
    "total_income": 50000.00,
    "total_expenses": 10000.00,
    "net_income": 40000.00,
    "total_payments": 100,
    "total_leases": 20,
    "occupancy_rate": 85.50
}
```

#### تقرير العقود | Leases Report
```http
GET /api/v1/reports/leases/
```

**Response:**
```json
{
    "total_leases": 25,
    "active_leases": 20,
    "expired_leases": 3,
    "cancelled_leases": 2,
    "expiring_soon": 5,
    "total_monthly_rent": 12500.00
}
```

#### تقرير الإشغال | Occupancy Report
```http
GET /api/v1/reports/occupancy/
```

**Response:**
```json
{
    "total_units": 50,
    "occupied_units": 42,
    "available_units": 8,
    "occupancy_rate": 84.00,
    "by_building": [...]
}
```

---

## 🔍 البحث والفلترة | Search & Filtering

### البحث | Search
```http
GET /api/v1/tenants/?search=أحمد
GET /api/v1/leases/?search=2023/001
```

### الفلترة | Filtering
```http
GET /api/v1/units/?building=1&unit_type=apartment
GET /api/v1/leases/?status=active&tenant=1
GET /api/v1/payments/?payment_method=cash
```

### الترتيب | Ordering
```http
GET /api/v1/payments/?ordering=-payment_date
GET /api/v1/leases/?ordering=start_date
```

### الصفحات | Pagination
```http
GET /api/v1/buildings/?page=2
GET /api/v1/tenants/?page_size=50
```

---

## 🔒 الصلاحيات | Permissions

### الصلاحيات المخصصة | Custom Permissions

- `IsAuthenticated`: يجب تسجيل الدخول
- `CanManageBuildings`: صلاحية إدارة المباني
- `CanManageUnits`: صلاحية إدارة الوحدات
- `CanManageLeases`: صلاحية إدارة العقود
- `CanManageTenants`: صلاحية إدارة المستأجرين
- `CanManagePayments`: صلاحية إدارة الدفعات
- `CanManageExpenses`: صلاحية إدارة المصروفات
- `CanViewReports`: صلاحية عرض التقارير

---

## ⚡ Rate Limiting

### الحدود الافتراضية | Default Limits

- **مستخدمين مسجلين**: 1000 طلب/ساعة
- **مستخدمين غير مسجلين**: 100 طلب/ساعة

### رسائل الخطأ | Error Messages

```json
{
    "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

---

## 📝 أمثلة كاملة | Complete Examples

### مثال 1: إنشاء عقد جديد | Example 1: Create New Lease

```bash
# 1. الحصول على Token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# 2. إنشاء العقد
curl -X POST http://localhost:8000/api/v1/leases/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "unit_id": 1,
    "tenant_id": 1,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "monthly_rent": 500.00,
    "deposit_amount": 500.00
  }'
```

### مثال 2: الحصول على تقرير مالي | Example 2: Get Financial Report

```bash
curl -X GET "http://localhost:8000/api/v1/reports/financial/?start_date=2025-01-01&end_date=2025-12-31" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## ❌ رموز الأخطاء | Error Codes

| Code | الوصف | Description |
|------|--------|-------------|
| 200 | نجح الطلب | Success |
| 201 | تم الإنشاء | Created |
| 400 | طلب خاطئ | Bad Request |
| 401 | غير مصرح | Unauthorized |
| 403 | ممنوع | Forbidden |
| 404 | غير موجود | Not Found |
| 429 | تجاوز الحد | Too Many Requests |
| 500 | خطأ في الخادم | Server Error |

---

## 🛠️ أدوات التطوير | Development Tools

### Postman Collection
يمكنك استيراد Swagger JSON في Postman:
```
http://localhost:8000/api/swagger.json
```

### cURL Examples
جميع الأمثلة أعلاه تستخدم cURL.

### Python Requests
```python
import requests

# الحصول على Token
response = requests.post('http://localhost:8000/api/v1/auth/token/', 
    json={'username': 'admin', 'password': 'password'})
token = response.json()['access']

# استخدام Token
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/api/v1/buildings/', headers=headers)
buildings = response.json()
```

---

## 📞 الدعم | Support

للمساعدة والدعم:
- **Email**: contact@rentmanagement.local
- **Documentation**: http://localhost:8000/api/docs/

---

## 📄 الترخيص | License

BSD License

---

**تم التطوير بواسطة | Developed by**: Rent Management Team
**الإصدار | Version**: 1.0.0
**آخر تحديث | Last Updated**: 2025-01-23

from django.urls import path
from .views import (
    DashboardHomeView,
    TenantListView, TenantDetailView, TenantCreateView, TenantUpdateView, TenantDeleteView,
    UnitListView, UnitDetailView, UnitCreateView, UnitUpdateView, UnitDeleteView,
    BuildingListView, BuildingCreateView, BuildingUpdateView, BuildingDeleteView,
    LeaseListView, LeaseDetailView, LeaseCreateView, LeaseUpdateView, LeaseDeleteView, renew_lease, LeaseCancelView,
    DocumentUploadView, DocumentDeleteView,
    MaintenanceRequestAdminListView, MaintenanceRequestAdminUpdateView,
    ExpenseListView, ExpenseCreateView, ExpenseUpdateView, ExpenseDeleteView,
    PaymentListView, PaymentCreateView, PaymentUpdateView, PaymentDeleteView, PaymentReceiptPDFView,
    CheckManagementView, CheckStatusUpdateView,
    UserManagementView, UserCreateView, UserUpdateView, UserDeleteView,
    ReportSelectionView, LeaseReportView, GenerateTenantStatementPDF, GenerateMonthlyPLReportPDF, GenerateAnnualPLReportPDF, GenerateOccupancyReportPDF, GeneratePaymentReceiptPDF,
    CompanyUpdateView, UpdateTenantRatingView,
    InvoiceListView, InvoiceDetailView, InvoiceCreateView, InvoiceUpdateView, InvoiceDeleteView,
    # Real Estate Office Management Views
    RealEstateOfficeListView, RealEstateOfficeDetailView, RealEstateOfficeCreateView, RealEstateOfficeUpdateView, RealEstateOfficeDeleteView,
    BuildingOwnerListView, BuildingOwnerDetailView, BuildingOwnerCreateView, BuildingOwnerUpdateView, BuildingOwnerDeleteView,
    CommissionAgreementListView, CommissionAgreementDetailView, CommissionAgreementCreateView, CommissionAgreementUpdateView, CommissionAgreementDeleteView,
    RentCollectionListView, RentCollectionCreateView, RentCollectionUpdateView, RentCollectionDeleteView,
    CommissionDistributionListView, CommissionDistributionCreateView, CommissionDistributionUpdateView, CommissionDistributionDeleteView,
    SecurityDepositListView, SecurityDepositCreateView, SecurityDepositUpdateView, SecurityDepositDeleteView,
    create_commission_distribution,
    finance_unlock, finance_lock,
    backup_now, custom_logout, backup_restore_page, restore_backup,
    media_diagnostics,
    # Payment Overdue Notice Views
    PaymentOverdueNoticeListView, PaymentOverdueNoticeDetailView,
    generate_automatic_notices, notice_update_status, notice_print_view, notices_bulk_actions,
    # Lease Renewal Notice Views
    LeaseRenewalNoticeListView, LeaseRenewalNoticeDetailView,
    renewal_notice_update_response, renewal_notice_print_view, generate_renewal_notices_preview, renewal_notices_bulk_actions,
    # Registration Invoice
    registration_invoice_view,
    # New Report Views
    renewal_invoice_view, cancellation_form_view, renewal_form_view,
    tenant_comprehensive_report_view,
)
from .auth_views import (
    EnhancedLoginView, send_login_otp, verify_login_otp, user_profile,
)
from .otp_views import (
    send_otp_view, verify_otp_view, setup_phone_number, verify_phone_number, send_phone_verification_otp
)
from .export_views import (
    export_tenants_excel,
    export_leases_excel,
    export_payments_excel,
    export_expenses_excel,
    export_buildings_excel,
    export_units_excel,
    export_maintenance_excel,
)

urlpatterns = [
    path('', DashboardHomeView.as_view(), name='dashboard_home'),
    # Backup & Custom Logout
    path('backup/', backup_now, name='dashboard_backup_now'),
    path('backup/restore/', backup_restore_page, name='dashboard_backup_restore_page'),
    path('backup/restore/apply/', restore_backup, name='dashboard_restore_backup'),
    path('logout/', custom_logout, name='dashboard_custom_logout'),
    # Finance lock/unlock
    path('finance/unlock/', finance_unlock, name='finance_unlock'),
    path('finance/lock/', finance_lock, name='finance_lock'),
    
    # Media Diagnostics
    path('diagnostics/media/', media_diagnostics, name='media_diagnostics'),

    # Company Settings
    path('settings/company/', CompanyUpdateView.as_view(), name='company_update'),

    # Tenants
    path('tenants/', TenantListView.as_view(), name='tenant_list'),
    path('tenants/<int:pk>/', TenantDetailView.as_view(), name='tenant_detail'),
    path('tenants/new/', TenantCreateView.as_view(), name='tenant_create'),
    path('tenants/<int:pk>/edit/', TenantUpdateView.as_view(), name='tenant_update'),
    path('tenants/<int:pk>/delete/', TenantDeleteView.as_view(), name='tenant_delete'),

    # Units
    path('units/', UnitListView.as_view(), name='unit_list'),
    path('units/<int:pk>/', UnitDetailView.as_view(), name='unit_detail'),
    path('units/new/', UnitCreateView.as_view(), name='unit_create'),
    path('units/<int:pk>/edit/', UnitUpdateView.as_view(), name='unit_update'),
    path('units/<int:pk>/delete/', UnitDeleteView.as_view(), name='unit_delete'),

    # Buildings
    path('buildings/', BuildingListView.as_view(), name='building_list'),
    path('buildings/new/', BuildingCreateView.as_view(), name='building_create'),
    path('buildings/<int:pk>/edit/', BuildingUpdateView.as_view(), name='building_update'),
    path('buildings/<int:pk>/delete/', BuildingDeleteView.as_view(), name='building_delete'),

    # Leases
    path('lease/', LeaseListView.as_view(), name='lease_list'),
    path('lease/<int:pk>/', LeaseDetailView.as_view(), name='lease_detail'),
    path('lease/new/', LeaseCreateView.as_view(), name='lease_create'),
    path('lease/<int:pk>/edit/', LeaseUpdateView.as_view(), name='lease_update'),
    path('lease/<int:pk>/delete/', LeaseDeleteView.as_view(), name='lease_delete'),
    path('lease/<int:pk>/renew/', renew_lease, name='lease_renew'),
    path('lease/<int:pk>/cancel/', LeaseCancelView.as_view(), name='lease_cancel'), # ADDED
    path('lease/<int:lease_id>/registration-invoice/', registration_invoice_view, name='registration_invoice'),
    path('lease/<int:lease_id>/renewal-invoice/', renewal_invoice_view, name='renewal_invoice'),
    path('lease/<int:lease_id>/cancellation-form/', cancellation_form_view, name='cancellation_form'),
    path('lease/<int:lease_id>/renewal-form/', renewal_form_view, name='renewal_form'),

    # Tenant Reports
    path('tenant/<int:tenant_id>/comprehensive-report/', tenant_comprehensive_report_view, name='tenant_comprehensive_report'),

    # Tenant Rating - ADDED
    path('tenant/<int:pk>/rate/', UpdateTenantRatingView.as_view(), name='tenant_rate'),

    # Documents
    path('lease/<int:lease_pk>/documents/upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('documents/<int:pk>/delete/', DocumentDeleteView.as_view(), name='document_delete'),

    # Maintenance
    path('maintenance/', MaintenanceRequestAdminListView.as_view(), name='maintenance_admin_list'),
    path('maintenance/<int:pk>/', MaintenanceRequestAdminUpdateView.as_view(), name='maintenance_admin_update'),

    # Expenses
    path('expenses/', ExpenseListView.as_view(), name='expense_list'),
    path('expenses/new/', ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/<int:pk>/edit/', ExpenseUpdateView.as_view(), name='expense_update'),
    path('expenses/<int:pk>/delete/', ExpenseDeleteView.as_view(), name='expense_delete'),

    # Payments
    path('payments/', PaymentListView.as_view(), name='payment_list'),
    path('payments/new/', PaymentCreateView.as_view(), name='payment_create'),
    path('payments/<int:pk>/edit/', PaymentUpdateView.as_view(), name='payment_update'),
    path('payments/<int:pk>/delete/', PaymentDeleteView.as_view(), name='payment_delete'), # ADDED
    path('payments/<int:pk>/receipt/', PaymentReceiptPDFView.as_view(), name='payment_receipt'),

    # Security Deposits
    path('security-deposits/', SecurityDepositListView.as_view(), name='security_deposit_list'),
    path('security-deposits/new/', SecurityDepositCreateView.as_view(), name='security_deposit_create'),
    path('security-deposits/<int:pk>/edit/', SecurityDepositUpdateView.as_view(), name='security_deposit_update'),
    path('security-deposits/<int:pk>/delete/', SecurityDepositDeleteView.as_view(), name='security_deposit_delete'),
    
    # Check Management
    path('checks/', CheckManagementView.as_view(), name='check_management'),
    path('checks/<int:pk>/update-status/', CheckStatusUpdateView.as_view(), name='check_status_update'),
    
    # User Management
    path('users/', UserManagementView.as_view(), name='user_management'),
    path('users/new/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),

    # Reports
    path('reports/', ReportSelectionView.as_view(), name='report_selection'),
    path('reports/leases/', LeaseReportView.as_view(), name='report_leases'),
    path('reports/tenant/<int:lease_pk>/', GenerateTenantStatementPDF.as_view(), name='report_tenant_statement'),
    path('reports/payment/<int:pk>/receipt/', GeneratePaymentReceiptPDF.as_view(), name='report_payment_receipt'), # ADDED
    path('reports/monthly-pl/', GenerateMonthlyPLReportPDF.as_view(), name='report_monthly_pl'),
    path('reports/annual-pl/', GenerateAnnualPLReportPDF.as_view(), name='report_annual_pl'), # ADDED
    path('reports/occupancy/', GenerateOccupancyReportPDF.as_view(), name='report_occupancy'), # ADDED
    
    # Excel Exports
    path('export/tenants/', export_tenants_excel, name='export_tenants_excel'),
    path('export/leases/', export_leases_excel, name='export_leases_excel'),
    path('export/payments/', export_payments_excel, name='export_payments_excel'),
    path('export/expenses/', export_expenses_excel, name='export_expenses_excel'),
    path('export/buildings/', export_buildings_excel, name='export_buildings_excel'),
    path('export/units/', export_units_excel, name='export_units_excel'),
    path('export/maintenance/', export_maintenance_excel, name='export_maintenance_excel'),

    # Invoices
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/new/', InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/edit/', InvoiceUpdateView.as_view(), name='invoice_update'),
    path('invoices/<int:pk>/delete/', InvoiceDeleteView.as_view(), name='invoice_delete'),
    
    # Authentication & Profile
    path('profile/', user_profile, name='profile'),
    path('setup-phone/', setup_phone_number, name='setup_phone'),
    path('verify-phone/', verify_phone_number, name='verify_phone'),
    
    # Real Estate Office Management
    # Real Estate Offices
    path('real-estate-offices/', RealEstateOfficeListView.as_view(), name='real_estate_office_list'),
    path('real-estate-offices/<int:pk>/', RealEstateOfficeDetailView.as_view(), name='real_estate_office_detail'),
    path('real-estate-offices/new/', RealEstateOfficeCreateView.as_view(), name='real_estate_office_create'),
    path('real-estate-offices/<int:pk>/edit/', RealEstateOfficeUpdateView.as_view(), name='real_estate_office_update'),
    path('real-estate-offices/<int:pk>/delete/', RealEstateOfficeDeleteView.as_view(), name='real_estate_office_delete'),
    
    # Building Owners
    path('building-owners/', BuildingOwnerListView.as_view(), name='building_owner_list'),
    path('building-owners/<int:pk>/', BuildingOwnerDetailView.as_view(), name='building_owner_detail'),
    path('building-owners/new/', BuildingOwnerCreateView.as_view(), name='building_owner_create'),
    path('building-owners/<int:pk>/edit/', BuildingOwnerUpdateView.as_view(), name='building_owner_update'),
    path('building-owners/<int:pk>/delete/', BuildingOwnerDeleteView.as_view(), name='building_owner_delete'),
    
    # Commission Agreements
    path('commission-agreements/', CommissionAgreementListView.as_view(), name='commission_agreement_list'),
    path('commission-agreements/<int:pk>/', CommissionAgreementDetailView.as_view(), name='commission_agreement_detail'),
    path('commission-agreements/new/', CommissionAgreementCreateView.as_view(), name='commission_agreement_create'),
    path('commission-agreements/<int:pk>/edit/', CommissionAgreementUpdateView.as_view(), name='commission_agreement_update'),
    path('commission-agreements/<int:pk>/delete/', CommissionAgreementDeleteView.as_view(), name='commission_agreement_delete'),
    
    # Rent Collections
    path('rent-collections/', RentCollectionListView.as_view(), name='rent_collection_list'),
    path('rent-collections/new/', RentCollectionCreateView.as_view(), name='rent_collection_create'),
    path('rent-collections/<int:pk>/edit/', RentCollectionUpdateView.as_view(), name='rent_collection_update'),
    path('rent-collections/<int:pk>/delete/', RentCollectionDeleteView.as_view(), name='rent_collection_delete'),
    path('rent-collections/<int:collection_pk>/create-distribution/', create_commission_distribution, name='create_commission_distribution'),
    
    # Commission Distributions
    path('commission-distributions/', CommissionDistributionListView.as_view(), name='commission_distribution_list'),
    path('commission-distributions/<int:pk>/', CommissionDistributionListView.as_view(), name='commission_distribution_detail'),
    path('commission-distributions/new/', CommissionDistributionCreateView.as_view(), name='commission_distribution_create'),
    path('commission-distributions/<int:pk>/edit/', CommissionDistributionUpdateView.as_view(), name='commission_distribution_update'),
    path('commission-distributions/<int:pk>/delete/', CommissionDistributionDeleteView.as_view(), name='commission_distribution_delete'),
    
    # Lease Renewal Notices
    path('renewal-notices/', LeaseRenewalNoticeListView.as_view(), name='renewal_notices_list'),
    path('renewal-notices/<int:pk>/', LeaseRenewalNoticeDetailView.as_view(), name='renewal_notice_detail'),
    path('renewal-notices/<int:pk>/update-response/', renewal_notice_update_response, name='renewal_notice_update_response'),
    path('renewal-notices/<int:pk>/print/', renewal_notice_print_view, name='renewal_notice_print_view'),
    path('renewal-notices/generate-preview/', generate_renewal_notices_preview, name='generate_renewal_notices_preview'),
    path('renewal-notices/bulk-actions/', renewal_notices_bulk_actions, name='renewal_notices_bulk_actions'),
]
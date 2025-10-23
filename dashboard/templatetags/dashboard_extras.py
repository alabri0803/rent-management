from django import template
from dashboard.models import Company

register = template.Library()

@register.simple_tag
def get_company_name():
    company = Company.objects.first()
    return company.name if company else 'Rent Management'

@register.simple_tag
def get_company_logo():
    company = Company.objects.first()
    return company.logo.url if company and company.logo else None

# ==== Building Delete Context Filters ====
@register.filter
def leaselist_active_count(units):
    """Return number of active leases for all units in a building."""
    from dashboard.models import Lease
    return Lease.objects.filter(unit__in=units, status='active').count()

@register.filter
def leaselist_tenants_count(units):
    """Return number of unique tenants with active leases for all units."""
    from dashboard.models import Lease
    return Lease.objects.filter(unit__in=units, status='active').values('tenant').distinct().count()

@register.filter
def leaselist_maintenance_count(units):
    """Return number of maintenance requests for all units."""
    from dashboard.models import MaintenanceRequest
    return MaintenanceRequest.objects.filter(lease__unit__in=units).count()
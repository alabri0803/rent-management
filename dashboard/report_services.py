"""
خدمات التقارير والتحليلات - Report Services
توفر دوال لإنشاء وتحليل التقارير المختلفة
"""

from django.db.models import Sum, Count, Avg, Q, F, DecimalField, Case, When
from django.db.models.functions import TruncMonth, TruncYear, Coalesce
from django.utils import timezone
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import calendar


class ReportService:
    """خدمة التقارير الرئيسية"""
    
    @staticmethod
    def get_profitability_report(start_date, end_date, building_id=None):
        """
        تقرير الربحية
        يحسب الإيرادات والمصروفات وصافي الربح
        """
        from .models import Payment, Expense, Lease
        
        # فلترة حسب المبنى إذا تم تحديده
        filters = Q(payment_date__gte=start_date, payment_date__lte=end_date)
        if building_id:
            filters &= Q(lease__unit__building_id=building_id)
        
        # حساب الإيرادات
        payments = Payment.objects.filter(filters)
        total_revenue = payments.aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']
        
        # تفصيل الإيرادات حسب طريقة الدفع
        revenue_by_method = payments.values('payment_method').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # حساب المصروفات
        expense_filters = Q(expense_date__gte=start_date, expense_date__lte=end_date)
        if building_id:
            expense_filters &= Q(building_id=building_id)
        
        expenses = Expense.objects.filter(expense_filters)
        total_expenses = expenses.aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']
        
        # تفصيل المصروفات حسب النوع
        expenses_by_category = expenses.values('category').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # حساب صافي الربح
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # الإيرادات الشهرية
        monthly_revenue = payments.annotate(
            month=TruncMonth('payment_date')
        ).values('month').annotate(
            revenue=Sum('amount')
        ).order_by('month')
        
        # المصروفات الشهرية
        monthly_expenses = expenses.annotate(
            month=TruncMonth('expense_date')
        ).values('month').annotate(
            expenses=Sum('amount')
        ).order_by('month')
        
        return {
            'period': {
                'start': start_date,
                'end': end_date,
            },
            'revenue': {
                'total': float(total_revenue),
                'by_method': list(revenue_by_method),
                'monthly': list(monthly_revenue),
            },
            'expenses': {
                'total': float(total_expenses),
                'by_category': list(expenses_by_category),
                'monthly': list(monthly_expenses),
            },
            'profitability': {
                'net_profit': float(net_profit),
                'profit_margin': float(profit_margin),
            }
        }
    
    @staticmethod
    def get_cash_flow_report(start_date, end_date, building_id=None):
        """
        تقرير التدفق النقدي
        يحلل التدفقات النقدية الداخلة والخارجة
        """
        from .models import Payment, Expense
        
        # التدفقات الداخلة (المدفوعات)
        payment_filters = Q(payment_date__gte=start_date, payment_date__lte=end_date)
        if building_id:
            payment_filters &= Q(lease__unit__building_id=building_id)
        
        inflows = Payment.objects.filter(payment_filters).annotate(
            month=TruncMonth('payment_date')
        ).values('month').annotate(
            amount=Sum('amount'),
            count=Count('id')
        ).order_by('month')
        
        # التدفقات الخارجة (المصروفات)
        expense_filters = Q(expense_date__gte=start_date, expense_date__lte=end_date)
        if building_id:
            expense_filters &= Q(building_id=building_id)
        
        outflows = Expense.objects.filter(expense_filters).annotate(
            month=TruncMonth('expense_date')
        ).values('month').annotate(
            amount=Sum('amount'),
            count=Count('id')
        ).order_by('month')
        
        # حساب صافي التدفق النقدي لكل شهر
        cash_flow = []
        inflows_dict = {item['month']: item for item in inflows}
        outflows_dict = {item['month']: item for item in outflows}
        
        all_months = set(list(inflows_dict.keys()) + list(outflows_dict.keys()))
        
        for month in sorted(all_months):
            inflow_amount = inflows_dict.get(month, {}).get('amount', 0) or 0
            outflow_amount = outflows_dict.get(month, {}).get('amount', 0) or 0
            net_flow = inflow_amount - outflow_amount
            
            cash_flow.append({
                'month': month,
                'inflow': float(inflow_amount),
                'outflow': float(outflow_amount),
                'net_flow': float(net_flow),
            })
        
        # الإجماليات
        total_inflow = sum(item['inflow'] for item in cash_flow)
        total_outflow = sum(item['outflow'] for item in cash_flow)
        total_net_flow = total_inflow - total_outflow
        
        return {
            'period': {
                'start': start_date,
                'end': end_date,
            },
            'monthly_cash_flow': cash_flow,
            'totals': {
                'inflow': total_inflow,
                'outflow': total_outflow,
                'net_flow': total_net_flow,
            }
        }
    
    @staticmethod
    def get_occupancy_report(date=None, building_id=None):
        """
        تقرير معدل الإشغال
        يحلل معدل إشغال الوحدات
        """
        from .models import Unit, Lease
        
        if date is None:
            date = timezone.now().date()
        
        # فلترة الوحدات
        units_query = Unit.objects.all()
        if building_id:
            units_query = units_query.filter(building_id=building_id)
        
        # إجمالي الوحدات
        total_units = units_query.count()
        
        # الوحدات المشغولة (لها عقد نشط)
        occupied_units = units_query.filter(
            is_available=False
        ).count()
        
        # الوحدات الشاغرة
        vacant_units = total_units - occupied_units
        
        # معدل الإشغال
        occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
        
        # تفصيل حسب نوع الوحدة
        by_type = units_query.values('unit_type').annotate(
            total=Count('id'),
            occupied=Count('id', filter=Q(is_available=False)),
            vacant=Count('id', filter=Q(is_available=True))
        )
        
        for item in by_type:
            item['occupancy_rate'] = (item['occupied'] / item['total'] * 100) if item['total'] > 0 else 0
        
        # تفصيل حسب المبنى
        by_building = units_query.values('building__name', 'building_id').annotate(
            total=Count('id'),
            occupied=Count('id', filter=Q(is_available=False)),
            vacant=Count('id', filter=Q(is_available=True))
        )
        
        for item in by_building:
            item['occupancy_rate'] = (item['occupied'] / item['total'] * 100) if item['total'] > 0 else 0
        
        # الاتجاه التاريخي (آخر 12 شهر)
        historical = []
        for i in range(12, 0, -1):
            month_date = date - relativedelta(months=i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
            
            # العقود النشطة في ذلك الشهر
            active_leases = Lease.objects.filter(
                start_date__lte=month_end,
                end_date__gte=month_start,
                status='active'
            )
            
            if building_id:
                active_leases = active_leases.filter(unit__building_id=building_id)
            
            occupied_count = active_leases.count()
            rate = (occupied_count / total_units * 100) if total_units > 0 else 0
            
            historical.append({
                'month': month_start,
                'occupied': occupied_count,
                'vacant': total_units - occupied_count,
                'occupancy_rate': float(rate),
            })
        
        return {
            'date': date,
            'summary': {
                'total_units': total_units,
                'occupied_units': occupied_units,
                'vacant_units': vacant_units,
                'occupancy_rate': float(occupancy_rate),
            },
            'by_type': list(by_type),
            'by_building': list(by_building),
            'historical': historical,
        }
    
    @staticmethod
    def get_overdue_tenants_report(as_of_date=None, min_days_overdue=30):
        """
        تقرير المستأجرين المتأخرين
        يعرض المستأجرين الذين لديهم دفعات متأخرة
        """
        from .models import Lease, Tenant
        
        if as_of_date is None:
            as_of_date = timezone.now().date()
        
        overdue_tenants = []
        
        # العقود النشطة
        active_leases = Lease.objects.filter(
            status='active',
            start_date__lte=as_of_date
        ).select_related('tenant', 'unit', 'unit__building')
        
        for lease in active_leases:
            payment_summary = lease.get_payment_summary()
            
            # البحث عن الشهور المتأخرة
            overdue_months = [
                month for month in payment_summary
                if month['status'] == 'overdue' and 
                month['balance'] > 0 and
                month.get('days_overdue', 0) >= min_days_overdue
            ]
            
            if overdue_months:
                total_overdue = sum(month['balance'] for month in overdue_months)
                max_days_overdue = max(month.get('days_overdue', 0) for month in overdue_months)
                
                overdue_tenants.append({
                    'tenant_id': lease.tenant.id,
                    'tenant_name': lease.tenant.name,
                    'tenant_phone': lease.tenant.phone,
                    'tenant_email': lease.tenant.email,
                    'lease_id': lease.id,
                    'lease_number': lease.lease_number,
                    'unit': f"{lease.unit.building.name} - {lease.unit.unit_number}",
                    'monthly_rent': float(lease.monthly_rent),
                    'overdue_months_count': len(overdue_months),
                    'total_overdue_amount': float(total_overdue),
                    'max_days_overdue': max_days_overdue,
                    'overdue_months': overdue_months,
                })
        
        # ترتيب حسب المبلغ المتأخر (الأعلى أولاً)
        overdue_tenants.sort(key=lambda x: x['total_overdue_amount'], reverse=True)
        
        # الإحصائيات
        total_overdue_amount = sum(t['total_overdue_amount'] for t in overdue_tenants)
        total_overdue_months = sum(t['overdue_months_count'] for t in overdue_tenants)
        
        return {
            'as_of_date': as_of_date,
            'min_days_overdue': min_days_overdue,
            'summary': {
                'total_overdue_tenants': len(overdue_tenants),
                'total_overdue_amount': total_overdue_amount,
                'total_overdue_months': total_overdue_months,
            },
            'tenants': overdue_tenants,
        }
    
    @staticmethod
    def get_lease_expiry_report(months_ahead=3):
        """
        تقرير انتهاء العقود
        يعرض العقود التي ستنتهي خلال فترة محددة
        """
        from .models import Lease
        
        today = timezone.now().date()
        end_date = today + relativedelta(months=months_ahead)
        
        expiring_leases = Lease.objects.filter(
            status='active',
            end_date__gte=today,
            end_date__lte=end_date
        ).select_related('tenant', 'unit', 'unit__building').order_by('end_date')
        
        leases_data = []
        for lease in expiring_leases:
            days_until_expiry = (lease.end_date - today).days
            
            leases_data.append({
                'lease_id': lease.id,
                'lease_number': lease.lease_number,
                'tenant_name': lease.tenant.name,
                'tenant_phone': lease.tenant.phone,
                'unit': f"{lease.unit.building.name} - {lease.unit.unit_number}",
                'start_date': lease.start_date,
                'end_date': lease.end_date,
                'days_until_expiry': days_until_expiry,
                'monthly_rent': float(lease.monthly_rent),
                'total_rent': float(lease.total_rent),
            })
        
        # تجميع حسب الشهر
        by_month = {}
        for lease in leases_data:
            month_key = lease['end_date'].strftime('%Y-%m')
            if month_key not in by_month:
                by_month[month_key] = {
                    'month': lease['end_date'].replace(day=1),
                    'count': 0,
                    'leases': []
                }
            by_month[month_key]['count'] += 1
            by_month[month_key]['leases'].append(lease)
        
        return {
            'period': {
                'start': today,
                'end': end_date,
                'months_ahead': months_ahead,
            },
            'summary': {
                'total_expiring': len(leases_data),
            },
            'leases': leases_data,
            'by_month': list(by_month.values()),
        }
    
    @staticmethod
    def get_dashboard_analytics():
        """
        تحليلات لوحة التحكم
        يوفر البيانات الأساسية للوحة التحكم
        """
        from .models import Lease, Payment, Expense, Unit, Tenant
        
        today = timezone.now().date()
        current_month_start = today.replace(day=1)
        last_month_start = (current_month_start - relativedelta(months=1))
        last_month_end = current_month_start - timedelta(days=1)
        
        # KPIs الأساسية
        total_units = Unit.objects.count()
        occupied_units = Unit.objects.filter(is_available=False).count()
        occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
        
        active_leases = Lease.objects.filter(status='active').count()
        total_tenants = Tenant.objects.count()
        
        # الإيرادات هذا الشهر
        current_month_revenue = Payment.objects.filter(
            payment_date__gte=current_month_start,
            payment_date__lte=today
        ).aggregate(total=Coalesce(Sum('amount'), Decimal('0')))['total']
        
        # الإيرادات الشهر الماضي
        last_month_revenue = Payment.objects.filter(
            payment_date__gte=last_month_start,
            payment_date__lte=last_month_end
        ).aggregate(total=Coalesce(Sum('amount'), Decimal('0')))['total']
        
        # نسبة التغيير
        revenue_change = 0
        if last_month_revenue > 0:
            revenue_change = ((current_month_revenue - last_month_revenue) / last_month_revenue * 100)
        
        # المصروفات هذا الشهر
        current_month_expenses = Expense.objects.filter(
            expense_date__gte=current_month_start,
            expense_date__lte=today
        ).aggregate(total=Coalesce(Sum('amount'), Decimal('0')))['total']
        
        # المدفوعات المتأخرة
        overdue_report = ReportService.get_overdue_tenants_report(today, 1)
        
        # العقود المنتهية قريباً (خلال 90 يوم)
        expiring_soon = Lease.objects.filter(
            status='active',
            end_date__gte=today,
            end_date__lte=today + timedelta(days=90)
        ).count()
        
        return {
            'kpis': {
                'total_units': total_units,
                'occupied_units': occupied_units,
                'vacant_units': total_units - occupied_units,
                'occupancy_rate': float(occupancy_rate),
                'active_leases': active_leases,
                'total_tenants': total_tenants,
                'expiring_soon': expiring_soon,
            },
            'financial': {
                'current_month_revenue': float(current_month_revenue),
                'last_month_revenue': float(last_month_revenue),
                'revenue_change_percent': float(revenue_change),
                'current_month_expenses': float(current_month_expenses),
                'net_income': float(current_month_revenue - current_month_expenses),
            },
            'overdue': {
                'total_tenants': overdue_report['summary']['total_overdue_tenants'],
                'total_amount': overdue_report['summary']['total_overdue_amount'],
            }
        }

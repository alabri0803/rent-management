#!/usr/bin/env python
"""فحص الحالة المالية للعقد 21053/2024"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rent_management.settings')
django.setup()

from dashboard.models import Lease, SecurityDeposit
from decimal import Decimal

# جلب العقد
lease = Lease.objects.get(contract_number='21053/2024')

print(f'العقد: {lease.contract_number}')
print(f'الحالة: {lease.status}')
print(f'تاريخ البدء: {lease.start_date}')
print(f'تاريخ الانتهاء: {lease.end_date}')
print(f'الإيجار الشهري: {lease.monthly_rent} ر.ع')

# التأمين
print(f'\n{"="*50}')
print(f'التأمين:')
print(f'{"="*50}')
deposits = lease.security_deposits.all()
total_deposit = Decimal('0')
refunded_deposit = Decimal('0')

if deposits.exists():
    for d in deposits:
        print(f'  - {d.amount} ر.ع | الحالة: {d.get_status_display()} | التاريخ: {d.received_date}')
        if d.status == 'refunded':
            refunded_deposit += d.amount
        else:
            total_deposit += d.amount
    print(f'\nإجمالي التأمين المحتفظ به: {total_deposit} ر.ع')
    print(f'إجمالي التأمين المسترد: {refunded_deposit} ر.ع')
else:
    print('  لا يوجد تأمين مسجل')
    total_deposit = Decimal('0')

# كشف الحساب
print(f'\n{"="*50}')
print(f'كشف حساب الإيجار:')
print(f'{"="*50}')
summary = lease.get_payment_summary()
total_paid = sum(Decimal(str(m['amount_paid'])) for m in summary)
total_balance = sum(Decimal(str(m['balance'])) for m in summary)
total_rent = sum(Decimal(str(m['rent_due'])) for m in summary)

print(f'إجمالي الإيجار المستحق: {total_rent} ر.ع')
print(f'إجمالي المدفوع: {total_paid} ر.ع')
print(f'إجمالي المتبقي: {total_balance} ر.ع')

# الشهور المتأخرة
overdue = [m for m in summary if m['status'] == 'overdue']
print(f'\nعدد الشهور المتأخرة: {len(overdue)}')
if overdue:
    overdue_amount = sum(Decimal(str(m["balance"])) for m in overdue)
    print(f'مبلغ المتأخرات: {overdue_amount} ر.ع')
    print(f'\nتفاصيل الشهور المتأخرة:')
    for m in overdue[:5]:  # أول 5 فقط
        print(f'  - {m["month_name"]}: {m["balance"]} ر.ع (متأخر {m["days_overdue"]} يوم)')

# رسوم الخدمات (افتراضياً 0 إذا لم تكن موجودة)
print(f'\n{"="*50}')
print(f'رسوم الخدمات:')
print(f'{"="*50}')
registration_fees = getattr(lease, 'registration_fees', Decimal('0'))
services_fees = getattr(lease, 'services_fees', Decimal('0'))
print(f'رسوم التسجيل: {registration_fees} ر.ع')
print(f'رسوم الخدمات: {services_fees} ر.ع')

# الملخص النهائي للإلغاء
print(f'\n{"="*50}')
print(f'ملخص الالتزامات المالية عند الإلغاء:')
print(f'{"="*50}')
print(f'1. الإيجار المستحق حتى تاريخ الإلغاء: {total_balance} ر.ع')
print(f'2. رسوم الخدمات المستحقة: 0.00 ر.ع')  # افتراضياً
print(f'3. التأمين القابل للاسترداد: {total_deposit} ر.ع')
print(f'\nصافي المبلغ:')
if total_balance > total_deposit:
    net = total_balance - total_deposit
    print(f'   مستحق من المستأجر: {net} ر.ع')
else:
    net = total_deposit - total_balance
    print(f'   قابل للاسترداد للمستأجر: {net} ر.ع')

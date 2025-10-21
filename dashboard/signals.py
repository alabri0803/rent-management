from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import models
from .models import Tenant, MaintenanceRequest, Lease, Notification, Building, Expense, Payment, PaymentOverdueNotice, PaymentOverdueDetail
from .utils import auto_translate_to_english
from decimal import Decimal

@receiver(post_save, sender=Tenant)
def create_tenant_user_account(sender, instance, created, **kwargs):
    if created and not instance.user:
        if instance.email:
            username = instance.email.split('@')[0]
        else:
            username = f"user_{instance.phone}"
        if User.objects.filter(username=username).exists():
            username = f"{username}_{instance.id}"
        user = User.objects.create_user(username=username, email=instance.email, password=instance.phone)
        user.first_name = instance.name
        user.save()
        instance.user = user
        instance.save()

@receiver(post_save, sender=MaintenanceRequest)
def maintenance_request_notification(sender, instance, created, **kwargs):
    if created:
        message = _("'تم تقديم طلب صيانة جديد بعنوان {} من قبل المستأجر {}'").format(instance.title, instance.lease.tenant.name)
        staff_users = User.objects.filter(is_staff=True)
        for user in staff_users:
            Notification.objects.create(user=user, message=message, related_object=instance)
    else:
        try:
            old_instance = MaintenanceRequest.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                message = _("'تم تحديث حالة طلب الصيانة {} إلى {}'").format(instance.title, instance.get_status_display())
                if instance.lease.tenant.user:
                    Notification.objects.create(user=instance.lease.tenant.user, message=message, related_object=instance)
        except MaintenanceRequest.DoesNotExist:
            pass

@receiver(post_save, sender=Lease)
def lease_status_notification(sender, instance, **kwargs):
    if instance.status == 'expiring_soon' and instance.tenant.user:
        message = _("'عقد الإيجار الخاص بك رقم {} سينتهي قريب في تاريخ {}'").format(instance.contract_number, instance.end_date.strftime('%Y-%m-%d'))
        if not Notification.objects.filter(user=instance.tenant.user, message=message).exists():
            Notification.objects.create(user=instance.tenant.user, message=message, related_object=instance)


@receiver(pre_save, sender=Building)
def auto_translate_building(sender, instance, **kwargs):
    if instance.name_ar and not instance.name_en:
        instance.name_en = auto_translate_to_english(instance.name_ar)
    if instance.address_ar and not instance.address_en:
        instance.address_en = auto_translate_to_english(instance.address_ar)


@receiver(pre_save, sender=Tenant)
def auto_translate_tenant(sender, instance, **kwargs):
    if instance.name and not hasattr(instance, 'name_en'):
        instance.name_en = auto_translate_to_english(instance.name)
    elif hasattr(instance, 'name_ar') and instance.name_ar and not instance.name_en:
        instance.name_en = auto_translate_to_english(instance.name_ar)
    
    if hasattr(instance, 'authorized_signatory_ar') and instance.authorized_signatory_ar and not instance.authorized_signatory_en:
        instance.authorized_signatory_en = auto_translate_to_english(instance.authorized_signatory_ar)


@receiver(pre_save, sender=Expense)
def auto_translate_expense(sender, instance, **kwargs):
    if instance.description_ar and not instance.description_en:
        instance.description_en = auto_translate_to_english(instance.description_ar)


@receiver(post_save, sender=Payment)
def update_overdue_notices_on_payment(sender, instance, created, **kwargs):
    """تحديث الإنذارات تلقائياً عند دفع مبلغ لشهر متأخر"""
    if created:
        # البحث عن الإنذارات المرتبطة بهذا العقد والشهر
        overdue_details = PaymentOverdueDetail.objects.filter(
            notice__lease=instance.lease,
            overdue_month=instance.payment_for_month,
            overdue_year=instance.payment_for_year,
            notice__status__in=['draft', 'sent', 'acknowledged']  # الإنذارات غير المحلولة
        )
        
        for detail in overdue_details:
            notice = detail.notice
            
            # حساب المبلغ المدفوع لهذا الشهر
            total_paid_for_month = Payment.objects.filter(
                lease=instance.lease,
                payment_for_month=instance.payment_for_month,
                payment_for_year=instance.payment_for_year
            ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
            
            # حساب المبلغ المتبقي
            monthly_rent = instance.lease.monthly_rent
            remaining_amount = monthly_rent - total_paid_for_month
            
            if remaining_amount <= 0:
                # تم دفع المبلغ كاملاً - حذف هذا التفصيل من الإنذار
                detail.delete()
                
                # إضافة ملاحظة للإنذار
                current_notes = notice.notes or ""
                new_note = f"\n✅ تم دفع مبلغ {monthly_rent} ر.ع كاملاً لشهر {instance.payment_for_month}/{instance.payment_for_year} بتاريخ {instance.payment_date.strftime('%d/%m/%Y')}"
                notice.notes = current_notes + new_note
                
                # فحص إذا لم تعد هناك تفاصيل متأخرة - تحديث حالة الإنذار إلى محلول
                if not notice.details.exists():
                    notice.status = 'resolved'
                    notice.resolved_date = instance.payment_date
                    final_note = f"\n🎉 تم حل الإنذار بالكامل - دفع جميع المبالغ المتأخرة بتاريخ {instance.payment_date.strftime('%d/%m/%Y')}"
                    notice.notes = notice.notes + final_note
                    # مسح محتوى الإنذار لأنه تم حله
                    notice.content = f"""
                    <div style="text-align: center; font-family: Arial, sans-serif; direction: rtl; color: #4caf50;">
                        <h2>✅ تم حل الإنذار بالكامل</h2>
                        <p>تم دفع جميع المبالغ المستحقة بتاريخ {instance.payment_date.strftime('%d/%m/%Y')}</p>
                        <p>شكراً لكم على التزامكم بالسداد</p>
                    </div>
                    """
                else:
                    # تحديث محتوى الإنذار ليعكس المبالغ المتبقية
                    notice.content = notice.generate_formal_payment_request()
                
                notice.save()
                
            else:
                # تم دفع جزء من المبلغ - تحديث المبلغ المتأخر
                detail.overdue_amount = remaining_amount
                detail.save()
                
                # إضافة ملاحظة للدفع الجزئي
                current_notes = notice.notes or ""
                new_note = f"\n💰 دفع جزئي لشهر {instance.payment_for_month}/{instance.payment_for_year}: دفع {instance.amount} ر.ع، المتبقي {remaining_amount} ر.ع بتاريخ {instance.payment_date.strftime('%d/%m/%Y')}"
                notice.notes = current_notes + new_note
                
                # تحديث محتوى الإنذار الرسمي ليعكس المبالغ الجديدة
                notice.content = notice.generate_formal_payment_request()
                notice.save()
                
                # إنشاء إشعار للمستأجر
                if instance.lease.tenant.user:
                    message = f"تم استلام دفعة جزئية بمبلغ {instance.amount} ر.ع لشهر {instance.payment_for_month}/{instance.payment_for_year}. المبلغ المتبقي: {remaining_amount} ر.ع"
                    Notification.objects.create(
                        user=instance.lease.tenant.user,
                        message=message,
                        related_object=notice
                    )
            
            # إنشاء إشعار للموظفين
            staff_users = User.objects.filter(is_staff=True)
            for user in staff_users:
                if remaining_amount <= 0:
                    message = f"✅ تم دفع مبلغ {monthly_rent} ر.ع كاملاً لشهر {instance.payment_for_month}/{instance.payment_for_year} من العقد {instance.lease.contract_number}"
                else:
                    message = f"💰 دفعة جزئية: {instance.amount} ر.ع لشهر {instance.payment_for_month}/{instance.payment_for_year} من العقد {instance.lease.contract_number}. المتبقي: {remaining_amount} ر.ع"
                
                Notification.objects.create(
                    user=user,
                    message=message,
                    related_object=notice
                )
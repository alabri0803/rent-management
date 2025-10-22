"""
نظام الإشعارات المتقدم
يدعم: Email, SMS, WhatsApp, Push Notifications
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import json
import logging

logger = logging.getLogger('dashboard.notifications')


# ==================== Notification Models ====================

class NotificationChannel(models.TextChoices):
    """قنوات الإشعارات المتاحة"""
    IN_APP = 'in_app', _('داخل التطبيق')
    EMAIL = 'email', _('البريد الإلكتروني')
    SMS = 'sms', _('رسالة نصية')
    WHATSAPP = 'whatsapp', _('واتساب')
    PUSH = 'push', _('إشعار فوري')


class NotificationPriority(models.TextChoices):
    """أولوية الإشعار"""
    LOW = 'low', _('منخفضة')
    NORMAL = 'normal', _('عادية')
    HIGH = 'high', _('عالية')
    URGENT = 'urgent', _('عاجلة')


class NotificationCategory(models.TextChoices):
    """تصنيفات الإشعارات"""
    PAYMENT = 'payment', _('دفعة')
    LEASE = 'lease', _('عقد')
    MAINTENANCE = 'maintenance', _('صيانة')
    OVERDUE = 'overdue', _('تأخير سداد')
    REMINDER = 'reminder', _('تذكير')
    SYSTEM = 'system', _('نظام')
    SECURITY = 'security', _('أمان')
    GENERAL = 'general', _('عام')


class NotificationTemplate(models.Model):
    """قوالب الإشعارات"""
    name = models.CharField(_("اسم القالب"), max_length=100, unique=True)
    category = models.CharField(
        _("التصنيف"),
        max_length=20,
        choices=NotificationCategory.choices,
        default=NotificationCategory.GENERAL
    )
    
    # محتوى القالب
    subject = models.CharField(_("الموضوع"), max_length=200)
    body_text = models.TextField(_("المحتوى النصي"))
    body_html = models.TextField(_("المحتوى HTML"), blank=True, null=True)
    
    # إعدادات القالب
    channels = models.JSONField(
        _("القنوات المفعلة"),
        default=list,
        help_text=_("قائمة القنوات: in_app, email, sms, whatsapp, push")
    )
    variables = models.JSONField(
        _("المتغيرات"),
        default=dict,
        help_text=_("المتغيرات المتاحة في القالب")
    )
    
    # حالة القالب
    is_active = models.BooleanField(_("مفعل"), default=True)
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("قالب إشعار")
        verbose_name_plural = _("قوالب الإشعارات")
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def render(self, context):
        """تطبيق المتغيرات على القالب"""
        subject = self.subject
        body_text = self.body_text
        body_html = self.body_html
        
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            subject = subject.replace(placeholder, str(value))
            body_text = body_text.replace(placeholder, str(value))
            if body_html:
                body_html = body_html.replace(placeholder, str(value))
        
        return {
            'subject': subject,
            'body_text': body_text,
            'body_html': body_html
        }


class NotificationPreference(models.Model):
    """تفضيلات الإشعارات للمستخدمين"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name=_("المستخدم")
    )
    
    # القنوات المفعلة
    enable_in_app = models.BooleanField(_("تفعيل الإشعارات الداخلية"), default=True)
    enable_email = models.BooleanField(_("تفعيل البريد الإلكتروني"), default=True)
    enable_sms = models.BooleanField(_("تفعيل الرسائل النصية"), default=False)
    enable_whatsapp = models.BooleanField(_("تفعيل واتساب"), default=False)
    enable_push = models.BooleanField(_("تفعيل الإشعارات الفورية"), default=True)
    
    # التصنيفات المفعلة
    categories = models.JSONField(
        _("التصنيفات المفعلة"),
        default=dict,
        help_text=_("تفعيل/تعطيل كل تصنيف لكل قناة")
    )
    
    # أوقات الإرسال
    quiet_hours_start = models.TimeField(_("بداية وقت الهدوء"), null=True, blank=True)
    quiet_hours_end = models.TimeField(_("نهاية وقت الهدوء"), null=True, blank=True)
    
    # معلومات الاتصال
    phone_number = models.CharField(_("رقم الهاتف"), max_length=20, blank=True, null=True)
    whatsapp_number = models.CharField(_("رقم واتساب"), max_length=20, blank=True, null=True)
    
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    
    class Meta:
        verbose_name = _("تفضيلات الإشعارات")
        verbose_name_plural = _("تفضيلات الإشعارات")
    
    def __str__(self):
        return f"تفضيلات {self.user.get_full_name() or self.user.username}"
    
    def is_channel_enabled(self, channel, category=None):
        """التحقق من تفعيل قناة معينة"""
        channel_map = {
            'in_app': self.enable_in_app,
            'email': self.enable_email,
            'sms': self.enable_sms,
            'whatsapp': self.enable_whatsapp,
            'push': self.enable_push,
        }
        
        if not channel_map.get(channel, False):
            return False
        
        # التحقق من التصنيف إذا تم تحديده
        if category and self.categories:
            return self.categories.get(category, {}).get(channel, True)
        
        return True
    
    def is_quiet_time(self):
        """التحقق من وقت الهدوء"""
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        now = timezone.now().time()
        return self.quiet_hours_start <= now <= self.quiet_hours_end


class EnhancedNotification(models.Model):
    """نموذج الإشعارات المحسّن"""
    
    # المستخدم والمحتوى
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enhanced_notifications',
        verbose_name=_("المستخدم")
    )
    
    # تفاصيل الإشعار
    title = models.CharField(_("العنوان"), max_length=200)
    message = models.TextField(_("الرسالة"))
    category = models.CharField(
        _("التصنيف"),
        max_length=20,
        choices=NotificationCategory.choices,
        default=NotificationCategory.GENERAL
    )
    priority = models.CharField(
        _("الأولوية"),
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL
    )
    
    # القنوات المستخدمة
    channels = models.JSONField(
        _("القنوات"),
        default=list,
        help_text=_("القنوات التي تم إرسال الإشعار عبرها")
    )
    
    # الكائن المرتبط
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # البيانات الإضافية
    data = models.JSONField(
        _("بيانات إضافية"),
        default=dict,
        blank=True
    )
    
    # رابط الإجراء
    action_url = models.CharField(_("رابط الإجراء"), max_length=500, blank=True, null=True)
    action_text = models.CharField(_("نص الإجراء"), max_length=100, blank=True, null=True)
    
    # حالة الإشعار
    is_read = models.BooleanField(_("مقروء"), default=False)
    read_at = models.DateTimeField(_("وقت القراءة"), null=True, blank=True)
    
    # حالة الإرسال
    sent_via_email = models.BooleanField(_("تم الإرسال عبر البريد"), default=False)
    sent_via_sms = models.BooleanField(_("تم الإرسال عبر SMS"), default=False)
    sent_via_whatsapp = models.BooleanField(_("تم الإرسال عبر واتساب"), default=False)
    sent_via_push = models.BooleanField(_("تم الإرسال عبر Push"), default=False)
    
    # سجل الإرسال
    delivery_log = models.JSONField(
        _("سجل التسليم"),
        default=dict,
        blank=True
    )
    
    # التواريخ
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    scheduled_at = models.DateTimeField(_("موعد الإرسال"), null=True, blank=True)
    expires_at = models.DateTimeField(_("تاريخ الانتهاء"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("إشعار محسّن")
        verbose_name_plural = _("الإشعارات المحسّنة")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['category', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name() or self.user.username}"
    
    def mark_as_read(self):
        """تحديد الإشعار كمقروء"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
            logger.info(f"Notification {self.id} marked as read by {self.user.username}")
    
    def is_expired(self):
        """التحقق من انتهاء صلاحية الإشعار"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def get_priority_color(self):
        """الحصول على لون الأولوية"""
        colors = {
            'low': 'gray',
            'normal': 'blue',
            'high': 'orange',
            'urgent': 'red'
        }
        return colors.get(self.priority, 'blue')
    
    def get_category_icon(self):
        """الحصول على أيقونة التصنيف"""
        icons = {
            'payment': '💰',
            'lease': '📝',
            'maintenance': '🔧',
            'overdue': '⚠️',
            'reminder': '🔔',
            'system': '⚙️',
            'security': '🔒',
            'general': 'ℹ️'
        }
        return icons.get(self.category, 'ℹ️')


class NotificationLog(models.Model):
    """سجل إرسال الإشعارات"""
    
    notification = models.ForeignKey(
        EnhancedNotification,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name=_("الإشعار")
    )
    
    channel = models.CharField(
        _("القناة"),
        max_length=20,
        choices=NotificationChannel.choices
    )
    
    status = models.CharField(
        _("الحالة"),
        max_length=20,
        choices=[
            ('pending', _('قيد الانتظار')),
            ('sent', _('تم الإرسال')),
            ('delivered', _('تم التسليم')),
            ('failed', _('فشل')),
            ('bounced', _('مرتد')),
        ],
        default='pending'
    )
    
    recipient = models.CharField(_("المستلم"), max_length=200)
    
    # تفاصيل الإرسال
    provider = models.CharField(_("مزود الخدمة"), max_length=50, blank=True, null=True)
    provider_id = models.CharField(_("معرف المزود"), max_length=200, blank=True, null=True)
    
    # الاستجابة
    response_data = models.JSONField(_("بيانات الاستجابة"), default=dict, blank=True)
    error_message = models.TextField(_("رسالة الخطأ"), blank=True, null=True)
    
    # التكلفة
    cost = models.DecimalField(_("التكلفة"), max_digits=10, decimal_places=4, null=True, blank=True)
    
    # التواريخ
    sent_at = models.DateTimeField(_("وقت الإرسال"), auto_now_add=True)
    delivered_at = models.DateTimeField(_("وقت التسليم"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("سجل إشعار")
        verbose_name_plural = _("سجلات الإشعارات")
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.get_channel_display()} - {self.recipient} - {self.get_status_display()}"


# ==================== Notification Service ====================

class NotificationService:
    """خدمة إرسال الإشعارات"""
    
    @staticmethod
    def create_notification(
        user,
        title,
        message,
        category=NotificationCategory.GENERAL,
        priority=NotificationPriority.NORMAL,
        channels=None,
        related_object=None,
        action_url=None,
        action_text=None,
        data=None,
        scheduled_at=None,
        expires_at=None
    ):
        """إنشاء إشعار جديد"""
        
        # إنشاء الإشعار
        notification = EnhancedNotification.objects.create(
            user=user,
            title=title,
            message=message,
            category=category,
            priority=priority,
            channels=channels or ['in_app'],
            content_type=ContentType.objects.get_for_model(related_object) if related_object else None,
            object_id=related_object.pk if related_object else None,
            action_url=action_url,
            action_text=action_text,
            data=data or {},
            scheduled_at=scheduled_at,
            expires_at=expires_at
        )
        
        logger.info(f"Created notification {notification.id} for user {user.username}")
        
        # إرسال الإشعار عبر القنوات المحددة
        if not scheduled_at or scheduled_at <= timezone.now():
            NotificationService.send_notification(notification)
        
        return notification
    
    @staticmethod
    def send_notification(notification):
        """إرسال الإشعار عبر القنوات المحددة"""
        
        # الحصول على تفضيلات المستخدم
        try:
            preferences = notification.user.notification_preferences
        except NotificationPreference.DoesNotExist:
            preferences = NotificationPreference.objects.create(user=notification.user)
        
        # التحقق من وقت الهدوء
        if preferences.is_quiet_time() and notification.priority != NotificationPriority.URGENT:
            logger.info(f"Notification {notification.id} delayed due to quiet hours")
            return
        
        # إرسال عبر القنوات المفعلة
        for channel in notification.channels:
            if preferences.is_channel_enabled(channel, notification.category):
                try:
                    if channel == 'email':
                        NotificationService._send_email(notification, preferences)
                    elif channel == 'sms':
                        NotificationService._send_sms(notification, preferences)
                    elif channel == 'whatsapp':
                        NotificationService._send_whatsapp(notification, preferences)
                    elif channel == 'push':
                        NotificationService._send_push(notification, preferences)
                except Exception as e:
                    logger.error(f"Failed to send notification {notification.id} via {channel}: {str(e)}")
    
    @staticmethod
    def _send_email(notification, preferences):
        """إرسال عبر البريد الإلكتروني"""
        try:
            subject = notification.title
            message = notification.message
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [notification.user.email]
            
            # إرسال البريد
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False
            )
            
            notification.sent_via_email = True
            notification.save(update_fields=['sent_via_email'])
            
            # تسجيل الإرسال
            NotificationLog.objects.create(
                notification=notification,
                channel='email',
                status='sent',
                recipient=notification.user.email
            )
            
            logger.info(f"Email sent for notification {notification.id}")
            
        except Exception as e:
            logger.error(f"Failed to send email for notification {notification.id}: {str(e)}")
            NotificationLog.objects.create(
                notification=notification,
                channel='email',
                status='failed',
                recipient=notification.user.email,
                error_message=str(e)
            )
    
    @staticmethod
    def _send_sms(notification, preferences):
        """إرسال عبر SMS"""
        try:
            from dashboard.notification_providers import NotificationProviderFactory
            
            if not preferences.phone_number:
                logger.warning(f"No phone number for user {notification.user.username}")
                return
            
            provider = NotificationProviderFactory.get_sms_provider()
            result = provider.send_sms(
                to_number=preferences.phone_number,
                message=f"{notification.title}\n\n{notification.message}"
            )
            
            if result['status'] == 'sent':
                notification.sent_via_sms = True
                notification.save(update_fields=['sent_via_sms'])
                
                NotificationLog.objects.create(
                    notification=notification,
                    channel='sms',
                    status='sent',
                    recipient=preferences.phone_number,
                    provider=result.get('provider'),
                    provider_id=result.get('provider_id'),
                    cost=result.get('cost')
                )
                
                logger.info(f"SMS sent for notification {notification.id}")
            else:
                NotificationLog.objects.create(
                    notification=notification,
                    channel='sms',
                    status='failed',
                    recipient=preferences.phone_number,
                    error_message=result.get('error')
                )
                logger.error(f"SMS failed for notification {notification.id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Failed to send SMS for notification {notification.id}: {str(e)}")
    
    @staticmethod
    def _send_whatsapp(notification, preferences):
        """إرسال عبر WhatsApp"""
        try:
            from dashboard.notification_providers import NotificationProviderFactory
            
            if not preferences.whatsapp_number:
                logger.warning(f"No WhatsApp number for user {notification.user.username}")
                return
            
            provider = NotificationProviderFactory.get_whatsapp_provider()
            result = provider.send_message(
                to_number=preferences.whatsapp_number,
                message=f"*{notification.title}*\n\n{notification.message}"
            )
            
            if result['status'] == 'sent':
                notification.sent_via_whatsapp = True
                notification.save(update_fields=['sent_via_whatsapp'])
                
                NotificationLog.objects.create(
                    notification=notification,
                    channel='whatsapp',
                    status='sent',
                    recipient=preferences.whatsapp_number,
                    provider=result.get('provider'),
                    provider_id=result.get('provider_id'),
                    cost=result.get('cost')
                )
                
                logger.info(f"WhatsApp sent for notification {notification.id}")
            else:
                NotificationLog.objects.create(
                    notification=notification,
                    channel='whatsapp',
                    status='failed',
                    recipient=preferences.whatsapp_number,
                    error_message=result.get('error')
                )
                logger.error(f"WhatsApp failed for notification {notification.id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Failed to send WhatsApp for notification {notification.id}: {str(e)}")
    
    @staticmethod
    def _send_push(notification, preferences):
        """إرسال إشعار فوري"""
        try:
            from dashboard.notification_providers import NotificationProviderFactory
            
            # الحصول على device token من بيانات المستخدم
            device_token = notification.user.profile.device_token if hasattr(notification.user, 'profile') else None
            
            if not device_token:
                logger.warning(f"No device token for user {notification.user.username}")
                return
            
            provider = NotificationProviderFactory.get_push_provider()
            result = provider.send_push(
                device_token=device_token,
                title=notification.title,
                body=notification.message,
                data=notification.data
            )
            
            if result['status'] == 'sent':
                notification.sent_via_push = True
                notification.save(update_fields=['sent_via_push'])
                
                NotificationLog.objects.create(
                    notification=notification,
                    channel='push',
                    status='sent',
                    recipient=device_token[:20] + '...',
                    provider=result.get('provider'),
                    provider_id=result.get('provider_id')
                )
                
                logger.info(f"Push notification sent for {notification.id}")
            else:
                NotificationLog.objects.create(
                    notification=notification,
                    channel='push',
                    status='failed',
                    recipient=device_token[:20] + '...' if device_token else 'N/A',
                    error_message=result.get('error')
                )
                logger.error(f"Push failed for notification {notification.id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Failed to send push for notification {notification.id}: {str(e)}")

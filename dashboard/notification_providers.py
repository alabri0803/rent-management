"""
مزودي خدمات الإشعارات الخارجية
Twilio SMS, WhatsApp, AWS SNS, Firebase Push
"""

from django.conf import settings
import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger('dashboard.notifications')


# ==================== Twilio SMS Provider ====================

class TwilioSMSProvider:
    """مزود خدمة Twilio للرسائل النصية"""
    
    def __init__(self):
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
        self.enabled = all([self.account_sid, self.auth_token, self.from_number])
    
    def send_sms(self, to_number: str, message: str) -> Dict:
        """إرسال رسالة نصية"""
        if not self.enabled:
            logger.warning("Twilio SMS is not configured")
            return {'status': 'failed', 'error': 'Twilio not configured'}
        
        try:
            from twilio.rest import Client
            
            client = Client(self.account_sid, self.auth_token)
            
            sms = client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"SMS sent via Twilio: {sms.sid}")
            
            return {
                'status': 'sent',
                'provider': 'twilio',
                'provider_id': sms.sid,
                'cost': float(sms.price) if sms.price else 0
            }
            
        except Exception as e:
            logger.error(f"Twilio SMS error: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }


# ==================== Twilio WhatsApp Provider ====================

class TwilioWhatsAppProvider:
    """مزود خدمة Twilio لواتساب"""
    
    def __init__(self):
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.from_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)
        self.enabled = all([self.account_sid, self.auth_token, self.from_number])
    
    def send_message(self, to_number: str, message: str) -> Dict:
        """إرسال رسالة واتساب"""
        if not self.enabled:
            logger.warning("Twilio WhatsApp is not configured")
            return {'status': 'failed', 'error': 'WhatsApp not configured'}
        
        try:
            from twilio.rest import Client
            
            client = Client(self.account_sid, self.auth_token)
            
            # تنسيق رقم واتساب
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            if not self.from_number.startswith('whatsapp:'):
                from_number = f'whatsapp:{self.from_number}'
            else:
                from_number = self.from_number
            
            msg = client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            
            logger.info(f"WhatsApp message sent via Twilio: {msg.sid}")
            
            return {
                'status': 'sent',
                'provider': 'twilio_whatsapp',
                'provider_id': msg.sid,
                'cost': float(msg.price) if msg.price else 0
            }
            
        except Exception as e:
            logger.error(f"Twilio WhatsApp error: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }


# ==================== AWS SNS Provider ====================

class AWSSNSProvider:
    """مزود خدمة AWS SNS للرسائل النصية"""
    
    def __init__(self):
        self.access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        self.secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        self.region = getattr(settings, 'AWS_SNS_REGION', 'us-east-1')
        self.enabled = all([self.access_key, self.secret_key])
    
    def send_sms(self, to_number: str, message: str) -> Dict:
        """إرسال رسالة نصية عبر AWS SNS"""
        if not self.enabled:
            logger.warning("AWS SNS is not configured")
            return {'status': 'failed', 'error': 'AWS SNS not configured'}
        
        try:
            import boto3
            
            sns_client = boto3.client(
                'sns',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
            
            response = sns_client.publish(
                PhoneNumber=to_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': 'RentMgmt'
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            
            logger.info(f"SMS sent via AWS SNS: {response['MessageId']}")
            
            return {
                'status': 'sent',
                'provider': 'aws_sns',
                'provider_id': response['MessageId']
            }
            
        except Exception as e:
            logger.error(f"AWS SNS error: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }


# ==================== Firebase Push Notification Provider ====================

class FirebasePushProvider:
    """مزود خدمة Firebase للإشعارات الفورية"""
    
    def __init__(self):
        self.server_key = getattr(settings, 'FIREBASE_SERVER_KEY', None)
        self.enabled = bool(self.server_key)
        self.fcm_url = 'https://fcm.googleapis.com/fcm/send'
    
    def send_push(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """إرسال إشعار فوري"""
        if not self.enabled:
            logger.warning("Firebase Push is not configured")
            return {'status': 'failed', 'error': 'Firebase not configured'}
        
        try:
            headers = {
                'Authorization': f'key={self.server_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'to': device_token,
                'notification': {
                    'title': title,
                    'body': body,
                    'sound': 'default',
                    'badge': '1'
                },
                'data': data or {},
                'priority': 'high'
            }
            
            response = requests.post(
                self.fcm_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('success', 0) > 0:
                logger.info(f"Push notification sent via Firebase")
                return {
                    'status': 'sent',
                    'provider': 'firebase',
                    'provider_id': result.get('multicast_id')
                }
            else:
                error = result.get('results', [{}])[0].get('error', 'Unknown error')
                logger.error(f"Firebase push error: {error}")
                return {
                    'status': 'failed',
                    'error': error
                }
            
        except Exception as e:
            logger.error(f"Firebase push error: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }


# ==================== WhatsApp Business API Provider ====================

class WhatsAppBusinessProvider:
    """مزود خدمة WhatsApp Business API"""
    
    def __init__(self):
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', None)
        self.api_token = getattr(settings, 'WHATSAPP_API_TOKEN', None)
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', None)
        self.enabled = all([self.api_url, self.api_token, self.phone_number_id])
    
    def send_message(self, to_number: str, message: str) -> Dict:
        """إرسال رسالة واتساب عبر Business API"""
        if not self.enabled:
            logger.warning("WhatsApp Business API is not configured")
            return {'status': 'failed', 'error': 'WhatsApp Business not configured'}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_number,
                'type': 'text',
                'text': {
                    'body': message
                }
            }
            
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"WhatsApp message sent via Business API")
            
            return {
                'status': 'sent',
                'provider': 'whatsapp_business',
                'provider_id': result.get('messages', [{}])[0].get('id')
            }
            
        except Exception as e:
            logger.error(f"WhatsApp Business API error: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def send_template(
        self,
        to_number: str,
        template_name: str,
        language_code: str = 'ar',
        parameters: Optional[list] = None
    ) -> Dict:
        """إرسال قالب واتساب"""
        if not self.enabled:
            return {'status': 'failed', 'error': 'WhatsApp Business not configured'}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_number,
                'type': 'template',
                'template': {
                    'name': template_name,
                    'language': {
                        'code': language_code
                    }
                }
            }
            
            if parameters:
                payload['template']['components'] = [
                    {
                        'type': 'body',
                        'parameters': [
                            {'type': 'text', 'text': param}
                            for param in parameters
                        ]
                    }
                ]
            
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"WhatsApp template sent via Business API")
            
            return {
                'status': 'sent',
                'provider': 'whatsapp_business',
                'provider_id': result.get('messages', [{}])[0].get('id')
            }
            
        except Exception as e:
            logger.error(f"WhatsApp Business API template error: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }


# ==================== Notification Provider Factory ====================

class NotificationProviderFactory:
    """مصنع مزودي الإشعارات"""
    
    @staticmethod
    def get_sms_provider():
        """الحصول على مزود SMS المفضل"""
        provider_type = getattr(settings, 'SMS_PROVIDER', 'twilio')
        
        if provider_type == 'twilio':
            return TwilioSMSProvider()
        elif provider_type == 'aws_sns':
            return AWSSNSProvider()
        else:
            logger.warning(f"Unknown SMS provider: {provider_type}")
            return TwilioSMSProvider()  # Default
    
    @staticmethod
    def get_whatsapp_provider():
        """الحصول على مزود WhatsApp المفضل"""
        provider_type = getattr(settings, 'WHATSAPP_PROVIDER', 'twilio')
        
        if provider_type == 'twilio':
            return TwilioWhatsAppProvider()
        elif provider_type == 'business_api':
            return WhatsAppBusinessProvider()
        else:
            logger.warning(f"Unknown WhatsApp provider: {provider_type}")
            return TwilioWhatsAppProvider()  # Default
    
    @staticmethod
    def get_push_provider():
        """الحصول على مزود Push Notifications"""
        return FirebasePushProvider()

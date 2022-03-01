import logging
from typing import List

from django.conf import settings

from common.notification_service import SMSNotificationService

sms_notification_service = SMSNotificationService(
    settings.NOTIFICATION_SERVICE_API_TOKEN, settings.NOTIFICATION_SERVICE_API_URL
)

logger = logging.getLogger(__name__)


def send_sms_notification(destinations: List[str], body_text: str, language=None):
    if not language:
        language = settings.LANGUAGES[0][0]

    if language in getattr(settings, "TRANSLATED_SMS_SENDER", {}):
        sender = settings.TRANSLATED_SMS_SENDER[language]
    else:
        sender = settings.DEFAULT_SMS_SENDER

    resp = sms_notification_service.send_sms(
        sender=sender, destinations=destinations, text=body_text
    )

    if resp.status_code != 200:
        logger.warning("SMS message sent failed")

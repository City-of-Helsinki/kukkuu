from unittest.mock import patch

import pytest

from common.notification_service import SMSNotificationService
from kukkuu.notification_service import send_sms_notification


@patch.object(SMSNotificationService, "send_sms")
def test_send_sms_notification(mock_send_sms, settings):
    recipients = ["1234567890", "0987654321"]
    message = "text message"
    send_sms_notification(recipients, message)
    mock_send_sms.assert_called_once_with(
        sender=settings.DEFAULT_SMS_SENDER, destinations=recipients, text=message
    )


@patch.object(SMSNotificationService, "send_sms")
@pytest.mark.parametrize("language", ["fi", "sv", "en"])
def test_send_sms_notification_in_different_languages(
    mock_send_sms, language, settings
):
    settings.TRANSLATED_SMS_SENDER = {
        "fi": "Kukkuu suomeksi",
        "sv": "Kukkuu på svenska",
        "en": "Kukkuu in English",
    }
    sender = settings.TRANSLATED_SMS_SENDER[language]
    recipients = ["1234567890", "0987654321"]
    message = "text message"
    send_sms_notification(recipients, message, language)
    mock_send_sms.assert_called_once_with(
        sender=sender, destinations=recipients, text=message
    )


@patch.object(SMSNotificationService, "send_sms")
def test_send_sms_notification_in_language_not_supported(mock_send_sms, settings):
    settings.TRANSLATED_SMS_SENDER = {
        "fi": "Kukkuu suomeksi",
        "sv": "Kukkuu på svenska",
        "en": "Kukkuu in English",
    }
    language = "not-set"
    recipients = ["1234567890", "0987654321"]
    message = "text message"
    send_sms_notification(recipients, message, language)
    mock_send_sms.assert_called_once_with(
        sender=settings.DEFAULT_SMS_SENDER, destinations=recipients, text=message
    )

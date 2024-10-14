from typing import TYPE_CHECKING

from django.conf import settings
from django.utils import timezone
from parler.utils.context import switch_language

from django_ilmoitin.utils import Message as MailerMessage
from django_ilmoitin.utils import send_all, send_mail
from kukkuu.notification_service import send_sms_notification
from messaging.exceptions import AlreadySentError
from users.models import Guardian

if TYPE_CHECKING:
    from messaging.models import Message


def send_message(message: "Message", *, force=False):
    from messaging.models import Message

    if message.sent_at and not force:
        raise AlreadySentError()

    guardians = message.get_recipient_guardians()

    message.sent_at = timezone.now()
    message.recipient_count = len(guardians)

    message.save(update_fields=("sent_at", "recipient_count"))

    for guardian in guardians:
        with switch_language(message, guardian.language):
            if message.protocol == Message.EMAIL:
                send_email_notification(guardian, message)
            elif message.protocol == Message.SMS:
                send_sms_notification([guardian.phone_number], message.body_text)

    if not getattr(settings, "ILMOITIN_QUEUE_NOTIFICATIONS", False):
        MailerMessage.objects.retry_deferred()
        send_all()


def send_email_notification(guardian: Guardian, message: "Message"):
    # hopefully this functionality that uses django-ilmoitin's internals
    # is only temporarily here, and will be removed when either
    # 1) we need to use a notification template and thus will use
    #    ilmoitin's regular send_notification(), or
    # 2) support for sending a mail without a notification template will
    #    be added to ilmoitin and we can use that
    if guardian.language in getattr(settings, "ILMOITIN_TRANSLATED_FROM_EMAIL", {}):
        from_email = settings.ILMOITIN_TRANSLATED_FROM_EMAIL[guardian.language]
    else:
        from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        message.subject,
        message.body_text,
        guardian.email,
        from_email=from_email,
    )

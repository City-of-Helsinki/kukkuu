from django.core import mail
from django_ilmoitin.models import NotificationTemplate
from parler.utils.context import switch_language

from kukkuu.consts import PERMISSION_DENIED_ERROR


def assert_permission_denied(response):
    assert_match_error_code(response, PERMISSION_DENIED_ERROR)


def assert_mails_match_snapshot(snapshot):
    snapshot.assert_match(
        [f"{m.from_email}|{m.to}|{m.subject}|{m.body}" for m in mail.outbox]
    )


def assert_match_error_code(response, error_code):
    assert response["errors"][0].get("extensions").get("code") == error_code


def create_notification_template_in_language(
    notification_type, language, **translations
):
    try:
        template = NotificationTemplate.objects.get(type=notification_type)
    except NotificationTemplate.DoesNotExist:
        template = NotificationTemplate(type=notification_type)
    with switch_language(template, language):
        for field, value in translations.items():
            setattr(template, field, value)
            template.save()

    return template

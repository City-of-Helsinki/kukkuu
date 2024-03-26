from django.utils.translation import gettext_lazy as _
from django_ilmoitin.dummy_context import dummy_context
from django_ilmoitin.registry import notifications

from .factories import GuardianFactory


class NotificationType:
    GUARDIAN_EMAIL_CHANGED = "guardian_email_changed"
    GUARDIAN_EMAIL_CHANGE_TOKEN = "guardian_email_change_token"


notifications.register(
    NotificationType.GUARDIAN_EMAIL_CHANGED, _("guardian email changed")
)
notifications.register(
    NotificationType.GUARDIAN_EMAIL_CHANGE_TOKEN,
    _("guardian email change token requested"),
)

guardian = GuardianFactory.build()

# NOTE: Should the unsubscribe link be available in mandatory emails,
# like transactional emails?
unsubscribe_url = "https://kukkuu-ui-domain/fi/profile/subscriptions?authToken=abc123"
dummy_context.update(
    {
        NotificationType.GUARDIAN_EMAIL_CHANGED: {
            "guardian": guardian,
            "unsubscribe_url": unsubscribe_url,
        },
        NotificationType.GUARDIAN_EMAIL_CHANGE_TOKEN: {
            "guardian": guardian,
            "verification_token": "aBcDXyZ123-",
            "unsubscribe_url": unsubscribe_url,
        },
    }
)

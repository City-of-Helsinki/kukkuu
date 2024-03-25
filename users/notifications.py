from django.utils.translation import gettext_lazy as _
from django_ilmoitin.dummy_context import dummy_context
from django_ilmoitin.registry import notifications

from users.utils import get_marketing_unsubscribe_ui_url
from verification_tokens.factories import (
    UserEmailVerificationTokenFactory,
    UserSubscriptionsAuthVerificationTokenFactory,
)

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

email_verification_token = UserEmailVerificationTokenFactory.build(user=guardian.user)

# NOTE: Should the unsubscribe link be available in mandatory emails,
# like transactional emails?
auth_verification_token = UserSubscriptionsAuthVerificationTokenFactory.build(
    user=guardian.user
)

dummy_context.update(
    {
        NotificationType.GUARDIAN_EMAIL_CHANGED: {
            "guardian": guardian,
            "unsubscribe_url": get_marketing_unsubscribe_ui_url(
                guardian, guardian.language, auth_verification_token
            ),
        },
        NotificationType.GUARDIAN_EMAIL_CHANGE_TOKEN: {
            "guardian": guardian,
            "verification_token": email_verification_token.key,
            "unsubscribe_url": get_marketing_unsubscribe_ui_url(
                guardian, guardian.language, auth_verification_token
            ),
        },
    }
)

from django.utils.translation import gettext_lazy as _
from django_ilmoitin.dummy_context import dummy_context
from django_ilmoitin.registry import notifications

from .factories import GuardianFactory


class NotificationType:
    GUARDIAN_EMAIL_CHANGED = "guardian_email_changed"


notifications.register(
    NotificationType.GUARDIAN_EMAIL_CHANGED, _("guardian email changed")
)

guardian = GuardianFactory.build()

dummy_context.update({NotificationType.GUARDIAN_EMAIL_CHANGED: {"guardian": guardian}})

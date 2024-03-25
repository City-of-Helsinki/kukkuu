from django.utils.translation import gettext_lazy as _
from django_ilmoitin.dummy_context import dummy_context
from django_ilmoitin.registry import notifications

from projects.factories import ProjectFactory
from users.factories import GuardianFactory
from users.utils import get_marketing_unsubscribe_ui_url
from verification_tokens.factories import UserSubscriptionsAuthVerificationTokenFactory

from .factories import ChildWithGuardianFactory


class NotificationType:
    SIGNUP = "signup"


notifications.register(NotificationType.SIGNUP, _("signup"))


project = ProjectFactory.build(year=2020)
guardian = GuardianFactory.build()
children = ChildWithGuardianFactory.build_batch(
    3, relationship__guardian=guardian, project=project
)
# NOTE: Should the unsubscribe link be available in mandatory emails,
# like transactional emails?
auth_verification_token = UserSubscriptionsAuthVerificationTokenFactory.build(
    user=guardian.user
)

dummy_context.update(
    {
        NotificationType.SIGNUP: {
            "children": children,
            "guardian": guardian,
            "unsubscribe_url": get_marketing_unsubscribe_ui_url(
                guardian, guardian.language, auth_verification_token
            ),
        }
    }
)

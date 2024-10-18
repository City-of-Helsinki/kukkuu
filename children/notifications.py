from django.utils.translation import gettext_lazy as _

from django_ilmoitin.dummy_context import dummy_context
from django_ilmoitin.registry import notifications
from projects.factories import ProjectFactory
from users.factories import GuardianFactory

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
unsubscribe_url = "https://kukkuu-ui-domain/fi/profile/subscriptions?authToken=abc123"
dummy_context.update(
    {
        NotificationType.SIGNUP: {
            "children": children,
            "guardian": guardian,
            "unsubscribe_url": unsubscribe_url,
        }
    }
)

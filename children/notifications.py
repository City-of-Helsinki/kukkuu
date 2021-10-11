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

dummy_context.update(
    {NotificationType.SIGNUP: {"children": children, "guardian": guardian}}
)

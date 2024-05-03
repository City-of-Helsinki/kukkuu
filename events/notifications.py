from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_ilmoitin.dummy_context import dummy_context
from django_ilmoitin.registry import notifications

from children.factories import ChildWithGuardianFactory
from common.utils import get_global_id
from events.consts import NotificationType
from events.factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    OccurrenceFactory,
)
from events.utils import (
    get_event_group_ui_url,
    get_event_ui_url,
    get_occurrence_enrol_ui_url,
    get_occurrence_ui_url,
)
from projects.factories import ProjectFactory
from users.factories import GuardianFactory
from venues.factories import VenueFactory

notifications.register(NotificationType.EVENT_PUBLISHED, _("event published"))
notifications.register(
    NotificationType.EVENT_GROUP_PUBLISHED, _("event group published")
)
notifications.register(NotificationType.OCCURRENCE_FEEDBACK, _("occurrence feedback"))
notifications.register(NotificationType.OCCURRENCE_ENROLMENT, _("occurrence enrolment"))
notifications.register(
    NotificationType.OCCURRENCE_UNENROLMENT, _("occurrence unenrolment")
)
notifications.register(NotificationType.OCCURRENCE_CANCELLED, _("occurrence cancelled"))
notifications.register(NotificationType.OCCURRENCE_REMINDER, _("occurrence reminder"))

project = ProjectFactory.build(year=2020)
event = EventFactory.build(project=project)
event_group = EventGroupFactory.build(project=project)
event_with_event_group = EventFactory.build(project=project, event_group=event_group)
venue = VenueFactory.build(project=project)
guardian = GuardianFactory.build()
child = ChildWithGuardianFactory.build(relationship__guardian=guardian, project=project)
occurrence = OccurrenceFactory.build(event=event, venue=venue)
enrolment = EnrolmentFactory.build(occurrence=occurrence, child=child)
unsubscribe_url = "https://kukkuu-ui-domain/fi/profile/subscriptions?authToken=abc123"
common_event_context = {
    "event": event,
    "child": child,
    "guardian": guardian,
    "event_url": get_event_ui_url(event, child, guardian.language),
    "localtime": timezone.template_localtime,
    "get_global_id": get_global_id,
    "unsubscribe_url": unsubscribe_url,
    "is_obsoleted": True,
}

common_occurrence_context = {
    "occurrence": occurrence,
    "occurrence_url": get_occurrence_ui_url(occurrence, child, guardian.language),
    "occurrence_enrol_url": get_occurrence_enrol_ui_url(
        occurrence, child, guardian.language
    ),
    **common_event_context,
}

dummy_context.update(
    {
        NotificationType.EVENT_PUBLISHED: {**common_event_context},
        NotificationType.OCCURRENCE_FEEDBACK: {**common_occurrence_context},
        NotificationType.OCCURRENCE_ENROLMENT: {**common_occurrence_context},
        NotificationType.OCCURRENCE_UNENROLMENT: {**common_occurrence_context},
        NotificationType.OCCURRENCE_CANCELLED: {**common_occurrence_context},
        NotificationType.OCCURRENCE_REMINDER: {
            "enrolment": enrolment,
            **common_occurrence_context,
        },
        NotificationType.EVENT_GROUP_PUBLISHED: {
            "guardian": guardian,
            "event_group": event_group,
            "event_group_url": get_event_group_ui_url(event, child, guardian.language),
            "events": [
                {
                    "obj": event,
                    "event_url": get_event_ui_url(event, child, guardian.language),
                }
            ],
            "localtime": timezone.template_localtime,
            "get_global_id": get_global_id,
            "unsubscribe_url": unsubscribe_url,
            "is_obsoleted": True,
        },
    }
)

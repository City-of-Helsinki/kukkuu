from django.utils.translation import ugettext_lazy as _
from django_ilmoitin.dummy_context import dummy_context
from django_ilmoitin.registry import notifications
from projects.factories import ProjectFactory
from subscriptions.consts import NotificationType
from subscriptions.factories import FreeSpotNotificationSubscriptionFactory

from children.factories import ChildWithGuardianFactory
from events.factories import EventFactory, OccurrenceFactory
from events.utils import get_event_ui_url, get_occurrence_ui_url
from users.factories import GuardianFactory
from venues.factories import VenueFactory

notifications.register(NotificationType.FREE_SPOT, _("free spot"))

project = ProjectFactory.build(year=2020)
event = EventFactory.build(project=project)
venue = VenueFactory.build(project=project)
guardian = GuardianFactory.build()
child = ChildWithGuardianFactory.build(relationship__guardian=guardian, project=project)
occurrence = OccurrenceFactory.build(event=event, venue=venue)
subscription = FreeSpotNotificationSubscriptionFactory.build(
    child=child, occurrence=occurrence
)

dummy_context.update(
    {
        NotificationType.FREE_SPOT: {
            "guardian": guardian,
            "event": event,
            "child": child,
            "event_url": get_event_ui_url(event, child, guardian.language),
            "occurrence": occurrence,
            "occurrence_url": get_occurrence_ui_url(event, child, guardian.language),
            "subscription": subscription,
        },
    }
)

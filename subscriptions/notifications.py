from uuid import uuid4

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_ilmoitin.dummy_context import dummy_context
from django_ilmoitin.registry import notifications

from children.factories import ChildWithGuardianFactory
from events.factories import EventFactory, OccurrenceFactory
from events.utils import (
    get_event_ui_url,
    get_occurrence_enrol_ui_url,
    get_occurrence_ui_url,
)
from projects.factories import ProjectFactory
from subscriptions.consts import NotificationType
from subscriptions.factories import FreeSpotNotificationSubscriptionFactory
from users.factories import GuardianFactory
from venues.factories import VenueFactory

notifications.register(NotificationType.FREE_SPOT, _("free spot"))

project = ProjectFactory.build(pk=uuid4(), year=2020)
event = EventFactory.build(pk=uuid4(), project=project)
venue = VenueFactory.build(pk=uuid4(), project=project)
guardian = GuardianFactory.build(pk=uuid4())
child = ChildWithGuardianFactory.build(
    pk=uuid4(), relationship__guardian=guardian, project=project
)
occurrence = OccurrenceFactory.build(pk=uuid4(), event=event, venue=venue)
subscription = FreeSpotNotificationSubscriptionFactory.build(
    pk=uuid4(), child=child, occurrence=occurrence
)
unsubscribe_url = "https://kukkuu-ui-domain/fi/profile/subscriptions?authToken=abc123"
dummy_context.update(
    {
        NotificationType.FREE_SPOT: {
            "guardian": guardian,
            "event": event,
            "child": child,
            "event_url": get_event_ui_url(event, child, guardian.language),
            "occurrence": occurrence,
            "occurrence_url": get_occurrence_ui_url(
                occurrence, child, guardian.language
            ),
            "occurrence_enrol_url": get_occurrence_enrol_ui_url(
                occurrence, child, guardian.language
            ),
            "subscription": subscription,
            "localtime": timezone.template_localtime,
            "unsubscribe_url": unsubscribe_url,
        },
    }
)

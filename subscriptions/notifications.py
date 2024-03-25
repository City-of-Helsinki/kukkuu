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
from users.utils import get_marketing_unsubscribe_ui_url
from venues.factories import VenueFactory
from verification_tokens.factories import UserSubscriptionsAuthVerificationTokenFactory

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
auth_verification_token = UserSubscriptionsAuthVerificationTokenFactory.build(
    user=guardian.user
)

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
            "unsubscribe_url": get_marketing_unsubscribe_ui_url(
                guardian, guardian.language, auth_verification_token
            ),
        },
    }
)

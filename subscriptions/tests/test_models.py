from datetime import timedelta

import pytest
from django.utils.timezone import now
from subscriptions.factories import FreeSpotNotificationSubscriptionFactory
from subscriptions.tests.utils import assert_child_has_subscriptions

from events.factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    OccurrenceFactory,
)


@pytest.mark.django_db
def test_enrolling_deletes_same_event_free_spot_subscriptions(
    notification_template_free_spot, child
):
    event = EventFactory(published_at=now())
    occurrence, occurrence_2 = OccurrenceFactory.create_batch(
        2, time=now() + timedelta(days=14), event=event, capacity_override=1,
    )
    EnrolmentFactory(occurrence=occurrence)
    FreeSpotNotificationSubscriptionFactory(
        child=child, occurrence=occurrence
    )  # same event subscription
    other_event_subscription = FreeSpotNotificationSubscriptionFactory(child=child)

    # create an enrolment for the child, subscriptions should be updated accordingly
    EnrolmentFactory(occurrence=occurrence_2, child=child)

    assert_child_has_subscriptions(child, other_event_subscription)


@pytest.mark.django_db
def test_enrolling_deletes_same_event_group_free_spot_subscriptions(child):
    event_group = EventGroupFactory(published_at=now())
    event = EventFactory(published_at=now(), event_group=event_group)
    same_group_event = EventFactory(published_at=now(), event_group=event_group)
    other_group_event = EventFactory(
        published_at=now(), event_group=EventGroupFactory()
    )

    occurrence = OccurrenceFactory.create(time=now() + timedelta(days=1), event=event)
    same_event_occurrence = OccurrenceFactory.create(
        time=now() + timedelta(days=2), event=event
    )
    same_group_occurrence = OccurrenceFactory(
        time=now() + timedelta(days=3), event=same_group_event
    )
    other_group_occurrence = OccurrenceFactory(
        time=now() + timedelta(days=4), event=other_group_event
    )

    same_event_subscription = FreeSpotNotificationSubscriptionFactory(  # noqa: F841
        child=child, occurrence=same_event_occurrence
    )
    same_group_subscription = FreeSpotNotificationSubscriptionFactory(  # noqa: F841
        child=child, occurrence=same_group_occurrence
    )
    other_group_subscription = FreeSpotNotificationSubscriptionFactory(
        child=child, occurrence=other_group_occurrence
    )

    # create an enrolment for the child, subscriptions should be updated accordingly
    EnrolmentFactory(child=child, occurrence=occurrence)

    assert_child_has_subscriptions(child, other_group_subscription)

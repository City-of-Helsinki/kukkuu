from datetime import timedelta

import pytest
from django.core import mail
from django.utils.timezone import now

from common.tests.utils import assert_mails_match_snapshot
from events.factories import EnrolmentFactory, OccurrenceFactory
from subscriptions.factories import FreeSpotNotificationSubscriptionFactory
from subscriptions.tests.utils import assert_child_has_subscriptions


@pytest.mark.django_db
@pytest.mark.parametrize("final_occurrence_capacity", (4, None))
def test_free_spot_notification_occurrence_capacity_changes(
    snapshot, notification_template_free_spot, child, final_occurrence_capacity
):
    occurrence = OccurrenceFactory(
        id=777,
        time=now() + timedelta(days=14),
        event__id=777,
        event__published_at=now(),
        event__capacity_per_occurrence=4,
        capacity_override=3,
    )
    EnrolmentFactory.create_batch(3, occurrence=occurrence)
    FreeSpotNotificationSubscriptionFactory(occurrence=occurrence, child=child)
    other_subscription = FreeSpotNotificationSubscriptionFactory(child=child)

    occurrence.capacity_override = 2
    occurrence.save()

    assert len(mail.outbox) == 0

    occurrence.capacity_override = 3
    occurrence.save()

    assert len(mail.outbox) == 0

    occurrence.capacity_override = final_occurrence_capacity
    occurrence.save()

    assert len(mail.outbox) == 1
    assert_mails_match_snapshot(snapshot)
    assert_child_has_subscriptions(child, other_subscription)


@pytest.mark.django_db
def test_free_spot_notification_event_capacity_changes(
    snapshot, notification_template_free_spot, child
):
    occurrence = OccurrenceFactory(
        id=777,
        time=now() + timedelta(days=14),
        event__id=777,
        event__published_at=now(),
        event__capacity_per_occurrence=3,
    )
    EnrolmentFactory.create_batch(3, occurrence=occurrence)
    FreeSpotNotificationSubscriptionFactory(occurrence=occurrence, child=child)
    other_subscription = FreeSpotNotificationSubscriptionFactory(child=child)
    event = occurrence.event

    event.capacity_per_occurrence = 2
    event.save()

    assert len(mail.outbox) == 0

    event.capacity_per_occurrence = 3
    event.save()

    assert len(mail.outbox) == 0

    event.capacity_per_occurrence = 4
    event.save()

    assert len(mail.outbox) == 1
    assert_mails_match_snapshot(snapshot)
    assert_child_has_subscriptions(child, other_subscription)


@pytest.mark.django_db
def test_free_spot_notification_someone_unenrols(
    snapshot, notification_template_free_spot, child
):
    occurrence = OccurrenceFactory(
        id=777,
        time=now() + timedelta(days=14),
        event__id=777,
        event__published_at=now(),
        event__capacity_per_occurrence=2,
        capacity_override=3,
    )
    enrolments = EnrolmentFactory.create_batch(4, occurrence=occurrence)
    FreeSpotNotificationSubscriptionFactory(occurrence=occurrence, child=child)
    other_subscription = FreeSpotNotificationSubscriptionFactory(child=child)

    enrolments[0].delete()

    assert len(mail.outbox) == 0

    enrolments[1].delete()

    assert len(mail.outbox) == 1
    assert_mails_match_snapshot(snapshot)
    assert_child_has_subscriptions(child, other_subscription)

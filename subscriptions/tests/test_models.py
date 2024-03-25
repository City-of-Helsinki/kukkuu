from datetime import timedelta

import pytest
from django.utils.timezone import now

from events.factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    OccurrenceFactory,
)
from subscriptions.factories import FreeSpotNotificationSubscriptionFactory
from subscriptions.models import FreeSpotNotificationSubscription
from subscriptions.tests.utils import assert_child_has_subscriptions


@pytest.mark.django_db
def test_enrolling_deletes_same_event_free_spot_subscriptions(
    notification_template_free_spot, child
):
    event = EventFactory(published_at=now())
    occurrence, occurrence_2 = OccurrenceFactory.create_batch(
        2,
        time=now() + timedelta(days=14),
        event=event,
        capacity_override=1,
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


@pytest.mark.django_db
def test_user_subscriptions(child):
    guardian = child.guardians.first()
    user = guardian.user

    user_child_subscriptions = list(
        FreeSpotNotificationSubscriptionFactory.create_batch(5, child=child)
    )
    users_other_subscriptions = list(
        FreeSpotNotificationSubscriptionFactory.create_batch(5)
    )
    for subscription in users_other_subscriptions:
        subscription.child.guardians.set([guardian])
    users_subscriptions = user_child_subscriptions + users_other_subscriptions

    # Other users subscriptions in database
    FreeSpotNotificationSubscriptionFactory.create_batch(10)

    # when user_subscriptions is called without args
    results_without_args = FreeSpotNotificationSubscription.objects.user_subscriptions(
        user
    )
    # then it should match with the list of user's all subscriptions,
    # no matter the child
    assert len(users_subscriptions) == len(results_without_args) == 10
    assert all(s in results_without_args for s in users_subscriptions)

    # when user_subscriptions is called with child arg
    results_with_child_arg = (
        FreeSpotNotificationSubscription.objects.user_subscriptions(user, child)
    )
    # then it should match with the list of user's subscriptions for the child
    assert len(results_with_child_arg) == len(user_child_subscriptions) == 5
    assert all(s in results_with_child_arg for s in user_child_subscriptions)

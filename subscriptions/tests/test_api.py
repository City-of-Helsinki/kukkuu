from datetime import timedelta

import pytest
from django.utils.timezone import now

from children.factories import ChildWithGuardianFactory
from common.tests.utils import assert_match_error_code
from common.utils import get_global_id
from events.factories import EventFactory, OccurrenceFactory
from kukkuu.consts import (
    ALREADY_SUBSCRIBED_ERROR,
    OBJECT_DOES_NOT_EXIST_ERROR,
    OCCURRENCE_IS_NOT_FULL_ERROR,
)
from subscriptions.factories import FreeSpotNotificationSubscriptionFactory
from subscriptions.models import FreeSpotNotificationSubscription


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


CHILD_FREE_SPOT_NOTIFICATION_SUBSCRIPTIONS_QUERY = """
query ChildFreeSpotNotificationSubscriptionsQuery($id: ID!) {
  child(id: $id) {
    freeSpotNotificationSubscriptions {
      edges {
        node {
          createdAt
          id
          child {
            firstName
          }
          occurrence {
            time
          }
        }
      }
    }
  }
}
"""

OCCURRENCES_HAS_CHILD_FREE_SPOT_NOTIFICATION_SUBSCRIPTION_QUERY = """
query OccurrencesHasChildFreeSpotNotificationSubscription($childId: ID!) {
  child(id: $childId) {
    availableEvents {
      edges {
        node {
            occurrences {
              edges {
                node {
                  time
                  childHasFreeSpotNotificationSubscription(childId: $childId)
                }
              }
            }
        }
      }
    }
  }
}
"""


@pytest.fixture
def guardian_child(guardian_api_client):
    return ChildWithGuardianFactory(
        first_name="Subscriber",
        relationship__guardian__user=guardian_api_client.user,
    )


def test_child_free_spot_notifications_query(
    snapshot, guardian_api_client, guardian_child
):
    FreeSpotNotificationSubscriptionFactory(id=1, child=guardian_child)

    executed = guardian_api_client.execute(
        CHILD_FREE_SPOT_NOTIFICATION_SUBSCRIPTIONS_QUERY,
        variables={"id": get_global_id(guardian_child)},
    )

    snapshot.assert_match(executed)


def test_occurrences_has_child_free_spot_notification_query(
    snapshot, guardian_api_client, guardian_child
):
    event = EventFactory(published_at=now())
    FreeSpotNotificationSubscriptionFactory(
        child=guardian_child,
        occurrence__event=event,
        occurrence__time=now() + timedelta(days=14),
    )
    FreeSpotNotificationSubscriptionFactory(
        occurrence__event=event, occurrence__time=now() + timedelta(days=15)
    )

    executed = guardian_api_client.execute(
        OCCURRENCES_HAS_CHILD_FREE_SPOT_NOTIFICATION_SUBSCRIPTION_QUERY,
        variables={"childId": get_global_id(guardian_child)},
    )

    snapshot.assert_match(executed)


SUBSCRIBE_TO_FREE_SPOT_NOTIFICATION_MUTATION = """
mutation SubscribeToFreeSpotNotification($input: SubscribeToFreeSpotNotificationMutationInput!) {
  subscribeToFreeSpotNotification(input: $input) {
    child {
      firstName
    }
    occurrence {
      time
    }
  }
}

"""  # noqa


def test_subscribe_to_free_spot_notification(
    snapshot, guardian_api_client, guardian_child
):
    occurrence = OccurrenceFactory(
        event__published_at=now(),
        time=now() + timedelta(days=14),
        event__capacity_per_occurrence=0,
    )

    executed = guardian_api_client.execute(
        SUBSCRIBE_TO_FREE_SPOT_NOTIFICATION_MUTATION,
        variables={
            "input": {
                "occurrenceId": get_global_id(occurrence),
                "childId": get_global_id(guardian_child),
            }
        },
    )

    snapshot.assert_match(executed)
    assert FreeSpotNotificationSubscription.objects.get(
        child=guardian_child, occurrence=occurrence
    )

    executed = guardian_api_client.execute(
        SUBSCRIBE_TO_FREE_SPOT_NOTIFICATION_MUTATION,
        variables={
            "input": {
                "occurrenceId": get_global_id(occurrence),
                "childId": get_global_id(guardian_child),
            }
        },
    )

    assert_match_error_code(executed, ALREADY_SUBSCRIBED_ERROR)


def test_cannot_subscribe_to_free_spot_notification_with_someone_elses_child(
    guardian_api_client,
):
    occurrence = OccurrenceFactory(
        event__published_at=now(), time=now() + timedelta(days=14)
    )
    child = ChildWithGuardianFactory(first_name="Subscriber")

    executed = guardian_api_client.execute(
        SUBSCRIBE_TO_FREE_SPOT_NOTIFICATION_MUTATION,
        variables={
            "input": {
                "occurrenceId": get_global_id(occurrence),
                "childId": get_global_id(child),
            }
        },
    )

    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)


def test_cannot_subscribe_to_free_spot_notification_when_occurrence_not_full(
    guardian_api_client, guardian_child
):
    occurrence = OccurrenceFactory(
        event__published_at=now(),
        time=now() + timedelta(days=14),
        capacity_override=1,
    )

    executed = guardian_api_client.execute(
        SUBSCRIBE_TO_FREE_SPOT_NOTIFICATION_MUTATION,
        variables={
            "input": {
                "occurrenceId": get_global_id(occurrence),
                "childId": get_global_id(guardian_child),
            }
        },
    )

    assert_match_error_code(executed, OCCURRENCE_IS_NOT_FULL_ERROR)


UNSUBSCRIBE_FROM_FREE_SPOT_NOTIFICATION_MUTATION = """
mutation UnsubscribeFromFreeSpotNotification($input: UnsubscribeFromFreeSpotNotificationMutationInput!) {
  unsubscribeFromFreeSpotNotification(input: $input) {
    child {
      firstName
    }
    occurrence {
      time
    }
  }
}

"""  # noqa


def test_unsubscribe_from_free_spot_notification(
    snapshot, guardian_api_client, guardian_child
):
    subscription = FreeSpotNotificationSubscriptionFactory(child=guardian_child)

    executed = guardian_api_client.execute(
        UNSUBSCRIBE_FROM_FREE_SPOT_NOTIFICATION_MUTATION,
        variables={
            "input": {
                "occurrenceId": get_global_id(subscription.occurrence),
                "childId": get_global_id(guardian_child),
            }
        },
    )

    snapshot.assert_match(executed)
    assert not FreeSpotNotificationSubscription.objects.filter(
        child=guardian_child, occurrence=subscription.occurrence
    ).exists()


def test_cannot_unsubscribe_from_free_spot_notification_with_someone_elses_child(
    guardian_api_client,
):
    child = ChildWithGuardianFactory(first_name="Subscriber")
    subscription = FreeSpotNotificationSubscriptionFactory(child=child)

    executed = guardian_api_client.execute(
        UNSUBSCRIBE_FROM_FREE_SPOT_NOTIFICATION_MUTATION,
        variables={
            "input": {
                "occurrenceId": get_global_id(subscription.occurrence),
                "childId": get_global_id(child),
            }
        },
    )

    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)

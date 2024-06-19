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
    PERMISSION_DENIED_ERROR,
)
from subscriptions.factories import FreeSpotNotificationSubscriptionFactory
from subscriptions.models import FreeSpotNotificationSubscription
from users.factories import GuardianFactory


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
            name
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
        name="Subscriber",
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
      name
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
    child = ChildWithGuardianFactory(name="Subscriber")

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
      name
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
    child = ChildWithGuardianFactory(name="Subscriber")
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


UNSUBSCRIBE_FROM_ALL_NOTIFICATIONS_MUTATION = """
mutation UnsubscribeFromAllNotifications(
    $input: UnsubscribeFromAllNotificationsMutationInput!
) {
  unsubscribeFromAllNotifications(input: $input) {
    guardian {
        user {
            username
        }
    }
    unsubscribed
  }
}
"""


def test_unsubscribe_from_all_notifications(
    snapshot, guardian_api_client, guardian_child
):
    guardian = guardian_child.guardians.first()
    user = guardian.user
    FreeSpotNotificationSubscriptionFactory(child=guardian_child)
    executed = guardian_api_client.execute(
        UNSUBSCRIBE_FROM_ALL_NOTIFICATIONS_MUTATION,
        variables={"input": {}},
    )
    assert (
        executed["data"]["unsubscribeFromAllNotifications"]["guardian"]["user"][
            "username"
        ]
        == user.username
    )
    snapshot.assert_match(executed)
    assert not FreeSpotNotificationSubscription.objects.filter(
        child=guardian_child
    ).exists()


def test_unsubscribe_from_all_notifications_using_auth_verification_token(
    snapshot, api_client, guardian_child
):
    guardian = guardian_child.guardians.first()
    user = guardian.user
    FreeSpotNotificationSubscriptionFactory(child=guardian_child)
    auth_verification_token = user.create_subscriptions_management_auth_token()
    executed = api_client.execute(
        UNSUBSCRIBE_FROM_ALL_NOTIFICATIONS_MUTATION,
        variables={
            "input": {
                "authToken": auth_verification_token.key,
            }
        },
    )
    assert (
        executed["data"]["unsubscribeFromAllNotifications"]["guardian"]["user"][
            "username"
        ]
        == user.username
    )
    snapshot.assert_match(executed)
    assert not FreeSpotNotificationSubscription.objects.filter(
        child=guardian_child
    ).exists()


def test_unsubscribe_from_all_notifications_using_invalid_auth_verification_token(
    api_client, guardian_child
):
    guardian = guardian_child.guardians.first()
    user = guardian.user
    FreeSpotNotificationSubscriptionFactory(child=guardian_child)
    user.create_subscriptions_management_auth_token()
    executed = api_client.execute(
        UNSUBSCRIBE_FROM_ALL_NOTIFICATIONS_MUTATION,
        variables={
            "input": {
                "authToken": "invalid token",
            }
        },
    )
    assert_match_error_code(executed, PERMISSION_DENIED_ERROR)
    assert FreeSpotNotificationSubscription.objects.filter(
        child=guardian_child
    ).exists()


def test_unsubscribe_from_all_notifications_using_auth_verification_token_as_logged_in(
    snapshot, guardian_api_client, guardian_child
):
    logged_in_guardian = guardian_api_client.user.guardian
    child_guardian = guardian_child.guardians.first()

    assert logged_in_guardian.id == child_guardian.id

    user = child_guardian.user
    FreeSpotNotificationSubscriptionFactory(child=guardian_child)

    # Token is created for another user
    auth_verification_token = user.create_subscriptions_management_auth_token()
    executed = guardian_api_client.execute(
        UNSUBSCRIBE_FROM_ALL_NOTIFICATIONS_MUTATION,
        variables={
            "input": {
                "authToken": auth_verification_token.key,
            }
        },
    )
    assert (
        executed["data"]["unsubscribeFromAllNotifications"]["guardian"]["user"][
            "username"
        ]
        == user.username
    )
    snapshot.assert_match(executed)
    assert not FreeSpotNotificationSubscription.objects.filter(
        child=guardian_child
    ).exists()


def test_unsubscribe_from_all_notifications_when_logged_in_user_not_auth_token_user(
    snapshot, user_api_client, guardian_child
):
    logged_in_guardian = GuardianFactory(user=user_api_client.user)
    child_guardian = guardian_child.guardians.first()

    assert logged_in_guardian != child_guardian

    FreeSpotNotificationSubscriptionFactory(child=guardian_child)

    # Token is created for another user
    auth_verification_token = (
        child_guardian.user.create_subscriptions_management_auth_token()
    )
    executed = user_api_client.execute(
        UNSUBSCRIBE_FROM_ALL_NOTIFICATIONS_MUTATION,
        variables={
            "input": {
                "authToken": auth_verification_token.key,
            }
        },
    )
    assert (
        executed["data"]["unsubscribeFromAllNotifications"]["guardian"]["user"][
            "username"
        ]
        == logged_in_guardian.user.username
    )
    snapshot.assert_match(executed)
    assert FreeSpotNotificationSubscription.objects.filter(
        child=guardian_child
    ).exists()

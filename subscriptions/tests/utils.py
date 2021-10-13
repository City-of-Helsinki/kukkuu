from collections import Iterable


def assert_child_has_subscriptions(child, subscriptions):
    if not isinstance(subscriptions, Iterable):
        subscriptions = {subscriptions} if subscriptions else {}
    subscription_ids = {s.pk for s in child.free_spot_notification_subscriptions.all()}
    expected_ids = {s.pk for s in subscriptions}
    assert (
        subscription_ids == expected_ids
    ), f"Subscriptions IDs {subscription_ids} do not match expected {expected_ids}"

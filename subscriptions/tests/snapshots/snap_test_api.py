# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_child_free_spot_notifications_query 1"] = {
    "data": {
        "child": {
            "freeSpotNotificationSubscriptions": {
                "edges": [
                    {
                        "node": {
                            "child": {"firstName": "Subscriber"},
                            "createdAt": "2020-12-12T00:00:00+00:00",
                            "id": "RnJlZVNwb3ROb3RpZmljYXRpb25TdWJzY3JpcHRpb25Ob2RlOjE=",
                            "occurrence": {"time": "1971-11-04T13:17:08+00:00"},
                        }
                    }
                ]
            }
        }
    }
}

snapshots["test_occurrences_has_child_free_spot_notification_query 1"] = {
    "data": {
        "child": {
            "availableEvents": {
                "edges": [
                    {
                        "node": {
                            "occurrences": {
                                "edges": [
                                    {
                                        "node": {
                                            "childHasFreeSpotNotificationSubscription": True,
                                            "time": "2020-12-26T00:00:00+00:00",
                                        }
                                    },
                                    {
                                        "node": {
                                            "childHasFreeSpotNotificationSubscription": False,
                                            "time": "2020-12-27T00:00:00+00:00",
                                        }
                                    },
                                ]
                            }
                        }
                    }
                ]
            }
        }
    }
}

snapshots["test_subscribe_to_free_spot_notification 1"] = {
    "data": {
        "subscribeToFreeSpotNotification": {
            "child": {"firstName": "Subscriber"},
            "occurrence": {"time": "2020-12-26T00:00:00+00:00"},
        }
    }
}

snapshots["test_unsubscribe_from_free_spot_notification 1"] = {
    "data": {
        "unsubscribeFromFreeSpotNotification": {
            "child": {"firstName": "Subscriber"},
            "occurrence": {"time": "1971-11-04T13:17:08+00:00"},
        }
    }
}

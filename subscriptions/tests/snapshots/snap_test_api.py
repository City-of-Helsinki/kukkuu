# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_child_free_spot_notifications_query 1'] = {
    'data': {
        'child': {
            'freeSpotNotificationSubscriptions': {
                'edges': [
                    {
                        'node': {
                            'child': {
                                'name': 'Subscriber'
                            },
                            'createdAt': '2020-12-12T00:00:00+00:00',
                            'id': 'RnJlZVNwb3ROb3RpZmljYXRpb25TdWJzY3JpcHRpb25Ob2RlOjE=',
                            'occurrence': {
                                'time': '1993-10-11T08:38:57.954874+00:00'
                            }
                        }
                    }
                ]
            }
        }
    }
}

snapshots['test_occurrences_has_child_free_spot_notification_query 1'] = {
    'data': {
        'child': {
            'availableEvents': {
                'edges': [
                    {
                        'node': {
                            'occurrences': {
                                'edges': [
                                    {
                                        'node': {
                                            'childHasFreeSpotNotificationSubscription': True,
                                            'time': '2020-12-26T00:00:00+00:00'
                                        }
                                    },
                                    {
                                        'node': {
                                            'childHasFreeSpotNotificationSubscription': False,
                                            'time': '2020-12-27T00:00:00+00:00'
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }
    }
}

snapshots['test_subscribe_to_free_spot_notification 1'] = {
    'data': {
        'subscribeToFreeSpotNotification': {
            'child': {
                'name': 'Subscriber'
            },
            'occurrence': {
                'time': '2020-12-26T00:00:00+00:00'
            }
        }
    }
}

snapshots['test_unsubscribe_from_all_notifications 1'] = {
    'data': {
        'unsubscribeFromAllNotifications': {
            'guardian': {
                'user': {
                    'username': 'blake64'
                }
            },
            'unsubscribed': True
        }
    }
}

snapshots['test_unsubscribe_from_all_notifications_using_auth_verification_token 1'] = {
    'data': {
        'unsubscribeFromAllNotifications': {
            'guardian': {
                'user': {
                    'username': 'blake64'
                }
            },
            'unsubscribed': True
        }
    }
}

snapshots['test_unsubscribe_from_all_notifications_using_auth_verification_token_as_logged_in 1'] = {
    'data': {
        'unsubscribeFromAllNotifications': {
            'guardian': {
                'user': {
                    'username': 'blake64'
                }
            },
            'unsubscribed': True
        }
    }
}

snapshots['test_unsubscribe_from_all_notifications_when_logged_in_user_not_auth_token_user 1'] = {
    'data': {
        'unsubscribeFromAllNotifications': {
            'guardian': {
                'user': {
                    'username': 'jeffersonkimberly'
                }
            },
            'unsubscribed': True
        }
    }
}

snapshots['test_unsubscribe_from_free_spot_notification 1'] = {
    'data': {
        'unsubscribeFromFreeSpotNotification': {
            'child': {
                'name': 'Subscriber'
            },
            'occurrence': {
                'time': '1993-10-11T08:38:57.954874+00:00'
            }
        }
    }
}

# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_signup_notification 1"] = [
    """kukkuu@example.com|['michellewalker@example.net']|SIGNUP-notifikaation aihe|
SIGNUP-notifikaation sisältö tekstimuodossa.
Lapset: [<Child: Matti (2020)>, <Child: Jussi (2020)>]
Huoltaja: Gulle Guardian (michellewalker@example.net)
Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8"""
]

snapshots["test_signup_notification_language[EN] 1"] = [
    """kukkuu@example.com|['michellewalker@example.net']|SIGNUP notification subject|
SIGNUP notification body text.
Children: [<Child: Matti (2020)>, <Child: Jussi (2020)>]
Guardian: Gulle Guardian (michellewalker@example.net)
Unsubscribe: http://localhost:3000/en/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8"""
]

snapshots["test_signup_notification_language[FI] 1"] = [
    """kukkuu@example.com|['michellewalker@example.net']|SIGNUP-notifikaation aihe|
SIGNUP-notifikaation sisältö tekstimuodossa.
Lapset: [<Child: Matti (2020)>, <Child: Jussi (2020)>]
Huoltaja: Gulle Guardian (michellewalker@example.net)
Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8"""
]

snapshots["test_signup_notification_language[SV] 1"] = [
    """kukkuu@example.com|['michellewalker@example.net']|SIGNUP-notifikaation aihe|
SIGNUP-notifikaation sisältö tekstimuodossa.
Lapset: [<Child: Matti (2020)>, <Child: Jussi (2020)>]
Huoltaja: Gulle Guardian (michellewalker@example.net)
Unsubscribe: http://localhost:3000/sv/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8"""
]

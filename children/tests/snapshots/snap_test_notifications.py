# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_signup_notification 1"] = [
    """kukkuu@example.com|['michellewalker@example.net']|SIGNUP-notifikaation aihe|
SIGNUP-notifikaation sisältö tekstimuodossa.
Lapset: [<Child: Matti (2020)>, <Child: Jussi (2020)>]
Huoltaja: Gulle Guardian (michellewalker@example.net)"""
]

snapshots["test_signup_notification_language[EN] 1"] = [
    """kukkuu@example.com|['michellewalker@example.net']|SIGNUP notification subject|
SIGNUP notification body text.
Children: [<Child: Matti (2020)>, <Child: Jussi (2020)>]
Guardian: Gulle Guardian (michellewalker@example.net)"""
]

snapshots["test_signup_notification_language[FI] 1"] = [
    """kukkuu@example.com|['michellewalker@example.net']|SIGNUP-notifikaation aihe|
SIGNUP-notifikaation sisältö tekstimuodossa.
Lapset: [<Child: Matti (2020)>, <Child: Jussi (2020)>]
Huoltaja: Gulle Guardian (michellewalker@example.net)"""
]

snapshots["test_signup_notification_language[SV] 1"] = [
    """kukkuu@example.com|['michellewalker@example.net']|SIGNUP-notifikaation aihe|
SIGNUP-notifikaation sisältö tekstimuodossa.
Lapset: [<Child: Matti (2020)>, <Child: Jussi (2020)>]
Huoltaja: Gulle Guardian (michellewalker@example.net)"""
]

# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_signup_notification 1"] = [
    """kukkuu@example.com|['mperez@cox.com']|SIGNUP-notifikaation aihe|
SIGNUP-notifikaation sisältö tekstimuodossa.
Lapset: [<Child: Matti Mainio (2020-01-01)>, <Child: Jussi Juonio (2020-02-02)>]
Huoltaja: Gulle Guardian (mperez@cox.com)"""
]

snapshots["test_signup_notification_language[EN] 1"] = [
    """kukkuu@example.com|['mperez@cox.com']|SIGNUP notification subject|
SIGNUP notification body text.
Children: [<Child: Matti Mainio (2020-01-01)>, <Child: Jussi Juonio (2020-02-02)>]
Guardian: Gulle Guardian (mperez@cox.com)"""
]

snapshots["test_signup_notification_language[FI] 1"] = [
    """kukkuu@example.com|['mperez@cox.com']|SIGNUP-notifikaation aihe|
SIGNUP-notifikaation sisältö tekstimuodossa.
Lapset: [<Child: Matti Mainio (2020-01-01)>, <Child: Jussi Juonio (2020-02-02)>]
Huoltaja: Gulle Guardian (mperez@cox.com)"""
]

snapshots["test_signup_notification_language[SV] 1"] = [
    """kukkuu@example.com|['mperez@cox.com']|SIGNUP-notifikaation aihe|
SIGNUP-notifikaation sisältö tekstimuodossa.
Lapset: [<Child: Matti Mainio (2020-01-01)>, <Child: Jussi Juonio (2020-02-02)>]
Huoltaja: Gulle Guardian (mperez@cox.com)"""
]

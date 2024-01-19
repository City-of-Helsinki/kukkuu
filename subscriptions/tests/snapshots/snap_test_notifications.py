# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_free_spot_notification_event_capacity_changes 1"] = [
    """kukkuu@example.com|['matthewbrooks@example.com']|Free spot FI|
        Event FI: Answer entire increase thank certainly again thought.
        Guardian FI: Todd Sellers (matthewbrooks@example.com)
        Event URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOmU0Y2U1YmRiLWRlODQtNGU3Zi1hOWE0LTUxY2Y2NWNjN2QzMg==/event/RXZlbnROb2RlOjc3Nw==
        Child: Alexis (2020-07-19)
        Occurrence enrol URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOmU0Y2U1YmRiLWRlODQtNGU3Zi1hOWE0LTUxY2Y2NWNjN2QzMg==/event/RXZlbnROb2RlOjc3Nw==/occurrence/T2NjdXJyZW5jZU5vZGU6Nzc3/enrol
        Subscription created at: 2020-12-12 00:00:00+00:00"""
]

snapshots["test_free_spot_notification_occurrence_capacity_changes[4] 1"] = [
    """kukkuu@example.com|['matthewbrooks@example.com']|Free spot FI|
        Event FI: Answer entire increase thank certainly again thought.
        Guardian FI: Todd Sellers (matthewbrooks@example.com)
        Event URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOmU0Y2U1YmRiLWRlODQtNGU3Zi1hOWE0LTUxY2Y2NWNjN2QzMg==/event/RXZlbnROb2RlOjc3Nw==
        Child: Alexis (2020-07-19)
        Occurrence enrol URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOmU0Y2U1YmRiLWRlODQtNGU3Zi1hOWE0LTUxY2Y2NWNjN2QzMg==/event/RXZlbnROb2RlOjc3Nw==/occurrence/T2NjdXJyZW5jZU5vZGU6Nzc3/enrol
        Subscription created at: 2020-12-12 00:00:00+00:00"""
]

snapshots["test_free_spot_notification_occurrence_capacity_changes[None] 1"] = [
    """kukkuu@example.com|['matthewbrooks@example.com']|Free spot FI|
        Event FI: Answer entire increase thank certainly again thought.
        Guardian FI: Todd Sellers (matthewbrooks@example.com)
        Event URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOmU0Y2U1YmRiLWRlODQtNGU3Zi1hOWE0LTUxY2Y2NWNjN2QzMg==/event/RXZlbnROb2RlOjc3Nw==
        Child: Alexis (2020-07-19)
        Occurrence enrol URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOmU0Y2U1YmRiLWRlODQtNGU3Zi1hOWE0LTUxY2Y2NWNjN2QzMg==/event/RXZlbnROb2RlOjc3Nw==/occurrence/T2NjdXJyZW5jZU5vZGU6Nzc3/enrol
        Subscription created at: 2020-12-12 00:00:00+00:00"""
]

snapshots["test_free_spot_notification_someone_unenrols 1"] = [
    """kukkuu@example.com|['matthewbrooks@example.com']|Free spot FI|
        Event FI: Answer entire increase thank certainly again thought.
        Guardian FI: Todd Sellers (matthewbrooks@example.com)
        Event URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOmU0Y2U1YmRiLWRlODQtNGU3Zi1hOWE0LTUxY2Y2NWNjN2QzMg==/event/RXZlbnROb2RlOjc3Nw==
        Child: Alexis (2020-07-19)
        Occurrence enrol URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOmU0Y2U1YmRiLWRlODQtNGU3Zi1hOWE0LTUxY2Y2NWNjN2QzMg==/event/RXZlbnROb2RlOjc3Nw==/occurrence/T2NjdXJyZW5jZU5vZGU6Nzc3/enrol
        Subscription created at: 2020-12-12 00:00:00+00:00"""
]

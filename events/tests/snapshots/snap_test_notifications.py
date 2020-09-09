# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_occurrence_cancelled_notification[True] 1"] = [
    """kukkuu@example.com|['mperez@cox.com']|Occurrence cancelled FI|
        Event FI: Address prove color effort.
        Guardian FI: I Should Receive A Notification Thompson
        Occurrence: 2020-12-12 01:00:00+00:00
        Child: John Terrell (2020-09-07)"""
]

snapshots["test_occurrence_cancelled_notification[False] 1"] = [
    """kukkuu@example.com|['mperez@cox.com']|Occurrence cancelled FI|
        Event FI: Address prove color effort.
        Guardian FI: I Should Receive A Notification Thompson
        Occurrence: 2020-12-12 01:00:00+00:00
        Child: John Terrell (2020-09-07)"""
]

snapshots["test_occurrence_enrolment_notifications_on_model_level 1"] = [
    """kukkuu@example.com|['mperez@cox.com']|Occurrence enrolment FI|
        Event FI: Free heart significant machine try.
        Guardian FI: Willie Frey
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Andrea Ward (2020-06-23)
        Occurrence URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjU0NWM1ZmU1LTIzNWItNDZmZC1hYTJhLWNkNWRlNmZkZDBmYw==/occurrence/T2NjdXJyZW5jZU5vZGU6NzQ="""
]

snapshots["test_unenrol_occurrence_notification 1"] = [
    """kukkuu@example.com|['mollythomas@eaton.com']|Occurrence unenrolment FI|
        Event FI: Detail audience campaign college career fight data.
        Guardian FI: Calvin Gutierrez
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Mary Brown (2020-10-12)"""
]

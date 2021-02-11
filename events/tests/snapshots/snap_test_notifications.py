# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_event_group_publish_notification 1"] = [
    """kukkuu@example.com|['shannon76@yahoo.com']|Event group published FI|
        Event group FI: Public high concern glass person along age.
        Guardian FI: Cody Ramirez (shannon76@yahoo.com)
        Url: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event-group/RXZlbnRHcm91cE5vZGU6Nzc3
        Events:
            Benefit treat final central. Past ready join enjoy. 2020-12-12 00:00:00+00:00 http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event/RXZlbnROb2RlOjc3Nw==
"""
]

snapshots["test_occurrence_cancelled_notification[False] 1"] = [
    """kukkuu@example.com|['mperez@cox.com']|Occurrence cancelled FI|
        Event FI: Address prove color effort.
        Guardian FI: I Should Receive A Notification Thompson (mperez@cox.com)
        Occurrence: 2020-12-12 01:00:00+00:00
        Child: John Terrell (2020-09-07)"""
]

snapshots["test_occurrence_cancelled_notification[True] 1"] = [
    """kukkuu@example.com|['mperez@cox.com']|Occurrence cancelled FI|
        Event FI: Address prove color effort.
        Guardian FI: I Should Receive A Notification Thompson (mperez@cox.com)
        Occurrence: 2020-12-12 01:00:00+00:00
        Child: John Terrell (2020-09-07)"""
]

snapshots["test_occurrence_enrolment_notifications_on_model_level 1"] = [
    """kukkuu@example.com|['mperez@cox.com']|Occurrence enrolment FI|
        Event FI: Free heart significant machine try.
        Guardian FI: Victoria Moon (mperez@cox.com)
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Alice Hobbs (2020-03-28)
        Occurrence URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjU0NWM1ZmU1LTIzNWItNDZmZC1hYTJhLWNkNWRlNmZkZDBmYw==/occurrence/T2NjdXJyZW5jZU5vZGU6NzQ="""
]

snapshots["test_occurrence_reminder_notification 1"] = [
    """kukkuu@example.com|['shannon76@yahoo.com']|Occurrence reminder FI|
        Event FI: Success answer entire increase thank. Least then top sing.
        Guardian FI: I Should Receive A Notification (shannon76@yahoo.com)
        Occurrence: 2020-12-19 00:00:00+00:00
        Child: Alexis Black (2020-07-29)
        Enrolment: 2020-12-19 00:00:00+00:00""",
    """kukkuu@example.com|['laurensmith@davidson.com']|Occurrence reminder FI|
        Event FI: Difficult special respond.
        Guardian FI: I Should Receive A Notification (laurensmith@davidson.com)
        Occurrence: 2020-12-13 00:00:00+00:00
        Child: Robert Williams (2020-06-11)
        Enrolment: 2020-12-13 00:00:00+00:00""",
]

snapshots["test_unenrol_occurrence_notification 1"] = [
    """kukkuu@example.com|['mollythomas@eaton.com']|Occurrence unenrolment FI|
        Event FI: Detail audience campaign college career fight data.
        Guardian FI: Calvin Gutierrez (mollythomas@eaton.com)
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Mary Brown (2020-10-12)"""
]

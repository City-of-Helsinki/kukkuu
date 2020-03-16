# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_occurrence_enrolment_notifications 1"] = [
    """kukkuu@example.com|['mperez@cox.com']|Occurrence enrolment FI|
        Event FI: Free heart significant machine try.
        Guardian FI: Victoria Moon
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Alice Hobbs (2020-03-28)""",
    """kukkuu@example.com|['mperez@cox.com']|Occurrence unenrolment FI|
        Event FI: Free heart significant machine try.
        Guardian FI: Victoria Moon
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Alice Hobbs (2020-03-28)""",
]

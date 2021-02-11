# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_guardian_changed_email_notification[None] 1"] = []

snapshots["test_guardian_changed_email_notification[new.email@example.com] 1"] = [
    "kukkuu@example.com|['new.email@example.com']|Guardian email changed FI|Guardian FI: White Guardian (new.email@example.com)"
]

snapshots["test_guardian_changed_email_notification[old.email@example.com] 1"] = []

# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_guardian_change_email_token_requested_notification[None] 1'] = [
]

snapshots['test_guardian_change_email_token_requested_notification[new.email@example.com] 1'] = [
    '''kukkuu@example.com|['new.email@example.com']|Guardian email change verification token requested FI|Guardian FI: Michael Patton (old.email@example.com).
        Token: abc123+-.
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8
        '''
]

snapshots['test_guardian_change_email_token_requested_notification[old.email@example.com] 1'] = [
    '''kukkuu@example.com|['old.email@example.com']|Guardian email change verification token requested FI|Guardian FI: Michael Patton (old.email@example.com).
        Token: abc123+-.
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8
        '''
]

snapshots['test_guardian_changed_email_notification[None] 1'] = [
]

snapshots['test_guardian_changed_email_notification[new.email@example.com] 1'] = [
    "kukkuu@example.com|['new.email@example.com']|Guardian email changed FI|Guardian FI: Michael Patton (new.email@example.com). Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8"
]

snapshots['test_guardian_changed_email_notification[old.email@example.com] 1'] = [
]

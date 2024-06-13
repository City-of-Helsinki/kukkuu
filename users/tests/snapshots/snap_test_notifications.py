# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_guardian_change_email_token_requested_notification[None] 1"] = []

snapshots[
    "test_guardian_change_email_token_requested_notification[new.email@example.com] 1"
] = [
    """kukkuu@example.com|['new.email@example.com']|Guardian email change verification token requested FI|Guardian FI: Michael Patton (old.email@example.com).
        Token: abc123+-.
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8
        """
]

snapshots[
    "test_guardian_change_email_token_requested_notification[old.email@example.com] 1"
] = [
    """kukkuu@example.com|['old.email@example.com']|Guardian email change verification token requested FI|Guardian FI: Michael Patton (old.email@example.com).
        Token: abc123+-.
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8
        """
]

snapshots["test_guardian_changed_email_notification[None] 1"] = []

snapshots["test_guardian_changed_email_notification[new.email@example.com] 1"] = [
    "kukkuu@example.com|['new.email@example.com']|Guardian email changed FI|Guardian FI: Michael Patton (new.email@example.com). Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8"
]

snapshots["test_guardian_changed_email_notification[old.email@example.com] 1"] = []

snapshots["test_send_user_auth_service_is_changing_with_children 1"] = [
    """kukkuu@example.com|['michellewalker@example.net']|User authorization service is changing FI|
Guardian FI: Michael Patton (michellewalker@example.net).
The change is happening 17.6.2024.
Childrens' event participation history:

Child name: Jason Berg

Event: Enjoy when one wonder fund nor white.
Occurrence: 2011-01-05 08:35:11+00:00

Event: Affect money school military statement.
Occurrence: 1972-02-01 22:06:34+00:00

Child name: Katherine Gomez

Event: Data table TV minute. Agree room laugh prevent make.
Occurrence: 1971-04-02 05:11:11+00:00

Event: Include and individual effort indeed discuss challenge school.
Occurrence: 1974-05-30 15:30:48+00:00

Markdown: 
# Jason Berg


1. **Affect money school military statement.:** 2.2.1972 00:06

    Peace mean education college daughter.


2. **Enjoy when one wonder fund nor white.:** 5.1.2011 10:35

    Sort deep phone such water price including.



# Katherine Gomez


1. **Data table TV minute. Agree room laugh prevent make.:** 2.4.1971 07:11

    Enter everything history remember stay public high.


2. **Include and individual effort indeed discuss challenge school.:** 30.5.1974 17:30

    Second know say former conference carry factor.
"""
]

snapshots[
    "test_send_user_auth_service_is_changing_with_date_of_change_str_param[24.12.2024] 1"
] = [
    """kukkuu@example.com|['michellewalker@example.net']|User authorization service is changing FI|
Guardian FI: Michael Patton (michellewalker@example.net).
The change is happening 24.12.2024.
"""
]

snapshots[
    "test_send_user_auth_service_is_changing_with_date_of_change_str_param[None] 1"
] = [
    """kukkuu@example.com|['michellewalker@example.net']|User authorization service is changing FI|
Guardian FI: Michael Patton (michellewalker@example.net).
The change is happening 17.6.2024.
"""
]

snapshots[
    "test_send_user_auth_service_is_changing_with_date_of_change_str_param[] 1"
] = [
    """kukkuu@example.com|['michellewalker@example.net']|User authorization service is changing FI|
Guardian FI: Michael Patton (michellewalker@example.net).
The change is happening 17.6.2024.
"""
]

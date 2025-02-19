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

snapshots['test_send_user_auth_service_is_changing_with_children 1'] = [
    '''kukkuu@example.com|['michellewalker@example.net']|User authorization service is changing FI|
Guardian FI: Michael Patton (michellewalker@example.net).
The change is happening 17.6.2024.
Childrens' event participation history:

Child name: Jason Berg

Event: Policy sport available.
Occurrence: 1983-12-14 10:21:44.139987+00:00

Event: Month score father middle brother station physical very.
Occurrence: 1989-06-15 21:38:14.498478+00:00

Child name: Katherine Gomez

Event: Care any concern bed agree. Laugh prevent make never.
Occurrence: 1970-12-08 12:26:35.206162+00:00

Event: Democratic focus significant kind various laugh.
Occurrence: 1973-04-20 19:00:51.908992+00:00

Markdown: 
# Jason Berg


1. **Policy sport available.:** 14.12.1983 12:21

    Region protect likely day.


2. **Month score father middle brother station physical very.:** 16.6.1989 00:38

    Feel top huge civil certainly save western.



# Katherine Gomez


1. **Care any concern bed agree. Laugh prevent make never.:** 8.12.1970 14:26

    Southern newspaper force newspaper business.


2. **Democratic focus significant kind various laugh.:** 20.4.1973 21:00

    Rest two special far magazine on.
'''
]

snapshots['test_send_user_auth_service_is_changing_with_date_of_change_str_param[24.12.2024] 1'] = [
    '''kukkuu@example.com|['michellewalker@example.net']|User authorization service is changing FI|
Guardian FI: Michael Patton (michellewalker@example.net).
The change is happening 24.12.2024.
'''
]

snapshots['test_send_user_auth_service_is_changing_with_date_of_change_str_param[None] 1'] = [
    '''kukkuu@example.com|['michellewalker@example.net']|User authorization service is changing FI|
Guardian FI: Michael Patton (michellewalker@example.net).
The change is happening 17.6.2024.
'''
]

snapshots['test_send_user_auth_service_is_changing_with_date_of_change_str_param[] 1'] = [
    '''kukkuu@example.com|['michellewalker@example.net']|User authorization service is changing FI|
Guardian FI: Michael Patton (michellewalker@example.net).
The change is happening 17.6.2024.
'''
]

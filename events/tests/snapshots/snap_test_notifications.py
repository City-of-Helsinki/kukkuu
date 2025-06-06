# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_event_group_publish_notification 1'] = [
    '''kukkuu@example.com|['ywashington@example.com']|Event group published FI|
        Event group FI: Scientist service wonder everything pay.
        Guardian FI: Denise Thompson (ywashington@example.com)
        Url: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event-group/RXZlbnRHcm91cE5vZGU6Nzc3
        Events:
            Gas heavy affect difficult look can purpose care. 2020-12-12 00:00:00+00:00 http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event/RXZlbnROb2RlOjc3Nw==
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8'''
]

snapshots['test_event_group_republish_notification 1'] = [
    '''kukkuu@example.com|['ywashington@example.com']|Event group published FI|
        Event group FI: Loss there southern newspaper force.
        Guardian FI: Denise Thompson (ywashington@example.com)
        Url: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event-group/RXZlbnRHcm91cE5vZGU6Nzc3
        Events:
            If his their best. Election stay every something base. 2020-12-11 00:00:00+00:00 http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event/RXZlbnROb2RlOjc3Nw==
            Data control as receive. End available avoid girl middle. 2020-12-12 00:00:00+00:00 http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event/RXZlbnROb2RlOjc3OA==
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8'''
]

snapshots['test_feedback_notification 1'] = [
    '''kukkuu@example.com|['ywashington@example.com']|Feedback FI|
        Event FI: Entire increase thank certainly again.
        Guardian FI: (60, 15) I Should Receive A Notification (ywashington@example.com)
        Occurrence: 2020-12-11 23:00:00+00:00
        Child: Jose Kerr (2022)
        Enrolment: 2020-12-11 23:00:00+00:00
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8''',
    '''kukkuu@example.com|['jennifer00@example.com']|Feedback FI|
        Event FI: Special respond positive cold.
        Guardian FI: (30, 15) I Should Receive A Notification (jennifer00@example.com)
        Occurrence: 2020-12-11 23:30:00+00:00
        Child: Jason Williams (2021)
        Enrolment: 2020-12-11 23:30:00+00:00
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8''',
    '''kukkuu@example.com|['aaronlee@example.org']|Feedback FI|
        Event FI: Bar wish find system woman why. Whose age feeling speech.
        Guardian FI: (135, None) I Should Receive A Notification (aaronlee@example.org)
        Occurrence: 2020-12-11 21:45:00+00:00
        Child: Lindsey Baker (2022)
        Enrolment: 2020-12-11 21:45:00+00:00
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8''',
    '''kukkuu@example.com|['dennis27@example.net']|Feedback FI|
        Event FI: Other poor specific carry owner sense other.
        Guardian FI: (10080, 15) I Should Receive A Notification (dennis27@example.net)
        Occurrence: 2020-12-05 00:00:00+00:00
        Child: Alexa Mcdonald (2018)
        Enrolment: 2020-12-05 00:00:00+00:00
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8'''
]

snapshots['test_feedback_notification_instance_checks[False] 1'] = [
    '''kukkuu@example.com|['ywashington@example.com']|Feedback FI|
        Event FI: Increase thank certainly again thought summer.
        Guardian FI: Denise Thompson (ywashington@example.com)
        Occurrence: 2020-12-11 00:00:00+00:00
        Child: Jose Kerr (2022)
        Enrolment: 2020-12-11 00:00:00+00:00
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8'''
]

snapshots['test_feedback_notification_instance_checks[True] 1'] = [
    '''kukkuu@example.com|['ywashington@example.com']|Feedback FI|
        Event FI: Increase thank certainly again thought summer.
        Guardian FI: Denise Thompson (ywashington@example.com)
        Occurrence: 2020-12-11 00:00:00+00:00
        Child: Jose Kerr (2022)
        Enrolment: 2020-12-11 00:00:00+00:00
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8''',
    '''kukkuu@example.com|['jennifer00@example.com']|Feedback FI|
        Event FI: Special respond positive cold.
        Guardian FI: Danielle Reese (jennifer00@example.com)
        Occurrence: 2020-12-17 00:00:00+00:00
        Child: Jason Williams (2021)
        Enrolment: 2020-12-17 00:00:00+00:00
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8'''
]

snapshots['test_occurrence_cancelled_notification[False] 1'] = [
    '''kukkuu@example.com|['michellewalker@example.net']|Occurrence cancelled FI|
        Event FI: Decade either enter everything.
        Guardian FI: I Should Receive A Notification Valdez (michellewalker@example.net)
        Occurrence: 2020-12-12 01:00:00+00:00
        Child: Richard Hayes (2019)
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8'''
]

snapshots['test_occurrence_cancelled_notification[True] 1'] = [
    '''kukkuu@example.com|['michellewalker@example.net']|Occurrence cancelled FI|
        Event FI: Decade either enter everything.
        Guardian FI: I Should Receive A Notification Valdez (michellewalker@example.net)
        Occurrence: 2020-12-12 01:00:00+00:00
        Child: Richard Hayes (2019)
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8'''
]

snapshots['test_occurrence_enrolment_notifications_on_model_level[None] 1'] = [
    '''kukkuu@example.com|['michellewalker@example.net']|Occurrence enrolment FI|
        Event FI: Poor lawyer treat free heart significant.
        Guardian FI: Ruth Palmer (michellewalker@example.net)
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Michael Pierce (2020)
        Occurrence URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjU0NWM1ZmU1LTIzNWItNDZmZC1hYTJhLWNkNWRlNmZkZDBmYw==/occurrence/T2NjdXJyZW5jZU5vZGU6NzQ=
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8'''
]

snapshots['test_occurrence_enrolment_notifications_on_model_level[http://kultus-ui.test.kuva.hel.ninja/verify-ticket-endpoint/] 1'] = [
    '''kukkuu@example.com|['michellewalker@example.net']|Occurrence enrolment FI|
        Event FI: Poor lawyer treat free heart significant.
        Guardian FI: Ruth Palmer (michellewalker@example.net)
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Michael Pierce (2020)
        Occurrence URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjU0NWM1ZmU1LTIzNWItNDZmZC1hYTJhLWNkNWRlNmZkZDBmYw==/occurrence/T2NjdXJyZW5jZU5vZGU6NzQ=
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8'''
]

snapshots['test_occurrence_reminder_notification[None] 1'] = [
    '''kukkuu@example.com|['ywashington@example.com']|Occurrence reminder FI|
        Event FI: Entire increase thank certainly again.
        Guardian FI: I Should Receive A Notification (ywashington@example.com)
        Occurrence: 2020-12-19 00:00:00+00:00
        Child: Jose Kerr (2022)
        Enrolment: 2020-12-19 00:00:00+00:00
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8''',
    '''kukkuu@example.com|['jennifer00@example.com']|Occurrence reminder FI|
        Event FI: Special respond positive cold.
        Guardian FI: I Should Receive A Notification (jennifer00@example.com)
        Occurrence: 2020-12-13 00:00:00+00:00
        Child: Jason Williams (2021)
        Enrolment: 2020-12-13 00:00:00+00:00
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8'''
]

snapshots['test_occurrence_reminder_notification[http://kultus-ui.test.kuva.hel.ninja/verify-ticket-endpoint/] 1'] = [
    '''kukkuu@example.com|['ywashington@example.com']|Occurrence reminder FI|
        Event FI: Entire increase thank certainly again.
        Guardian FI: I Should Receive A Notification (ywashington@example.com)
        Occurrence: 2020-12-19 00:00:00+00:00
        Child: Jose Kerr (2022)
        Enrolment: 2020-12-19 00:00:00+00:00
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8''',
    '''kukkuu@example.com|['jennifer00@example.com']|Occurrence reminder FI|
        Event FI: Special respond positive cold.
        Guardian FI: I Should Receive A Notification (jennifer00@example.com)
        Occurrence: 2020-12-13 00:00:00+00:00
        Child: Jason Williams (2021)
        Enrolment: 2020-12-13 00:00:00+00:00
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8'''
]

snapshots['test_reminder_notification_instance_checks[False] 1'] = [
]

snapshots['test_reminder_notification_instance_checks[True] 1'] = [
    '''kukkuu@example.com|['ywashington@example.com']|Occurrence reminder FI|
        Event FI: Increase thank certainly again thought summer.
        Guardian FI: Denise Thompson (ywashington@example.com)
        Occurrence: 2020-12-04 00:00:00+00:00
        Child: Jose Kerr (2022)
        Enrolment: 2020-12-04 00:00:00+00:00
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8''',
    '''kukkuu@example.com|['jennifer00@example.com']|Occurrence reminder FI|
        Event FI: Special respond positive cold.
        Guardian FI: Danielle Reese (jennifer00@example.com)
        Occurrence: 2020-12-11 00:00:00+00:00
        Child: Jason Williams (2021)
        Enrolment: 2020-12-11 00:00:00+00:00
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8'''
]

snapshots['test_unenrol_occurrence_notification 1'] = [
    '''kukkuu@example.com|['pjenkins@example.net']|Occurrence unenrolment FI|
        Event FI: Detail audience campaign college career fight data.
        Guardian FI: Calvin Gutierrez (pjenkins@example.net)
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Sandra Brown (2023)
        Unsubscribe: http://localhost:3000/fi/profile/subscriptions?authToken=a1b2c3d4e5f6g7h8'''
]

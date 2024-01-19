# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_event_group_publish_notification 1"] = [
    """kukkuu@example.com|['matthewbrooks@example.com']|Event group published FI|
        Event group FI: Beat at success decade either enter everything.
        Guardian FI: Todd Sellers (matthewbrooks@example.com)
        Url: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event-group/RXZlbnRHcm91cE5vZGU6Nzc3
        Events:
            If his their best. Election stay every something base. 2020-12-12 00:00:00+00:00 http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event/RXZlbnROb2RlOjc3Nw==
"""
]

snapshots["test_event_group_republish_notification 1"] = [
    """kukkuu@example.com|['matthewbrooks@example.com']|Event group published FI|
        Event group FI: Beat at success decade either enter everything.
        Guardian FI: Todd Sellers (matthewbrooks@example.com)
        Url: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event-group/RXZlbnRHcm91cE5vZGU6Nzc3
        Events:
            If his their best. Election stay every something base. 2020-12-11 00:00:00+00:00 http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event/RXZlbnROb2RlOjc3Nw==
            Data control as receive. End available avoid girl middle. 2020-12-12 00:00:00+00:00 http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event/RXZlbnROb2RlOjc3OA==
"""
]

snapshots["test_feedback_notification 1"] = [
    """kukkuu@example.com|['matthewbrooks@example.com']|Feedback FI|
        Event FI: Respond draw military dog hospital number.
        Guardian FI: (60, 15) I Should Receive A Notification (matthewbrooks@example.com)
        Occurrence: 2020-12-11 23:00:00+00:00
        Child: Alexis (2020-07-19)
        Enrolment: 2020-12-11 23:00:00+00:00""",
    """kukkuu@example.com|['daniel58@example.com']|Feedback FI|
        Event FI: Mr amount conference thing much like test.
        Guardian FI: (30, 15) I Should Receive A Notification (daniel58@example.com)
        Occurrence: 2020-12-11 23:30:00+00:00
        Child: Calvin (2020-06-09)
        Enrolment: 2020-12-11 23:30:00+00:00""",
    """kukkuu@example.com|['itodd@example.net']|Feedback FI|
        Event FI: Eat design give per kind history ahead.
        Guardian FI: (135, None) I Should Receive A Notification (itodd@example.net)
        Occurrence: 2020-12-11 21:45:00+00:00
        Child: Melissa (2020-08-22)
        Enrolment: 2020-12-11 21:45:00+00:00""",
    """kukkuu@example.com|['melinda81@example.com']|Feedback FI|
        Event FI: Become leave reduce language though sort clearly.
        Guardian FI: (10080, 15) I Should Receive A Notification (melinda81@example.com)
        Occurrence: 2020-12-05 00:00:00+00:00
        Child: Kathleen (2020-04-03)
        Enrolment: 2020-12-05 00:00:00+00:00""",
]

snapshots["test_feedback_notification_instance_checks[False] 1"] = [
    """kukkuu@example.com|['matthewbrooks@example.com']|Feedback FI|
        Event FI: Answer entire increase thank certainly again thought.
        Guardian FI: Todd Sellers (matthewbrooks@example.com)
        Occurrence: 2020-12-11 00:00:00+00:00
        Child: Alexis (2020-07-19)
        Enrolment: 2020-12-11 00:00:00+00:00"""
]

snapshots["test_feedback_notification_instance_checks[True] 1"] = [
    """kukkuu@example.com|['matthewbrooks@example.com']|Feedback FI|
        Event FI: Answer entire increase thank certainly again thought.
        Guardian FI: Todd Sellers (matthewbrooks@example.com)
        Occurrence: 2020-12-11 00:00:00+00:00
        Child: Alexis (2020-07-19)
        Enrolment: 2020-12-11 00:00:00+00:00""",
    """kukkuu@example.com|['daniel58@example.com']|Feedback FI|
        Event FI: Front Mr amount conference thing much like test.
        Guardian FI: Jennifer Nielsen (daniel58@example.com)
        Occurrence: 2020-12-17 00:00:00+00:00
        Child: Calvin (2020-06-09)
        Enrolment: 2020-12-17 00:00:00+00:00""",
]

snapshots["test_occurrence_cancelled_notification[False] 1"] = [
    """kukkuu@example.com|['michellewalker@example.net']|Occurrence cancelled FI|
        Event FI: Our very television beat at success decade.
        Guardian FI: I Should Receive A Notification Washington (michellewalker@example.net)
        Occurrence: 2020-12-12 01:00:00+00:00
        Child: Michael (2020-10-30)"""
]

snapshots["test_occurrence_cancelled_notification[True] 1"] = [
    """kukkuu@example.com|['michellewalker@example.net']|Occurrence cancelled FI|
        Event FI: Our very television beat at success decade.
        Guardian FI: I Should Receive A Notification Washington (michellewalker@example.net)
        Occurrence: 2020-12-12 01:00:00+00:00
        Child: Michael (2020-10-30)"""
]

snapshots["test_occurrence_enrolment_notifications_on_model_level[None] 1"] = [
    """kukkuu@example.com|['michellewalker@example.net']|Occurrence enrolment FI|
        Event FI: Poor lawyer treat free heart significant.
        Guardian FI: Allen Riddle (michellewalker@example.net)
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Andrew (2020-09-21)
        Occurrence URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjU0NWM1ZmU1LTIzNWItNDZmZC1hYTJhLWNkNWRlNmZkZDBmYw==/occurrence/T2NjdXJyZW5jZU5vZGU6NzQ="""
]

snapshots[
    "test_occurrence_enrolment_notifications_on_model_level[http://kultus-ui.test.kuva.hel.ninja/verify-ticket-endpoint/] 1"
] = [
    """kukkuu@example.com|['michellewalker@example.net']|Occurrence enrolment FI|
        Event FI: Poor lawyer treat free heart significant.
        Guardian FI: Allen Riddle (michellewalker@example.net)
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Andrew (2020-09-21)
        Occurrence URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjU0NWM1ZmU1LTIzNWItNDZmZC1hYTJhLWNkNWRlNmZkZDBmYw==/occurrence/T2NjdXJyZW5jZU5vZGU6NzQ="""
]

snapshots["test_occurrence_reminder_notification[None] 1"] = [
    """kukkuu@example.com|['matthewbrooks@example.com']|Occurrence reminder FI|
        Event FI: Respond draw military dog hospital number.
        Guardian FI: I Should Receive A Notification (matthewbrooks@example.com)
        Occurrence: 2020-12-19 00:00:00+00:00
        Child: Alexis (2020-07-19)
        Enrolment: 2020-12-19 00:00:00+00:00""",
    """kukkuu@example.com|['daniel58@example.com']|Occurrence reminder FI|
        Event FI: Mr amount conference thing much like test.
        Guardian FI: I Should Receive A Notification (daniel58@example.com)
        Occurrence: 2020-12-13 00:00:00+00:00
        Child: Calvin (2020-06-09)
        Enrolment: 2020-12-13 00:00:00+00:00""",
]

snapshots[
    "test_occurrence_reminder_notification[http://kultus-ui.test.kuva.hel.ninja/verify-ticket-endpoint/] 1"
] = [
    """kukkuu@example.com|['matthewbrooks@example.com']|Occurrence reminder FI|
        Event FI: Respond draw military dog hospital number.
        Guardian FI: I Should Receive A Notification (matthewbrooks@example.com)
        Occurrence: 2020-12-19 00:00:00+00:00
        Child: Alexis (2020-07-19)
        Enrolment: 2020-12-19 00:00:00+00:00""",
    """kukkuu@example.com|['daniel58@example.com']|Occurrence reminder FI|
        Event FI: Mr amount conference thing much like test.
        Guardian FI: I Should Receive A Notification (daniel58@example.com)
        Occurrence: 2020-12-13 00:00:00+00:00
        Child: Calvin (2020-06-09)
        Enrolment: 2020-12-13 00:00:00+00:00""",
]

snapshots["test_reminder_notification_instance_checks[False] 1"] = []

snapshots["test_reminder_notification_instance_checks[True] 1"] = [
    """kukkuu@example.com|['matthewbrooks@example.com']|Occurrence reminder FI|
        Event FI: Answer entire increase thank certainly again thought.
        Guardian FI: Todd Sellers (matthewbrooks@example.com)
        Occurrence: 2020-12-04 00:00:00+00:00
        Child: Alexis (2020-07-19)
        Enrolment: 2020-12-04 00:00:00+00:00""",
    """kukkuu@example.com|['daniel58@example.com']|Occurrence reminder FI|
        Event FI: Front Mr amount conference thing much like test.
        Guardian FI: Jennifer Nielsen (daniel58@example.com)
        Occurrence: 2020-12-11 00:00:00+00:00
        Child: Calvin (2020-06-09)
        Enrolment: 2020-12-11 00:00:00+00:00""",
]

snapshots["test_unenrol_occurrence_notification 1"] = [
    """kukkuu@example.com|['pjenkins@example.net']|Occurrence unenrolment FI|
        Event FI: Detail audience campaign college career fight data.
        Guardian FI: Michael Ross (pjenkins@example.net)
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Brandy (2020-11-20)"""
]

# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_event_group_publish_notification 1'] = [
    '''kukkuu@example.com|['tonya77@example.com']|Event group published FI|
        Event group FI: Alone our very television beat at success.
        Guardian FI: Samantha Bryant (tonya77@example.com)
        Url: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event-group/RXZlbnRHcm91cE5vZGU6Nzc3
        Events:
            Base may middle good father boy economy. 2020-12-12 00:00:00+00:00 http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event/RXZlbnROb2RlOjc3Nw==
'''
]

snapshots['test_event_group_republish_notification 1'] = [
    '''kukkuu@example.com|['tonya77@example.com']|Event group published FI|
        Event group FI: Alone our very television beat at success.
        Guardian FI: Samantha Bryant (tonya77@example.com)
        Url: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event-group/RXZlbnRHcm91cE5vZGU6Nzc3
        Events:
            Girl middle same space speak. 2020-12-12 00:00:00+00:00 http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event/RXZlbnROb2RlOjc3OA==
            Base may middle good father boy economy. 2020-12-11 00:00:00+00:00 http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjAwMDAwMDAwLTAwMDAtMDAwMC0wMDAwLTAwMDAwMDAwMDMwOQ==/event/RXZlbnROb2RlOjc3Nw==
'''
]

snapshots['test_feedback_notification 1'] = [
    '''kukkuu@example.com|['tonya77@example.com']|Feedback FI|
        Event FI: Answer entire increase thank certainly again thought.
        Guardian FI: (60, 15) I Should Receive A Notification (tonya77@example.com)
        Occurrence: 2020-12-11 23:00:00+00:00
        Child: Alexis Black (2020-07-29)
        Enrolment: 2020-12-11 23:00:00+00:00''',
    '''kukkuu@example.com|['johnsonnathaniel@example.com']|Feedback FI|
        Event FI: Mr amount conference thing much like test.
        Guardian FI: (30, 15) I Should Receive A Notification (johnsonnathaniel@example.com)
        Occurrence: 2020-12-11 23:30:00+00:00
        Child: Calvin Gutierrez (2020-01-18)
        Enrolment: 2020-12-11 23:30:00+00:00''',
    '''kukkuu@example.com|['aaronlee@example.org']|Feedback FI|
        Event FI: History ahead well herself consider fight.
        Guardian FI: (135, None) I Should Receive A Notification (aaronlee@example.org)
        Occurrence: 2020-12-11 21:45:00+00:00
        Child: Melissa Morrison (2020-04-12)
        Enrolment: 2020-12-11 21:45:00+00:00''',
    '''kukkuu@example.com|['christine87@example.com']|Feedback FI|
        Event FI: Sort clearly happy peace really brother.
        Guardian FI: (10080, 15) I Should Receive A Notification (christine87@example.com)
        Occurrence: 2020-12-05 00:00:00+00:00
        Child: Kathleen Allen (2020-01-06)
        Enrolment: 2020-12-05 00:00:00+00:00'''
]

snapshots['test_feedback_notification_instance_checks[False] 1'] = [
    '''kukkuu@example.com|['tonya77@example.com']|Feedback FI|
        Event FI: Respond draw military dog hospital number.
        Guardian FI: Samantha Bryant (tonya77@example.com)
        Occurrence: 2020-12-11 00:00:00+00:00
        Child: Alexis Black (2020-07-29)
        Enrolment: 2020-12-11 00:00:00+00:00'''
]

snapshots['test_feedback_notification_instance_checks[True] 1'] = [
    '''kukkuu@example.com|['tonya77@example.com']|Feedback FI|
        Event FI: Respond draw military dog hospital number.
        Guardian FI: Samantha Bryant (tonya77@example.com)
        Occurrence: 2020-12-11 00:00:00+00:00
        Child: Alexis Black (2020-07-29)
        Enrolment: 2020-12-11 00:00:00+00:00''',
    '''kukkuu@example.com|['johnsonnathaniel@example.com']|Feedback FI|
        Event FI: Front Mr amount conference thing much like test.
        Guardian FI: Jennifer Nielsen (johnsonnathaniel@example.com)
        Occurrence: 2020-12-17 00:00:00+00:00
        Child: Calvin Gutierrez (2020-01-18)
        Enrolment: 2020-12-17 00:00:00+00:00'''
]

snapshots['test_occurrence_cancelled_notification[False] 1'] = [
    '''kukkuu@example.com|['michellewalker@example.net']|Occurrence cancelled FI|
        Event FI: Our very television beat at success decade.
        Guardian FI: I Should Receive A Notification Sellers (michellewalker@example.net)
        Occurrence: 2020-12-12 01:00:00+00:00
        Child: Michael Patton (2020-06-24)'''
]

snapshots['test_occurrence_cancelled_notification[True] 1'] = [
    '''kukkuu@example.com|['michellewalker@example.net']|Occurrence cancelled FI|
        Event FI: Our very television beat at success decade.
        Guardian FI: I Should Receive A Notification Sellers (michellewalker@example.net)
        Occurrence: 2020-12-12 01:00:00+00:00
        Child: Michael Patton (2020-06-24)'''
]

snapshots['test_occurrence_enrolment_notifications_on_model_level[None] 1'] = [
    '''kukkuu@example.com|['michellewalker@example.net']|Occurrence enrolment FI|
        Event FI: Poor lawyer treat free heart significant.
        Guardian FI: Allen Riddle (michellewalker@example.net)
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Andrew Becker (2020-08-01)
        Occurrence URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjU0NWM1ZmU1LTIzNWItNDZmZC1hYTJhLWNkNWRlNmZkZDBmYw==/occurrence/T2NjdXJyZW5jZU5vZGU6NzQ='''
]

snapshots['test_occurrence_enrolment_notifications_on_model_level[http://kultus-ui.test.kuva.hel.ninja/verify-ticket-endpoint/] 1'] = [
    '''kukkuu@example.com|['michellewalker@example.net']|Occurrence enrolment FI|
        Event FI: Poor lawyer treat free heart significant.
        Guardian FI: Allen Riddle (michellewalker@example.net)
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Andrew Becker (2020-08-01)
        Occurrence URL: http://localhost:3000/fi/profile/child/Q2hpbGROb2RlOjU0NWM1ZmU1LTIzNWItNDZmZC1hYTJhLWNkNWRlNmZkZDBmYw==/occurrence/T2NjdXJyZW5jZU5vZGU6NzQ='''
]

snapshots['test_occurrence_reminder_notification[None] 1'] = [
    '''kukkuu@example.com|['tonya77@example.com']|Occurrence reminder FI|
        Event FI: Answer entire increase thank certainly again thought.
        Guardian FI: I Should Receive A Notification (tonya77@example.com)
        Occurrence: 2020-12-19 00:00:00+00:00
        Child: Alexis Black (2020-07-29)
        Enrolment: 2020-12-19 00:00:00+00:00''',
    '''kukkuu@example.com|['johnsonnathaniel@example.com']|Occurrence reminder FI|
        Event FI: Mr amount conference thing much like test.
        Guardian FI: I Should Receive A Notification (johnsonnathaniel@example.com)
        Occurrence: 2020-12-13 00:00:00+00:00
        Child: Calvin Gutierrez (2020-01-18)
        Enrolment: 2020-12-13 00:00:00+00:00'''
]

snapshots['test_occurrence_reminder_notification[http://kultus-ui.test.kuva.hel.ninja/verify-ticket-endpoint/] 1'] = [
    '''kukkuu@example.com|['tonya77@example.com']|Occurrence reminder FI|
        Event FI: Answer entire increase thank certainly again thought.
        Guardian FI: I Should Receive A Notification (tonya77@example.com)
        Occurrence: 2020-12-19 00:00:00+00:00
        Child: Alexis Black (2020-07-29)
        Enrolment: 2020-12-19 00:00:00+00:00''',
    '''kukkuu@example.com|['johnsonnathaniel@example.com']|Occurrence reminder FI|
        Event FI: Mr amount conference thing much like test.
        Guardian FI: I Should Receive A Notification (johnsonnathaniel@example.com)
        Occurrence: 2020-12-13 00:00:00+00:00
        Child: Calvin Gutierrez (2020-01-18)
        Enrolment: 2020-12-13 00:00:00+00:00'''
]

snapshots['test_reminder_notification_instance_checks[False] 1'] = [
]

snapshots['test_reminder_notification_instance_checks[True] 1'] = [
    '''kukkuu@example.com|['tonya77@example.com']|Occurrence reminder FI|
        Event FI: Respond draw military dog hospital number.
        Guardian FI: Samantha Bryant (tonya77@example.com)
        Occurrence: 2020-12-04 00:00:00+00:00
        Child: Alexis Black (2020-07-29)
        Enrolment: 2020-12-04 00:00:00+00:00''',
    '''kukkuu@example.com|['johnsonnathaniel@example.com']|Occurrence reminder FI|
        Event FI: Front Mr amount conference thing much like test.
        Guardian FI: Jennifer Nielsen (johnsonnathaniel@example.com)
        Occurrence: 2020-12-11 00:00:00+00:00
        Child: Calvin Gutierrez (2020-01-18)
        Enrolment: 2020-12-11 00:00:00+00:00'''
]

snapshots['test_unenrol_occurrence_notification 1'] = [
    '''kukkuu@example.com|['pjenkins@example.net']|Occurrence unenrolment FI|
        Event FI: Detail audience campaign college career fight data.
        Guardian FI: Kari Wolf (pjenkins@example.net)
        Occurrence: 2020-12-12 00:00:00+00:00
        Child: Brandy Flowers (2020-01-25)'''
]

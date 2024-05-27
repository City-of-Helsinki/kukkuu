import threading
from copy import deepcopy
from datetime import timedelta
from unittest import mock

import pytest
from django.core import mail
from django.core.management import call_command
from django.db import Error
from django.utils.timezone import now
from freezegun import freeze_time
from graphql_relay import to_global_id

from children.factories import ChildWithGuardianFactory
from common.tests.utils import (
    assert_mails_match_snapshot,
    create_notification_template_in_language,
)
from common.utils import get_global_id
from events.factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    OccurrenceFactory,
)
from events.models import Enrolment, Occurrence
from events.notifications import NotificationType
from events.tests.mutations import PUBLISH_EVENT_MUTATION, UNENROL_OCCURRENCE_MUTATION
from events.tests.test_api import PUBLISH_EVENT_VARIABLES
from projects.factories import ProjectFactory
from users.factories import GuardianFactory


def _wait_until_thread_terminates(thread_name: str, ignore_errors=False):
    # The notifications are sent in another thread
    # and the mailer outbox is not seeable here.
    try:
        event_notification_sender_thread = next(
            (thread for thread in threading.enumerate() if thread.name == thread_name),
        )
        event_notification_sender_thread.join()
    except StopIteration:
        if not ignore_errors:
            raise


@pytest.fixture(autouse=True)
def setup(settings):
    settings.KUKKUU_FEEDBACK_NOTIFICATION_DELAY = 15


@pytest.fixture
def notification_template_event_published_fi():
    return create_notification_template_in_language(
        NotificationType.EVENT_PUBLISHED,
        "fi",
        subject="Event published FI",
        body_text="""
        Event FI: {{ event.name }}
        Guardian FI: {{ guardian }}
        Event URL: {{ event_url }}
        Unsubscribe: {{unsubscribe_url}}
        Obsoleted: {{is_obsolete}}
""",
    )


@pytest.fixture
def notification_template_event_group_published_fi():
    return create_notification_template_in_language(
        NotificationType.EVENT_GROUP_PUBLISHED,
        "fi",
        subject="Event group published FI",
        body_text="""
        Event group FI: {{ event_group.name }}
        Guardian FI: {{ guardian }}
        Url: {{ event_group_url }}
        Events:
        {% for event in events %}
            {{ event.obj.name}} {{ event.obj.published_at }} {{ event.event_url }}
        {% endfor %}
        Unsubscribe: {{unsubscribe_url}}
        Obsoleted: {{is_obsolete}}
""",
    )


@pytest.fixture
def notification_template_occurrence_enrolment_fi():
    return create_notification_template_in_language(
        NotificationType.OCCURRENCE_ENROLMENT,
        "fi",
        subject="Occurrence enrolment FI",
        body_text="""
        Event FI: {{ occurrence.event.name }}
        Guardian FI: {{ guardian }}
        Occurrence: {{ occurrence.time }}
        Child: {{ child }}
        Occurrence URL: {{ occurrence_url }}
        Unsubscribe: {{unsubscribe_url}}
        Obsoleted: {{is_obsolete}}
""",
    )


@pytest.fixture
def notification_template_occurrence_unenrolment_fi():
    return create_notification_template_in_language(
        NotificationType.OCCURRENCE_UNENROLMENT,
        "fi",
        subject="Occurrence unenrolment FI",
        body_text="""
        Event FI: {{ occurrence.event.name }}
        Guardian FI: {{ guardian }}
        Occurrence: {{ occurrence.time }}
        Child: {{ child }}
        Unsubscribe: {{unsubscribe_url}}
        Obsoleted: {{is_obsolete}}
""",
    )


@pytest.fixture
def notification_template_occurrence_cancelled_fi():
    return create_notification_template_in_language(
        NotificationType.OCCURRENCE_CANCELLED,
        "fi",
        subject="Occurrence cancelled FI",
        body_text="""
        Event FI: {{ occurrence.event.name }}
        Guardian FI: {{ guardian }}
        Occurrence: {{ occurrence.time }}
        Child: {{ child }}
        Unsubscribe: {{unsubscribe_url}}
        Obsoleted: {{is_obsolete}}
""",
    )


@pytest.fixture
def notification_template_occurrence_reminder_fi():
    return create_notification_template_in_language(
        NotificationType.OCCURRENCE_REMINDER,
        "fi",
        subject="Occurrence reminder FI",
        body_text="""
        Event FI: {{ occurrence.event.name }}
        Guardian FI: {{ guardian }}
        Occurrence: {{ occurrence.time }}
        Child: {{ child }}
        Enrolment: {{ enrolment.occurrence.time }}
        Unsubscribe: {{unsubscribe_url}}
        Obsoleted: {{is_obsolete}}
""",
    )


@pytest.fixture
def notification_template_occurrence_feedback_fi():
    return create_notification_template_in_language(
        NotificationType.OCCURRENCE_FEEDBACK,
        "fi",
        subject="Feedback FI",
        body_text="""
        Event FI: {{ occurrence.event.name }}
        Guardian FI: {{ guardian }}
        Occurrence: {{ occurrence.time }}
        Child: {{ child }}
        Enrolment: {{ enrolment.occurrence.time }}
        Unsubscribe: {{unsubscribe_url}}
        Obsoleted: {{is_obsolete}}
""",
    )


@pytest.mark.django_db(transaction=True)  # transaction=True for threading
def test_event_publish_notification(
    snapshot,
    publisher_api_client,
    notification_template_event_published_fi,
    unpublished_event,
    project,
    another_project,
    mock_user_create_subscriptions_management_auth_token,
):
    GuardianFactory(language="fi", has_accepted_communication=True)
    children = ChildWithGuardianFactory.create_batch(
        3, project=project, relationship__guardian__has_accepted_communication=True
    )
    children[1].guardians.set(
        GuardianFactory.create_batch(3, language="fi", has_accepted_communication=True)
    )
    # children in another project
    ChildWithGuardianFactory.create_batch(
        2,
        project=another_project,
        relationship__guardian__has_accepted_communication=True,
    )
    # Children whose guardians have not accepted communication
    ChildWithGuardianFactory.create_batch(
        10,
        project=project,
        relationship__guardian__has_accepted_communication=False,
    )

    event_variables = deepcopy(PUBLISH_EVENT_VARIABLES)
    event_variables["input"]["id"] = to_global_id("EventNode", unpublished_event.id)

    publisher_api_client.execute(PUBLISH_EVENT_MUTATION, variables=event_variables)

    _wait_until_thread_terminates("event-notification-sender")

    assert len(mail.outbox) == 5  # 3 children of which one has 3 guardians


@pytest.mark.django_db(transaction=True)  # transaction=True for threading
def test_event_publish_notification_not_sent_when_publication_fails(
    snapshot,
    publisher_api_client,
    notification_template_event_published_fi,
    mock_user_create_subscriptions_management_auth_token,
    unpublished_event,
    project,
):
    GuardianFactory(language="fi", has_accepted_communication=True)
    children = ChildWithGuardianFactory.create_batch(3, project=project)
    children[1].guardians.set(
        GuardianFactory.create_batch(3, language="fi", has_accepted_communication=True)
    )
    ChildWithGuardianFactory.create_batch(2, project=ProjectFactory(year=2019))

    event_variables = deepcopy(PUBLISH_EVENT_VARIABLES)
    event_variables["input"]["id"] = to_global_id("EventNode", unpublished_event.id)

    with mock.patch(
        "events.models.Event.save",
        side_effect=Error("Some error occured"),
    ):
        publisher_api_client.execute(PUBLISH_EVENT_MUTATION, variables=event_variables)

        # Even if it would try to send,
        # then the notification sender thread needs to be joined.
        _wait_until_thread_terminates(
            "eventgroup-notification-sender", ignore_errors=True
        )

        # No mails sent because publication failed
        assert len(mail.outbox) == 0


@pytest.mark.django_db(transaction=True)  # transaction=True for threading
def test_event_group_publish_notification(
    snapshot,
    notification_template_event_published_fi,
    notification_template_event_group_published_fi,
    mock_user_create_subscriptions_management_auth_token,
    project,
    another_project,
):
    ChildWithGuardianFactory(
        id=777, project=project, relationship__guardian__has_accepted_communication=True
    )
    ChildWithGuardianFactory(
        project=project,
        relationship__guardian__has_accepted_communication=False,
    )
    ChildWithGuardianFactory(
        project=another_project, relationship__guardian__has_accepted_communication=True
    )
    event = EventFactory(id=777, event_group=EventGroupFactory(id=777))

    event.event_group.publish()

    _wait_until_thread_terminates("eventgroup-notification-sender")

    assert len(mail.outbox) == 1
    assert_mails_match_snapshot(snapshot)


@pytest.mark.django_db(transaction=True)  # transaction=True for threading
def test_event_group_republish_notification(
    snapshot,
    notification_template_event_published_fi,
    notification_template_event_group_published_fi,
    mock_user_create_subscriptions_management_auth_token,
    project,
    another_project,
    past,
):
    ChildWithGuardianFactory(
        id=777, project=project, relationship__guardian__has_accepted_communication=True
    )
    ChildWithGuardianFactory(
        project=another_project, relationship__guardian__has_accepted_communication=True
    )
    event_group = EventGroupFactory(id=777, published_at=past)
    EventFactory(
        id=777,
        event_group=event_group,
        ready_for_event_group_publishing=True,
        published_at=past,
    )
    EventFactory(
        id=778,
        event_group=event_group,
        ready_for_event_group_publishing=True,
    )

    event_group.publish()

    _wait_until_thread_terminates("eventgroup-notification-sender")
    assert len(mail.outbox) == 1
    assert_mails_match_snapshot(snapshot)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "ticket_verification_url_setting",
    [None, "http://kultus-ui.test.kuva.hel.ninja/verify-ticket-endpoint/"],
)
def test_occurrence_enrolment_notifications_on_model_level(
    ticket_verification_url_setting,
    settings,
    snapshot,
    user_api_client,
    notification_template_occurrence_unenrolment_fi,
    notification_template_occurrence_enrolment_fi,
    mock_user_create_subscriptions_management_auth_token,
    project,
):
    settings.KUKKUU_TICKET_VERIFICATION_URL = ticket_verification_url_setting
    occurrence = OccurrenceFactory(id=74, time=now())
    child = ChildWithGuardianFactory(
        pk="545c5fe5-235b-46fd-aa2a-cd5de6fdd0fc",
        relationship__guardian__user=user_api_client.user,
        project=project,
    )
    enrolment = Enrolment.objects.create(child=child, occurrence=occurrence)
    # unenrolling on model level should NOT trigger a notification
    occurrence.children.remove(child)
    assert len(mail.outbox) == 1
    if ticket_verification_url_setting:
        # qrcode should be attached
        assert len(mail.outbox[0].attachments) == 1
        # verify the name of the file
        assert (
            mail.outbox[0].attachments[0][0] == "KuKu-ticket-"
            f"{str(enrolment.occurrence.time.date())}-{enrolment.reference_id}.png"
        )
    else:
        assert len(mail.outbox[0].attachments) == 0
    assert_mails_match_snapshot(snapshot)


@pytest.mark.django_db
def test_unenrol_occurrence_notification(
    guardian_api_client,
    snapshot,
    project,
    occurrence,
    notification_template_occurrence_unenrolment_fi,
    mock_user_create_subscriptions_management_auth_token,
):
    child = ChildWithGuardianFactory(
        relationship__guardian__user=guardian_api_client.user,
        project=project,
    )
    EnrolmentFactory(occurrence=occurrence, child=child)
    unenrolment_variables = {
        "input": {
            "occurrenceId": get_global_id(occurrence),
            "childId": get_global_id(child),
        },
    }

    guardian_api_client.execute(
        UNENROL_OCCURRENCE_MUTATION, variables=unenrolment_variables
    )

    assert len(mail.outbox) == 1
    assert_mails_match_snapshot(snapshot)


@pytest.mark.django_db
@pytest.mark.parametrize("is_queryset", (True, False))
def test_occurrence_cancelled_notification(
    snapshot,
    user_api_client,
    notification_template_occurrence_cancelled_fi,
    mock_user_create_subscriptions_management_auth_token,
    project,
    is_queryset,
):
    child = ChildWithGuardianFactory(
        relationship__guardian__user=user_api_client.user,
        relationship__guardian__first_name="I Should Receive A Notification",
        project=project,
    )
    other_child = ChildWithGuardianFactory(
        relationship__guardian__first_name="I Should NOT Receive A Notification",
        project=project,
    )

    occurrence = OccurrenceFactory(
        time=now() + timedelta(hours=1), event__project=project
    )
    past_occurrence = OccurrenceFactory(
        time=now() - timedelta(hours=1), event=occurrence.event
    )
    other_event_occurrence = OccurrenceFactory(
        time=now() + timedelta(hours=1), event__project=project
    )

    Enrolment.objects.create(child=child, occurrence=occurrence)
    Enrolment.objects.create(child=child, occurrence=past_occurrence)
    Enrolment.objects.create(child=other_child, occurrence=other_event_occurrence)

    if is_queryset:
        Occurrence.objects.filter(id=occurrence.id).delete()
    else:
        occurrence.delete()

    assert len(mail.outbox) == 1
    assert_mails_match_snapshot(snapshot)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "ticket_verification_url_setting",
    [None, "http://kultus-ui.test.kuva.hel.ninja/verify-ticket-endpoint/"],
)
def test_occurrence_reminder_notification(
    ticket_verification_url_setting,
    settings,
    snapshot,
    notification_template_occurrence_reminder_fi,
    mock_user_create_subscriptions_management_auth_token,
    project,
):
    settings.KUKKUU_TICKET_VERIFICATION_URL = ticket_verification_url_setting
    actual_now = now()
    notifiable_enrolments = []

    # time frozen so that the Enrolments will get created_at in the past
    with freeze_time(actual_now - timedelta(days=8)):
        # occurrences 7 and 1 days away (and reminder not sent already),
        # both should create a reminder notification
        for delta in (timedelta(days=7), timedelta(days=1)):
            child = ChildWithGuardianFactory(
                relationship__guardian__first_name="I Should",
                relationship__guardian__last_name="Receive A Notification",
                project=project,
            )
            notifiable_enrolments.append(
                EnrolmentFactory(
                    child=child,
                    occurrence__time=actual_now + delta,
                    occurrence__event__project=project,
                )
            )

        # these should not create a reminder notification
        for delta in (
            timedelta(days=8),  # too far in the future
            timedelta(hours=12),  # too close
            timedelta(days=-1),  # in the past
        ):
            child = ChildWithGuardianFactory(
                relationship__guardian__first_name="I Should NOT",
                relationship__guardian__last_name="Receive A Notification",
                project=project,
            )
            EnrolmentFactory(
                child=child,
                occurrence__time=actual_now + delta,
                occurrence__event__project=project,
            )

    # otherwise a fine reminder creator but the Enrolment hasn't been created enough in
    # the past
    child = ChildWithGuardianFactory(
        relationship__guardian__first_name="I Should NOT",
        relationship__guardian__last_name="Receive A Notification",
        project=project,
    )
    EnrolmentFactory(
        child=child,
        occurrence__time=actual_now + timedelta(days=7),
        occurrence__event__project=project,
    )

    call_command("send_reminder_notifications")

    assert len(mail.outbox) == 2
    # Test the mail QR-code-ticket attachment
    if ticket_verification_url_setting:
        for index, enrolment in enumerate(notifiable_enrolments):
            # qrcode should be attached
            assert len(mail.outbox[index].attachments) == 1
            # verify the name of the file
            assert (
                mail.outbox[index].attachments[0][0] == "KuKu-ticket-"
                f"{str(enrolment.occurrence.time.date())}-{enrolment.reference_id}.png"
            )
    else:
        assert len(mail.outbox[0].attachments) == 0

    assert_mails_match_snapshot(snapshot)

    enrolments = Enrolment.objects.order_by("id")
    assert all(e.reminder_sent_at == now() for e in enrolments[0:2])
    assert all(e.reminder_sent_at is None for e in enrolments[2:6])

    # second call should not change anything
    call_command("send_reminder_notifications")

    assert len(mail.outbox) == 2
    enrolments = Enrolment.objects.order_by("id")
    assert all(e.reminder_sent_at == now() for e in enrolments[0:2])
    assert all(e.reminder_sent_at is None for e in enrolments[2:6])


@pytest.mark.django_db
@pytest.mark.parametrize("force", (False, True))
def test_feedback_notification_instance_checks(
    snapshot,
    notification_template_occurrence_feedback_fi,
    mock_user_create_subscriptions_management_auth_token,
    force,
):
    enrolment_already_in_past = EnrolmentFactory(
        occurrence__time=now() - timedelta(days=1), child=ChildWithGuardianFactory()
    )
    already_sent_enrolment = EnrolmentFactory(
        occurrence__time=now() + timedelta(days=5),
        feedback_notification_sent_at=now(),
        child=ChildWithGuardianFactory(),
    )

    enrolment_already_in_past.send_feedback_notification(force)
    already_sent_enrolment.send_feedback_notification(force)

    assert_mails_match_snapshot(snapshot)


@pytest.mark.django_db
def test_feedback_notification(
    snapshot,
    notification_template_occurrence_feedback_fi,
    mock_user_create_subscriptions_management_auth_token,
):
    seven_days_in_minutes = 60 * 24 * 7

    suitable_start_time_deltas_and_durations = [
        (60, 15),  # occurrence started 60min ago, duration 15min
        (30, 15),  # ended 15min ago, should be the last suitable (delay is 15min)
        (135, None),  # should be the last suitable for the default duration 120min
        (seven_days_in_minutes, 15),  # the last minute that is not too old
    ]
    suitable_enrolments = [
        EnrolmentFactory(
            child=ChildWithGuardianFactory(
                relationship__guardian__first_name=f"{d[0], d[1]}",
                relationship__guardian__last_name="I Should Receive A Notification",
            ),
            occurrence__time=now() - timedelta(minutes=d[0]),
            occurrence__event__duration=d[1],
        )
        for d in suitable_start_time_deltas_and_durations
    ]

    not_suitable_start_time_deltas_and_durations = [
        (-60, 15),  # occurrence starts in 60min
        (-5, 15),
        (29, 15),  # should be the first not suitable (delay is 15min)
        (134, None),  # should be the first not suitable for the default duration 120min
        (seven_days_in_minutes + 1, 15),  # the first minute that is too old
    ]
    not_suitable_enrolments = [
        EnrolmentFactory(
            child=ChildWithGuardianFactory(
                relationship__guardian__first_name=f"{d[0], d[1]}",
                relationship__guardian__last_name="I Should NOT Receive A Notification",
            ),
            occurrence__time=now() - timedelta(minutes=d[0]),
            occurrence__event__duration=d[1],
        )
        for d in not_suitable_start_time_deltas_and_durations
    ]

    call_command("send_feedback_notifications")

    assert_mails_match_snapshot(snapshot)

    for enrolment in suitable_enrolments:
        enrolment.refresh_from_db()
        assert enrolment.feedback_notification_sent_at == now()

    for enrolment in not_suitable_enrolments:
        enrolment.refresh_from_db()
        assert enrolment.feedback_notification_sent_at is None


@pytest.mark.django_db
@pytest.mark.parametrize("force", (False, True))
def test_reminder_notification_instance_checks(
    snapshot,
    notification_template_occurrence_reminder_fi,
    mock_user_create_subscriptions_management_auth_token,
    force,
):
    too_old_enrolment = EnrolmentFactory(
        occurrence__time=now() - timedelta(days=8), child=ChildWithGuardianFactory()
    )
    already_sent_enrolment = EnrolmentFactory(
        occurrence__time=now() - timedelta(days=1),
        feedback_notification_sent_at=now(),
        child=ChildWithGuardianFactory(),
    )

    too_old_enrolment.send_reminder_notification(force)
    already_sent_enrolment.send_reminder_notification(force)

    assert_mails_match_snapshot(snapshot)

from datetime import timedelta

import pytest
from django.core import mail
from django.utils import timezone
from django.utils.timezone import now
from freezegun import freeze_time

from children.factories import ChildWithGuardianFactory
from common.tests.utils import assert_mails_match_snapshot
from events.factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    OccurrenceFactory,
)
from messaging.factories import MessageFactory
from messaging.models import AlreadySentError, Message
from projects.factories import ProjectFactory
from subscriptions.factories import FreeSpotNotificationSubscriptionFactory


@pytest.mark.parametrize("guardian_language", ("fi", "en"))
def test_message_sending(snapshot, guardian_language, message):
    ChildWithGuardianFactory(
        relationship__guardian__email="johndoe@example.com",
        relationship__guardian__language=guardian_language,
    )

    message.send()

    assert_mails_match_snapshot(snapshot)
    assert message.recipient_count == 1
    assert message.sent_at


def test_cannot_send_message_again_without_force(snapshot, message):
    message.sent_at = now()
    message.save(update_fields=("sent_at",))
    ChildWithGuardianFactory(relationship__guardian__email="johndoe@example.com")

    with pytest.raises(AlreadySentError):
        message.send()

    assert len(mail.outbox) == 0

    message.send(force=True)

    assert_mails_match_snapshot(snapshot)
    assert message.recipient_count == 1
    assert message.sent_at


@freeze_time("2020-11-11")
@pytest.mark.parametrize(
    "recipient_selection",
    (
        Message.ALL,
        Message.INVITED,
        Message.ATTENDED,
        Message.ENROLLED,
        Message.SUBSCRIBED_TO_FREE_SPOT_NOTIFICATION,
    ),
)
@pytest.mark.parametrize(
    "event_selection",
    (
        "no_event_or_occurrence",
        "event",
        "occurrence_tomorrow_1",
        "occurrence_yesterday_1",
    ),
)
def test_message_sending_with_filters(snapshot, recipient_selection, event_selection):
    """Ridiculously complex filtering test

    There are three events:
        * event with 4 occurrences (2 in the past and 2 in the future):
            * tomorrow_1 with 1 enrolled child and 1 subscribed child
            * yesterday_1 with 1 attended child
            * tomorrow_2
            * yesterday_2
        * another event with 1 occurrence with 1 enrolled child and 1 subscribed child
        * event from another project with 1 enrolled child

    With those we test all the combinations of recipient_selection and
    event/occurrences selection.
    """
    yesterday = timezone.now() - timedelta(days=1)
    tomorrow = timezone.now() + timedelta(days=1)

    event = EventFactory(published_at=timezone.now())

    occurrence_tomorrow_1 = OccurrenceFactory(event=event, time=tomorrow)
    occurrence_yesterday_1 = OccurrenceFactory(event=event, time=yesterday)

    child_enrolled_tomorrow_1 = ChildWithGuardianFactory(
        relationship__guardian__email="enrolled-occurrence-tomorrow-1@example.com",
    )
    child_attended_yesterday_1 = ChildWithGuardianFactory(
        relationship__guardian__email="attended-occurrence-yesterday-1@example.com",
    )
    EnrolmentFactory(occurrence=occurrence_tomorrow_1, child=child_enrolled_tomorrow_1)
    EnrolmentFactory(
        occurrence=occurrence_yesterday_1,
        child=child_attended_yesterday_1,
        attended=True,
    )

    occurrence_tomorrow_2 = OccurrenceFactory(event=event, time=tomorrow)
    occurrence_yesterday_2 = OccurrenceFactory(event=event, time=yesterday)

    child_enrolled_tomorrow_2 = ChildWithGuardianFactory(
        relationship__guardian__email="enrolled-occurrence-tomorrow-2@example.com",
    )
    child_attended_yesterday_2 = ChildWithGuardianFactory(
        relationship__guardian__email="attended-occurrence-yesterday-2@example.com",
    )
    EnrolmentFactory(occurrence=occurrence_tomorrow_2, child=child_enrolled_tomorrow_2)
    EnrolmentFactory(
        occurrence=occurrence_yesterday_2,
        child=child_attended_yesterday_2,
        attended=True,
    )

    child_subscribed_tomorrow_1 = ChildWithGuardianFactory(
        relationship__guardian__email="subscribed-occurrence-tomorrow-1@example.com",
    )
    FreeSpotNotificationSubscriptionFactory(
        child=child_subscribed_tomorrow_1,
        occurrence=occurrence_tomorrow_1,
    )
    child_subscribed_tomorrow_2 = ChildWithGuardianFactory(
        relationship__guardian__email="subscribed-occurrence-tomorrow-2@example.com",
    )
    FreeSpotNotificationSubscriptionFactory(
        child=child_subscribed_tomorrow_2,
        occurrence=occurrence_tomorrow_2,
    )

    another_event = EventFactory(published_at=timezone.now())

    another_event_occurrence_tomorrow = OccurrenceFactory(
        event=another_event, time=tomorrow
    )
    another_event_occurrence_yesterday = OccurrenceFactory(
        event=another_event, time=yesterday
    )

    child_enrolled_another_event = ChildWithGuardianFactory(
        relationship__guardian__email="enrolled-another-event@example.com",
    )
    child_attended_another_event = ChildWithGuardianFactory(
        relationship__guardian__email="attended-another-event@example.com",
    )
    EnrolmentFactory(
        occurrence=another_event_occurrence_tomorrow, child=child_enrolled_another_event
    )
    EnrolmentFactory(
        occurrence=another_event_occurrence_yesterday,
        child=child_attended_another_event,
        attended=True,
    )

    child_subscribed_another_event = ChildWithGuardianFactory(
        relationship__guardian__email="subscribed-another-event@example.com",
    )
    FreeSpotNotificationSubscriptionFactory(
        child=child_subscribed_another_event,
        occurrence=another_event_occurrence_tomorrow,
    )

    child_both_events = ChildWithGuardianFactory(
        relationship__guardian__email="enrolled-both-events@example.com",
    )  # this child should have no invitations
    EnrolmentFactory(
        child=child_both_events,
        occurrence=another_event_occurrence_tomorrow,
    )
    EnrolmentFactory(
        child=child_both_events,
        occurrence=occurrence_tomorrow_1,
    )

    ChildWithGuardianFactory(
        project=ProjectFactory(year=3000),
        relationship__guardian__email="another-project@example.com",
    )

    message = MessageFactory(recipient_selection=recipient_selection)

    if event_selection == "event":
        message.event = event
        message.save()
    elif event_selection == "occurrence_tomorrow_1":
        message.event = event
        message.occurrences.set([occurrence_tomorrow_1])
    elif event_selection == "occurrence_yesterday_1":
        message.event = event
        message.occurrences.set([occurrence_yesterday_1])

    message.send()

    snapshot.assert_match(sorted(m.to for m in mail.outbox))
    assert message.recipient_count == len(mail.outbox)
    assert message.sent_at


@freeze_time("2020-11-11")
@pytest.mark.parametrize("upcoming_occurrence", (True, False))
def test_message_sending_to_invited_group_and_event_groups(upcoming_occurrence):
    """Sending message to invited group when an event group has to be considered.

    Event group consists of two events, with one occurrence each:
        * event 1
            * tomorrow with 1 enrolled child
            * yesterday with 1 attended child
        * event 2
            * yesterday with 1 attended child
    """
    yesterday = timezone.now() - timedelta(days=1)
    tomorrow = timezone.now() + timedelta(days=1)

    event_group = EventGroupFactory(published_at=timezone.now())
    event_1 = EventFactory(event_group=event_group, published_at=timezone.now())
    event_2 = EventFactory(event_group=event_group, published_at=timezone.now())

    occurrence_yesterday_1 = OccurrenceFactory(event=event_1, time=yesterday)
    occurrence_yesterday_2 = OccurrenceFactory(event=event_2, time=yesterday)

    child_attended_yesterday_1 = ChildWithGuardianFactory(
        relationship__guardian__email="attended-occurrence-yesterday-1@example.com",
    )
    child_attended_yesterday_2 = ChildWithGuardianFactory(
        relationship__guardian__email="attended-occurrence-yesterday-2@example.com",
    )

    EnrolmentFactory(
        occurrence=occurrence_yesterday_1,
        child=child_attended_yesterday_1,
        attended=True,
    )
    EnrolmentFactory(
        occurrence=occurrence_yesterday_2,
        child=child_attended_yesterday_2,
        attended=True,
    )

    if upcoming_occurrence:
        occurrence_tomorrow = OccurrenceFactory(event=event_1, time=tomorrow)

        child_enrolled_tomorrow = ChildWithGuardianFactory(
            relationship__guardian__email="enrolled-occurrence-tomorrow@example.com",
        )
        EnrolmentFactory(occurrence=occurrence_tomorrow, child=child_enrolled_tomorrow)

    # Child hasn't attended any events in the event group.
    ChildWithGuardianFactory(
        relationship__guardian__email="should-receive-mail@example.com",
    )

    message = MessageFactory(recipient_selection=Message.INVITED)

    message.send()

    emails = sorted(m.to for m in mail.outbox)

    if upcoming_occurrence:
        assert emails == [["should-receive-mail@example.com"]]
    else:
        assert emails == []
    assert message.recipient_count == len(mail.outbox)
    assert message.sent_at


@freeze_time("2020-11-11")
@pytest.mark.parametrize(
    "enrolled_amount,should_send", [(0, True), (1, True), (2, False), (3, False)]
)
def test_message_sending_to_invited_with_enrolment_limit(
    child_with_user_guardian, enrolled_amount, should_send
):
    """Child who has already enrolled to exactly or more events this year than what is
    allowed by the project's yearly enrolment limit, should not receive an email.
    """
    yesterday = timezone.now() - timedelta(days=1)
    tomorrow = timezone.now() + timedelta(days=1)
    expected_email = child_with_user_guardian.relationships.first().guardian.email

    occurrences = OccurrenceFactory.create_batch(
        enrolled_amount, time=yesterday, event__published_at=yesterday
    )
    for i in range(enrolled_amount):
        EnrolmentFactory(
            child=child_with_user_guardian, occurrence=occurrences[i], attended=True
        )

    # Should receive a message regarding this event (occurrence)
    OccurrenceFactory.create(time=tomorrow, event__published_at=timezone.now())

    message = MessageFactory(recipient_selection=Message.INVITED)

    message.send()

    emails = sorted(m.to for m in mail.outbox)

    if should_send:
        assert emails == [[expected_email]]
    else:
        assert emails == []
    assert message.recipient_count == len(mail.outbox)
    assert message.sent_at

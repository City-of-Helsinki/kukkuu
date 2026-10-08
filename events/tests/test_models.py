from datetime import timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from children.factories import ChildFactory
from kukkuu.consts import DATA_VALIDATION_ERROR, EVENT_GROUP_ALREADY_PUBLISHED_ERROR
from projects.factories import ProjectFactory
from projects.models import Project
from venues.models import Venue

from ..enums import EnrolmentDeniedReason
from ..factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    LippupisteEventFactory,
    OccurrenceFactory,
    TicketmasterEventFactory,
    TicketSystemPasswordFactory,
    TixlyEventFactory,
)
from ..models import (
    Enrolment,
    Event,
    EventGroup,
    Occurrence,
    validate_registration_opens_at,
)

User = get_user_model()


@pytest.mark.django_db
def test_event_creation():
    EventFactory(project=Project.objects.get_or_create(year=2020)[0])

    assert Event.objects.count() == 1


@pytest.mark.django_db
def test_occurrence_creation(event, venue):
    OccurrenceFactory(event=event, venue=venue)

    assert Occurrence.objects.count() == 1
    assert Event.objects.count() == 1
    assert Venue.objects.count() == 1


@pytest.mark.django_db
def test_enrolment_creation(occurrence, project):
    child = ChildFactory(project=project)
    occurrence.children.add(child)
    assert occurrence.children.count() == 1
    assert child.occurrences.count() == 1
    assert Enrolment.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("event_published", [False, True])
@pytest.mark.parametrize(
    "ticket_system",
    [Event.TICKETMASTER, Event.LIPPUPISTE, Event.TIXLY],
)
def test_occurrence_clean_ticket_system_url(event_published, ticket_system):
    occurrence = OccurrenceFactory.build(
        event__ticket_system=ticket_system,
        event__published_at=now() if event_published else None,
    )

    if event_published:
        with pytest.raises(ValidationError) as ei:
            occurrence.clean()
        assert ei.value.code == "TICKET_SYSTEM_URL_MISSING_ERROR"
    else:
        occurrence.clean()


@pytest.mark.django_db
def test_enrolment_reference_id():
    enrolments = EnrolmentFactory.create_batch(10)
    for enrolment in enrolments:
        assert len(enrolment.reference_id) == settings.KUKKUU_HASHID_MIN_LENGTH
        assert Enrolment.decode_reference_id(enrolment.reference_id) == enrolment.id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "has_enrolled,can_child_enroll", [(True, False), (False, True)]
)
@pytest.mark.parametrize("use_ticket_system_passwords", [True, False])
def test_event_group_can_child_enroll_already_enrolled(
    has_enrolled,
    can_child_enroll,
    child_with_random_guardian,
    future,
    use_ticket_system_passwords,
):
    """Enrolment shouldn't be allowed since child has enrolled to a different event
    in the same event group.
    """
    event_group = EventGroupFactory(
        name="Event group with one of two events enrolled", published_at=now()
    )
    OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__ticket_system=(
            Event.TICKETMASTER if use_ticket_system_passwords else Event.INTERNAL
        ),
        event__event_group=event_group,
    )
    enrolled_occurrence = OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__event_group=event_group,
    )
    if has_enrolled:
        if use_ticket_system_passwords:
            TicketSystemPasswordFactory(
                event=enrolled_occurrence.event, child=child_with_random_guardian
            )
        else:
            EnrolmentFactory(
                child=child_with_random_guardian, occurrence=enrolled_occurrence
            )
    assert event_group.can_child_enroll(child_with_random_guardian) is can_child_enroll


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_published,can_child_enroll",
    [(True, True), (False, False)],
)
def test_event_group_can_child_enroll_unpublished(
    is_published, can_child_enroll, child_with_random_guardian, future
):
    """Enrolment shouldn't be allowed since the event group is unpublished"""
    event_group = EventGroupFactory(
        name="Event group with an occurrence but might not be published yet",
        published_at=now() if is_published else None,
    )
    OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__event_group=event_group,
    )
    assert event_group.can_child_enroll(child_with_random_guardian) is can_child_enroll


@pytest.mark.django_db
def test_event_group_can_child_enroll_no_occurrence(child_with_random_guardian):
    event_group = EventGroupFactory(
        name="Event group without any occurrences", published_at=now()
    )
    assert event_group.can_child_enroll(child_with_random_guardian) is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    "enrolment_limit,can_child_enroll",
    [(3, True), (2, False), (1, False), (0, False)],
)
@pytest.mark.parametrize("use_ticket_system_passwords", [True, False])
def test_event_group_can_child_enroll_project_limit_reached(
    enrolment_limit,
    can_child_enroll,
    child_with_random_guardian,
    future,
    use_ticket_system_passwords,
):
    """
    Enrolment shouldn't be possible when event group enrolment limit is reached.
    If the child's enrolments count in this year is lower
    than the limit set in the child's project, enrolment should be possible.
    """
    project = ProjectFactory(enrolment_limit=enrolment_limit)
    child_with_random_guardian.project = project
    child_with_random_guardian.save()

    for _ in range(2):
        enrolled_event_group = EventGroupFactory(
            name="Event group where the child has already enrolled",
            published_at=now(),
            project=project,
        )
        enrolled_occurrence = OccurrenceFactory(
            time=future,
            event__published_at=now(),
            event__ticket_system=(
                Event.TICKETMASTER if use_ticket_system_passwords else Event.INTERNAL
            ),
            event__event_group=enrolled_event_group,
        )

        if use_ticket_system_passwords:
            TicketSystemPasswordFactory(
                event=enrolled_occurrence.event, child=child_with_random_guardian
            )
        else:
            EnrolmentFactory(
                child=child_with_random_guardian, occurrence=enrolled_occurrence
            )

    assert EventGroup.objects.count() == 2
    assert Enrolment.objects.count() == 0 if use_ticket_system_passwords else 2
    event_group = EventGroupFactory(
        name="Event group with an occurrence", published_at=now(), project=project
    )
    OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__event_group=event_group,
    )
    assert event_group.can_child_enroll(child_with_random_guardian) is can_child_enroll


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_published,can_child_enroll",
    [(True, True), (False, False)],
)
def test_event_can_child_enroll_unpublished(
    is_published, can_child_enroll, child_with_random_guardian, future
):
    """Enrolment shouldn't be allowed since the event is unpublished"""
    event_group = EventGroupFactory(
        published_at=now(),
    )
    occurrence = OccurrenceFactory(
        time=future,
        event__published_at=now() if is_published else None,
        event__event_group=event_group,
    )
    assert (
        occurrence.event.can_child_enroll(child_with_random_guardian)
        is can_child_enroll
    )


@pytest.mark.django_db
def test_event_can_child_enroll_no_occurrence(child_with_random_guardian):
    """Enrolment shouldn't be allowed since it has no occurrences"""
    event_group = EventGroupFactory(
        published_at=now(),
    )
    event = EventFactory(published_at=now(), event_group=event_group)
    assert event.can_child_enroll(child_with_random_guardian) is False


@pytest.mark.django_db
def test_event_can_child_enroll_event_group_unenrollable(child_with_random_guardian):
    """Enrolment shouldn't be allowed since the event group is rejected"""
    event_group = EventGroupFactory(
        name="Unpublished Event Group",
        published_at=None,
    )
    event = EventFactory(published_at=now(), event_group=event_group)
    assert event.can_child_enroll(child_with_random_guardian) is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    "enrolment_limit,can_child_enroll",
    [(3, True), (2, False), (1, False), (0, False)],
)
@pytest.mark.parametrize("use_ticket_system_passwords", [True, False])
def test_event_can_child_enroll_project_limit_reached(
    enrolment_limit,
    can_child_enroll,
    child_with_random_guardian,
    future,
    use_ticket_system_passwords,
):
    """
    Enrolment shouldn't be possible when event enrolment limit is reached.
    If the child's enrolments count in this year is lower
    than the limit set in the child's project, enrolment should be possible.
    """
    project = ProjectFactory(enrolment_limit=enrolment_limit)
    child_with_random_guardian.project = project
    child_with_random_guardian.save()

    for _ in range(2):
        enrolled_event_group = EventGroupFactory(
            name="Event group where the child has already enrolled",
            published_at=now(),
            project=project,
        )
        enrolled_occurrence = OccurrenceFactory(
            time=future,
            event__project=project,
            event__published_at=now(),
            event__ticket_system=(
                Event.TICKETMASTER if use_ticket_system_passwords else Event.INTERNAL
            ),
            event__event_group=enrolled_event_group,
        )

        if use_ticket_system_passwords:
            TicketSystemPasswordFactory(
                event=enrolled_occurrence.event, child=child_with_random_guardian
            )
        else:
            EnrolmentFactory(
                child=child_with_random_guardian, occurrence=enrolled_occurrence
            )

    assert EventGroup.objects.count() == 2
    assert Enrolment.objects.count() == 0 if use_ticket_system_passwords else 2
    event_group = EventGroupFactory(
        name="Event group with an occurrence", published_at=now(), project=project
    )
    occurrence = OccurrenceFactory(
        time=future,
        event__project=project,
        event__published_at=now(),
        event__event_group=event_group,
    )
    assert (
        occurrence.event.can_child_enroll(child_with_random_guardian)
        is can_child_enroll
    )


@pytest.mark.django_db
@pytest.mark.parametrize("use_ticket_system_passwords", [True, False])
def test_event_can_child_enroll_already_enrolled(
    child_with_random_guardian, future, use_ticket_system_passwords
):
    event_group = EventGroupFactory(published_at=now())
    enrolled_occurrence = OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__ticket_system=(
            Event.TICKETMASTER if use_ticket_system_passwords else Event.INTERNAL
        ),
        event__event_group=event_group,
    )
    if use_ticket_system_passwords:
        TicketSystemPasswordFactory(
            event=enrolled_occurrence.event, child=child_with_random_guardian
        )
    else:
        EnrolmentFactory(
            child=child_with_random_guardian, occurrence=enrolled_occurrence
        )
    assert (
        enrolled_occurrence.event.can_child_enroll(child_with_random_guardian) is False
    )


@pytest.mark.django_db
@pytest.mark.parametrize("registration_open", [True, False])
def test_event_can_child_enroll_registration_opens_at(
    registration_open, child_with_random_guardian, future
):
    """Event registration opening time is checked on event level only"""
    event_group = EventGroupFactory(published_at=now())
    occurrence = OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__registration_opens_at=now() if registration_open else future,
        event__capacity_per_occurrence=10,
        event__event_group=event_group,
    )
    expected_reason = (
        None if registration_open else EnrolmentDeniedReason.REGISTRATION_NOT_OPEN
    )

    assert (
        occurrence.event.get_enrolment_denied_reason(child_with_random_guardian)
        == expected_reason
    )
    assert (
        occurrence.get_enrolment_denied_reason(child_with_random_guardian)
        == expected_reason
    )
    # The event group has only this one published event, so the group can be
    # enrolled to only when this event's registration is open.
    assert event_group.can_child_enroll(child_with_random_guardian) is registration_open


@pytest.mark.django_db
@pytest.mark.parametrize(
    "events_registration_opens_at_deltas,expected_reason",
    [
        # no published event has registration open yet
        ([timedelta(days=1)], EnrolmentDeniedReason.REGISTRATION_NOT_OPEN),
        (
            [timedelta(days=1), timedelta(days=2)],
            EnrolmentDeniedReason.REGISTRATION_NOT_OPEN,
        ),
        # null registration_opens_at means there is no limitation
        ([None], None),
        ([None, timedelta(days=1)], None),
        # at least one event is open
        ([timedelta(days=-1), timedelta(days=1)], None),
        ([timedelta(days=-2), timedelta(days=-1)], None),
        ([timedelta(microseconds=-1)], None),
    ],
)
def test_event_group_can_child_enroll_registration_opens_at(
    events_registration_opens_at_deltas,
    expected_reason,
    child_with_random_guardian,
    future,
):
    """Event group is enrollable only if at least one of its published events has
    its registration open (null registration_opens_at means open)."""
    event_group = EventGroupFactory(published_at=now())
    for delta in events_registration_opens_at_deltas:
        OccurrenceFactory(
            time=future,
            event__published_at=now(),
            event__registration_opens_at=None if delta is None else now() + delta,
            event__event_group=event_group,
        )

    assert (
        event_group.get_enrolment_denied_reason(child_with_random_guardian)
        == expected_reason
    )
    assert event_group.can_child_enroll(child_with_random_guardian) is (
        expected_reason is None
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "unpublished_registration_opens_at_delta,published_registration_opens_at_delta,"
    "expected_reason",
    [
        # unpublished event with no limit doesn't make the group open
        (None, timedelta(days=1), EnrolmentDeniedReason.REGISTRATION_NOT_OPEN),
        # unpublished event with a future opening time doesn't close the group
        (timedelta(days=1), timedelta(days=-1), None),
    ],
)
def test_event_group_can_child_enroll_registration_opens_at_ignores_unpublished(
    unpublished_registration_opens_at_delta,
    published_registration_opens_at_delta,
    expected_reason,
    child_with_random_guardian,
    future,
):
    event_group = EventGroupFactory(published_at=now())
    OccurrenceFactory(
        time=future,
        event__published_at=None,
        event__registration_opens_at=(
            None
            if unpublished_registration_opens_at_delta is None
            else now() + unpublished_registration_opens_at_delta
        ),
        event__event_group=event_group,
    )
    OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__registration_opens_at=now() + published_registration_opens_at_delta,
        event__event_group=event_group,
    )

    assert (
        event_group.get_enrolment_denied_reason(child_with_random_guardian)
        == expected_reason
    )


@pytest.mark.django_db
def test_event_group_can_child_enroll_changes_when_event_registration_opens(
    child_with_random_guardian, future
):
    event_group = EventGroupFactory(published_at=now())
    assert (
        event_group.get_enrolment_denied_reason(child_with_random_guardian)
        == EnrolmentDeniedReason.EMPTY_EVENT_GROUP
    )

    occurrence = OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__registration_opens_at=future,
        event__event_group=event_group,
    )
    assert event_group.can_child_enroll(child_with_random_guardian) is False
    assert (
        occurrence.event.get_enrolment_denied_reason(child_with_random_guardian)
        == EnrolmentDeniedReason.REGISTRATION_NOT_OPEN
    )

    occurrence.event.registration_opens_at = now()
    occurrence.event.save()
    assert event_group.can_child_enroll(child_with_random_guardian) is True

    EnrolmentFactory(child=child_with_random_guardian, occurrence=occurrence)
    assert (
        event_group.get_enrolment_denied_reason(child_with_random_guardian)
        == EnrolmentDeniedReason.ALREADY_JOINED_EVENT_GROUP
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "registration_opens_at_delta,expected",
    [
        (None, True),
        (timedelta(days=-1), True),
        (timedelta(0), True),
        (timedelta(microseconds=1), False),
    ],
)
def test_event_is_registration_open(registration_opens_at_delta, expected):
    event = EventFactory.build(
        registration_opens_at=(
            None
            if registration_opens_at_delta is None
            else now() + registration_opens_at_delta
        )
    )

    assert event.is_registration_open() is expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "registration_opens_at_delta", [None, timedelta(microseconds=-1)]
)
def test_validate_registration_opens_at_invalid(registration_opens_at_delta):
    with pytest.raises(ValidationError) as ei:
        validate_registration_opens_at(
            None
            if registration_opens_at_delta is None
            else now() + registration_opens_at_delta
        )
    assert ei.value.code == DATA_VALIDATION_ERROR


@pytest.mark.parametrize("registration_opens_at_delta", [timedelta(0), timedelta(1)])
def test_validate_registration_opens_at_valid(registration_opens_at_delta):
    validate_registration_opens_at(now() + registration_opens_at_delta)


@pytest.mark.django_db
def test_validate_registration_opens_at_naive_datetime_is_invalid():
    naive_future = (now() + timedelta(days=1)).replace(tzinfo=None)
    with pytest.raises(ValidationError) as ei:
        validate_registration_opens_at(naive_future)
    assert ei.value.code == DATA_VALIDATION_ERROR


@pytest.mark.django_db
@pytest.mark.parametrize("already_published", [False, True])
def test_event_publish_sets_registration_opens_at(already_published, past, future):
    event = EventFactory(
        published_at=past if already_published else None,
        registration_opens_at=past if already_published else None,
    )

    event.publish(registration_opens_at=future, send_notifications=False)

    event.refresh_from_db()
    assert event.published_at == now()
    assert event.registration_opens_at == future


@pytest.mark.django_db
def test_event_publish_invalid_registration_opens_at(past):
    event = EventFactory()

    with pytest.raises(ValidationError):
        event.publish(registration_opens_at=past, send_notifications=False)

    event.refresh_from_db()
    assert event.published_at is None
    assert event.registration_opens_at is None


@pytest.mark.django_db
def test_event_group_initial_publish_sets_registration_opens_at_to_all_events(
    past, future
):
    event_group = EventGroupFactory()
    unpublished_event = EventFactory(event_group=event_group)
    directly_published_event = EventFactory(
        event_group=event_group, published_at=past, registration_opens_at=past
    )
    other_event = EventFactory(registration_opens_at=past)

    event_group.publish(registration_opens_at=future, send_notifications=False)

    for event in (unpublished_event, directly_published_event, other_event):
        event.refresh_from_db()
    assert event_group.published_at == now()
    assert unpublished_event.published_at == now()
    assert unpublished_event.registration_opens_at == future
    assert directly_published_event.published_at == past
    assert directly_published_event.registration_opens_at == future
    assert other_event.registration_opens_at == past


@pytest.mark.django_db
def test_event_group_republish_sets_registration_opens_at_to_unpublished_events(
    past, future
):
    event_group = EventGroupFactory(published_at=past)
    published_event = EventFactory(
        event_group=event_group, published_at=past, registration_opens_at=past
    )
    new_event = EventFactory(event_group=event_group)

    event_group.publish(registration_opens_at=future, send_notifications=False)

    published_event.refresh_from_db()
    new_event.refresh_from_db()
    assert published_event.published_at == past
    assert published_event.registration_opens_at == past
    assert new_event.published_at == now()
    assert new_event.registration_opens_at == future


@pytest.mark.django_db
def test_event_group_republish_without_unpublished_events(past, future):
    event_group = EventGroupFactory(published_at=past)
    event = EventFactory(
        event_group=event_group, published_at=past, registration_opens_at=past
    )

    with pytest.raises(ValidationError) as ei:
        event_group.publish(registration_opens_at=future, send_notifications=False)

    assert ei.value.code == EVENT_GROUP_ALREADY_PUBLISHED_ERROR
    event_group.refresh_from_db()
    event.refresh_from_db()
    assert event_group.published_at == past
    assert event.registration_opens_at == past


@pytest.mark.django_db
def test_event_group_publish_failure_rolls_back_registration_opens_at(past, future):
    event_group = EventGroupFactory()
    directly_published_event = EventFactory(
        event_group=event_group, published_at=past, registration_opens_at=past
    )
    # Publishing fails, because an occurrence of an external ticket system event
    # is missing the ticket system URL.
    OccurrenceFactory(
        event__event_group=event_group,
        event__ticket_system=Event.TICKETMASTER,
        ticket_system_url="",
    )

    with pytest.raises(ValidationError):
        event_group.publish(registration_opens_at=future, send_notifications=False)

    event_group.refresh_from_db()
    directly_published_event.refresh_from_db()
    assert event_group.published_at is None
    assert directly_published_event.registration_opens_at == past
    assert not Event.objects.filter(registration_opens_at=future).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "external_event_factory",
    [TicketmasterEventFactory, LippupisteEventFactory, TixlyEventFactory],
)
def test_external_event_factories(external_event_factory):
    assert Event.objects.count() == 0
    external_event_factory()
    assert Event.objects.count() == 1

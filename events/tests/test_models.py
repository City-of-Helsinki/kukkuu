from datetime import timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.timezone import now

from children.factories import ChildFactory
from kukkuu.consts import (
    DATA_VALIDATION_ERROR,
    EVENT_GROUP_ALREADY_PUBLISHED_ERROR,
    TICKET_SYSTEM_URL_MISSING_ERROR,
)
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
)
from ..services import validate_registration_opens_at

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
def test_enrolment_serialize():
    enrolment = EnrolmentFactory(extra_children_count=2, extra_guardians_count=1)
    serialized = enrolment.serialize()
    assert serialized["key"] == "ENROLMENT"
    data = {
        item["key"]: item["value"] for item in serialized["children"] if "value" in item
    }
    assert data["EXTRA_CHILDREN_COUNT"] == 2
    assert data["EXTRA_GUARDIANS_COUNT"] == 1


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
        event__project=event_group.project,
    )
    enrolled_occurrence = OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__event_group=event_group,
        event__project=event_group.project,
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
        event__project=event_group.project,
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
            event__project=enrolled_event_group.project,
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
        event__project=event_group.project,
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
        event__project=event_group.project,
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
            event__published_at=now(),
            event__ticket_system=(
                Event.TICKETMASTER if use_ticket_system_passwords else Event.INTERNAL
            ),
            event__event_group=enrolled_event_group,
            event__project=enrolled_event_group.project,
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
        event__published_at=now(),
        event__event_group=event_group,
        event__project=event_group.project,
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
        event__project=event_group.project,
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
def test_enrolment_denied_reason_registration_opens_at(
    registration_open, child_with_random_guardian, future
):
    """Registration opening is decided by the event. Its occurrences report the
    same enrolment denied reason."""
    occurrence = OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__registration_opens_at=now() if registration_open else future,
        event__capacity_per_occurrence=10,
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


@pytest.mark.django_db
def test_event_save_accepts_empty_registration_opens_at_and_published_at():
    # Should not raise an exception:
    EventFactory.create(published_at=None, registration_opens_at=None)


@pytest.mark.django_db
@pytest.mark.parametrize("registration_opens_at_delta_days", [-100, 0, 100])
def test_event_save_accepts_any_registration_opens_at_if_published_at_not_set(
    registration_opens_at_delta_days,
):
    # Should not raise an exception:
    EventFactory.create(
        published_at=None,
        registration_opens_at=now() + timedelta(days=registration_opens_at_delta_days),
    )


@pytest.mark.django_db
@pytest.mark.parametrize("published_at_delta_days", [-100, 0, 100])
def test_event_save_accepts_any_published_at_if_registration_opens_at_not_set(
    published_at_delta_days,
):
    # Should not raise an exception:
    EventFactory.create(
        published_at=now() + timedelta(days=published_at_delta_days),
        registration_opens_at=None,
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "published_at_delta_h, registration_opens_at_delta_h",
    [
        (-1, -1),
        (-1, 100),
        (0, 0),
        (0, 100),
        (100, 100),
        (100, 200),
    ],
)
def test_event_save_accepts_registration_opens_at_not_before_published_at(
    published_at_delta_h, registration_opens_at_delta_h
):
    # Should not raise an exception:
    EventFactory.create(
        published_at=now() + timedelta(seconds=published_at_delta_h),
        registration_opens_at=now() + timedelta(seconds=registration_opens_at_delta_h),
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "published_at_delta_h, registration_opens_at_delta_h",
    [
        (-1, -2),
        (0, -1),
        (0, -100),
        (100, 99),
        (100, -200),
    ],
)
def test_event_save_rejects_registration_opens_at_before_published_at(
    published_at_delta_h, registration_opens_at_delta_h
):
    with pytest.raises(ValidationError) as e:
        EventFactory.create(
            published_at=now() + timedelta(hours=published_at_delta_h),
            registration_opens_at=now()
            + timedelta(hours=registration_opens_at_delta_h),
        )
    assert e.value.code == DATA_VALIDATION_ERROR
    assert (
        e.value.message
        == "Registration opening time must not be before publication time"
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "events_registration_opens_at_deltas",
    [
        # no published event has registration open yet
        [timedelta(microseconds=1)],
        [timedelta(days=1), timedelta(days=2)],
    ],
)
def test_event_group_can_child_enroll_registration_opens_at_failure(
    events_registration_opens_at_deltas,
    child_with_random_guardian,
    future,
):
    """Event group is not enrollable if none of its published events has
    its registration open (null registration_opens_at means open)."""
    event_group = EventGroupFactory(published_at=now())
    for delta in events_registration_opens_at_deltas:
        OccurrenceFactory(
            time=future,
            event__published_at=now(),
            event__registration_opens_at=now() + delta,
            event__event_group=event_group,
        )

    assert (
        event_group.get_enrolment_denied_reason(child_with_random_guardian)
        == EnrolmentDeniedReason.REGISTRATION_NOT_OPEN
    )
    assert event_group.can_child_enroll(child_with_random_guardian) is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    "events_registration_opens_at_deltas",
    [
        # null registration_opens_at means there is no limitation
        [None],
        [None, timedelta(days=1)],
        # at least one event is open
        [timedelta(microseconds=0)],
        [timedelta(seconds=0), timedelta(days=1)],
    ],
)
def test_event_group_can_child_enroll_registration_opens_at_success(
    events_registration_opens_at_deltas,
    child_with_random_guardian,
    future,
):
    """Event group is enrollable if at least one of its published events has
    its registration open (null registration_opens_at means open)."""
    event_group = EventGroupFactory(published_at=now())
    for delta in events_registration_opens_at_deltas:
        OccurrenceFactory(
            time=future,
            event__published_at=now(),
            event__registration_opens_at=None if delta is None else now() + delta,
            event__event_group=event_group,
        )

    assert event_group.get_enrolment_denied_reason(child_with_random_guardian) is None
    assert event_group.can_child_enroll(child_with_random_guardian) is True


@pytest.mark.django_db
@pytest.mark.parametrize(
    "unpublished_registration_opens_at_delta,published_registration_opens_at_delta,"
    "expected_reason",
    [
        # unpublished event with no limit doesn't make the group open
        (None, timedelta(days=1), EnrolmentDeniedReason.REGISTRATION_NOT_OPEN),
        # unpublished event with a future opening time doesn't close the group
        (timedelta(days=1), timedelta(days=0), None),
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
    """
    Test that EventGroup's can_child_enroll and get_enrolment_denied_reason
    values change through the process, including when registration is not
    open, and after it has opened.
    """
    event_group = EventGroupFactory(published_at=now())
    assert event_group.can_child_enroll(child_with_random_guardian) is False
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
        event_group.get_enrolment_denied_reason(child_with_random_guardian)
        == EnrolmentDeniedReason.REGISTRATION_NOT_OPEN
    )

    occurrence.event.registration_opens_at = now()
    occurrence.event.save()
    assert event_group.can_child_enroll(child_with_random_guardian) is True
    assert event_group.get_enrolment_denied_reason(child_with_random_guardian) is None

    EnrolmentFactory(child=child_with_random_guardian, occurrence=occurrence)
    assert event_group.can_child_enroll(child_with_random_guardian) is False
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


def test_validate_registration_opens_at_none_is_invalid():
    with pytest.raises(ValidationError) as e:
        validate_registration_opens_at(None)
    assert e.value.code == DATA_VALIDATION_ERROR


@pytest.mark.parametrize(
    "registration_opens_at_delta",
    [timedelta(microseconds=-1), timedelta(days=-1), timedelta(weeks=-100)],
)
def test_validate_registration_opens_at_past_is_invalid(registration_opens_at_delta):
    with pytest.raises(ValidationError) as e:
        validate_registration_opens_at(now() + registration_opens_at_delta)
    assert e.value.code == DATA_VALIDATION_ERROR


def test_validate_registration_opens_at_now_is_valid():
    # Should not raise an exception:
    validate_registration_opens_at(now())


@pytest.mark.parametrize(
    "registration_opens_at_delta",
    [timedelta(microseconds=1), timedelta(days=1), timedelta(weeks=100)],
)
def test_validate_registration_opens_at_future_is_valid(registration_opens_at_delta):
    # Should not raise an exception:
    validate_registration_opens_at(now() + registration_opens_at_delta)


def test_validate_registration_opens_at_naive_datetime_is_invalid():
    naive_future = (now() + timedelta(days=1)).replace(tzinfo=None)
    with pytest.raises(ValidationError) as e:
        validate_registration_opens_at(naive_future)
    assert e.value.code == DATA_VALIDATION_ERROR


@pytest.mark.django_db
def test_unpublished_event_publish_sets_registration_opens_at(future):
    """Test that publishing an unpublished event sets its registration_opens_at"""
    event = EventFactory(published_at=None, registration_opens_at=None)
    event.publish(registration_opens_at=future, send_notifications=False)

    event.refresh_from_db()
    assert event.published_at == now()
    assert event.registration_opens_at == future


@pytest.mark.django_db
def test_event_republish_sets_registration_opens_at(past, future):
    """Test that republishing a published event updates its registration_opens_at"""
    event = EventFactory(published_at=past, registration_opens_at=past)
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
def test_event_group_initial_publish_sets_registration_opens_at_to_unpublished_events(
    past, future
):
    unpublished_event_group = EventGroupFactory(published_at=None)
    unpublished_event = EventFactory(
        event_group=unpublished_event_group,
        published_at=None,
        registration_opens_at=None,
    )
    published_event = EventFactory(
        event_group=unpublished_event_group,
        published_at=past,
        registration_opens_at=past,
    )
    other_event = EventFactory(published_at=None, registration_opens_at=past)

    unpublished_event_group.publish(
        registration_opens_at=future, send_notifications=False
    )

    for event in unpublished_event, published_event, other_event:
        event.refresh_from_db()
    assert unpublished_event_group.published_at == now()
    assert unpublished_event.published_at == now()
    assert unpublished_event.registration_opens_at == future
    # The already published event should remain unchanged:
    assert published_event.published_at == past
    assert published_event.registration_opens_at == past
    # The event not in the published event group should remain unchanged:
    assert other_event.published_at is None
    assert other_event.registration_opens_at == past


@pytest.mark.django_db
def test_event_group_initial_publish_without_unpublished_events(past, future):
    """An unpublished event group can be published even if it has no unpublished
    events. Then the registration opening time is not set to any event.
    """
    empty_event_group = EventGroupFactory(published_at=None)
    event_group_with_published_event = EventGroupFactory(published_at=None)
    published_event = EventFactory(
        event_group=event_group_with_published_event,
        published_at=past,
        registration_opens_at=past,
    )

    empty_event_group.publish(registration_opens_at=future, send_notifications=False)
    event_group_with_published_event.publish(
        registration_opens_at=future, send_notifications=False
    )

    published_event.refresh_from_db()
    assert empty_event_group.published_at == now()
    assert event_group_with_published_event.published_at == now()
    assert published_event.published_at == past
    assert published_event.registration_opens_at == past


@pytest.mark.django_db
def test_event_group_republish_sets_registration_opens_at_to_unpublished_events(
    past, future
):
    event_group = EventGroupFactory(published_at=past)
    published_event = EventFactory(
        event_group=event_group, published_at=past, registration_opens_at=past
    )
    new_event = EventFactory(
        event_group=event_group, published_at=None, registration_opens_at=None
    )

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

    with pytest.raises(ValidationError) as e:
        event_group.publish(registration_opens_at=future, send_notifications=False)

    assert e.value.code == EVENT_GROUP_ALREADY_PUBLISHED_ERROR
    event_group.refresh_from_db()
    event.refresh_from_db()
    assert event_group.published_at == past
    assert event.registration_opens_at == past


@pytest.mark.django_db
def test_event_group_publish_failure_rolls_back_registration_opens_at(past, future):
    event_group = EventGroupFactory()
    unpublished_event = EventFactory(
        event_group=event_group, published_at=None, registration_opens_at=None
    )
    # Unpublished event with empty ticket system URL occurrence so it fails to publish:
    occurrence = OccurrenceFactory(
        event__event_group=event_group,
        event__published_at=None,
        event__registration_opens_at=None,
        event__ticket_system=Event.TICKETMASTER,
        ticket_system_url="",
    )

    with pytest.raises(ValidationError) as e:
        event_group.publish(registration_opens_at=future, send_notifications=False)

    assert e.value.code == TICKET_SYSTEM_URL_MISSING_ERROR

    event_group.refresh_from_db()
    unpublished_event.refresh_from_db()
    occurrence.refresh_from_db()
    occurrence.event.refresh_from_db()

    assert event_group.published_at is None
    assert unpublished_event.published_at is None
    assert occurrence.event.published_at is None
    assert unpublished_event.registration_opens_at is None
    assert occurrence.event.registration_opens_at is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "external_event_factory",
    [TicketmasterEventFactory, LippupisteEventFactory, TixlyEventFactory],
)
def test_external_event_factories(external_event_factory):
    assert Event.objects.count() == 0
    external_event_factory()
    assert Event.objects.count() == 1


@pytest.mark.django_db
def test_event_group_project_mismatch_raises_validation_error():
    """
    Test that an Event cannot be assigned to an EventGroup if they belong to different projects.
    Validates that both `clean()` and `save()` raise a ValidationError to prevent mismatched projects
    when creating or updating an Event.
    """
    project1 = ProjectFactory(year=3000)
    project2 = ProjectFactory(year=3001)
    event_group = EventGroupFactory(project=project1)

    event = EventFactory.build(project=project2, event_group=event_group)

    with pytest.raises(
        ValidationError,
        match="The event and the event group must belong to the same project.",
    ):
        event.save()

    with pytest.raises(
        ValidationError,
        match="The event and the event group must belong to the same project.",
    ):
        event.clean()


@pytest.mark.django_db
def test_event_group_events_project_mismatch_raises_validation_error():
    """
    Test that an EventGroup's project cannot be changed if it contains Events that would
    end up belonging to a different project than the new one assigned to the EventGroup.
    Validates that `save()` raises a ValidationError.
    """
    project1 = ProjectFactory(year=3002)
    project2 = ProjectFactory(year=3003)
    event_group = EventGroupFactory(project=project1)
    EventFactory(project=project1, event_group=event_group)

    # Change project of event_group to mismatch its events
    event_group.project = project2

    with pytest.raises(
        ValidationError,
        match="The event group and its events must belong to the same project.",
    ):
        event_group.save()

    with pytest.raises(
        ValidationError,
        match="The event group and its events must belong to the same project.",
    ):
        event_group.clean()


@pytest.mark.django_db
def test_occurrence_reserved_seats_legacy():
    occurrence = OccurrenceFactory()
    enrolment = EnrolmentFactory(
        occurrence=occurrence,
        extra_children_count=None,
        extra_guardians_count=None,
    )
    assert enrolment.total_seats == 1
    assert occurrence.get_reserved_seats() == 1
    annotated = Occurrence.objects.with_reserved_seats().get(pk=occurrence.pk)
    assert annotated.reserved_seats == 1


@pytest.mark.django_db
def test_occurrence_reserved_seats_new():
    occurrence = OccurrenceFactory()
    enrolment = EnrolmentFactory(
        occurrence=occurrence,
        extra_children_count=0,
        extra_guardians_count=0,
    )
    assert enrolment.total_seats == 2
    assert occurrence.get_reserved_seats() == 2
    annotated = Occurrence.objects.with_reserved_seats().get(pk=occurrence.pk)
    assert annotated.reserved_seats == 2


@pytest.mark.django_db
def test_occurrence_reserved_seats_family():
    occurrence = OccurrenceFactory()
    enrolment = EnrolmentFactory(
        occurrence=occurrence,
        extra_children_count=2,
        extra_guardians_count=1,
    )
    assert enrolment.total_seats == 5
    assert occurrence.get_reserved_seats() == 5
    annotated = Occurrence.objects.with_reserved_seats().get(pk=occurrence.pk)
    assert annotated.reserved_seats == 5


@pytest.mark.django_db
def test_occurrence_with_reserved_seats_query_matches_method():
    from subscriptions.factories import FreeSpotNotificationSubscriptionFactory

    occ_empty = OccurrenceFactory()
    occ_mixed = OccurrenceFactory()

    # Legacy enrolment (1 seat)
    EnrolmentFactory(
        occurrence=occ_mixed,
        extra_children_count=None,
        extra_guardians_count=None,
    )
    # Family enrolment (2 + 1 + 0 = 3 seats)
    EnrolmentFactory(
        occurrence=occ_mixed,
        extra_children_count=1,
        extra_guardians_count=0,
    )
    # Add subscriptions to ensure correlated subquery does not multiply or break
    FreeSpotNotificationSubscriptionFactory(occurrence=occ_mixed)
    FreeSpotNotificationSubscriptionFactory(occurrence=occ_mixed)

    qs = Occurrence.objects.with_reserved_seats()
    res_empty = qs.get(pk=occ_empty.pk)
    res_mixed = qs.get(pk=occ_mixed.pk)

    assert res_empty.reserved_seats == occ_empty.get_reserved_seats() == 0
    assert res_mixed.reserved_seats == occ_mixed.get_reserved_seats() == 4


@pytest.mark.django_db
def test_event_and_event_group_reserved_seats():
    event_group = EventGroupFactory()
    event_1 = EventFactory(event_group=event_group)
    event_2 = EventFactory(event_group=event_group)

    occ_1 = OccurrenceFactory(event=event_1)
    occ_2 = OccurrenceFactory(event=event_2)

    # Legacy enrolment (1 seat)
    EnrolmentFactory(
        occurrence=occ_1, extra_children_count=None, extra_guardians_count=None
    )
    # Family enrolment (2 + 1 + 1 = 4 seats)
    EnrolmentFactory(occurrence=occ_2, extra_children_count=1, extra_guardians_count=1)

    assert occ_1.get_reserved_seats() == 1
    assert occ_2.get_reserved_seats() == 4
    assert event_1.get_reserved_seats() == 1
    assert event_2.get_reserved_seats() == 4
    assert event_group.get_reserved_seats() == 5


@pytest.mark.django_db
def test_enrolment_negative_extra_participants_check_constraint():
    occurrence = OccurrenceFactory()
    child = ChildFactory()

    with pytest.raises(IntegrityError):
        Enrolment.objects.create(
            occurrence=occurrence,
            child=child,
            extra_children_count=-1,
            extra_guardians_count=0,
        )

    with pytest.raises(IntegrityError):
        Enrolment.objects.create(
            occurrence=occurrence,
            child=child,
            extra_children_count=0,
            extra_guardians_count=-1,
        )


@pytest.mark.django_db
def test_occurrence_has_free_seats_threshold():
    occurrence = OccurrenceFactory(capacity_override=3)
    EnrolmentFactory(
        occurrence=occurrence,
        extra_children_count=0,
        extra_guardians_count=0,
    )  # 2 seats reserved -> remaining = 1
    assert occurrence.get_remaining_capacity() == 1
    assert occurrence.has_free_seats() is False

    occurrence.capacity_override = 4
    occurrence.save()
    assert occurrence.get_remaining_capacity() == 2
    assert occurrence.has_free_seats() is True


@pytest.mark.django_db
def test_enrolment_denied_reason_capacity_threshold(child_with_random_guardian, future):
    occurrence = OccurrenceFactory(
        time=future,
        event__published_at=now(),
        event__project=child_with_random_guardian.project,
        capacity_override=3,
    )
    EnrolmentFactory(
        occurrence=occurrence,
        extra_children_count=0,
        extra_guardians_count=0,
    )  # 2 seats reserved -> remaining = 1

    # Default requested_seats is 2 -> denied because remaining 1 < 2
    assert (
        occurrence.get_enrolment_denied_reason(child_with_random_guardian)
        == EnrolmentDeniedReason.OCCURRENCE_FULL
    )
    # Explicit requested_seats = 3 -> denied
    assert (
        occurrence.get_enrolment_denied_reason(
            child_with_random_guardian, requested_seats=3
        )
        == EnrolmentDeniedReason.OCCURRENCE_FULL
    )

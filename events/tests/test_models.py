import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from children.factories import ChildFactory
from projects.factories import ProjectFactory
from projects.models import Project
from venues.models import Venue

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
from ..models import Enrolment, Event, EventGroup, Occurrence

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
def test_occurrence_clean_ticket_system_url(event_published):
    occurrence = OccurrenceFactory.build(
        event__ticket_system=Event.TICKETMASTER,
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
@pytest.mark.parametrize(
    "external_event_factory",
    [TicketmasterEventFactory, LippupisteEventFactory, TixlyEventFactory],
)
def test_external_event_factories(external_event_factory):
    assert Event.objects.count() == 0
    external_event_factory()
    assert Event.objects.count() == 1

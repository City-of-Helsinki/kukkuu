from datetime import datetime

import pytest
from django.utils import timezone

from children.factories import ChildWithGuardianFactory
from events.factories import EnrolmentFactory, EventFactory, OccurrenceFactory
from users.factories import GuardianFactory
from users.services import AuthServiceNotificationService


def get_local_timestamp(dt: datetime):
    dt = dt.astimezone(timezone.get_current_timezone())
    return f"{dt.day}.{dt.month}.{dt.year} {dt.hour:02d}:{dt.minute:02d}"


@pytest.fixture
def guardian_with_children_and_enrolments():
    guardian = GuardianFactory()
    [child1, child2] = ChildWithGuardianFactory.create_batch(
        2, relationship__guardian=guardian
    )

    event1 = EventFactory(name="Event 1 for child1")
    event2 = EventFactory(name="Event 2 for child2", short_description="")
    event3 = EventFactory(name="Event 3 for child2")
    event4 = EventFactory(name="Event 4 for child2")

    occurrence1 = OccurrenceFactory(
        event=event1, time=timezone.datetime(year=2024, month=1, day=1)
    )
    occurrence2 = OccurrenceFactory(
        event=event2, time=timezone.datetime(year=2023, month=12, day=24)
    )
    occurrence3 = OccurrenceFactory(
        event=event3, time=timezone.datetime(year=2023, month=6, day=16)
    )
    occurrence4 = OccurrenceFactory(
        event=event4, time=timezone.datetime(year=2023, month=12, day=6)
    )

    EnrolmentFactory(child=child1, occurrence=occurrence1)
    EnrolmentFactory(child=child2, occurrence=occurrence2)
    EnrolmentFactory(child=child2, occurrence=occurrence3)
    EnrolmentFactory(child=child2, occurrence=occurrence4)

    return guardian


@pytest.mark.django_db
def test_generate_children_event_history_markdown_no_children(
    guardian_with_children_and_enrolments,
):
    """Test with a guardian who has no children."""
    guardian = GuardianFactory()
    markdown = AuthServiceNotificationService.generate_children_event_history_markdown(
        guardian
    )
    assert markdown == ""  # Expect an empty string


@pytest.mark.django_db
def test_generate_children_event_history_markdown_no_enrolments(
    guardian_with_children_and_enrolments,
):
    """Test with a guardian who has children but no enrollments."""
    guardian = GuardianFactory()
    child = ChildWithGuardianFactory(relationship__guardian=guardian)
    markdown = AuthServiceNotificationService.generate_children_event_history_markdown(
        guardian
    )
    assert markdown == f"# {child.name}"  # Expect only the child's name as a header


@pytest.mark.django_db
def test_generate_children_event_history_markdown_with_data(
    snapshot,
    guardian_with_children_and_enrolments,
):
    """Test with a guardian who has children with enrollments."""
    guardian = guardian_with_children_and_enrolments
    markdown = AuthServiceNotificationService.generate_children_event_history_markdown(
        guardian
    )
    for child in guardian.children.all():
        # Check for headers with children's names
        assert child.name in markdown
        # Check for event names and dates in the correct format
        for enrolment in child.enrolments.all():
            occurrence = enrolment.occurrence
            event = occurrence.event
            assert (
                f"**{event.name}:** {get_local_timestamp(occurrence.time)}" in markdown
            )
            if event.short_description:
                assert event.short_description in markdown
    # NOTE: This is markdown, so the line changes and white spaces are important!
    # Also, check that the order is right: they should be ordered by date
    snapshot.assert_match(markdown)

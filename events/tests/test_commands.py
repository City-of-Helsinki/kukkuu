from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from events.factories import (
    OccurrenceFactory,
    RandomExternalTicketSystemEventFactory,
)
from venues.factories import SystemVenueFactory


@pytest.mark.django_db
def test_check_command_all_valid():
    RandomExternalTicketSystemEventFactory()
    out = StringIO()
    call_command("check_external_events_before_occurrence_migration", stdout=out)
    assert "are valid for occurrence migration" in out.getvalue()


@pytest.mark.django_db
def test_check_command_missing_end_time_fails_with_hint():
    event = RandomExternalTicketSystemEventFactory()
    event.ticket_system_end_time = None
    event.save(update_fields=["ticket_system_end_time"])

    out = StringIO()
    err = StringIO()
    with pytest.raises(SystemExit) as exc_info:
        call_command(
            "check_external_events_before_occurrence_migration",
            stdout=out,
            stderr=err,
        )
    assert exc_info.value.code == 1
    assert "missing ticket_system_end_time" in err.getvalue()
    assert "--fix" in err.getvalue()


@pytest.mark.django_db
def test_check_command_fix_uses_published_at_and_created_at():
    published_time = timezone.now() - timezone.timedelta(days=5)
    ev_published = RandomExternalTicketSystemEventFactory(
        published_at=published_time,
    )
    ev_published.ticket_system_end_time = None
    ev_published.save(update_fields=["ticket_system_end_time"])

    ev_unpublished = RandomExternalTicketSystemEventFactory(
        published_at=None,
    )
    ev_unpublished.ticket_system_end_time = None
    ev_unpublished.save(update_fields=["ticket_system_end_time"])

    out = StringIO()
    err = StringIO()
    call_command(
        "check_external_events_before_occurrence_migration",
        "--fix",
        stdout=out,
        stderr=err,
    )

    ev_published.refresh_from_db()
    ev_unpublished.refresh_from_db()

    assert ev_published.ticket_system_end_time == published_time
    assert ev_unpublished.ticket_system_end_time == ev_unpublished.created_at
    assert "are valid for occurrence migration" in out.getvalue()


@pytest.mark.django_db
def test_check_command_multiple_occurrences_fails():
    event = RandomExternalTicketSystemEventFactory()
    system_venue = SystemVenueFactory()
    # Create two occurrences directly
    OccurrenceFactory(event=event, venue=system_venue)
    OccurrenceFactory(event=event, venue=system_venue)

    out = StringIO()
    err = StringIO()
    with pytest.raises(SystemExit) as exc_info:
        call_command(
            "check_external_events_before_occurrence_migration",
            stdout=out,
            stderr=err,
        )
    assert exc_info.value.code == 1
    assert "more than 1 occurrence" in err.getvalue()

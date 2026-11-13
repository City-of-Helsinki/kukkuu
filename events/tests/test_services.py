from datetime import timedelta

import pytest
from django.conf import settings
from django.utils.timezone import now

from events.factories import (
    EventFactory,
    OccurrenceFactory,
    TicketmasterEventFactory,
)
from events.models import Event
from events.services import (
    sync_external_event_occurrence,
    sync_external_occurrence_to_event,
)


@pytest.mark.django_db
def test_sync_external_event_occurrence_creates_occurrence():
    event = TicketmasterEventFactory(
        occurrence=False,
        ticket_system_url="https://example.com/tickets",
        ticket_system_end_time=now() + timedelta(days=10),
    )
    assert event.occurrences.count() == 0

    occ = sync_external_event_occurrence(event)
    assert occ is not None
    assert event.occurrences.count() == 1
    assert occ.venue.is_system is True
    assert occ.venue.name == settings.KUKKUU_DEFAULT_VENUE_NAME
    assert occ.time == event.ticket_system_end_time
    assert occ.ticket_system_url == "https://example.com/tickets"
    assert occ.occurrence_language == "fi"


@pytest.mark.django_db
def test_sync_external_event_occurrence_updates_existing_occurrence():
    event = TicketmasterEventFactory(
        ticket_system_url="https://example.com/old",
        ticket_system_end_time=now() + timedelta(days=5),
    )
    occ1 = sync_external_event_occurrence(event)

    new_time = now() + timedelta(days=20)
    event.ticket_system_end_time = new_time
    event.ticket_system_url = "https://example.com/new"
    event.save(update_fields=["ticket_system_end_time", "ticket_system_url"])

    occ2 = sync_external_event_occurrence(event)
    assert occ2.pk == occ1.pk
    assert event.occurrences.count() == 1
    occ2.refresh_from_db()
    assert occ2.time == new_time
    assert occ2.ticket_system_url == "https://example.com/new"


@pytest.mark.django_db
def test_sync_external_event_occurrence_language_defaulting():
    # Only Swedish translation
    event_sv = TicketmasterEventFactory(occurrence=False)
    event_sv.translations.all().delete()
    event_sv.create_translation(language_code="sv", name="Svenskt namn")
    occ_sv = sync_external_event_occurrence(event_sv)
    assert occ_sv.occurrence_language == "sv"

    # Both Finnish and Swedish
    event_fi = TicketmasterEventFactory(occurrence=False)
    event_fi.create_translation(language_code="sv", name="Svenskt namn")
    occ_fi = sync_external_event_occurrence(event_fi)
    assert occ_fi.occurrence_language == "fi"


@pytest.mark.django_db
def test_sync_external_event_occurrence_ignores_internal_event():
    event = EventFactory(ticket_system=Event.INTERNAL)
    occ = sync_external_event_occurrence(event)
    assert occ is None
    assert event.occurrences.count() == 0


@pytest.mark.django_db
def test_sync_external_occurrence_to_event():
    event = TicketmasterEventFactory(
        ticket_system_url="https://example.com/initial",
        ticket_system_end_time=now() + timedelta(days=5),
    )
    occ = event.occurrences.first()
    new_time = now() + timedelta(days=20)
    occ.time = new_time
    occ.ticket_system_url = "https://example.com/updated"

    synced_event = sync_external_occurrence_to_event(occ)
    assert synced_event is not None
    event.refresh_from_db()
    assert event.ticket_system_end_time == new_time
    assert event.ticket_system_url == "https://example.com/updated"


@pytest.mark.django_db
def test_sync_external_occurrence_to_event_ignores_internal():
    occ = OccurrenceFactory(event__ticket_system=Event.INTERNAL)
    assert sync_external_occurrence_to_event(occ) is None

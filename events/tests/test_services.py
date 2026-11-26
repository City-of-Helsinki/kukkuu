import re
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from django.conf import settings
from django.utils.timezone import now
from graphql import GraphQLResolveInfo

from common.utils import get_global_id
from events.factories import (
    EnrolmentFactory,
    EventFactory,
    OccurrenceFactory,
    TicketmasterEventFactory,
)
from events.models import Enrolment, Event
from events.services import (
    EnrolmentAPIService,
    OccurrenceAPIService,
    sync_external_event_occurrence,
    sync_external_occurrence_to_event,
)
from kukkuu.exceptions import DataValidationError, ObjectDoesNotExistError
from kukkuu.schema import schema
from languages.models import Language
from users.factories import UserFactory
from venues.factories import VenueFactory


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
    assert [language.alpha_3_code for language in occ.languages.all()] == ["fin"]


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
    assert [language.alpha_3_code for language in occ_sv.languages.all()] == ["swe"]

    # Both Finnish and Swedish
    event_fi = TicketmasterEventFactory(occurrence=False)
    event_fi.create_translation(language_code="sv", name="Svenskt namn")
    occ_fi = sync_external_event_occurrence(event_fi)
    assert [language.alpha_3_code for language in occ_fi.languages.all()] == ["fin"]


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
def test_sync_external_occurrence_to_event_preserves_url_when_empty():
    event = TicketmasterEventFactory(
        ticket_system_url="https://example.com/initial",
        ticket_system_end_time=now() + timedelta(days=5),
    )
    occ = event.occurrences.first()
    new_time = now() + timedelta(days=20)
    occ.time = new_time
    occ.ticket_system_url = ""

    synced_event = sync_external_occurrence_to_event(occ)
    assert synced_event is not None
    event.refresh_from_db()
    assert event.ticket_system_end_time == new_time
    assert event.ticket_system_url == "https://example.com/initial"


@pytest.mark.django_db
def test_sync_external_occurrence_to_event_ignores_internal():
    occ = OccurrenceFactory(event__ticket_system=Event.INTERNAL)
    assert sync_external_occurrence_to_event(occ) is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "enrolment_data,arrival_input,expected_result",
    [
        # Explicit arrived counts (including full, partial, and 0/0 absent)
        pytest.param(
            {"extra_children_count": 0, "extra_guardians_count": 0},
            {"arrived_children_count": 1, "arrived_guardians_count": 1},
            {
                "attended": True,
                "arrived_children_count": 1,
                "arrived_guardians_count": 1,
                "arrived_seats": 2,
            },
            id="explicit_counts_full_arrival_with_zero_extras",
        ),
        pytest.param(
            {"extra_children_count": None, "extra_guardians_count": None},
            {"arrived_children_count": 1, "arrived_guardians_count": 1},
            {
                "attended": True,
                "arrived_children_count": 1,
                "arrived_guardians_count": 1,
                "arrived_seats": 2,
            },
            id="explicit_counts_full_arrival_with_null_extras",
        ),
        pytest.param(
            {"extra_children_count": 2, "extra_guardians_count": 1},
            {"arrived_children_count": 2, "arrived_guardians_count": 1},
            {
                "attended": True,
                "arrived_children_count": 2,
                "arrived_guardians_count": 1,
                "arrived_seats": 3,
            },
            id="explicit_counts_partial_family_arrival",
        ),
        pytest.param(
            {"extra_children_count": 2, "extra_guardians_count": 1},
            {"arrived_children_count": 3, "arrived_guardians_count": 2},
            {
                "attended": True,
                "arrived_children_count": 3,
                "arrived_guardians_count": 2,
                "arrived_seats": 5,
            },
            id="explicit_counts_full_family_arrival",
        ),
        pytest.param(
            {"extra_children_count": 2, "extra_guardians_count": 1},
            {"arrived_children_count": 0, "arrived_guardians_count": 1},
            {
                "attended": True,
                "arrived_children_count": 0,
                "arrived_guardians_count": 1,
                "arrived_seats": 1,
            },
            id="explicit_counts_guardian_only_arrival",
        ),
        pytest.param(
            {"extra_children_count": 2, "extra_guardians_count": 1},
            {"arrived_children_count": 0, "arrived_guardians_count": 0},
            {
                "attended": False,
                "arrived_children_count": 0,
                "arrived_guardians_count": 0,
                "arrived_seats": 0,
            },
            id="explicit_counts_zero_arrival_marks_not_attended",
        ),
        pytest.param(
            {"extra_children_count": 2, "extra_guardians_count": 1},
            {
                "attended": True,
                "arrived_children_count": 1,
                "arrived_guardians_count": 1,
            },
            {
                "attended": True,
                "arrived_children_count": 1,
                "arrived_guardians_count": 1,
                "arrived_seats": 2,
            },
            id="explicit_counts_with_matching_attended_true",
        ),
        pytest.param(
            {"extra_children_count": 2, "extra_guardians_count": 1},
            {
                "attended": False,
                "arrived_children_count": 0,
                "arrived_guardians_count": 0,
            },
            {
                "attended": False,
                "arrived_children_count": 0,
                "arrived_guardians_count": 0,
                "arrived_seats": 0,
            },
            id="explicit_counts_with_matching_attended_false",
        ),
        # Boolean attended flag only (defaults counts to booked counts / 0 / None)
        pytest.param(
            {"extra_children_count": None, "extra_guardians_count": None},
            {"attended": True},
            {
                "attended": True,
                "arrived_children_count": 1,
                "arrived_guardians_count": 1,
                "arrived_seats": 2,
            },
            id="attended_true_only_defaults_to_booked_counts_for_null_extras",
        ),
        pytest.param(
            {"extra_children_count": 0, "extra_guardians_count": 0},
            {"attended": True},
            {
                "attended": True,
                "arrived_children_count": 1,
                "arrived_guardians_count": 1,
                "arrived_seats": 2,
            },
            id="attended_true_only_defaults_to_booked_counts_for_zero_extras",
        ),
        pytest.param(
            {"extra_children_count": 2, "extra_guardians_count": 1},
            {"attended": True},
            {
                "attended": True,
                "arrived_children_count": 3,
                "arrived_guardians_count": 2,
                "arrived_seats": 5,
            },
            id="attended_true_only_defaults_to_booked_family_counts",
        ),
        pytest.param(
            {"extra_children_count": 2, "extra_guardians_count": 1},
            {"attended": False},
            {
                "attended": False,
                "arrived_children_count": 0,
                "arrived_guardians_count": 0,
                "arrived_seats": 0,
            },
            id="attended_false_only_defaults_counts_to_zero",
        ),
        pytest.param(
            {"extra_children_count": 2, "extra_guardians_count": 1},
            {"attended": None},
            {
                "attended": None,
                "arrived_children_count": None,
                "arrived_guardians_count": None,
                "arrived_seats": 0,
            },
            id="attended_none_only_clears_counts_to_null",
        ),
    ],
)
def test_enrolment_api_service_apply_arrival_valid(
    enrolment_data,
    arrival_input,
    expected_result,
):
    """
    Verify EnrolmentAPIService.apply_arrival updates and persists arrived
    children/guardian counts and attended status for explicit count pairs and
    attended-only calls across default (NULL/0) and family enrolments.
    """
    enrolment = EnrolmentFactory(
        attended=True,
        arrived_children_count=1,
        arrived_guardians_count=1,
        **enrolment_data,
    )

    updated = EnrolmentAPIService.apply_arrival(
        enrolment,
        **arrival_input,
    )
    updated.refresh_from_db()

    assert {
        "attended": updated.attended,
        "arrived_children_count": updated.arrived_children_count,
        "arrived_guardians_count": updated.arrived_guardians_count,
        "arrived_seats": updated.arrived_seats,
    } == expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "arrival_input,expected_message",
    [
        pytest.param(
            {"arrived_children_count": 1},
            "Both arrivedChildrenCount and arrivedGuardiansCount "
            "must be provided together.",
            id="only_arrived_children_provided",
        ),
        pytest.param(
            {"arrived_guardians_count": 1},
            "Both arrivedChildrenCount and arrivedGuardiansCount "
            "must be provided together.",
            id="only_arrived_guardians_provided",
        ),
        pytest.param(
            {"arrived_children_count": -1, "arrived_guardians_count": 1},
            "Arrived participant counts cannot be negative.",
            id="negative_arrived_children",
        ),
        pytest.param(
            {"arrived_children_count": 1, "arrived_guardians_count": -1},
            "Arrived participant counts cannot be negative.",
            id="negative_arrived_guardians",
        ),
        pytest.param(
            {"arrived_children_count": 3, "arrived_guardians_count": 1},
            "Arrived children count (3) cannot exceed booked children count (2).",
            id="arrived_children_exceeds_booked_children",
        ),
        pytest.param(
            {"arrived_children_count": 1, "arrived_guardians_count": 3},
            "Arrived guardians count (3) cannot exceed booked guardians count (2).",
            id="arrived_guardians_exceeds_booked_guardians",
        ),
        pytest.param(
            {
                "attended": False,
                "arrived_children_count": 1,
                "arrived_guardians_count": 1,
            },
            "Attended status contradicts the provided arrived participant counts.",
            id="attended_false_contradicts_nonzero_arrived_counts",
        ),
        pytest.param(
            {
                "attended": True,
                "arrived_children_count": 0,
                "arrived_guardians_count": 0,
            },
            "Attended status contradicts the provided arrived participant counts.",
            id="attended_true_contradicts_zero_arrived_counts",
        ),
        pytest.param(
            {
                "attended": None,
                "arrived_children_count": 1,
                "arrived_guardians_count": 0,
            },
            "Attended status contradicts the provided arrived participant counts.",
            id="attended_none_contradicts_explicit_arrived_counts",
        ),
        pytest.param(
            {},
            '"attended" or arrived participant counts are required.',
            id="empty_input_without_attended_or_counts",
        ),
    ],
)
def test_enrolment_api_service_apply_arrival_validation_errors(
    arrival_input,
    expected_message,
):
    """
    Verify EnrolmentAPIService.apply_arrival raises DataValidationError when
    only one arrived count is provided, counts are negative or exceed booked
    counts, attended contradicts counts, or neither attended nor counts are given.
    """
    enrolment = EnrolmentFactory(
        extra_children_count=1,
        extra_guardians_count=1,
    )

    with pytest.raises(DataValidationError, match=re.escape(expected_message)):
        EnrolmentAPIService.apply_arrival(
            enrolment,
            **arrival_input,
        )


@pytest.mark.django_db
def test_enrolment_api_service_apply_arrival_reloads_and_saves_only_arrival_fields():
    enrolment = EnrolmentFactory(extra_children_count=0, extra_guardians_count=0)
    Enrolment.objects.filter(pk=enrolment.pk).update(extra_children_count=2)

    enrolment.extra_guardians_count = 1  # unsaved stale/local change
    updated = EnrolmentAPIService.apply_arrival(
        enrolment,
        arrived_children_count=3,
        arrived_guardians_count=1,
    )

    updated.refresh_from_db()
    assert updated.extra_children_count == 2
    assert updated.extra_guardians_count == 0
    assert updated.arrived_children_count == 3
    assert updated.arrived_guardians_count == 1
    assert enrolment.extra_children_count == 2


@pytest.mark.django_db
def test_enrolment_api_service_apply_arrival_deleted_enrolment():
    """An enrolment deleted before the row lock is taken raises a typed API error."""
    enrolment = EnrolmentFactory()
    Enrolment.objects.filter(pk=enrolment.pk).delete()

    with pytest.raises(ObjectDoesNotExistError):
        EnrolmentAPIService.apply_arrival(
            enrolment,
            arrived_children_count=1,
            arrived_guardians_count=1,
        )


@pytest.mark.django_db
def test_occurrence_api_service_create_occurrence_with_attended_override():
    event = EventFactory(ticket_system=Event.INTERNAL, capacity_per_occurrence=20)
    venue = VenueFactory(project=event.project)
    language, _ = Language.objects.get_or_create(
        alpha_3_code="fin", defaults={"can_be_occurrence_language": True}
    )
    info = MagicMock(
        spec=GraphQLResolveInfo,
        context=SimpleNamespace(user=UserFactory(is_superuser=True)),
        schema=schema.graphql_schema,
    )

    occurrence = OccurrenceAPIService.create_occurrence(
        info,
        {
            "time": now() + timedelta(days=1),
            "event_id": get_global_id(event),
            "venue_id": get_global_id(venue),
            "language_ids": [get_global_id(language)],
            "attended_children_count_override": 4,
            "attended_adults_count_override": 3,
        },
    )

    assert occurrence.calculated_attended_seats == 0
    assert occurrence.attended_seats == 7
    assert occurrence.get_attended_seats() == 7
    assert occurrence.get_remaining_empty_seats() == 13

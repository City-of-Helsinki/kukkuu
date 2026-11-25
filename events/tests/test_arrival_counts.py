import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from guardian.shortcuts import assign_perm

from common.tests.conftest import create_api_client_with_user
from common.tests.utils import assert_match_error_code, assert_permission_denied
from common.utils import get_global_id
from events.factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    OccurrenceFactory,
    TicketmasterEventFactory,
)
from events.models import Enrolment, Event, Occurrence
from events.tests.mutations import (
    SET_ENROLMENT_ATTENDANCE_WITH_COUNTS_MUTATION,
    UPDATE_OCCURRENCE_MUTATION,
    UPDATE_OCCURRENCE_WITH_OVERRIDE_MUTATION,
    UPDATE_TICKET_ATTENDED_MUTATION,
)
from events.tests.queries import (
    OCCURRENCE_ARRIVAL_FIELDS_QUERY,
    OCCURRENCE_SINGLE_FIELD_QUERY_TEMPLATE,
    OCCURRENCES_ARRIVAL_FIELDS_QUERY,
    VERIFY_TICKET_QUERY,
)
from kukkuu.consts import API_USAGE_ERROR, DATA_VALIDATION_ERROR, GENERAL_ERROR
from organisations.factories import OrganisationFactory
from projects.models import ProjectPermission
from users.cache import UserRequestCache
from users.factories import UserFactory


@pytest.mark.parametrize(
    "extra_children,extra_guardians,attended,arrived_children,arrived_guardians,attended_seats",
    [
        (None, None, None, None, None, 0),
        (None, None, False, None, None, 0),
        (None, None, True, None, None, 2),
        (0, 0, True, None, None, 2),
        (2, 1, True, None, None, 5),
        (2, 1, True, 1, 2, 3),
        (2, 1, False, 0, 0, 0),
        (None, None, True, 1, 1, 2),
    ],
)
def test_enrolment_arrived_seats_property_and_queryset(
    occurrence,
    extra_children,
    extra_guardians,
    attended,
    arrived_children,
    arrived_guardians,
    attended_seats,
):
    """
    Verify Enrolment.arrived_seats and OccurrenceQueryset.with_attended_seats()
    match for explicit arrived counts as well as fallback cases without counts.
    """
    enrolment = EnrolmentFactory(
        occurrence=occurrence,
        extra_children_count=extra_children,
        extra_guardians_count=extra_guardians,
        attended=attended,
        arrived_children_count=arrived_children,
        arrived_guardians_count=arrived_guardians,
    )
    assert enrolment.arrived_seats == attended_seats

    annotated = Occurrence.objects.with_attended_seats().get(pk=occurrence.pk)
    assert annotated.calculated_attended_seats == attended_seats
    assert annotated.attended_seats == attended_seats
    assert occurrence.get_attended_seats() == attended_seats


@pytest.mark.parametrize(
    "arrived_children,arrived_guardians,attended,should_fail",
    [
        pytest.param(
            1,
            None,
            True,
            True,
            id="missing_arrived_guardians_count",
        ),
        pytest.param(
            None,
            1,
            True,
            True,
            id="missing_arrived_children_count",
        ),
        pytest.param(
            2,
            1,
            True,
            True,
            id="arrived_children_exceeds_single_booked_child_on_non_family_enrolment",
        ),
        pytest.param(
            1,
            2,
            True,
            True,
            id="arrived_guardians_exceeds_single_booked_guardian_on_non_family_enrolment",
        ),
        pytest.param(
            1,
            1,
            False,
            True,
            id="attended_false_contradicts_nonzero_arrived_counts",
        ),
        pytest.param(
            0,
            0,
            True,
            True,
            id="attended_true_contradicts_zero_arrived_counts",
        ),
        pytest.param(
            0,
            0,
            None,
            True,
            id="attended_none_contradicts_explicit_zero_arrived_counts",
        ),
        pytest.param(
            1,
            1,
            True,
            False,
            id="valid_all_booked_participants_arrived",
        ),
        pytest.param(
            0,
            0,
            False,
            False,
            id="valid_zero_arrived_when_marked_not_attended",
        ),
    ],
)
def test_enrolment_clean_arrived_count_invariants(
    occurrence, arrived_children, arrived_guardians, attended, should_fail
):
    """
    Verify Enrolment.clean() rejects mismatched pairs, out-of-bounds arrived
    counts, and attended flags contradicting arrived counts (Django admin safety).
    """
    # Non-family enrolment with no extra participants (extra_children_count=0,
    # extra_guardians_count=0), meaning only 1 child and 1 guardian are booked
    # (booked_children_count == 1, booked_guardians_count == 1).
    occurrence.event.participants_per_invite = Event.CHILD_AND_GUARDIAN
    enrolment = Enrolment(
        occurrence=occurrence,
        extra_children_count=0,
        extra_guardians_count=0,
        attended=attended,
        arrived_children_count=arrived_children,
        arrived_guardians_count=arrived_guardians,
    )
    if should_fail:
        with pytest.raises(ValidationError):
            enrolment.clean()
    else:
        enrolment.clean()


@pytest.mark.parametrize(
    "override,expected_effective",
    [
        (None, 3),
        ((0, 0), 0),
        ((6, 9), 15),
    ],
)
def test_occurrence_attended_count_override_precedence(
    project, override, expected_effective
):
    """
    Verify the children + adults arrival override (including 0 + 0) overrides
    calculated arrived seats on Occurrence, Event, and EventGroup while keeping
    calculated_attended_seats intact.
    """
    event_group = EventGroupFactory(project=project)
    event = EventFactory(project=project, event_group=event_group)
    children, adults = override if override else (None, None)
    occ = OccurrenceFactory(
        event=event,
        attended_children_count_override=children,
        attended_adults_count_override=adults,
    )
    assert occ.attended_count_override == (
        None if override is None else children + adults
    )
    # Enrolment 1: 3 booked children (1 default + 2 extra) and
    # 2 booked guardians (1 default + 1 extra) = 5 total seats.
    # Arrived: 2 children + 1 guardian = 3 arrived seats.
    enrolment_1 = EnrolmentFactory(
        occurrence=occ,
        extra_children_count=2,
        extra_guardians_count=1,
        attended=True,
        arrived_children_count=2,
        arrived_guardians_count=1,
    )
    # Enrolment 2: 2 booked children (1 default + 1 extra) and
    # 1 booked guardian (no extras) = 3 total seats.
    # Unhandled (attended=None), so all 3 booked seats are pending arrival.
    enrolment_2 = EnrolmentFactory(
        occurrence=occ,
        extra_children_count=1,
        extra_guardians_count=0,
        attended=None,
    )

    annotated = (
        Occurrence.objects.with_attended_seats()
        .with_handled_enrolment_count()
        .with_pending_arrival_seats()
        .get(pk=occ.pk)
    )
    assert annotated.calculated_attended_seats == enrolment_1.arrived_seats == 3
    assert annotated.attended_seats == expected_effective
    assert annotated.handled_enrolment_count == 1
    assert annotated.pending_arrival_seats == enrolment_2.total_seats == 3
    assert occ.get_calculated_attended_seats() == enrolment_1.arrived_seats == 3
    assert occ.get_attended_seats() == expected_effective
    assert occ.get_handled_enrolment_count() == 1
    assert occ.get_pending_arrival_seats() == enrolment_2.total_seats == 3
    assert occ.get_remaining_empty_seats() == max(
        event.capacity_per_occurrence - expected_effective, 0
    )
    assert event.get_attended_seats() == expected_effective
    assert event_group.get_attended_seats() == expected_effective


@pytest.mark.parametrize(
    "field_name",
    [
        "attendedCountOverride",
        "attendedSeats",
        "calculatedAttendedSeats",
        "handledEnrolmentCount",
        "pendingArrivalSeats",
        "remainingEmptySeats",
    ],
)
def test_occurrence_arrival_fields_permission_denied_for_non_admin(
    api_client, user_api_client, guardian_api_client, project, occurrence, field_name
):
    """
    Verify anonymous users, normal users, guardians, and members of another
    organisation cannot read private arrival/override fields on OccurrenceNode.
    """
    other_org = OrganisationFactory(name="Other Org")
    other_org_user = UserFactory()
    other_org_user.organisations.add(other_org)
    assign_perm(ProjectPermission.ADMIN.value, other_org_user, project)
    other_org_client = create_api_client_with_user(other_org_user)

    query = OCCURRENCE_SINGLE_FIELD_QUERY_TEMPLATE % field_name
    variables = {"id": get_global_id(occurrence)}

    for client in (api_client, user_api_client, guardian_api_client, other_org_client):
        executed = client.execute(query, variables=variables)
        assert_permission_denied(executed)


def test_occurrence_arrival_fields_accessible_to_org_admin_and_sysadmin(
    project_user_api_client, project, occurrence, django_assert_num_queries
):
    """
    Verify an organisation admin for the event's project can query all explicit
    capacity/arrival metrics and override indicator fields on OccurrenceNode.
    """
    capacity = 20
    attended_children_override = 5
    attended_adults_override = 7
    attended_count_override = attended_children_override + attended_adults_override
    occurrence.event.capacity_per_occurrence = capacity
    occurrence.event.save()
    occurrence.attended_children_count_override = attended_children_override
    occurrence.attended_adults_count_override = attended_adults_override
    occurrence.save()

    # Enrolment 1: 2 booked children (1 default + 1 extra) and
    # 2 booked guardians (1 default + 1 extra) = 4 total seats.
    # Marked attended with 2 arrived children and 1 arrived guardian = 3 arrived seats.
    enrolment_1 = EnrolmentFactory(
        occurrence=occurrence,
        extra_children_count=1,
        extra_guardians_count=1,
        attended=True,
        arrived_children_count=2,
        arrived_guardians_count=1,
    )
    # Enrolment 2: 1 booked child + 1 booked guardian (no extra participants) = 2 total seats.
    # Marked absent (attended=False) with 0 arrived children and 0 arrived guardians.
    enrolment_2 = EnrolmentFactory(
        occurrence=occurrence,
        extra_children_count=0,
        extra_guardians_count=0,
        attended=False,
        arrived_children_count=0,
        arrived_guardians_count=0,
    )
    # Enrolment 3: 2 booked children (1 default + 1 extra) and
    # 1 booked guardian (no extra guardians) = 3 total seats.
    # Attendance not yet handled (attended=None), so all 3 booked seats are pending arrival.
    enrolment_3 = EnrolmentFactory(
        occurrence=occurrence,
        extra_children_count=1,
        extra_guardians_count=0,
        attended=None,
    )

    # 11 queries total (constant regardless of the number of enrolments):
    # 1-3. Fetch user's administered_projects (django-guardian user/group perms + Project)
    # 4. Fetch Occurrence with all arrival/capacity annotations and select_related
    # 5. Prefetch venue translations
    # 6. Prefetch accessibilities
    # 7. Prefetch languages
    # 8. Prefetch language translations
    # 9. Memoise user's organisation IDs on info.context (1 query for all 7 protected fields)
    # 10. COUNT(*) for EnrolmentNodeConnection pagination
    # 11. Fetch occurrence's Enrolment rows (booked/arrived seats are computed in memory)
    with django_assert_num_queries(11):
        executed = project_user_api_client.execute(
            OCCURRENCE_ARRIVAL_FIELDS_QUERY,
            variables={"id": get_global_id(occurrence)},
        )
    assert "errors" not in executed

    expected_calculated_attended_seats = (
        enrolment_1.arrived_seats
        + enrolment_2.arrived_seats
        + enrolment_3.arrived_seats
    )
    expected_total_booked_seats = (
        enrolment_1.total_seats + enrolment_2.total_seats + enrolment_3.total_seats
    )
    assert executed["data"]["occurrence"] == {
        "id": get_global_id(occurrence),
        "attendedCountOverride": attended_count_override,
        "attendedChildrenCountOverride": attended_children_override,
        "attendedAdultsCountOverride": attended_adults_override,
        "attendedSeats": attended_count_override,
        "calculatedAttendedSeats": expected_calculated_attended_seats,
        "attendedEnrolmentCount": 1,
        "handledEnrolmentCount": 2,
        "pendingArrivalSeats": enrolment_3.total_seats,
        "remainingEmptySeats": capacity - attended_count_override,
        "enrolmentCount": 3,
        "seatCount": expected_total_booked_seats,
        "capacity": capacity,
        "enrolments": {
            "edges": [
                {
                    "node": {
                        "id": get_global_id(enrolment),
                        "attended": enrolment.attended,
                        "arrivedChildrenCount": enrolment.arrived_children_count,
                        "arrivedGuardiansCount": enrolment.arrived_guardians_count,
                        "bookedChildrenCount": enrolment.booked_children_count,
                        "bookedGuardiansCount": enrolment.booked_guardians_count,
                        "arrivedSeats": enrolment.arrived_seats,
                        "totalSeats": enrolment.total_seats,
                    }
                }
                for enrolment in (enrolment_1, enrolment_2, enrolment_3)
            ]
        },
    }


def test_occurrences_arrival_fields_query_count_does_not_scale_with_n(
    project_user_api_client, project, venue, django_assert_num_queries
):
    """
    Verify querying all arrival, override, and capacity fields across multiple
    occurrences executes a constant number of SQL queries (no N+1 queries as
    occurrences or enrolments per occurrence grow).
    """
    event = EventFactory(project=project, capacity_per_occurrence=30)
    for idx in range(4):
        occ = OccurrenceFactory(
            event=event,
            venue=venue,
            attended_children_count_override=4 if idx % 2 == 0 else None,
            attended_adults_count_override=6 if idx % 2 == 0 else None,
        )
        EnrolmentFactory(
            occurrence=occ,
            extra_children_count=1,
            extra_guardians_count=1,
            attended=True,
            arrived_children_count=2,
            arrived_guardians_count=1,
        )
        EnrolmentFactory(
            occurrence=occ,
            extra_children_count=0,
            extra_guardians_count=0,
            attended=None,
        )

    # Prime the user's cached `administered_projects` property so we measure the
    # GraphQL execution queries deterministically.
    _ = project_user_api_client.user.administered_projects
    UserRequestCache.invalidate(project_user_api_client.context)

    # 7 queries total across all 4 occurrences (and 8 enrolments):
    # 1. COUNT(*) for OccurrenceNodeConnection pagination
    # 2. Fetch all Occurrences with arrival/capacity annotations and select_related
    # 3. Prefetch venue translations
    # 4. Prefetch accessibilities
    # 5. Prefetch languages
    # 6. Prefetch language translations
    # 7. Memoise user's organisation IDs once on info.context for all 4x7 protected field resolvers
    with django_assert_num_queries(7):
        executed = project_user_api_client.execute(OCCURRENCES_ARRIVAL_FIELDS_QUERY)

    assert "errors" not in executed
    assert len(executed["data"]["occurrences"]["edges"]) == 4


def test_update_occurrence_set_and_clear_attended_count_override(
    project_user_api_client, occurrence
):
    """
    Verify updateOccurrence can set attendedCountOverride (including 0) and
    subsequently clear it back to null so calculated seats take over again.
    """
    # Create an enrolment with 1 arrived child and 1 arrived guardian (2 arrived seats).
    enrolment = EnrolmentFactory(
        occurrence=occurrence,
        extra_children_count=0,
        extra_guardians_count=0,
        attended=True,
        arrived_children_count=1,
        arrived_guardians_count=1,
    )

    # Set both overrides to 0 via updateOccurrence. The effective attendedSeats
    # should report the manual override (0), while calculatedAttendedSeats continues
    # to reflect the actual arrived seats from enrolments (2).
    set_res = project_user_api_client.execute(
        UPDATE_OCCURRENCE_WITH_OVERRIDE_MUTATION,
        variables={
            "input": {
                "id": get_global_id(occurrence),
                "attendedChildrenCountOverride": 0,
                "attendedAdultsCountOverride": 0,
            }
        },
    )
    assert "errors" not in set_res
    occ_data = set_res["data"]["updateOccurrence"]["occurrence"]
    assert occ_data["attendedCountOverride"] == 0
    assert occ_data["attendedChildrenCountOverride"] == 0
    assert occ_data["attendedAdultsCountOverride"] == 0
    assert occ_data["attendedSeats"] == 0
    assert occ_data["calculatedAttendedSeats"] == enrolment.arrived_seats == 2

    # Non-zero values: the total is the sum of children and adults.
    sum_res = project_user_api_client.execute(
        UPDATE_OCCURRENCE_WITH_OVERRIDE_MUTATION,
        variables={
            "input": {
                "id": get_global_id(occurrence),
                "attendedChildrenCountOverride": 5,
                "attendedAdultsCountOverride": 7,
            }
        },
    )
    assert "errors" not in sum_res
    sum_data = sum_res["data"]["updateOccurrence"]["occurrence"]
    assert sum_data["attendedCountOverride"] == 12
    assert sum_data["attendedSeats"] == 12

    # Clear both back to None. The effective attendedSeats should
    # fall back to calculatedAttendedSeats (2).
    clear_res = project_user_api_client.execute(
        UPDATE_OCCURRENCE_WITH_OVERRIDE_MUTATION,
        variables={
            "input": {
                "id": get_global_id(occurrence),
                "attendedChildrenCountOverride": None,
                "attendedAdultsCountOverride": None,
            }
        },
    )
    assert "errors" not in clear_res
    cleared_data = clear_res["data"]["updateOccurrence"]["occurrence"]
    assert cleared_data["attendedCountOverride"] is None
    assert cleared_data["attendedChildrenCountOverride"] is None
    assert cleared_data["attendedAdultsCountOverride"] is None
    assert cleared_data["attendedSeats"] == enrolment.arrived_seats == 2
    assert cleared_data["calculatedAttendedSeats"] == enrolment.arrived_seats == 2


@pytest.mark.parametrize(
    "input_override",
    [
        {"attendedChildrenCountOverride": 3},
        {"attendedAdultsCountOverride": 3},
        {"attendedChildrenCountOverride": 3, "attendedAdultsCountOverride": None},
        {"attendedChildrenCountOverride": None, "attendedAdultsCountOverride": 3},
        {"attendedChildrenCountOverride": -1, "attendedAdultsCountOverride": 1},
        {"attendedChildrenCountOverride": 32768, "attendedAdultsCountOverride": 1},
        {"attendedChildrenCountOverride": 1, "attendedAdultsCountOverride": -1},
        {"attendedChildrenCountOverride": 1, "attendedAdultsCountOverride": 32768},
    ],
)
def test_update_occurrence_invalid_attended_overrides_rejected(
    project_user_api_client, occurrence, input_override
):
    """
    Verify half-filled or out-of-range attended overrides are rejected with
    DataValidationError (before hitting the DB check constraint).
    """
    executed = project_user_api_client.execute(
        UPDATE_OCCURRENCE_MUTATION,
        variables={"input": {"id": get_global_id(occurrence), **input_override}},
    )
    assert_match_error_code(executed, DATA_VALIDATION_ERROR)
    occurrence.refresh_from_db()
    assert occurrence.attended_children_count_override is None
    assert occurrence.attended_adults_count_override is None


def test_update_occurrence_clearing_only_one_existing_override_rejected(
    project_user_api_client, occurrence
):
    """
    Verify that when both overrides are stored, clearing just one is rejected and
    omitting a key keeps its stored value.
    """
    occurrence.attended_children_count_override = 2
    occurrence.attended_adults_count_override = 3
    occurrence.save()

    executed = project_user_api_client.execute(
        UPDATE_OCCURRENCE_MUTATION,
        variables={
            "input": {
                "id": get_global_id(occurrence),
                "attendedAdultsCountOverride": None,
            }
        },
    )
    assert_match_error_code(executed, DATA_VALIDATION_ERROR)

    ok = project_user_api_client.execute(
        UPDATE_OCCURRENCE_MUTATION,
        variables={
            "input": {
                "id": get_global_id(occurrence),
                "attendedChildrenCountOverride": 4,
            }
        },
    )
    assert "errors" not in ok
    occurrence.refresh_from_db()
    assert occurrence.attended_children_count_override == 4
    assert occurrence.attended_adults_count_override == 3


def test_occurrence_attended_overrides_pair_enforced_by_clean_and_db(occurrence):
    """
    Verify Occurrence.clean() and the DB check constraint both reject a
    half-filled override pair, and the combined property is None for it.
    """
    occurrence.attended_children_count_override = 1
    assert occurrence.attended_count_override is None
    with pytest.raises(ValidationError):
        occurrence.clean()
    with pytest.raises(IntegrityError), transaction.atomic():
        occurrence.save()


def test_update_occurrence_external_event_attended_count_override_rejected(
    project_user_api_client,
):
    """
    Verify setting the attended overrides on an external ticket system occurrence
    is rejected with API_USAGE_ERROR, matching capacityOverride.
    """
    event = TicketmasterEventFactory()
    project_user_api_client.user.administered_projects = [event.project]
    occ = event.occurrences.first()

    executed = project_user_api_client.execute(
        UPDATE_OCCURRENCE_MUTATION,
        variables={
            "input": {
                "id": get_global_id(occ),
                "attendedChildrenCountOverride": 4,
                "attendedAdultsCountOverride": 6,
            }
        },
    )
    assert_match_error_code(executed, API_USAGE_ERROR)

    # Also verify Occurrence.clean() rejects the overrides on external events
    # and arrival getters return 0.
    occ.attended_children_count_override = 4
    occ.attended_adults_count_override = 6
    with pytest.raises(ValidationError):
        occ.clean()
    occ.attended_children_count_override = None
    occ.attended_adults_count_override = None
    assert occ.get_attended_seats() == 0
    assert occ.get_handled_enrolment_count() == 0
    assert occ.get_pending_arrival_seats() == 0
    assert occ.get_remaining_empty_seats() == 0
    assert event.get_attended_seats() == 0


@pytest.mark.parametrize(
    "extra_children,extra_guardians,arrived_children,arrived_guardians,expected_attended",
    [
        (2, 1, 2, 1, True),
        (2, 1, 0, 0, False),
        (None, None, 1, 1, True),
    ],
)
def test_verify_and_update_ticket_arrived_counts(
    api_client,
    django_assert_num_queries,
    extra_children,
    extra_guardians,
    arrived_children,
    arrived_guardians,
    expected_attended,
):
    """
    Verify verifyTicket exposes booked/arrived counts and all doorway summary
    metrics, and updateTicketAttended records exact arrived children/adults and
    derives attended = (children + adults > 0).
    """
    capacity = 20
    event = EventFactory(
        capacity_per_occurrence=capacity, participants_per_invite=Event.FAMILY
    )
    occ = OccurrenceFactory(event=event, time=timezone.now())
    enrolment = EnrolmentFactory(
        occurrence=occ,
        extra_children_count=extra_children,
        extra_guardians_count=extra_guardians,
    )
    # Second enrolment left unhandled (attended=None): 2 booked children + 1 guardian = 3 seats.
    pending_enrolment = EnrolmentFactory(
        occurrence=occ,
        extra_children_count=1,
        extra_guardians_count=0,
        attended=None,
    )

    # 4 queries for verifyTicket:
    # 1. Fetch Enrolment with end_time and select_related("occurrence")
    # 2. Fetch Occurrence with all 6 arrival/capacity annotations and select_related("event", "venue")
    # 3. Prefetch event translations
    # 4. Prefetch venue translations
    with django_assert_num_queries(4):
        verify_res = api_client.execute(
            VERIFY_TICKET_QUERY,
            variables={"referenceId": enrolment.reference_id},
        )
    assert "errors" not in verify_res
    ticket = verify_res["data"]["verifyTicket"]
    assert ticket["bookedChildrenCount"] == enrolment.booked_children_count
    assert ticket["bookedGuardiansCount"] == enrolment.booked_guardians_count
    assert ticket["arrivedChildrenCount"] is None
    assert ticket["arrivedGuardiansCount"] is None

    # 11 queries for updateTicketAttended (including savepoint + UPDATE + auditlog):
    # 1-2. SAVEPOINT + Fetch Enrolment with end_time and select_related("occurrence")
    # 3-7. Auditlog pre-save state lookup + UPDATE events_enrolment + INSERT auditlog_logentry
    # 8-11. Fetch annotated Occurrence + prefetch event/venue translations + RELEASE SAVEPOINT
    with django_assert_num_queries(11):
        update_res = api_client.execute(
            UPDATE_TICKET_ATTENDED_MUTATION,
            variables={
                "input": {
                    "referenceId": enrolment.reference_id,
                    "arrivedChildrenCount": arrived_children,
                    "arrivedGuardiansCount": arrived_guardians,
                }
            },
        )
    assert "errors" not in update_res
    updated_ticket = update_res["data"]["updateTicketAttended"]["ticket"]
    assert updated_ticket["attended"] is expected_attended
    assert updated_ticket["arrivedChildrenCount"] == arrived_children
    assert updated_ticket["arrivedGuardiansCount"] == arrived_guardians

    expected_attended_seats = arrived_children + arrived_guardians
    assert updated_ticket["occurrenceArrivalStatus"] == {
        "enrolmentCount": 2,
        "handledEnrolmentCount": 1,
        "attendedEnrolmentCount": 1 if expected_attended else 0,
        "attendedSeats": expected_attended_seats,
        "reservedSeats": enrolment.total_seats + pending_enrolment.total_seats,
        "capacity": capacity,
        "pendingArrivalSeats": pending_enrolment.total_seats,
        "remainingEmptySeats": capacity - expected_attended_seats,
    }


def test_update_ticket_attended_invalid_ticket_rejected(api_client, past):
    """
    Verify updateTicketAttended rejects expired tickets with an invalid-ticket error.
    """
    occ = OccurrenceFactory(time=past)
    enrolment = EnrolmentFactory(occurrence=occ)

    executed = api_client.execute(
        UPDATE_TICKET_ATTENDED_MUTATION,
        variables={
            "input": {
                "referenceId": enrolment.reference_id,
                "arrivedChildrenCount": 1,
                "arrivedGuardiansCount": 1,
            }
        },
    )
    assert_match_error_code(executed, GENERAL_ERROR)
    assert "The ticket was invalid." in executed["errors"][0]["message"]


def test_set_enrolment_attendance_arrival_wiring(
    project_user_api_client, occurrence, child_with_user_guardian
):
    """
    Verify SetEnrolmentAttendanceMutation wires explicit arrived counts, boolean
    attended defaulting, and validation errors through EnrolmentAPIService.
    """
    enrolment = EnrolmentFactory(
        occurrence=occurrence,
        child=child_with_user_guardian,
        extra_children_count=2,
        extra_guardians_count=1,
    )
    enrolment_gid = get_global_id(enrolment)

    # Explicit counts derive attended=True
    res = project_user_api_client.execute(
        SET_ENROLMENT_ATTENDANCE_WITH_COUNTS_MUTATION,
        variables={
            "input": {
                "enrolmentId": enrolment_gid,
                "arrivedChildrenCount": 2,
                "arrivedGuardiansCount": 1,
            }
        },
    )
    assert "errors" not in res
    assert res["data"]["setEnrolmentAttendance"]["enrolment"] == {
        "id": enrolment_gid,
        "attended": True,
        "bookedChildrenCount": 3,
        "bookedGuardiansCount": 2,
        "arrivedChildrenCount": 2,
        "arrivedGuardiansCount": 1,
        "arrivedSeats": 3,
    }

    # Boolean attended=False defaults counts to 0/0
    res_absent = project_user_api_client.execute(
        SET_ENROLMENT_ATTENDANCE_WITH_COUNTS_MUTATION,
        variables={"input": {"enrolmentId": enrolment_gid, "attended": False}},
    )
    assert "errors" not in res_absent
    assert res_absent["data"]["setEnrolmentAttendance"]["enrolment"] == {
        "id": enrolment_gid,
        "attended": False,
        "bookedChildrenCount": 3,
        "bookedGuardiansCount": 2,
        "arrivedChildrenCount": 0,
        "arrivedGuardiansCount": 0,
        "arrivedSeats": 0,
    }

    # Partial pair propagates DataValidationError
    res_err = project_user_api_client.execute(
        SET_ENROLMENT_ATTENDANCE_WITH_COUNTS_MUTATION,
        variables={"input": {"enrolmentId": enrolment_gid, "arrivedChildrenCount": 1}},
    )
    assert_match_error_code(res_err, DATA_VALIDATION_ERROR)

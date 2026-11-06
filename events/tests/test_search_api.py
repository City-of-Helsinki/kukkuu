from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone
from freezegun import freeze_time
from graphql_relay import to_global_id

from children.factories import ChildWithGuardianFactory
from common.tests.utils import assert_match_error_code, assert_permission_denied
from common.utils import get_global_id
from events.factories import (
    EnrolmentFactory,
    EventFactory,
    EventGroupFactory,
    OccurrenceFactory,
    TicketmasterEventFactory,
    TicketSystemPasswordFactory,
)
from events.models import Event, Occurrence
from events.tests.queries import EVENTS_SEARCH_QUERY
from kukkuu.consts import API_USAGE_ERROR, OBJECT_DOES_NOT_EXIST_ERROR
from tags.factories import ThemePathFactory
from users.factories import GuardianFactory


@pytest.mark.django_db
def test_occurrence_with_remaining_capacity_annotation(project, future):
    """
    Verify that OccurrenceQuerySet.with_remaining_capacity() annotates
    remaining capacity identically to Occurrence.get_remaining_capacity().

    Tests default capacity, capacity_override, clamping to 0 when overfull,
    and handling of events with null capacity.
    """
    event_default = EventFactory(
        project=project, published_at=timezone.now(), capacity_per_occurrence=10
    )
    occ_default = OccurrenceFactory(event=event_default, time=future)
    EnrolmentFactory(
        occurrence=occ_default, extra_children_count=1, extra_guardians_count=1
    )  # 1 child + 1 extra child + 1 guardian + 1 extra guardian = 4 seats reserved

    occ_override = OccurrenceFactory(
        event=event_default, time=future, capacity_override=5
    )
    EnrolmentFactory(
        occurrence=occ_override, extra_children_count=0, extra_guardians_count=0
    )  # 1 child + 1 guardian = 2 seats reserved -> 3 remaining

    occ_overfull = OccurrenceFactory(
        event=event_default, time=future, capacity_override=2
    )
    EnrolmentFactory(
        occurrence=occ_overfull, extra_children_count=1, extra_guardians_count=0
    )  # 2 children + 1 guardian = 3 seats reserved on capacity 2 -> clamped to 0

    event_null_cap = EventFactory(
        project=project, published_at=timezone.now(), capacity_per_occurrence=None
    )
    occ_null_cap = OccurrenceFactory(event=event_null_cap, time=future)

    annotated = {
        occ.id: occ
        for occ in Occurrence.objects.with_remaining_capacity().filter(
            id__in=[
                occ_default.id,
                occ_override.id,
                occ_overfull.id,
                occ_null_cap.id,
            ]
        )
    }

    # Default capacity 10 minus 4 reserved seats = 6 remaining
    assert annotated[occ_default.id].remaining_capacity == 6
    assert (
        annotated[occ_default.id].get_remaining_capacity()
        == occ_default.get_remaining_capacity()
        == 6
    )
    # Capacity override 5 minus 2 reserved seats = 3 remaining
    assert annotated[occ_override.id].remaining_capacity == 3
    # Overfull occurrence (3 reserved on capacity 2) is clamped to 0
    assert annotated[occ_overfull.id].remaining_capacity == 0
    # Null capacity on event produces 0 remaining capacity
    assert annotated[occ_null_cap.id].remaining_capacity == 0


@pytest.mark.django_db
def test_events_search_unauthenticated(api_client, child_with_random_guardian):
    """
    Ensure unauthenticated requests cannot access the events search API.

    Proves that calling eventsSearchQuery without an authorization token
    returns a PERMISSION_DENIED error rather than leaking event data.
    """
    executed = api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": get_global_id(child_with_random_guardian)},
    )
    assert_permission_denied(executed)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invalid_id_fn",
    [
        lambda other_child: get_global_id(other_child),
        lambda _other_child: "",
        lambda _other_child: "not-base64-!!!",
        lambda _other_child: to_global_id("ChildNode", "not-a-uuid"),
        lambda other_child: to_global_id("ProjectNode", other_child.project_id),
    ],
)
def test_events_search_not_own_child_returns_empty(
    guardian_api_client, child_with_random_guardian, future, invalid_id_fn
):
    """
    Ensure that querying with an unauthorized or malformed childId returns empty data.

    Tests multiple different invalid ID forms:
    - Another guardian's child global ID (data isolation)
    - Empty string ID
    - Non-base64 malformed string
    - Non-UUID Relay ID
    - Non-ChildNode Relay global ID (e.g. ProjectNode)

    Proves that:
    - data.child is None (cannot view child)
    - data.events.count == 0 (no events returned for unauthorized child)
    - data.events.edges == [] (empty list)
    """
    event = EventFactory(
        project=child_with_random_guardian.project,
        published_at=timezone.now(),
    )
    OccurrenceFactory(event=event, time=future)

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": invalid_id_fn(child_with_random_guardian)},
    )
    # child is None because user lacks view permission (or child ID is invalid)
    assert executed["data"]["child"] is None
    # count is 0 because child filtering requires a viewable child
    assert executed["data"]["events"]["count"] == 0
    assert executed["data"]["events"]["edges"] == []


@pytest.mark.django_db
def test_events_search_cannot_leak_enrolment_denied_reason_for_other_child(
    guardian_api_client, child_with_random_guardian, project, future
):
    """
    Verify that guardians cannot probe enrolment denied reasons for other children.

    Even if a guardian passes their own childId to the top-level `events(childId: ...)`
    connection, querying `enrolmentDeniedReason(childId: otherChildId)` on the event
    node must raise an ObjectDoesNotExistError rather than revealing eligibility.
    """
    own_child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    event = EventFactory(project=project, published_at=timezone.now())
    OccurrenceFactory(event=event, time=future)

    query = """
    query LeakCheck($ownChildId: ID!, $otherChildId: ID!) {
      events(childId: $ownChildId) {
        edges {
          node {
            id
            enrolmentDeniedReason(childId: $otherChildId)
          }
        }
      }
    }
    """
    executed = guardian_api_client.execute(
        query,
        variables={
            "ownChildId": get_global_id(own_child),
            "otherChildId": get_global_id(child_with_random_guardian),
        },
    )
    assert_match_error_code(executed, OBJECT_DOES_NOT_EXIST_ERROR)
    # Ensure no data leaked: the field must resolve to None in the response data
    assert (
        executed["data"]["events"]["edges"][0]["node"]["enrolmentDeniedReason"] is None
    )


@pytest.mark.django_db
def test_events_search_project_user_permissions(
    project_user_api_client,
    wrong_project_api_client,
    child_with_random_guardian,
    future,
):
    """
    Verify project user / staff access controls on the search API.

    Proves that:
    - A project administrator can search for children belonging to their project (count == 1).
    - An administrator of an unrelated project receives an empty result (count == 0)
      because they lack permission to view this child.
    """
    event = EventFactory(
        project=child_with_random_guardian.project,
        published_at=timezone.now(),
    )
    OccurrenceFactory(event=event, time=future)
    child_gid = get_global_id(child_with_random_guardian)

    # Project user administering this project can search for child
    executed = project_user_api_client.execute(
        EVENTS_SEARCH_QUERY, variables={"childId": child_gid}
    )
    assert executed.get("errors") is None
    # Exactly 1 event returned: user has project admin privileges for this child's project
    assert executed["data"]["events"]["count"] == 1

    # Project user without admin access to this child's project returns empty
    executed = wrong_project_api_client.execute(
        EVENTS_SEARCH_QUERY, variables={"childId": child_gid}
    )
    # Child is None and count is 0 because user lacks privileges in this project
    assert executed["data"]["child"] is None
    assert executed["data"]["events"]["count"] == 0
    assert executed["data"]["events"]["edges"] == []


@pytest.mark.django_db
def test_events_search_unpublished_and_other_project_never_returned(
    project_user_api_client, project, another_project, future
):
    """
    Verify that search strictly returns only published events in the child's project.

    Creates 4 events under the user's project/organisation:
    1. Published event in child's project (should be returned)
    2. Unpublished event (published_at=None) (must NOT be returned)
    3. Event inside an unpublished EventGroup (must NOT be returned)
    4. Published event belonging to another project (must NOT be returned)

    Proves that exactly 1 event (the published event) is returned, and unpublished
    or other-project events are never exposed through the search API.
    """
    guardian = GuardianFactory(user=project_user_api_client.user)
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian,
        project=project,
    )
    user_org = project_user_api_client.user.organisations.first()

    published_event = EventFactory(
        project=project, organisation=user_org, published_at=timezone.now()
    )
    OccurrenceFactory(event=published_event, time=future)

    unpublished_event = EventFactory(
        project=project, organisation=user_org, published_at=None
    )
    OccurrenceFactory(event=unpublished_event, time=future)

    unpublished_group = EventGroupFactory(project=project, published_at=None)
    event_in_unpublished_group = EventFactory(
        project=project,
        organisation=user_org,
        event_group=unpublished_group,
        published_at=timezone.now(),
    )
    OccurrenceFactory(event=event_in_unpublished_group, time=future)

    other_project_event = EventFactory(
        project=another_project, published_at=timezone.now()
    )
    OccurrenceFactory(event=other_project_event, time=future)

    executed = project_user_api_client.execute(
        EVENTS_SEARCH_QUERY, variables={"childId": get_global_id(child)}
    )
    assert executed.get("errors") is None
    returned_ids = [edge["node"]["id"] for edge in executed["data"]["events"]["edges"]]
    # Exactly 1 event returned: only the published event in the child's project
    assert returned_ids == [get_global_id(published_event)]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "extra_vars",
    [
        {"availableOnly": True},
        {"startDate": "2026-11-10"},
        {"languages": ["fi"]},
        {"themePaths": ["music"]},
        {"accessibility": ["wheelchair"]},
        {"familyOnly": True},
    ],
)
def test_events_search_args_without_child_id_raises_error(user_api_client, extra_vars):
    """
    Ensure search-specific filter arguments require childId.

    Verifies that passing availableOnly, startDate, languages, themePaths,
    accessibility, or familyOnly without childId raises an API_USAGE_ERROR.
    """
    query = """
    query EventsWithoutChild(
      $availableOnly: Boolean
      $startDate: Date
      $languages: [String]
      $themePaths: [String]
      $accessibility: [String]
      $familyOnly: Boolean
    ) {
      events(
        availableOnly: $availableOnly
        startDate: $startDate
        languages: $languages
        themePaths: $themePaths
        accessibility: $accessibility
        familyOnly: $familyOnly
      ) {
        count
      }
    }
    """
    executed = user_api_client.execute(query, variables=extra_vars)
    assert_match_error_code(executed, API_USAGE_ERROR)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "filter_args,expected_indices,description",
    [
        (
            {"familyOnly": True},
            [0, 1],
            "familyOnly matches only events with participants_per_invite == Event.FAMILY",
        ),
        (
            {"themePaths": ["circus"]},
            [2],
            "themePaths matches only events tagged with the circus theme path",
        ),
        (
            {"languages": ["SV"]},
            [0, 1],
            "languages matches upcoming occurrences in Swedish (case-insensitive)",
        ),
        (
            {"startDateOffset": 10, "languages": ["sv"]},
            [0],
            "startDate + languages requires a single occurrence satisfying both",
        ),
    ],
)
def test_events_search_filters_parametrized(
    guardian_api_client,
    project,
    past,
    filter_args,
    expected_indices,
    description,
):
    """
    Verify search filters individually and in combination using parametrization.

    Sets up 3 events:
    - Index 0 (ev_match): family event, music theme, occurrence on day 15 in Swedish.
    - Index 1 (ev_split): family event, music theme, day 5 in Swedish + day 15 in Finnish.
    - Index 2 (ev_past_sv): child+guardian event, circus theme, past in Swedish + day 15 in Finnish.
    """
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    now = timezone.now()
    day_5 = now + timedelta(days=5)
    day_15 = now + timedelta(days=15)

    tp_music = ThemePathFactory(slug="music", name="Musiikki", description="")
    tp_circus = ThemePathFactory(slug="circus", name="Sirkus", description="")

    ev_match = EventFactory(
        project=project,
        published_at=past,
        participants_per_invite=Event.FAMILY,
        theme_paths=[tp_music],
        name="Match",
    )
    OccurrenceFactory(event=ev_match, time=day_15, occurrence_language="sv")

    ev_split = EventFactory(
        project=project,
        published_at=past,
        participants_per_invite=Event.FAMILY,
        theme_paths=[tp_music],
        name="Split",
    )
    OccurrenceFactory(event=ev_split, time=day_5, occurrence_language="sv")
    OccurrenceFactory(event=ev_split, time=day_15, occurrence_language="fi")

    ev_past_sv = EventFactory(
        project=project,
        published_at=past,
        participants_per_invite=Event.CHILD_AND_GUARDIAN,
        theme_paths=[tp_circus],
        name="Past SV",
    )
    OccurrenceFactory(event=ev_past_sv, time=past, occurrence_language="sv")
    OccurrenceFactory(event=ev_past_sv, time=day_15, occurrence_language="fi")

    events = [ev_match, ev_split, ev_past_sv]
    expected_ids = {get_global_id(events[i]) for i in expected_indices}

    variables = {"childId": get_global_id(child)}
    for k, v in filter_args.items():
        if k == "startDateOffset":
            variables["startDate"] = (now + timedelta(days=v)).date().isoformat()
        else:
            variables[k] = v

    executed = guardian_api_client.execute(EVENTS_SEARCH_QUERY, variables=variables)
    assert executed.get("errors") is None
    actual_ids = {e["node"]["id"] for e in executed["data"]["events"]["edges"]}
    assert actual_ids == expected_ids, description


@pytest.mark.django_db
def test_events_search_returns_all_upcoming_occurrences_on_node(
    guardian_api_client, project, past
):
    """Verify that an event matching search filters returns all its upcoming occurrences."""
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    now = timezone.now()
    event = EventFactory(
        project=project,
        published_at=past,
        participants_per_invite=Event.FAMILY,
    )
    OccurrenceFactory(
        event=event, time=now + timedelta(days=5), occurrence_language="sv"
    )
    OccurrenceFactory(
        event=event, time=now + timedelta(days=15), occurrence_language="fi"
    )

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": get_global_id(child), "familyOnly": True},
    )
    assert executed.get("errors") is None
    node = executed["data"]["events"]["edges"][0]["node"]
    # Node includes both upcoming occurrences for UI card display
    assert len(node["occurrences"]["edges"]) == 2


@pytest.mark.django_db
def test_events_search_available_only_internal_event_with_seats(
    guardian_api_client, project, past, future
):
    """Internal event with >= 2 remaining seats is included."""
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    event = EventFactory(project=project, published_at=past, capacity_per_occurrence=10)
    OccurrenceFactory(event=event, time=future)

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": get_global_id(child), "availableOnly": True},
    )
    assert executed.get("errors") is None
    returned_ids = [e["node"]["id"] for e in executed["data"]["events"]["edges"]]
    assert returned_ids == [get_global_id(event)]


@pytest.mark.django_db
def test_events_search_available_only_internal_full_excluded(
    guardian_api_client, project, past, future
):
    """Internal event with remaining capacity < 2 seats is excluded."""
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    other_child = ChildWithGuardianFactory(project=project)
    event = EventFactory(project=project, published_at=past, capacity_per_occurrence=3)
    occ = OccurrenceFactory(event=event, time=future)
    # 2 seats reserved -> 1 seat left (< MIN_SEATS_PER_ENROLMENT)
    EnrolmentFactory(
        occurrence=occ,
        child=other_child,
        extra_children_count=0,
        extra_guardians_count=0,
    )

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": get_global_id(child), "availableOnly": True},
    )
    assert executed.get("errors") is None
    returned_ids = [e["node"]["id"] for e in executed["data"]["events"]["edges"]]
    assert returned_ids == []


@pytest.mark.django_db
def test_events_search_available_only_already_enrolled_excluded(
    guardian_api_client, project, past, future
):
    """Event the child is already enrolled in is excluded."""
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    event = EventFactory(project=project, published_at=past, capacity_per_occurrence=10)
    occ = OccurrenceFactory(event=event, time=future)
    EnrolmentFactory(occurrence=occ, child=child)

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": get_global_id(child), "availableOnly": True},
    )
    assert executed.get("errors") is None
    returned_ids = [e["node"]["id"] for e in executed["data"]["events"]["edges"]]
    assert returned_ids == []


@pytest.mark.django_db
def test_events_search_available_only_event_group_sibling_enrolled_excluded(
    guardian_api_client, project, past, future
):
    """Sibling event in an event group where child is already enrolled is excluded."""
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    group = EventGroupFactory(project=project, published_at=past)
    sibling = EventFactory(
        project=project,
        event_group=group,
        published_at=past,
        capacity_per_occurrence=10,
    )
    occ = OccurrenceFactory(event=sibling, time=future)
    EnrolmentFactory(occurrence=occ, child=child)

    event = EventFactory(
        project=project,
        event_group=group,
        published_at=past,
        capacity_per_occurrence=10,
    )
    OccurrenceFactory(event=event, time=future)

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": get_global_id(child), "availableOnly": True},
    )
    assert executed.get("errors") is None
    returned_ids = [e["node"]["id"] for e in executed["data"]["events"]["edges"]]
    assert returned_ids == []


@pytest.mark.django_db
def test_events_search_available_only_registration_opens_in_future_excluded(
    guardian_api_client, project, past, future
):
    """Event whose registration opens in the future is excluded."""
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    event = EventFactory(
        project=project,
        published_at=past,
        registration_opens_at=future,
        capacity_per_occurrence=10,
    )
    OccurrenceFactory(event=event, time=future + timedelta(days=5))

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": get_global_id(child), "availableOnly": True},
    )
    assert executed.get("errors") is None
    returned_ids = [e["node"]["id"] for e in executed["data"]["events"]["edges"]]
    assert returned_ids == []


@pytest.mark.django_db
def test_events_search_available_only_ticketmaster_with_passwords(
    guardian_api_client, project, past
):
    """External ticket system event with unassigned passwords is included."""
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    event = TicketmasterEventFactory(project=project, published_at=past)
    TicketSystemPasswordFactory(event=event, child=None, assigned_at=None)

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": get_global_id(child), "availableOnly": True},
    )
    assert executed.get("errors") is None
    returned_ids = [e["node"]["id"] for e in executed["data"]["events"]["edges"]]
    assert returned_ids == [get_global_id(event)]


@pytest.mark.django_db
def test_events_search_available_only_ticketmaster_exhausted_excluded(
    guardian_api_client, project, past
):
    """External ticket system event with zero unassigned passwords left is excluded."""
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    other_child = ChildWithGuardianFactory(project=project)
    event = TicketmasterEventFactory(project=project, published_at=past)
    TicketSystemPasswordFactory(event=event, child=other_child, assigned_at=past)

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": get_global_id(child), "availableOnly": True},
    )
    assert executed.get("errors") is None
    returned_ids = [e["node"]["id"] for e in executed["data"]["events"]["edges"]]
    assert returned_ids == []


@pytest.mark.django_db
def test_events_search_available_only_ticketmaster_already_assigned_excluded(
    guardian_api_client, project, past
):
    """External ticket event where child already has a password is excluded."""
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    event = TicketmasterEventFactory(project=project, published_at=past)
    TicketSystemPasswordFactory(event=event, child=child, assigned_at=past)
    TicketSystemPasswordFactory(event=event, child=None, assigned_at=None)

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": get_global_id(child), "availableOnly": True},
    )
    assert executed.get("errors") is None
    returned_ids = [e["node"]["id"] for e in executed["data"]["events"]["edges"]]
    assert returned_ids == []


@pytest.mark.django_db
def test_events_search_available_only_yearly_limit(
    guardian_api_client, project, past, future
):
    """Verify that events in a year where the child reached the yearly limit are excluded."""
    project.enrolment_limit = 2
    project.save()

    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    # Create 2 enrolments in future.year to exhaust the yearly limit
    ev1 = EventFactory(project=project, published_at=past, capacity_per_occurrence=10)
    occ1 = OccurrenceFactory(event=ev1, time=future)
    EnrolmentFactory(occurrence=occ1, child=child)

    ev2 = EventFactory(project=project, published_at=past, capacity_per_occurrence=10)
    occ2 = OccurrenceFactory(event=ev2, time=future + timedelta(days=1))
    EnrolmentFactory(occurrence=occ2, child=child)

    # Candidate event in same year with free capacity
    ev_candidate = EventFactory(
        project=project, published_at=past, capacity_per_occurrence=10
    )
    OccurrenceFactory(event=ev_candidate, time=future + timedelta(days=2))

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": get_global_id(child), "availableOnly": True},
    )
    assert executed.get("errors") is None
    # Yearly limit of 2 reached: candidate event in future.year must be excluded
    assert executed["data"]["events"]["edges"] == []


@pytest.mark.django_db
def test_events_search_ordering_and_cursor_pagination(
    guardian_api_client, project, past
):
    """
    Test cursor-based Relay pagination and chronological ordering across search results.

    Creates 3 events:
    - ev_early: upcoming occurrence in 2 days (1st in order)
    - ev_ext_middle: external event with registration opening in 5 days (2nd in order)
    - ev_late: upcoming occurrence in 10 days (3rd in order)

    Verifies pagination through exact object matching on page 1 and page 2 responses.
    """
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    now = timezone.now()

    ev_late = EventFactory(project=project, published_at=past, name="Late")
    OccurrenceFactory(event=ev_late, time=now + timedelta(days=10))

    ev_early = EventFactory(project=project, published_at=past, name="Early")
    OccurrenceFactory(event=ev_early, time=now + timedelta(days=2))

    ev_ext_middle = TicketmasterEventFactory(
        project=project,
        published_at=past,
        registration_opens_at=now + timedelta(days=5),
        name="External Middle",
    )

    pagination_query = """
    query EventsPagination($childId: ID!, $first: Int, $after: String) {
      events(childId: $childId, first: $first, after: $after) {
        count
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            id
            name
          }
        }
      }
    }
    """

    # Page 1 (first: 2): exact object match on first 2 items
    page1 = guardian_api_client.execute(
        pagination_query,
        variables={"childId": get_global_id(child), "first": 2},
    )
    cursor1 = page1["data"]["events"]["pageInfo"]["endCursor"]
    assert page1 == {
        "data": {
            "events": {
                "count": 3,
                "pageInfo": {
                    "hasNextPage": True,
                    "endCursor": cursor1,
                },
                "edges": [
                    {"node": {"id": get_global_id(ev_early), "name": "Early"}},
                    {
                        "node": {
                            "id": get_global_id(ev_ext_middle),
                            "name": "External Middle",
                        }
                    },
                ],
            }
        }
    }

    # Page 2 (first: 2, after: endCursor): exact object match on remaining item
    page2 = guardian_api_client.execute(
        pagination_query,
        variables={
            "childId": get_global_id(child),
            "first": 2,
            "after": cursor1,
        },
    )
    cursor2 = page2["data"]["events"]["pageInfo"]["endCursor"]
    assert page2 == {
        "data": {
            "events": {
                "count": 3,
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": cursor2,
                },
                "edges": [
                    {"node": {"id": get_global_id(ev_late), "name": "Late"}},
                ],
            }
        }
    }


@pytest.mark.django_db
def test_events_search_query_count_is_constant(
    guardian_api_client, project, past, future, django_assert_num_queries
):
    """
    Prove that the events search query count is strictly constant (O(1) database queries).

    1. Executes search with 3 events:
       - Captures baseline query count (13 queries):
         * User and child authorization check
         * Child project and prefetch relations (occurrences, passwords)
         * Events connection count query
         * Events page query with theme paths, occurrences, venues, and ticket passwords
       - Asserts 3 events returned.
    2. Adds 22 more events (total 25 events, including external ticketmaster events):
       - Asserts all 25 events returned.
       - Asserts query count is EXACTLY identical to the 3-event baseline (13 queries),
         proving complete absence of N+1 query regressions across event list scaling.
    """
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    tp = ThemePathFactory(slug="rhythm", name="Rytmi", description="")

    # Create initial 3 events with occurrences
    events_3 = EventFactory.create_batch(
        3,
        project=project,
        published_at=past,
        capacity_per_occurrence=10,
        theme_paths=[tp],
    )
    for i, ev in enumerate(events_3):
        OccurrenceFactory(event=ev, time=future + timedelta(days=i))

    variables = {"childId": get_global_id(child), "first": 25}
    # Warm up caches
    guardian_api_client.execute(EVENTS_SEARCH_QUERY, variables=variables)

    # Baseline: exactly 13 queries for 3 events
    with django_assert_num_queries(13) as captured_3:
        res_3 = guardian_api_client.execute(EVENTS_SEARCH_QUERY, variables=variables)
    assert res_3.get("errors") is None
    # Returns all 3 initial events
    assert len(res_3["data"]["events"]["edges"]) == 3

    # Add 22 more events: 20 internal + 2 ticketmaster (total 25 events)
    more_events = EventFactory.create_batch(
        20,
        project=project,
        published_at=past,
        capacity_per_occurrence=10,
        theme_paths=[tp],
    )
    for i, ev in enumerate(more_events):
        OccurrenceFactory(event=ev, time=future + timedelta(days=i + 3))
    ext_events = TicketmasterEventFactory.create_batch(
        2,
        project=project,
        published_at=past,
        theme_paths=[tp],
    )
    for ext in ext_events:
        TicketSystemPasswordFactory(event=ext, child=None)

    # 25 events must produce the EXACT same query count (13 queries) as 3 events
    with django_assert_num_queries(len(captured_3)):
        res_25 = guardian_api_client.execute(EVENTS_SEARCH_QUERY, variables=variables)
    assert res_25.get("errors") is None
    # Returns all 25 events in a single page
    assert len(res_25["data"]["events"]["edges"]) == 25


@pytest.mark.django_db
def test_events_search_query_count_with_all_filters(
    guardian_api_client, project, past, future, django_assert_num_queries
):
    """
    Verify constant O(1) query count when all search filters are simultaneously active.

    Sets up a child with past enrolments, 8 internal events, and 2 ticketmaster events
    matching all filters: availableOnly=True, themePaths=["rhythm"], languages=["fi"],
    startDate, familyOnly=False.

    Proves:
    - Search with all filters runs in exactly 14 queries (1 extra query compared to the
      basic search for filter join/count evaluations).
    - Querying 10 events: count == 10, len(edges) == 10.
    - Querying first 5 events (pagination): count == 10 (total matching), len(edges) == 5.
    - Query count for first 5 events is IDENTICAL to 10 events (14 queries), proving that
      pagination and heavy filtering do not introduce per-row N+1 queries.
    """
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    tp = ThemePathFactory(slug="rhythm", name="Rytmi", description="")

    # Existing enrolment on a past event for this child
    past_event = EventFactory(project=project, published_at=past, theme_paths=[tp])
    past_occ = OccurrenceFactory(event=past_event, time=past)
    EnrolmentFactory(child=child, occurrence=past_occ)

    # Create 10 matching events (8 internal + 2 ticketmaster)
    internal_events = EventFactory.create_batch(
        8,
        project=project,
        published_at=past,
        capacity_per_occurrence=10,
        theme_paths=[tp],
    )
    for i, ev in enumerate(internal_events):
        OccurrenceFactory(
            event=ev,
            time=future + timedelta(days=i + 1),
            occurrence_language="fi",
            capacity_override=10,
        )

    ticketmaster_events = TicketmasterEventFactory.create_batch(
        2,
        project=project,
        published_at=past,
        theme_paths=[tp],
    )
    for i, ext in enumerate(ticketmaster_events):
        OccurrenceFactory(
            event=ext,
            time=future + timedelta(days=i + 9),
            occurrence_language="fi",
        )
        TicketSystemPasswordFactory(event=ext, child=None)

    variables = {
        "childId": get_global_id(child),
        "first": 10,
        "availableOnly": True,
        "themePaths": ["rhythm"],
        "languages": ["fi"],
        "startDate": future.date().isoformat(),
        "familyOnly": False,
    }

    # Warm up caches
    guardian_api_client.execute(EVENTS_SEARCH_QUERY, variables=variables)

    # Exactly 14 queries when all filters are active (availableOnly, themePaths, languages, startDate)
    with django_assert_num_queries(14) as captured_10:
        res_10 = guardian_api_client.execute(EVENTS_SEARCH_QUERY, variables=variables)

    assert res_10.get("errors") is None
    # Exactly 10 events match all filter criteria
    assert res_10["data"]["events"]["count"] == 10
    # first: 10 returns all 10 matching edges
    assert len(res_10["data"]["events"]["edges"]) == 10

    # Querying first 5 events with same filters: query count is identical to 10 events (14 queries)
    variables_5 = dict(variables, first=5)
    with django_assert_num_queries(len(captured_10)):
        res_5 = guardian_api_client.execute(EVENTS_SEARCH_QUERY, variables=variables_5)

    assert res_5.get("errors") is None
    # Total matching count remains 10
    assert res_5["data"]["events"]["count"] == 10
    # first: 5 returns only the first 5 edges
    assert len(res_5["data"]["events"]["edges"]) == 5


@pytest.mark.django_db
def test_events_search_available_only_external_event_with_occurrence_filters(
    guardian_api_client, project, past, future
):
    """
    Verify that external ticket system events with `availableOnly=True` and
    `languages` / `startDate` filters check free passwords (not `remaining_capacity`).

    External ticket system events have `capacity_per_occurrence=None` and no
    `capacity_override`. When an upcoming occurrence matches `languages` and
    `startDate`:
    - Included when at least one unassigned `TicketSystemPassword` exists.
    - Excluded when all passwords are already assigned, even if `capacity_override`
      is artificially set.
    """
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    other_child = ChildWithGuardianFactory(project=project)

    ext_with_free_pw = TicketmasterEventFactory(project=project, published_at=past)
    OccurrenceFactory(
        event=ext_with_free_pw,
        time=future + timedelta(days=2),
        occurrence_language="sv",
    )
    TicketSystemPasswordFactory(event=ext_with_free_pw, child=None, assigned_at=None)

    ext_exhausted = TicketmasterEventFactory(project=project, published_at=past)
    OccurrenceFactory(
        event=ext_exhausted,
        time=future + timedelta(days=2),
        occurrence_language="sv",
        capacity_override=10,
    )
    TicketSystemPasswordFactory(
        event=ext_exhausted, child=other_child, assigned_at=past
    )

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={
            "childId": get_global_id(child),
            "availableOnly": True,
            "languages": ["sv"],
            "startDate": future.date().isoformat(),
        },
    )
    assert executed.get("errors") is None
    returned_ids = [e["node"]["id"] for e in executed["data"]["events"]["edges"]]
    assert returned_ids == [get_global_id(ext_with_free_pw)]


@pytest.mark.django_db
@freeze_time("2025-12-15T10:00:00Z")
def test_events_search_helsinki_new_year_boundary(guardian_api_client, project):
    """
    Verify that year boundaries use Helsinki local time (`Europe/Helsinki`)
    consistently across SQL `ExtractYear` and Python `year_of`.

    - `2025-12-31T23:30:00+02:00` (`2025-12-31T21:30:00Z`) belongs to 2025.
    - `2026-01-01T00:30:00+02:00` (`2025-12-31T22:30:00Z`) belongs to 2026 in
      Helsinki time (even though its UTC timestamp is in 2025).
    """
    helsinki = ZoneInfo("Europe/Helsinki")
    project.enrolment_limit = 1
    project.save()

    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    published = datetime(2025, 12, 1, 12, 0, tzinfo=helsinki)
    nye_2025 = datetime(2025, 12, 31, 23, 30, tzinfo=helsinki)
    nyd_2026 = datetime(2026, 1, 1, 0, 30, tzinfo=helsinki)

    # Child enrolls in an occurrence at 2026-01-01 00:30+02:00 (2025-12-31 22:30 UTC)
    ev_enrolled_2026 = EventFactory(
        project=project, published_at=published, capacity_per_occurrence=10
    )
    occ_enrolled_2026 = OccurrenceFactory(event=ev_enrolled_2026, time=nyd_2026)
    EnrolmentFactory(child=child, occurrence=occ_enrolled_2026)

    assert child.get_enrolment_count(year=2025) == 0
    assert child.get_enrolment_count(year=2026) == 1

    # Candidate event in 2025 (2025-12-31 23:30+02:00) is still available
    ev_candidate_2025 = EventFactory(
        project=project, published_at=published, capacity_per_occurrence=10
    )
    OccurrenceFactory(event=ev_candidate_2025, time=nye_2025)

    # Candidate event in 2026 (2026-01-01 00:30+02:00) is excluded because 2026 limit (1) is full
    ev_candidate_2026 = EventFactory(
        project=project, published_at=published, capacity_per_occurrence=10
    )
    OccurrenceFactory(event=ev_candidate_2026, time=nyd_2026 + timedelta(minutes=15))

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": get_global_id(child), "availableOnly": True},
    )
    assert executed.get("errors") is None
    returned_ids = [e["node"]["id"] for e in executed["data"]["events"]["edges"]]
    assert returned_ids == [get_global_id(ev_candidate_2025)]


@pytest.mark.django_db
def test_events_search_available_only_zero_enrolment_limit_returns_empty(
    guardian_api_client, project, past, future
):
    """When `project.enrolment_limit == 0`, `availableOnly=True` returns no events."""
    project.enrolment_limit = 0
    project.save()

    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    event = EventFactory(project=project, published_at=past, capacity_per_occurrence=10)
    OccurrenceFactory(event=event, time=future)

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={"childId": get_global_id(child), "availableOnly": True},
    )
    assert executed.get("errors") is None
    assert executed["data"]["events"]["count"] == 0
    assert executed["data"]["events"]["edges"] == []


@pytest.mark.django_db
def test_enrol_mutation_bypasses_child_cache_for_payload_resolvers(
    guardian_api_client, project, past, future
):
    """
    Verify that `enrolOccurrence` mutation payload resolvers (`canChildEnroll` and
    `enrolmentDeniedReason`) bypass `_child_cache` and return the updated post-enrolment state.
    """
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    event = EventFactory(project=project, published_at=past, capacity_per_occurrence=10)
    occurrence = OccurrenceFactory(event=event, time=future)

    mutation = """
    mutation EnrolAndCheck($input: EnrolOccurrenceMutationInput!, $childId: ID!) {
      enrolOccurrence(input: $input) {
        enrolment {
          occurrence {
            event {
              canChildEnroll(childId: $childId)
              enrolmentDeniedReason(childId: $childId)
            }
          }
        }
      }
    }
    """
    child_gid = get_global_id(child)
    executed = guardian_api_client.execute(
        mutation,
        variables={
            "input": {
                "occurrenceId": get_global_id(occurrence),
                "childId": child_gid,
            },
            "childId": child_gid,
        },
    )
    assert executed.get("errors") is None
    event_data = executed["data"]["enrolOccurrence"]["enrolment"]["occurrence"]["event"]
    assert event_data["canChildEnroll"] is False
    assert event_data["enrolmentDeniedReason"] == "ALREADY_JOINED_EVENT"


@pytest.mark.django_db
def test_events_search_grouped_events_query_count_is_constant(
    guardian_api_client, project, past, future, django_assert_num_queries
):
    """
    Verify that search query count with grouped events selecting enrolmentDeniedReason
    does not grow with page size.
    """
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    tp = ThemePathFactory(slug="rhythm", name="Rytmi", description="")

    for i in range(3):
        group = EventGroupFactory(project=project, published_at=past)
        ev = EventFactory(
            project=project,
            event_group=group,
            published_at=past,
            capacity_per_occurrence=10,
            theme_paths=[tp],
        )
        OccurrenceFactory(event=ev, time=future + timedelta(days=i))

    variables = {"childId": get_global_id(child), "first": 25}
    guardian_api_client.execute(EVENTS_SEARCH_QUERY, variables=variables)

    with django_assert_num_queries(14) as captured_3:
        res_3 = guardian_api_client.execute(EVENTS_SEARCH_QUERY, variables=variables)
    assert res_3.get("errors") is None
    assert len(res_3["data"]["events"]["edges"]) == 3
    assert all(
        edge["node"]["enrolmentDeniedReason"] is None
        for edge in res_3["data"]["events"]["edges"]
    )

    for i in range(22):
        group = EventGroupFactory(project=project, published_at=past)
        ev = EventFactory(
            project=project,
            event_group=group,
            published_at=past,
            capacity_per_occurrence=10,
            theme_paths=[tp],
        )
        OccurrenceFactory(event=ev, time=future + timedelta(days=i + 3))

    with django_assert_num_queries(len(captured_3)):
        res_25 = guardian_api_client.execute(EVENTS_SEARCH_QUERY, variables=variables)
    assert res_25.get("errors") is None
    assert len(res_25["data"]["events"]["edges"]) == 25
    assert all(
        edge["node"]["enrolmentDeniedReason"] is None
        for edge in res_25["data"]["events"]["edges"]
    )


@pytest.mark.django_db
def test_available_for_child_filter_exception_handling(
    guardian_api_client, user_api_client, project, past, future
):
    """
    Verify availableForChild preserves queryset for Child.DoesNotExist and returns
    empty queryset for ValidationError / ValueError.
    """
    from events.tests.queries import EVENT_GROUP_EVENTS_FILTER_QUERY

    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    event_group = EventGroupFactory(project=project, published_at=past)
    ev = EventFactory(
        project=project,
        event_group=event_group,
        published_at=past,
        name="Available Event",
    )
    OccurrenceFactory(event=ev, time=future)

    # Child.DoesNotExist (unviewable child for user_api_client) preserves qs
    res_does_not_exist = user_api_client.execute(
        EVENT_GROUP_EVENTS_FILTER_QUERY,
        variables={
            "id": get_global_id(event_group),
            "availableForChild": get_global_id(child),
        },
    )
    assert res_does_not_exist.get("errors") is None
    assert len(res_does_not_exist["data"]["eventGroup"]["events"]["edges"]) == 1

    # ValidationError (malformed UUID inside ChildNode global ID) returns empty qs
    res_invalid_uuid = guardian_api_client.execute(
        EVENT_GROUP_EVENTS_FILTER_QUERY,
        variables={
            "id": get_global_id(event_group),
            "availableForChild": to_global_id("ChildNode", "not-a-uuid"),
        },
    )
    assert res_invalid_uuid.get("errors") is None
    assert res_invalid_uuid["data"]["eventGroup"]["events"]["edges"] == []


@pytest.mark.django_db
@freeze_time("2025-12-15T10:00:00Z")
def test_events_search_available_only_checks_matching_occurrence_year_quota(
    guardian_api_client, project
):
    """
    Verify availableOnly checks the yearly quota against the matching upcoming
    available occurrence, even if the event's first occurrence is in an earlier
    year where the quota is not full.
    """
    helsinki = ZoneInfo("Europe/Helsinki")
    project.enrolment_limit = 1
    project.save()

    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    published = datetime(2025, 12, 1, 12, 0, tzinfo=helsinki)

    # Exhaust child's 2026 quota (limit = 1)
    ev_enrolled_2026 = EventFactory(
        project=project, published_at=published, capacity_per_occurrence=10
    )
    occ_enrolled_2026 = OccurrenceFactory(
        event=ev_enrolled_2026,
        time=datetime(2026, 1, 5, 12, 0, tzinfo=helsinki),
    )
    EnrolmentFactory(child=child, occurrence=occ_enrolled_2026)

    # Candidate event has a past/Finnish occurrence in 2025 (first occurrence year = 2025, not full)
    # and an upcoming Swedish occurrence in 2026 (where 2026 quota is full).
    ev_cross_year = EventFactory(
        project=project, published_at=published, capacity_per_occurrence=10
    )
    OccurrenceFactory(
        event=ev_cross_year,
        time=datetime(2025, 12, 20, 12, 0, tzinfo=helsinki),
        occurrence_language="fi",
    )
    OccurrenceFactory(
        event=ev_cross_year,
        time=datetime(2026, 1, 10, 12, 0, tzinfo=helsinki),
        occurrence_language="sv",
    )

    executed = guardian_api_client.execute(
        EVENTS_SEARCH_QUERY,
        variables={
            "childId": get_global_id(child),
            "availableOnly": True,
            "languages": ["sv"],
        },
    )
    assert executed.get("errors") is None
    assert executed["data"]["events"]["edges"] == []


@pytest.mark.django_db
def test_assign_password_mutation_invalidates_child_cache_on_success_and_preserves_on_failure(
    guardian_api_client, project, past
):
    """
    Verify that AssignTicketSystemPasswordMutation invalidates _child_cache for the child
    after a successful assignment and preserves _child_cache when assignment fails.
    """
    child = ChildWithGuardianFactory(
        relationship__guardian=guardian_api_client.user.guardian,
        project=project,
    )
    ev1 = TicketmasterEventFactory(project=project, published_at=past)
    TicketSystemPasswordFactory(event=ev1, value="PW-1", child=None)

    ev2 = TicketmasterEventFactory(project=project, published_at=past)

    mutation = """
    mutation AssignTwo(
      $input1: AssignTicketSystemPasswordMutationInput!
      $input2: AssignTicketSystemPasswordMutationInput!
      $childId: ID!
    ) {
      first: assignTicketSystemPassword(input: $input1) {
        password
        event {
          canChildEnroll(childId: $childId)
          enrolmentDeniedReason(childId: $childId)
          ticketSystem {
            ... on TicketmasterEventTicketSystem {
              childPassword(childId: $childId)
            }
          }
        }
      }
      second: assignTicketSystemPassword(input: $input2) {
        password
      }
    }
    """
    child_gid = get_global_id(child)
    executed = guardian_api_client.execute(
        mutation,
        variables={
            "input1": {"eventId": get_global_id(ev1), "childId": child_gid},
            "input2": {"eventId": get_global_id(ev2), "childId": child_gid},
            "childId": child_gid,
        },
    )
    first_data = executed["data"]["first"]
    assert first_data["password"] == "PW-1"
    assert first_data["event"]["canChildEnroll"] is False
    assert (
        first_data["event"]["enrolmentDeniedReason"] == "ALREADY_HAS_PASSWORD_TO_EVENT"
    )
    assert first_data["event"]["ticketSystem"]["childPassword"] == "PW-1"
    assert executed["data"]["second"] is None
    assert executed.get("errors") is not None
